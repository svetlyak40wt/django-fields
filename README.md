Introduction
------------

Django-fields is an application which includes different kinds of models fields.

Right now, application contains two fields with encryption support:
EncryptedCharField and EncryptedTextField.

This project uses Travis for continuous integration: [![Build Status](https://secure.travis-ci.org/svetlyak40wt/django-fields.png)](http://travis-ci.org/svetlyak40wt/django-fields)


ChangeLog
---------
### 0.2.3

* Added: Ability to specify `secret_key` as an argument to the field constructor (via [markkennedy](https://github.com/svetlyak40wt/django-fields/pull/40 "Issue #40")).
* Added: `EncryptedUSPhoneNumberField` and `EncryptedUSSocialSecurityNumberField` now try to import from the standalone django-localflavor before falling back to the version included in Django (this is necessary to support Django 1.6 and newer) (via [mjacksonw](https://github.com/svetlyak40wt/django-fields/pull/36 "Issue #33")).

### 0.2.2

* Fixed: Django admin needs to be able to create blank instances of the fields in order to create a new model. This broke with `BaseEncryptedNumberField`. (via [defrex](https://github.com/svetlyak40wt/django-fields/pull/32 "Issue #32"))
* Fixed: `block_type` wasn't added to the south rules. (via [defrex](https://github.com/svetlyak40wt/django-fields/pull/33 "Issue #33"))
* Fixed: Newer code paths with `block_type` specified couldn't reuse the `cipher` object on the field class. `to_python` was already redefining it before decrypting the value, but `get_db_prep_value` wasn't before encrypting. The first time you used a model it would be fine, but the second would fail. Thus the tests were passing but the classes were functionally useless in an application. (via [defrex](https://github.com/svetlyak40wt/django-fields/pull/34 "Issue #34"))

### 0.2.1

* Added: `EncryptedUSSocialSecurityNumberField`, which handles the special-case logic of validating and encrypting US Social Security Numbers, using `django.contrib.localflavor.us.forms.USSocialSecurityNumberField`. (via [Brooks Travis](https://github.com/svetlyak40wt/django-fields/pull/24 "Pull Request 24"))
* Fixed: Issue [#21](https://github.com/svetlyak40wt/django-fields/issues/21 "Issue #21").
* Changed: `django_fields.fields.BaseEncryptedField` now supports specification of cipher `block_type` via keyword argument. (via [kromem](https://github.com/svetlyak40wt/django-fields/pull/26 "Pull Request 26"))
* Added: Deprecation warning for fields that do not specify a `block_type`.

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
* kromem - Added support for specifying `block_type` on encrypted fields.
* Brooks Travis - new field for encrypted US Social Security Number and other fixes.


[![Bitdeli Badge](https://d2weczhvl823v0.cloudfront.net/svetlyak40wt/django-fields/trend.png)](https://bitdeli.com/free "Bitdeli Badge")

