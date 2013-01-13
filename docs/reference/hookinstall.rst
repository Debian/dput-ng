Installing Hooks
================

This guide will cover exactly how dput-ng handles hooks, and the proper way
to install, distribute and tool with hooks. Remember, Hooks are your friend!


So, what exactly are hooks?
---------------------------

Well, it's pretty simple, actually -- a hook is a Python importable function
that takes a few arguments, which are populated with internal dput-ng objects.
These objects contain such things as a way to talk to the user, the processed
.changes file, and the upload target.

Hooks can run either before or after an upload, and hooks that run before
the upload may halt an upload by raising a
:class:`dput.exceptions.HookException` (or a subclass of that).


Alright, you mentioned Python-importable, what exactly does that mean?
----------------------------------------------------------------------

The path given is a fully qualified path to the hook. Here's an example::

    >>> from os.path import abspath

The dput-ng style "fully qualified path" to that function (abspath) would
be::

    os.path.abspath

It's really that simple.

.. note::
    It's also worth noting dput-ng adds a few directories to sys.path to
    aid with debugging and distributing trivial scripts. For each directory
    in :data:`dput.core.CONFIG_LOCATIONS`, that directory plus "scripts" will
    be added to the system path, so (commonly) ``~/.dput.d/scripts`` and
    ``/etc/dput.d/scripts`` are valid Python path roots to dput-ng.

OK, let's do an example.
------------------------

Let's do a simple checker -- one that fails out if Arno is the maintainer::

    def check_for_arno(changes, profile, interface):
        """
        The ``arno`` checker will explode in a firey mess if
        Arno tries to upload anything to the archive.

        This checker doesn't change it's behavior given any Profile codes.
        """
        maintainer = changes['Maintainer']
        if "arno@debian.org" in maintainer:
            raise HookException("Arno's not alowed to Upload.")

I've saved this file to ``~/.dput.d/scripts/arno.py``. It should be noted that
dput-ng can now import this file as ``arno``, and the command (from inside
dput-ng) ``from arno import check_for_arno`` will work.

Since we need to tell dput-ng about this hook, we need to drop it's def into
a dput hook directory. Let's use our home directory again, even though it should
be noted both ``/usr/share/dput-ng/`` and ``/etc/dput.d/`` will work as well.

I've placed ``arno.json`` into ``~/.dput.d/hooks/arno.json``::

    {
        "description": "Blow up if Arno's maintaining this package.",
        "path": "arno.check_for_arno",
        "pre": true
    }

The ``pre`` key, or the ``post`` key must be present and set to a boolean. If no
key is given, it assumes it's a ``pre`` checker. The ``path`` is the
Python-importable path to the hook function, and ``description`` is for humans
looking to get some information on the hook.

We can make sure it works using ``dirt(1)``::

    $ dirt info --hook arno

        The ``arno`` checker will explode in a firey mess if Arno tries to upload
        anything to the archive.

        This checker doesn't change it's behavior given any Profile codes.

Remember, this pulls from the docstring, so please leave docstrings!


OK. Now that dput-ng is aware of the plugin, we can add it to a profile by
adding a "plus-key" to your profile choice. Let's add this to ``ftp-master``,
since we want to make sure Arno never uploads there.

Here's my (user-local) ftp-master config ``~/.dput.d/profiles/ftp-master.json``::

    {
        "+hooks": [
            "arno"
        ]
    }

If you want to learn more about why this syntax works, I'd suggest checking out
the :doc:`configs` documentation.

So, let's try uploading::

    $ dput [...]
    [...]
    running check-debs: makes sure the upload contains a binary package
    running checksum: verify checksums before uploading
    running suite-mismatch: check the target distribution for common errors
    running arno: Blow up if Arno's maintaining this package.
    Arno's not alowed to Upload.
    $ echo $?
    1

Nice!
