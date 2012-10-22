Migration guide from old-style dput
===================================

Welcome! This is a helpful starting guide for anyone looking to switch from
dput to dput-ng. dput-ng features a few interesting changes, so it's worthwhile
to run through this helpful starting guide.

Key points
----------

  * dput's configuration files *are* supported, and *will* override any
    new-style configuration file.

  * Behavior of pre-upload checks *may* be different.

  * dput-ng maintains backwards compatibility with the old dput's command line
    flags.

  * dcut has a totally revamped interface, but is similar in spirit and
    usability of dput's dcut interface.

  * This package *replaces* old style dput.

Big changes from dput
---------------------

  * Configuration can be defined in JSON. :doc:`configs` may be of
    some help.

  * More and better behaved checks are enabled by default, and more are
    ready for use out of the box, if you so wish.

  * post-upload hook and pre-upload checks (or hooks) may be written
    in Python, and have access to the objects which matter. For more on
    writing one, :doc:`checkers` may provide some insight, as well as
    :doc:`processors`.

Stability Notes
---------------

This *is not* finished. There are bits to be done, but this shows a decent
amount of progress being made on the tool, and is mostly ready for limited
use by technical people.

  * Bug reports are extremely welcome.

  * Ideas are extremely welcome.

  * Contributors are extremely welcome -- of all kinds (technical or
    otherwise) (see :doc:`contributing`)
