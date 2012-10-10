.. checkers:

=======================
Writing checker plugins
=======================

Writing checkers is fun and easy for the whole family.

Theory of Operation
-------------------

.. XXX: Overview

How a checker is invoked
------------------------

.. XXX: signature, etc.

What do do when you find an issue
---------------------------------

.. XXX: fuggn' thro an exception, dawg

How to enable the checker
-------------------------

.. XXX: Add it to checkers, dummy (but really, this is actually compelx.
        let's figure that out, first.)

Writing an idiomatic checker
----------------------------

Please stick to your own namespace, and don't depend on other checkers
being active. In general, you should only use values from the profile when
they're under your checker's name (e.g. for the GPG checker, the key would be
``gpg``).
