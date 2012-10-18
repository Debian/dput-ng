Misc. Utilities
===============

This module contains functions that don't have a rightful home elsewhere,
or are of general use.

Configuration Access
--------------------

These functions are used to read a config off the filesystem, for use
elsewhere in dput.

.. autofunction:: dput.util.get_configs

.. autofunction:: dput.util.load_config


Object Loaders
--------------

These functions aid in loading a defined, dynamically imported
"plugin".

.. autofunction:: dput.util.get_obj

.. autofunction:: dput.util.load_obj


Invocation
----------

These functions aid in running things.

.. autofunction:: dput.util.run_command

.. autofunction:: dput.util.run_func_by_name
