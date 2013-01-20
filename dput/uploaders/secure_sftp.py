# -*- coding: utf-8 -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

# Copyright (c) 2013 dput authors
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your Option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
# 02110-1301, USA.
"""
SFTP Uploader implementation
still EXPERIMENTAL, and only working with python >= 3.2
"""

import os.path
import subprocess
import select

from dput.core import logger
from dput.uploader import AbstractUploader
from dput.exceptions import UploadException

class EnumInternException(Exception):
    def __init__(self, v):
        super().__init__(v)
        self.value = v

class Enum:
    def __init__(self, name, value):
        if isinstance(name, str):
            self.name = name
        else:
            self.name = name[0]
        self.__name__ = self.name
        self.value = value
        type(self).byvalue[value] = self
        if isinstance(name, str):
            type(self).byname[name] = self
            setattr(type(self), name, self)
        else:
            for n in name:
                type(self).byname[n] = self
                setattr(type(self), n, self)

    def __int__(self):
        return self.value

    def __str__(self):
        return self.name

    @classmethod
    def intern(cls, l):
        try:
            if isinstance(l, cls):
                return l
            elif isinstance(l, int):
                return cls.byvalue[l]
            elif isinstance(l, str):
                return cls.byname[l]
            else:
                raise EnumInternException(repr(l))
        except KeyError:
            raise EnumInternException(repr(l))

    @classmethod
    def create(cls, name, values):
        class enum(Enum):
            __name__ = name
            byvalue = dict()
            byname = dict()
        for (k, v) in values.items():
            e = enum(k, v)
        return enum

class Bitmask(set):
    byname = dict()
    byvalue = dict()

    def __init__(self, l):
        if isinstance(l, int):
            super().__init__(
                             [i for (k, i) in self.Values.byvalue.items() if
                              (l & i.mask) == k])
            if l != int(self):
                raise Exception(
                    "Unrepresentable number %d (got parsed as %s = %d)" %
                    (l, str(self), int(self))
                    )
        elif isinstance(l, str):
            try:
                super().__init__([self.Values.intern(i) for i in l.split("|")])
                # test for inconsistencies:
                type(self)(int(self))
            except EnumInternException as e:
                raise Exception("Invalid value '%s' in value '%s' for %s" %
                                (e.value, str(l), type(self).__name__))
        else:
            try:
                super().__init__([self.Values.intern(i) for i in l])
                # test for inconsistencies:
                type(self)(int(self))
            except EnumInternException as e:
                raise Exception("Invalid value '%s' in value '%s' for %s" %
                                (e.value, str(l), type(self).__name__))

    def __int__(self):
        v = 0
        for i in self:
            v = v | int(i)
        return v

    def __str__(self):
        return "|".join([str(i) for i in self])

    @classmethod
    def create(cls, name, values):
        class bitmask(Bitmask):
            __name__ = "Bitmask of " + name

            class Values(Enum):
                __name__ = name
                byvalue = dict()
                byname = dict()
        bitmask.__name__ = "Bitmask of " + name
        for (k, v) in values.items():
            if isinstance(v, int):
                e = bitmask.Values(k, v)
                e.mask = v
            else:
                e = bitmask.Values(k, v[0])
                e.mask = v[1]
        return bitmask

class SftpUploadException(UploadException):
    """
    Thrown in the event of a problem connecting, uploading to or
    terminating the connection with the remote server. This is
    a subclass of :class:`dput.exceptions.UploadException`.
    """
    pass

# Unparseable stuff from server:
class SftpStrangeException(SftpUploadException):
    pass
class SftpUnexpectedAnswerException(SftpStrangeException):
    def __init__(self, answer, request):
        super().__init__("Unexpected answer '%s' to request '%s'" %
                         (str(answer), str(request)))
class SftpTooManyRequestsException(SftpUploadException):
    def __init__(self):
        super().__init__("Too many concurrent requests (out of request ids)")
# a programming or programmer mistake:
class SftpInternalException(SftpUploadException):
    pass

def ssh_data(b):
    return len(b).to_bytes(4, byteorder='big') + b
def ssh_string(s):
    b = str(s).encode(encoding='utf-8')
    return len(b).to_bytes(4, byteorder='big') + b
def ssh_u8(i):
    return int(i).to_bytes(1, byteorder='big')
def ssh_u32(i):
    return int(i).to_bytes(4, byteorder='big')
def ssh_u64(i):
    return int(i).to_bytes(8, byteorder='big')
def ssh_attrs(**opts):
    return int(0).to_bytes(4, byteorder='big')
def ssh_getu32(m):
    v = int.from_bytes(m[:4], byteorder='big')
    return v, m[4:]
def ssh_getstring(m):
    l = int.from_bytes(m[:4], byteorder='big')
    return (m[4:4 + l].decode(encoding='utf-8'), m[4 + l:])
def ssh_getdata(m):
    l = int.from_bytes(m[:4], byteorder='big')
    return (m[4:4 + l], m[4 + l:])


class Sftp:
    class Request:
        def __init__(self):
            pass

        def __int__(self):
            return self.requestid

        @classmethod
        def bin(cls, req, *payload):
            if isinstance(req, int):
                r = req
            else:
                r = req.requestid
            s = 5
            for b in payload:
                s = s + len(b)
            binary = ssh_u32(s) + ssh_u8(cls.typeid) + ssh_u32(r)
            for b in payload:
                binary = binary + b
            return binary

        def done(self):
            if self.requestid != None:
                del self.conn.requests[self.requestid]
                self.requestid = None

    class INIT(Request):
        typeid = 1

        @classmethod
        def bin(cls, version):
            # INIT has no request id but instead sends a protocol version
            return super().bin(int(version))
    VERSION = 2

    class OPEN(Request):
        typeid = 3
        Flags = Bitmask.create("SSH_FXF", {
                                           "READ": 0x00000001,
                                           "WRITE": 0x00000002,
                                           "APPEND": 0x00000004,
                                           "CREAT": 0x00000008,
                                           "TRUNC": 0x00000010,
                                           "EXCL": 0x00000020,
        })

        def __init__(self, name, flags, **attributes):
            super().__init__()
            self.name = name
            self.flags = self.Flags(flags)
            self.attrs = attributes

        @classmethod
        def bin(cls, req, name, flags, attrs):
            return super().bin(req, ssh_string(name), ssh_u32(flags),
                               ssh_attrs(**attrs))

        def send(self, conn):
            conn.send(self.bin(self, self.name, self.flags, self.attrs))

        def __str__(self):
            return "OPEN '%s' %s=%d" % (self.name, self.flags, self.flags)

    class CLOSE(Request):
        typeid = 4

        def __init__(self, handle):
            super().__init__()
            self.handle = handle

        @classmethod
        def bin(cls, req, handle):
            return super().bin(req, ssh_data(handle))

        def send(self, conn):
            conn.send(self.bin(self, self.handle))

        def __str__(self):
            return "close %s" % (self.handle)
    READ = 5

    class WRITE(Request):
        typeid = 6

        def __init__(self, handle, start, data):
            super().__init__()
            self.handle = handle
            self.start = start
            self.data = data

        @classmethod
        def bin(cls, req, handle, start, data):
            return super().bin(req, ssh_data(handle), ssh_u64(start),
                               ssh_data(bytes(data)))

        def send(self, conn):
            conn.send(self.bin(self, self.handle, self.start, self.data))

        def __str__(self):
            return "write %s,%d,%s" % (repr(self.handle), self.start,
                                       repr(self.data))

    LSTAT = 7
    FSTAT = 8
    SETSTAT = 9
    FSETSTAT = 10
    OPENDIR = 11
    READDIR = 12

    class REMOVE(Request):
        typeid = 13

        def __init__(self, name):
            super().__init__()
            self.name = name

        @classmethod
        def bin(cls, req, name):
            return super().bin(req, ssh_string(name))

        def send(self, conn):
            conn.send(self.bin(self, self.name))

        def __str__(self):
            return "rm '%s'" % self.name

    class MKDIR(Request):
        typeid = 14

        def __init__(self, directory, **attrs):
            super().__init__()
            self.dir = directory
            self.attrs = attrs

        @classmethod
        def bin(cls, req, directory, attrs):
            return super().bin(req, ssh_string(directory),
                ssh_attrs(**attrs))

        def send(self, conn):
            conn.send(self.bin(self, self.dir, self.attrs))

        def __str__(self):
            return "mkdir '%s'" % self.dir

    class RMDIR(Request):
        typeid = 15

        def __init__(self, directory):
            super().__init__()
            self.dir = directory

        @classmethod
        def bin(cls, req, directory):
            return super().bin(req, ssh_string(directory))

        def send(self, conn):
            conn.send(self.bin(self, self.dir))

        def __str__(self):
            return "rmdir '%s'" % self.dir
    REALPATH = 16
    STAT = 17


    class RENAME(Request):
        typeid = 18
        Flags = Bitmask.create("SSH_FXF_RENAME", {
                                                  'OVERWRITE': 0x00000001,
                                                  'ATOMIC': 0x00000002,
                                                  'NATIVE': 0x00000004})

        def __init__(self, src, dst, flags):
            super().__init__()
            self.src = src
            self.dst = dst
            if isinstance(flags, self.Flags):
                self.flags = flags
            else:
                self.flags = self.Flags(flags)

        @classmethod
        def bin(cls, req, src, dst, flags):
            return super().bin(req, ssh_string(src),
                ssh_string(dst), ssh_u32(flags))

        def send(self, conn):
            conn.send(self.bin(self, self.src, self.dst, self.flags))

        def __str__(self):
            return "rename '%s' into '%s' (%s)" % (
                                        self.src, self.dst, str(self.flags))
    READLINK = 19
    SYMLINK = 20
    EXTENDED = 200
    EXTENDED_REPLY = 201

    class Answer:
        def __int__(self):
            return self.typeid

    class STATUS(Answer):
        Status = Enum.create("SSH_FX", {
                                        "OK": 0,
                                        "EOF": 1,
                                        "NO_SUCH_FILE": 2,
                                        "PERMISSION_DENIED": 3,
                                        "FAILURE": 4,
                                        "BAD_MESSAGE": 5,
                                        "NO_CONNECTION": 6,
                                        "CONNECTION_LOST": 7,
                                        "OP_UNSUPPORTED": 8,
                                        "INVALID_HANDLE": 9,
                                        "NO_SUCH_PATH": 10,
                                        "FILE_ALREADY_EXISTS": 11,
                                        "WRITE_PROTECT": 12,
                                        "NO_MEDIA": 13})
        id = 101

        def __init__(self, m):
            s, m = ssh_getu32(m)
            self.status = self.Status.intern(s)
            self.message, m = ssh_getstring(m)
            self.lang, m = ssh_getstring(m)

        def __str__(self):
            return "STATUS %s: %s[%s]" % (
                str(self.status),
                self.message,
                self.lang)

    class HANDLE(Answer):
        id = 102

        def __init__(self, m):
            self.handle, m = ssh_getdata(m)

        def __str__(self):
            return "HANDLE %s" % repr(self.handle)

    class DATA(Answer):
        id = 103

        def __init__(self, m):
            self.data, m = ssh_getdata(m)

        def __str__(self):
            return "DATA %s" % repr(self.data)


    class NAME(Answer):
        id = 104

        def __init__(self, m):
            # TODO
            pass

        def __str__(self):
            return "NAME"

    class ATTRS(Answer):
        id = 105

        def __init__(self, m):
            # TODO
            pass

        def __str__(self):
            return "ATTRS"

    class Task:
        def start(self, connection):
            self.connection = connection

        def enqueuejobs(self, jobs):
            self.connection.enqueue(jobs, self)

    class TaskFromGenerator(Task):
        def __init__(self, gen):
            super().__init__()
            self.gen = gen

        def start(self, connection):
            super().start(connection)
            self.enqueuejobs(next(self.gen))

        def parentinfo(self, command):
            self.enqueuejobs(self.gen.send(command))

        def sftpanswer(self, answer):
            self.enqueuejobs(self.gen.send(answer))

        def __str__(self):
            return "Task(by %s)" % self.gen

    def next_request_id(self):
        i = self.requestid_try_next
        while i in self.requests:
            i = (i + 1) % 0x100000000
            if i == self.requestid_try_next:
                raise SftpTooManyRequestsException()
        self.requestid_try_next = (i + 1) % 0x100000000
        return i

    def __init__(self, **options):
        self.requests = dict()
        self.queue = list()
        self.requestid_try_next = 17
        commandline = ["ssh"]
        if "ssh_options" in options:
            commandline.extend(options["ssh_options"])
        # those defaults are after the user-supplied ones so they can be overriden.
        # (earlier ones win with ssh).
        commandline.extend(["-oProtocol 2", # "-oLogLevel DEBUG",
            "-oForwardX11 no", "-oForwardAgent no",
            "-oPermitLocalCommand no", "-oClearAllForwardings yes"])
        if "username" in options and options["username"]:
            commandline.extend(["-l", options["username"]])
        commandline.extend(["-s", "--", options["servername"], "sftp"])
        print(commandline)
        self.connection = subprocess.Popen(commandline,
                                           close_fds=True,
                                           stdin=subprocess.PIPE,
                                           stdout=subprocess.PIPE)
        self.poll = select.poll()
        self.poll.register(self.connection.stdout, select.POLLIN)
        self.inbuffer = bytes()
        self.send(self.INIT.bin(3))
        t, b = self.getpacket()
        if t != self.VERSION:
            raise SftpUnexpectedAnswerException(b, "INIT")
        # TODO: parse answer data (including available extensions)

    def close(self):
        self.connection.send_signal(15)

    def getmoreinput(self, minlen):
        while len(self.inbuffer) < minlen:
            o = self.connection.stdout.read(minlen - len(self.inbuffer))
            if o == None:
                continue
            if len(o) == 0:
                raise SftpStrangeException("unexpected EOF")
            self.inbuffer = self.inbuffer + o

    def getpacket(self):
        self.getmoreinput(5)
        s = int.from_bytes(self.inbuffer[:4], byteorder='big')
        if s < 1:
            raise SftpStrangeException("Strange size field in Paket from server!")
        s = s - 1
        t = self.inbuffer[4]
        self.inbuffer = self.inbuffer[5:]
        self.getmoreinput(s)
        d = self.inbuffer[:s]
        self.inbuffer = self.inbuffer[s:]
        #print("got: ", t, d)
        return (t, d)

    def send(self, b):
        if not isinstance(b, bytes):
            raise SftpInternalException("send not given byte sequence")
        #print(b)
        self.connection.stdin.write(b)

    def enqueue(self, joblist, gen):
        if len(joblist) == 0:
            return
        if len(self.queue) == 0:
            self.poll.register(self.connection.stdin, select.POLLOUT)
        for job in joblist:
            if isinstance(job, self.Request):
                job.task = gen
            else:
                raise SftpUploadException("Unexpected data from task: %s" %
                                          repr(gen))
        self.queue.extend(joblist)

    def start(self, task):
        task.start(self)


    def dispatchanswer(self, answer):
        task = answer.forr.task
        try:
            task.sftpanswer(answer)
        except StopIteration:
            orphanreqs = [r for r in self.requests.values() if
                          r.task == task]
            for r in orphanreqs:
                r.done()

    def readdata(self):
        t, m = self.getpacket()
        for answer in self.Answer.__subclasses__():
            if t == answer.id:
                request_id, m = ssh_getu32(m)
                a = answer(m)
                if not request_id in self.requests:
                    raise SftpUnexpectedAnswerException(a,
                                                    "unknown-id-%d" % request_id)
                else:
                    a.forr = self.requests[request_id]
                    self.dispatchanswer(a)
                break
        else:
            raise SftpUnexpectedAnswerException("Unknown answer type %d" %
                                                t, "")

    def dispatch(self):
        while self.requests or self.queue:
            for (_, event) in self.poll.poll():
                if event == select.POLLIN:
                    self.readdata()
                elif event == select.POLLHUP:
                    raise SftpStrangeException(
                                            "Server disconnected unexpectedly")
                elif event == select.POLLOUT:
                    request = self.queue.pop(0)
                    request.requestid = self.next_request_id()
                    request.conn = self
                    self.requests[request.requestid] = request
                    request.send(self)
                    if len(self.queue) == 0:
                        self.poll.unregister(self.connection.stdin)
                else:
                    raise SftpUploadException(
                                    "Unexpected event %d from poll" % event)

    def put(self, filename, localfilename):
        self.start(Sftp.TaskFromGenerator(writefile(filename, localfilename)))
        self.dispatch()

class filepart:

    def __init__(self, fh, start, length):
        self.fh = fh
        self.start = start
        self.len = length

    def __bytes__(self):
        self.fh.seek(self.start, 0)
        b = self.fh.read(self.len)
        while len(b) < self.len:
            b = b + self.fh.read(self.len - len(b))
        return b

def writefile(filename, localfile):
    localf = open(localfile, 'rb')
    size = os.fstat(localf.fileno()).st_size
    a = yield [Sftp.OPEN(filename, "CREAT|WRITE|TRUNC")]
    a.forr.done()
    if isinstance(a, Sftp.STATUS):
        if a.status == a.Status.NO_SUCH_FILE:
            raise SftpUploadException("Failed to create %s: No such file. (Perhaps the directory is missing?)" % filename)
        else:
            raise SftpUploadException("Failed to create %s: %s" % (filename, a))
    if not isinstance(a, Sftp.HANDLE):
            raise SftpUnexpectedAnswerException(a, a.forr)
    h = a.handle
    a.forr.done()
    ranges = list(range(0, size, 32600))
    if ranges:
        requests = [Sftp.WRITE(h, r, filepart(localf, r, 32600))
                     for r in ranges[:-1]]
        requests.append(Sftp.WRITE(h, ranges[-1],
                            filepart(localf, ranges[-1], size - ranges[-1])))
        a = yield requests
        while requests:
            a.forr.done()
            if not isinstance(a, Sftp.STATUS):
                raise SftpUnexpectedAnswerException(a, a.forr)
            elif a.status != a.Status.OK:
                raise SftpUploadException("Error writing to %s: %s: %s" % (
                                                  filename, a.forr, a))
            requests.remove(a.forr)
            a = yield []
    a = yield [Sftp.CLOSE(h)]
    a.forr.done()
    if not isinstance(a, Sftp.STATUS):
        raise SftpUnexpectedAnswerException(a, a.forr)
    elif a.status != a.Status.OK:
        raise SftpUploadException("Error writing to %s: %s: %s" % (
                                          filename, a.forr, a))

class SFTPUploader(AbstractUploader):
    """
    Provides an interface to upload files through SFTP.

    This is a subclass of :class:`dput.uploader.AbstractUploader`
    """

    def initialize(self, **kwargs):
        """
        See :meth:`dput.uploader.AbstractUploader.initialize`
        """
        fqdn = self._config['fqdn']
        incoming = self._config['incoming']

        ssh_options = []
        if "ssh_options" in self._config:
            ssh_options.extend(self._config['ssh_options'])
        if 'port' in self._config:
            ssh_options.append("-oPort=%d" % self._config['port'])
        username = None
        if 'login' in self._config and self._config['login'] != "*":
            username = self._config['login']

        if incoming.startswith('~/'):
            logger.warning("SFTP does not support ~/path, continuing with"
                           "relative directory name instead.")
            incoming = incoming[2:]

        if username:
            logger.info("Logging into host %s as %s" % (fqdn, username))
        else:
            logger.info("Logging into host %s" % fqdn)
        self._sftp = Sftp(servername=fqdn, username=username,
                               ssh_options=ssh_options)
        self.incoming = incoming

    def upload_file(self, filename, upload_filename=None):
        """
        See :meth:`dput.uploader.AbstractUploader.upload_file`
        """

        if not upload_filename:
            upload_filename = os.path.basename(filename)

        upload_filename = os.path.join(self.incoming, upload_filename)
        logger.debug("Writing to: %s" % (upload_filename))

        self._sftp.put(upload_filename, filename)

    def shutdown(self):
        """
        See :meth:`dput.uploader.AbstractUploader.shutdown`
        """
        self._sftp.close()
