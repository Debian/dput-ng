Object Core
===========

The *core* is a place where all the central objects live. This is used so that
all the different modules in dput can access common constants. This helps us
fake data (great for testing), and maintain sanity.

The Logger
----------

Printing to the screen using :func:`print` is wrong, m'kay? Please do **not**
use it under any conditions. In it's place, we have a central ``logger``
object, to use as all the bits of dput see fit.

The logger object is an instantiation of :class:`dput.logger.DputLogger`, so
feel free to use any if it's logging methods. In general, don't use
``info`` or above, unless the user *really* needs to know. Most calls should be
to ``debug`` or ``trace``.

Example usage::

    from dput.core import logger
    logger.debug("Hello, World!")
    logger.warning("OH MY DEAR GOD")

Configuration Objects
---------------------

The core contains two config directories, which are used by the config
modules (as well as other, more friendly places).

All configs are in the form of a dict, the key being the path, and the
value being the "weight" of the path. The higher the weight, the less
important it is.

Example ``dput.core.CONFIG_LOCATIONS``::

    {
        "/usr/share/dput-ng/": 30,
        "/etc/dput.d/": 20,
        os.path.expanduser("~/.dput.d"): 10,
    }

:func:`dput.util.load_config` is used to access a config from this list,
and handles meta-classes, and other edge cases when loading. Please use
:func:`dput.util.load_config` to load config files from these locations.

Example ``dput.core.DPUT_CONFIG_LOCATIONS``::

    {
        "/etc/dput.cf": 15,
        os.path.expanduser("~/.dput.cf"): 5
    }


Both are merged into a single list, sorted by list, and used by
:class:`dput.profile.MultiConfig` to handle loading and access.

Schema Directory
----------------

This is the path to search for validictory schemas. By default, this is
set to ``/usr/share/dput-ng/schemas``. These are not treated as normal
conf-files.
