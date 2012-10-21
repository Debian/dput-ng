Writing Checker Plugins
=======================

.. note::
    All of the information in this guide applies fully to writing
    ``processors``. Just rename the config class to ``processors``
    and you're good to go.

Checkers are a fundamental part of dput-ng. Checkers make sure the package
you've prepared is actually fit to upload given the target & current profile.

In general, one should implement checkers for things that the remote server
would ideally check for before accepting a package. Going beyond that is OK,
providing you have the user's go-ahead to do so.

Remember, this isn't some sort of magical restriction to upload, most remote
servers would be happy with almost anything you put there, these are simply
to help reduce the time to notice big errors.

Theory of Operation
-------------------

Checkers are a simple function which is invoked with a few objects to help
aid in the checking process & reduce code.

Checkers will always be run before an upload, and will be given the digested
.changes object, the current profile & a way to interface with the user.

All checkers (at their core) should preform a single check (as simply as it
can), and either raise a subclass of :class:`dput.exceptions.CheckerException`
or return normally.

How a Checker Is Invoked
------------------------

Throughout this overview, we'll be looking at the
:func:`dput.checkers.validate_checksums` checker. It's one of the most simple
checkers, and demonstrates the concept very clearly.

To start to understand how this all works, let's take a step back and
look at how :func:`dput.checker.run_checker` invokes the checker-function.

Basically, ``run_checker`` will grab all the strings in the ``checkers`` key
of the profile. They are just that -- simply strings. The checkers are looked
up using :func:`dput.util.get_obj` (which calls
:func:`dput.util.load_config` to resolve the .json definition of the checker).

All checkers are declared in the ``checkers`` config class, and look
something like the following::

    {
        "name": "checksum checker",
        "path": "dput.checkers.basics.validate_checksums"
    }

For more on this file & how it's used, check the other ref-doc on
config files: :doc:`configs`

Nextly, let's take a look at the ``path`` key. ``path`` is a
python-importable path to the function to invoke. Let's take a look
at it a bit more closely::

    >>> from dput.checkers.basics import validate_checksums
    >>> validate_checksums
    <function validate_checksums at 0x7f9be15e1e60>

As you can see, we've imported the target, and it is, in fact, the function
that we care about.

.. XXX: TODO: More better handling of small scripts which should just
              be put somewhere dput cares about?

Now that we're clear on how we got here, let's check back with the
implementation of :func:`dput.checkers.validate_checksums`::

    def validate_checksums(changes, profile, interface):

We're passed three objects -- the ``changes``, ``profile`` and ``interface``.
The ``changes`` object is an instance of :class:`dput.changes.Changes`,
pre-loaded with the target of this upload action. ``profile`` is a simple
dict, with the current upload profile. ``interface`` is a subclass of
:class:`dput.interface.AbstractInterface`, ready to be used to talk
to the user, if something comes up.

What To Do When You Find an Issue
---------------------------------

During runtime, and for any reason the checker sees fit to do so, the Checker
may abort the upload by raising a subclass of a
:class:`dput.exceptions.CheckerException`. In cases where the user aught to
make the decision (lintian errors, etc), please **prompt** the user for
what to do, rather then blindly raising the error. Remember, the user can't
override a checker's failure except by disabling the checker.

Don't make people disable you. Be nice.

Let's take a look at our reference implementation again::

    def validate_checksums(changes, profile, interface):
        try:
            changes.validate_checksums(check_hash=profile["hash"])
        except ChangesFileException as e:
            raise HashValidationError(
                "Bad checksums on %s: %s" % (changes.get_filename(), e)
            )

As you can see, the checker verifies the hashsums, catches any Exceptions
thrown by the code it uses, and raises sane error text. The Exception
raised (:class:`dput.checkers.basics.HashValidationError`) is a subclass
of the expected :class:`dput.exceptions.CheckerException`.


.. Idiomatic Checkers
   ------------------
   XXX: implement me.
