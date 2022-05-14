Introduction
------------

[![changelog](http://allmychanges.com/p/python/django-fields/badge/)](http://allmychanges.com/p/python/django-fields/?utm_source=badge)

Django-fields is an application which includes different kinds of models fields.

Right now, application contains two fields with encryption support:
EncryptedCharField and EncryptedTextField.


How to run tests
----------------

Examples can be found at the `examples` directory. Look at the, `tests.py`.
Same project is used to run unittests. To run them, just fire `../env/bin/python ./run-tests.py`.

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
