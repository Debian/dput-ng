Contributing to dput
====================

Firstly, thanks for reading! It's super cool of you to want to help!

Code + patches
--------------

This is one of the bigger areas in which hands are needed. Adding new features
and refactoring the codebase is a lot of work, and the more people who
want to help with such tasks, the better!

dput-ng is extremely pythonic, and it aims to be something enjoyable to hack
on. We aim to be, at any time, pep8 clean, pyflakes clean, well-tested
and fully documented.

If you decide to contribute, please stick to the following rules:

  * Use names that make sense. In general, try to make the import as
    descriptive as you can. ``from dput.foo import bar_function`` is pretty
    lame, try something like ``from dput.profile import load_profile``.

  * When you contribute a fix, please also contribute some tests to verify
    what you've done. That's fine if you don't use TDD, in fact, most of us
    here at dput-ng HQ don't.

  * docstring **all the things**. Use RST for the docstring blocks, there's
    a good chance it'll show up in the docs.

  * Please be explicit about licensing.

  * Please add your name to AUTHORS, on the first commit.

  * Ask for feedback *early*
