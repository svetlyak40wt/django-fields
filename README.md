Introduction
------------

Django-fields is an application which includes different kinds of models fields.

Right now, application contains two fields with encryption support:
EncryptedCharField and EncryptedTextField.

This project uses Travis for continuous integration: [![Build Status](https://secure.travis-ci.org/svetlyak40wt/django-fields.png)](http://travis-ci.org/svetlyak40wt/django-fields)


ChangeLog
---------

### 0.2.0

* Added: Class `django_fields.models.ModelWithPrivateFields`, which allows to use private fields, starting from two underscores.
* Fixed: `BaseEncryptedDateField.get_db_prep_value` errors.
* Changed: Now virtualenv is used for test enviroment. Buildout.cfg was removed.

### 0.1.3

* Fixed: `EOFError` handling in `PickleField`.
* Changed: Buildout file was changed to test against Django 1.2.5 and include `PyCrypto`.

### 0.1.2
* Added: `EncryptedEmail` and `USPhoneNumber` fields.
* Added: `EncryptedNumber` fields.
* Added: `EncryptedDateTimeField`.
* Added: `EncryptedDateField` class.
* Added: South support.
* Added: Unit tests and associated utility functions.
* Fixed: Deprecation warnings related to the settings in example project.
* Fixed: Deprecation warnings, related to `get_db_prep_vasue`.
* Fixed: Edge case in encryption consistency.
* Changed: `EncryptedCharField` now enforces max length.

### 0.1.1
* Added: `PickleField` class.
* Added: Encrypt field.
* Added: Buildout config and example application.
* Added: `setup.py` and `MANIFEST.in.`
* Fixed: Issue #1 - "`EncryptedCharField` raises a traceback in the django admin".
* Fixed: `max_length` issue.
* Changed: Now `__import__` compatible with python 2.4 in `BaseEncryptedField.__init__`.
* Changed: Code was moved to `src`.
* Changed: Get rid of custom string class. It was replaced with string prefix.
* Changed: Settings were changed to test with mysql.

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
