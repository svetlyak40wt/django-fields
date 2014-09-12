ChangeLog
=========

0.3.0 (2014-09-12)
------------------
	
* Added: Support for Django migrations (>=1.7) thanks to `Field.deconstruct()`.

0.2.3
-----

* Added: Ability to specify `secret_key` as an argument to the field constructor (via [markkennedy](https://github.com/svetlyak40wt/django-fields/pull/40 "Issue #40")).
* Added: `EncryptedUSPhoneNumberField` and `EncryptedUSSocialSecurityNumberField` now try to import from the standalone django-localflavor before falling back to the version included in Django (this is necessary to support Django 1.6 and newer) (via [mjacksonw](https://github.com/svetlyak40wt/django-fields/pull/36 "Issue #33")).

0.2.2
-----

* Fixed: Django admin needs to be able to create blank instances of the fields in order to create a new model. This broke with `BaseEncryptedNumberField`. (via [defrex](https://github.com/svetlyak40wt/django-fields/pull/32 "Issue #32"))
* Fixed: `block_type` wasn't added to the south rules. (via [defrex](https://github.com/svetlyak40wt/django-fields/pull/33 "Issue #33"))
* Fixed: Newer code paths with `block_type` specified couldn't reuse the `cipher` object on the field class. `to_python` was already redefining it before decrypting the value, but `get_db_prep_value` wasn't before encrypting. The first time you used a model it would be fine, but the second would fail. Thus the tests were passing but the classes were functionally useless in an application. (via [defrex](https://github.com/svetlyak40wt/django-fields/pull/34 "Issue #34"))

0.2.1
-----

* Added: `EncryptedUSSocialSecurityNumberField`, which handles the special-case logic of validating and encrypting US Social Security Numbers, using `django.contrib.localflavor.us.forms.USSocialSecurityNumberField`. (via [Brooks Travis](https://github.com/svetlyak40wt/django-fields/pull/24 "Pull Request 24"))
* Fixed: Issue [#21](https://github.com/svetlyak40wt/django-fields/issues/21 "Issue #21").
* Changed: `django_fields.fields.BaseEncryptedField` now supports specification of cipher `block_type` via keyword argument. (via [kromem](https://github.com/svetlyak40wt/django-fields/pull/26 "Pull Request 26"))
* Added: Deprecation warning for fields that do not specify a `block_type`.

0.2.0
-----

* Added: Class `django_fields.models.ModelWithPrivateFields`, which allows to use private fields, starting from two underscores.
* Fixed: `BaseEncryptedDateField.get_db_prep_value` errors.
* Changed: Now virtualenv is used for test enviroment. Buildout.cfg was removed.

0.1.3
-----

* Fixed: `EOFError` handling in `PickleField`.
* Changed: Buildout file was changed to test against Django 1.2.5 and include `PyCrypto`.

0.1.2
-----

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

0.1.1
-----

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
