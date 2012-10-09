.. configs:

===========================
Configuration File Overview
===========================

There are a few changes between dput and dput-ng's handling of configuration
files. The changes can be a bit overwhelming, but stick to what's in here
and it should all make great sense.

High level changes
==================

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
======

New-style config files have two core attributes -- ``class`` and ``name``.
For a upload target, that's known as a ``profile``. Technically speaking, any
config file is located in ``${CONFIG_DIR}/class/name.json``. The only exception
is the ``metas`` class. Any config may define a ``meta`` key, and it will also
inherit from the corresponding ``metas`` json file. Meta configuration files
may also declare a meta key.


