.. configs:

===========================
Configuration File Overview
===========================

There are a few changes between dput and dput-ng's handling of configuration
files. The changes can be a bit overwhelming, but stick to what's in here
and it should all make great sense.

High level changes
==================

Firstly, you should know dput-ng fully supports the old dput.cf style
configuration file. The biggest change is that dput-ng will prefer it's own,
`JSON <http://en.wikipedia.org/wiki/JSON>`_ encoded format over dput.cf.


