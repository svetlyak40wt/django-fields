import binascii
import random
import string

from django import forms
from django.db import models
from django.conf import settings
from django.utils.encoding import smart_str, force_unicode


USE_CPICKLE = getattr(settings, 'USE_CPICKLE', False)

if USE_CPICKLE:
    import cPickle as pickle
else:
    import pickle

class BaseEncryptedField(models.Field):
    '''This code is based on the djangosnippet #1095
       You can find the original at http://www.djangosnippets.org/snippets/1095/'''

    def __init__(self, *args, **kwargs):
        cipher = kwargs.pop('cipher', 'AES')
        try:
            imp = __import__('Crypto.Cipher', globals(), locals(), [cipher], -1)
        except:
            imp = __import__('Crypto.Cipher', globals(), locals(), [cipher])
        self.cipher = getattr(imp, cipher).new(settings.SECRET_KEY[:32])
        self.prefix = '$%s$' % cipher

        max_length = kwargs.get('max_length', 40)
        mod = max_length % self.cipher.block_size
        if mod > 0:
            max_length += self.cipher.block_size - mod
        kwargs['max_length'] = max_length * 2 + len(self.prefix)

        models.Field.__init__(self, *args, **kwargs)

    def _is_encrypted(self, value):
        return isinstance(value, basestring) and value.startswith(self.prefix)

    def _get_padding(self, value):
        mod = len(value) % self.cipher.block_size
        if mod > 0:
            return self.cipher.block_size - mod
        return 0


    def to_python(self, value):
        if self._is_encrypted(value):
            return force_unicode(
                self.cipher.decrypt(
                    binascii.a2b_hex(value[len(self.prefix):])
                ).split('\0')[0]
            )
        return value

    def get_db_prep_value(self, value):
        value = smart_str(value)

        if value is not None and not self._is_encrypted(value):
            padding  = self._get_padding(value)
            if padding > 0:
                value += "\0" + ''.join([random.choice(string.printable) for index in range(padding-1)])
            value = self.prefix + binascii.b2a_hex(self.cipher.encrypt(value))
        return value

class EncryptedTextField(BaseEncryptedField):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(EncryptedTextField, self).formfield(**defaults)

class EncryptedCharField(BaseEncryptedField):
    __metaclass__ = models.SubfieldBase

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(EncryptedCharField, self).formfield(**defaults)

class PickleField(models.TextField):
    __metaclass__ = models.SubfieldBase

    editable = False
    serialize = False

    def get_db_prep_value(self, value):
        return pickle.dumps(value)

    def to_python(self, value):
        if not isinstance(value, basestring):
            return value

        # Tries to convert unicode objects to string, cause loads pickle from
        # unicode excepts ugly ``KeyError: '\x00'``.
        try:
            return pickle.loads(smart_str(value))
        # If pickle could not loads from string it's means that it's Python
        # string saved to PickleField.
        except ValueError:
            return value
