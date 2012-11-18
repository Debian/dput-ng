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

Documentation
-------------

Documentation is another huge effort that's been going on. Working to better
document dput is something that's really important. Working on tutorials,
reviewing old & outdated docs, or expanding on existing documentation is
something that's sorely needed.

If you're also technical, documenting the internals is an ongoing effort,
so any help there would be amazing.

Some rules here, too:

  * Be sure to write in complete and clear English.

  * Cross-reference as much as you can. It really helps.

  * Include lots of examples.

  * As for feedback as you go along. Also be sure to have a technical person
    on the dput team review your work for slight errors as you go along.

  * Be explicit about licensing

  * Please add yourself to AUTHORS on your first commit.


Hooks
------

Hooks are hugely important as well. Writing new hooks is insanely cool,
and sharing them back with the dput-ng community & friends is an awesome thing
to do on it's own.

Some other random guidelines we thought up:

  * In general, treat your hook as self-contained and independent.

  * If you feel your checker hook be in the dput main, please ensure it's
    properly clean, follows the code guidelines above, and finds a nice home
    somewhere in the dput codebase. Make sure it's below ``dput.hooks``,
    though.

  * It must be distributable under the terms of the GPL-2+ license. Permissive
    licenses such as Expat or BSD-3 should be fine. When in doubt, ask!

.. XXX: Link to a tutorial about writing a checker, etc. MORE!
