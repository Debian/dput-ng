Writing Hooks
=============

.. note::
    Whether a hook runs before or after uploading a package is a
    matter of the JSON configuration file. Aside, they are identical.

Hooks are a fundamental part of dput-ng. Hooks make sure the package
you've prepared is actually fit to upload given the target & current profile.

In general, one should implement hooks for things that the remote server
would ideally check for before accepting a package. Going beyond that is OK,
providing you have the user's go-ahead to do so.

Remember, this isn't some sort of magical restriction to upload, most remote
servers would be happy with almost anything you put there, these are simply
to help reduce the time to notice big errors.

Theory of Operation
-------------------

Pre-upload Hooks are a simple function which is invoked with a few objects to
help aid in the checking process & reduce code.

Pre-upload hooks will always be run before an upload, and will be given the digested
.changes object, the current profile & a way to interface with the user.

Pre-upload hooks (at their core) should preform a single check (as simply as it
can), and either raise a subclass of :class:`dput.exceptions.HookException`
or return normally.

Post-upload hooks work likewise. They are just simple hooks as well, that are slightly different to pre-upload hooks. Firstly, register as a hook by placing the plugin def in the ``hooks`` class. In the event of an error, feel free to just bail out. There's not much you can do, and throwing an error is bad form. For now. This is likely to change.

How a Hook Is Invoked
------------------------

Throughout this overview, we'll be looking at the
:func:`dput.hooks.validate_checksums` pre-upload hook. It's one of the most
simple hooks, and demonstrates the concept very clearly.

To start to understand how this all works, let's take a step back and
look at how :func:`dput.hooks.run_hook` invokes the hook-function.

Basically, ``run_hook`` will grab all the strings in the ``hooks`` key
of the profile. They are just that -- simply strings. The hook are looked
up using :func:`dput.util.get_obj` (which calls
:func:`dput.util.load_config` to resolve the .json definition of the hook).

All hooks are declared in the ``hooks`` config class, and look
something like the following::

    {
        "name": "checksum pre-upload hook",
        "path": "dput.hooks.basics.validate_checksums"
    }

.. XXX TODO: Document the pre-/post-upload key

For more on this file & how it's used, check the other ref-doc on
config files: :doc:`configs`

Nextly, let's take a look at the ``path`` key. ``path`` is a
python-importable path to the function to invoke. Let's take a look
at it a bit more closely::

    >>> from dput.hooks.basics import validate_checksums
    >>> validate_checksums
    <function validate_checksums at 0x7f9be15e1e60>

As you can see, we've imported the target, and it is, in fact, the function
that we care about.

.. XXX: TODO: More better handling of small scripts which should just
              be put somewhere dput cares about?

Now that we're clear on how we got here, let's check back with the
implementation of :func:`dput.hooks.validate_checksums`::

    def validate_checksums(changes, profile, interface):

We're passed three objects -- the ``changes``, ``profile`` and ``interface``.
The ``changes`` object is an instance of :class:`dput.changes.Changes`,
pre-loaded with the target of this upload action. ``profile`` is a simple
dict, with the current upload profile. ``interface`` is a subclass of
:class:`dput.interface.AbstractInterface`, ready to be used to talk
to the user, if something comes up.

What To Do When You Find an Issue
---------------------------------

During runtime, and for any reason the checker sees fit to do so, the hook
may abort the upload by raising a subclass of a
:class:`dput.exceptions.HookException`. In cases where the user aught to
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
raised (:class:`dput.hooks.basics.HashValidationError`) is a subclass
of the expected :class:`dput.exceptions.HookException`.



