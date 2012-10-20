Processors Walkthrough
----------------------

Processors are just checkers, that have a few small changes. Firstly,
register as a processor, rather then a checker by placing the plugin def
in the ``processors`` class. In the event of an error, feel free to just
bail out. There's not much you can do, and throwing an error is bad form.

For now. This is likely to change.

Until this documentation is updated, please check out :doc:`checkers`.

.. XXX: Link to the other guide.
