Configuration File Overview
===========================

There are a few changes between dput and dput-ng's handling of configuration
files. The changes can be a bit overwhelming, but stick to what's in here
and it should all make great sense.

High level changes
------------------

Firstly, you should know dput-ng fully supports the old dput.cf style
configuration file. The biggest change is that dput-ng will prefer it's own,
`JSON <http://en.wikipedia.org/wiki/JSON>`_ encoded format over dput.cf.

By default, dput-ng will look for configuration files in one of three places:
``/usr/share/dput-ng/``, ``/etc/dput.d/`` and ``~/.dput.d/``. Files in each
location are additive, except in the case of a key conflict, in which case,
the key is overriden by the next file. The idea here is that packages must
ship defaults in ``/usr/share/dput-ng``. If the system admin wishes to override
the defaults on a per-host basis, the file may be overriden in ``/etc/dput.d``.
If a user wishes to override either of the decisions above, they may modify
it in the local ``~/.dput.d`` directory.

Defaults (e.g. the old [DEFAULT] section) are shared (new-style location is in
``profiles/DEFAULT.json``), so changing default behavior should affect the
target, regardless of how it's defined. In the case of two defaults conflicting,
the new-style configuration is chosen.

Theory
------

New-style config files have two core attributes -- ``class`` and ``name``.
For a upload target, that's known as a ``profile``. Technically speaking, any
config file is located in ``${CONFIG_DIR}/class/name.json``. The only exception
is the ``metas`` class. Any config may define a ``meta`` key, and it will also
inherit from the corresponding ``metas`` json file. Meta configuration files
may also declare a meta key.

Phew, that was a lot. I know that's a bit overwhelming, but basically, this
means you can ship a profile "default" group, such as ``ubuntu`` or ``debian``.
Since Ubuntu and Debian have different requirements on what to upload
(source-only vs binary-included), you will now be able to declare upload targets
as Ubuntu or Debian, which tell the file-checker different things.

Basically, this means, without changing the configuration, that you can set
dput to give you an error when you attempt to upload .debs to a PPA, and then
turn around, and get a warning that you've forgotten .debs on a push to
ftp-master.

Nice, right?

Practice
--------

OK, let's look at some real config files.

I've implemented PPAs as a pure-JSON upload target. This file lives in
profiles/ppa.json. It looks something like::

    {
        "meta": "ubuntu",
        "fqdn": "ppa.launchpad.net",
        "incoming": "~%(ppa)s/ubuntu",
        "login": "anonymous",
        "method": "ftp"
    }


You'll notice the old-style substring replacement is the same. While looking
a bit deeper, you'll also notice that we inherit from the Ubuntu meta-class.


Overriding default checker behavior
-----------------------------------

.. XXX TODO
