Welcome to dput's documentation!
================================

`dput-ng <http://people.debian.org/~paultag/dput-ng/>`_ is a brand-new retake
of the classic Debian tool, dput. We've made some important changes, which are
documented here. Please get acquainted with the documentation, in order to
fully understand the changes.

The :doc:`reference/migrating` might be helpful for new users.

Documentation Index
===================

Contents:

.. toctree::
   :maxdepth: 3

   reference/index
   library/index

Motiviation
===========

Many have asked "why rewrite dput", or "why not work with dput"?

Frankly, when it comes down to it, we were concerned with the bitrot that is
present in old dput, and decided to spend our time designing dput-ng to support
all of our ideas from the ground up, rather then further mangling old dput's
codebase to support them.

As far as what features, the biggest improvements in our mind are:

  * Enhanced pre-upload checks baked in and enabled by default.
  * Support for external checkers
  * Fragmented configuration, to allow external packages to include checks.
  * Real SFTP support
  * Dynamic checker behavior depending on host / profile
  * SHA support

We're both really big fans of dput, so we've decided to maintain 100%
compatibility with dput in dput-ng, as well as automagically reading from the
old-style dput.cf conf files.

You might see some behavior change, but we believe it to be in the spirit
of the original incarnation of dput. All the new features & functionality
is fully disable-able, and you should be able to use dput-ng just like
you were before.

dput-ng also features a lot of new features that might be of interest
to Debian derivatives, such as the ability to add a new upload target
(now called profiles) and unique checks, without having to fork dput.
Changes which make extending dput downstream will likely be accepted
in dput main. Please consider contributing.

Authors
=======

The bulk of the work was done by `Arno <http://daemonkeeper.net/>`_ and
`Paul <http://pault.ag/>`_ For a full list of contributors, please check
the AUTHORS file shipped with your copy of dput-ng.
