Introduction
------------

Django-fields is an application which includes different kinds of models fields.

Right now, the application contains these fields with encryption support:

* EncryptedCharField
* EncryptedDateField
* EncryptedDateTimeField
* EncryptedEmailField
* EncryptedFileField
* EncryptedFloatField
* EncryptedIntField
* EncryptedLongField
* EncryptedTextField
* EncryptedUSPhoneNumberField

They are each used in a similar fashion to their native, non-encrypted counterparts.

One thing to remember is `.filter()`, `.order_by()`, etc... methods on a queryset will
not work due to the text being encrypted in the database. Any filtering, sorting, etc...
on encrypted fields will need to be done in memory.

Requirements
-----------

This application depends on *python-crypto*, which can be found in many Linux
repositories, or downloaded from http://www.dlitz.net/software/pycrypto/.

Under Ubuntu, just do:

    sudo apt-get install python-crypto

Examples
--------

Examples can be found at the `examples` directory. Look at `tests.py`.

Also check out the doc strings for various special use cases (especially EncryptedFileField).

Contributors
------------

* [zbyte64](http://www.djangosnippets.org/users/zbyte64/) — thanks to for 
  his [django snippet](http://www.djangosnippets.org/snippets/1095/) for encrypted
  fields. After some fixes, this snippet works as supposed.
* John Morrissey — for fixing bug in PickleField.
* Joe Jasinski — different fixes and new fields for encrypted email and US Phone.
* Colin MacDonald — for many encrypted fields added.
* Igor Davydenko — PickleField.
* Bryan Helmig - encrypted file field.
