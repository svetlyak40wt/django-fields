Introduction
------------

Django-fields is an application which includes different kinds of models fields.

Right now, application contains two fields with encryption support:
EncryptedCharField and EncryptedTextField.

Requirements
-----------

This application depends on python-pycrypto, which can be found in many Linux
repositories, or downloaded from http://www.dlitz.net/software/pycrypto/.

Examples
--------

Examples can be found at the `examples` directory. Look at the, `tests.py`.

Credits
-------

Thanks to [zbyte64](http://www.djangosnippets.org/users/zbyte64/) for
his [django snippet](http://www.djangosnippets.org/snippets/1095/) for encrypted
fields. After some fixes, this snippet works as supposed.
