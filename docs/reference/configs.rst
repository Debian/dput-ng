Configuration File Overview
===========================

There are a few changes between dput and dput-ng's handling of configuration
files. The changes can be a bit overwhelming, but stick to what's in here
and it should all make great sense.

High Level Changes
------------------

Firstly, you should know dput-ng fully supports the old dput.cf style
configuration file. However, it also defines its own own,
`JSON <http://en.wikipedia.org/wiki/JSON>`_ encoded. Settings which are
specific to dput-ng, in particular hooks and profiles can only be defined
in dput-ng's configuration style. It is possible to run dput-ng with old-style
configuration files only, with new-style configuration files only and even with
shared profiles, where both new-style and old-style dput configuration files
partially define behavior of a stanza.

By default, dput-ng will look for configuration files in one of three places:
``/usr/share/dput-ng/``, ``/etc/dput.d/`` and ``~/.dput.d/``. Files in each
location are additive, except in the case of a key conflict, in which case,
the key is overridden by the next file. The idea here is that packages must
ship defaults in ``/usr/share/dput-ng``. If the system admin wishes to override
the defaults on a per-host basis, the file may be overridden in ``/etc/dput.d``.
If a user wishes to override either of the decisions above, they may modify
it in the local ``~/.dput.d`` directory.

Defaults (e.g. the old [DEFAULT] section) are shared (new-style location is in
``profiles/DEFAULT.json``), so changing default behavior should affect the
target, regardless of how it's defined. In the case of two defaults conflicting,
the new-style configuration is chosen.

Order of Loading
----------------

If all possible files and directories exist, this is order of loading of files:

1. /usr/share/dput-ng/ (new-style default profiles)
2. /etc/dput.d (new-style site-wide profiles),
3. /etc/dput.cf (old-style site-wide profiles)
4. ~/.dput.d (new-style local profiles)
5. ~/.dput.cf (old-style local profiles)
6. Any file supplied via command line.

To remove a profile entirely, see operator handling below.

Theory
------

New-style config files have two core attributes -- ``class`` and ``name``.
For a upload target, that's known as a ``profile``. Technically speaking, any
config file is located in ``${CONFIG_DIR}/class/name.json``.

Keys can also be prefixed with one of three "operators". Operators tell
dput-ng to preform an operation on the data structure when merging the
layers together.

Addition::


    # global configuration block
    {
        "foo": [
            'one',
            'two'
        ]
    }

    # local configuration block
    {
        "+foo": [
            'three'
        ]
    }

    # resulting data structure:
    {
        "foo": [
            'one',
            'two',
            'three'
        ]
    }

Subtraction::

    # global configuration block
    {
        "foo": [
            'one',
            'two',
            'three'
        ]
    }

    # local configuration block
    {
        "-foo": [
            'three'
        ]
    }

    # resulting data structure:
    {
        "foo": [
            'one',
            'two'
        ]
    }

Assignment::

    # It should be noted that this *IS* the same as not prefixing the block
    # by an "=" operator. Please don't use this? Kay? It just uses up cycles
    # and is only here to be a logical extension of the last two.

    # global configuration block
    {
        "foo": [
            'one',
            'two',
            'three'
        ]
    }

    # local configuration block
    {
        "=foo": [
            'three'
        ]
    }

    # resulting data structure:
    {
        "foo": [
            'three'
        ]
    }


Meta
----

The most complex part of these files is the "meta" target. Internally, this
will fetch the config file from the ``metas`` class with the name provided
in the config's ``meta`` attribute. The resulting object is placed under
the config.

Meta configs can declare another meta config, but will not work if it's
self-referencing. Don't do that.

Practice
--------

OK, let's look at some real config files.

I've implemented PPAs as a pure-JSON upload target. This file lives in
profiles/ppa.json. It looks something like::

    {
        "meta": "ubuntu",
        "fqdn": "ppa.launchpad.net",
        "incoming": "~%(ppa)s",
        "login": "anonymous",
        "method": "ftp"
    }


You'll notice the old-style substring replacement is the same. While looking
a bit deeper, you'll also notice that we inherit from the Ubuntu meta-class.


Overriding default hook behavior
-----------------------------------

It's idiomatic to just *extend* what you get from your parent (e.g. use the
prefix operators ``+`` or ``-``, so that you don't have to duplicate the same
list over and over.
