Upload Target / Profile Implementation
======================================

This contains a lot of backing code to get at profiles.

Commonly used functions
-----------------------

.. autofunction:: dput.profile.load_profile

.. autofunction:: dput.profile.load_profile

Multi Configuration Implementation
----------------------------------

.. warning::
    This is mostly just used internally, please don't use this directly unless you know what you're doing(tm). In most cases, :func:`dput.profile.load_profile` and :func:`dput.profile.load_profile` will do the trick.

.. autoclass:: dput.profile.MultiConfig
   :members:
   :private-members:
