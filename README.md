Introduction
------------

[![changelog](http://allmychanges.com/p/python/django-fields/badge/)](http://allmychanges.com/p/python/django-fields/?utm_source=badge)

Django-fields is an application which includes different kinds of models fields.

Right now, application contains two fields with encryption support:
EncryptedCharField and EncryptedTextField.

This project uses Travis for continuous integration: [![Build Status](https://secure.travis-ci.org/svetlyak40wt/django-fields.png)](http://travis-ci.org/svetlyak40wt/django-fields)


Requirements
-----------

This application depends on *python-crypto*, which can be found in many Linux
repositories, or downloaded from http://www.dlitz.net/software/pycrypto/.

Under Ubuntu, just do:

    sudo apt-get install python-crypto

How to run tests
----------------

Examples can be found at the `examples` directory. Look at the, `tests.py`.
Same project is used to run unittests. To run them, just fire `./run-tests.sh`.

Contributors
------------

* [zbyte64](http://www.djangosnippets.org/users/zbyte64/) — thanks to for 
  his [django snippet](http://www.djangosnippets.org/snippets/1095/) for encrypted
  fields. After some fixes, this snippet works as supposed.
* John Morrissey — for fixing bug in PickleField.
* Joe Jasinski — different fixes and new fields for encripted email and US Phone.
* Colin MacDonald — for many encripted fields added.
* Igor Davydenko — PickleField.
* kromem - Added support for specifying `block_type` on encrypted fields.
* Brooks Travis - new field for encrypted US Social Security Number and other fixes.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/svetlyak40wt/django-fields/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

