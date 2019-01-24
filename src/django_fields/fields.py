import binascii
import codecs
import datetime
import string
import sys
import warnings

from django import forms
from django.forms import fields
from django.db import models
from django.conf import settings
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from Cryptodome import Random
from Cryptodome.Random import random

if hasattr(settings, 'USE_CPICKLE'):
    warnings.warn(
        "The USE_CPICKLE options is now obsolete. cPickle will always "
        "be used unless it cannot be found or DEBUG=True",
        DeprecationWarning,
    )

if settings.DEBUG:
    import pickle
else:
    try:
        import cPickle as pickle
    except:
        import pickle

if sys.version_info[0] == 3:
    PYTHON3 = True
    from django.utils.encoding import smart_str, force_text as force_unicode
else:
    PYTHON3 = False
    from django.utils.encoding import smart_str, force_unicode

DEFAULT_BLOCK_TYPE = 'MODE_ECB'


class BaseEncryptedField(models.Field):
    '''This code is based on the djangosnippet #1095
       You can find the original at http://www.djangosnippets.org/snippets/1095/'''

    def __init__(self, *args, **kwargs):
        self.cipher_type = kwargs.pop('cipher', 'AES')
        self.block_type = kwargs.pop('block_type', None)
        self.secret_key = kwargs.pop('secret_key', settings.SECRET_KEY)
        self.secret_key = self.secret_key[:32]
        if PYTHON3 is True:
            self.secret_key = bytes(self.secret_key.encode('utf-8'))

        if self.block_type is None:
            warnings.warn(
                "Default usage of pycrypto's AES block type defaults has been "
                "deprecated and will be removed in 0.3.0 (default will become "
                "MODE_CBC). Please specify a secure block_type, such as CBC.",
                DeprecationWarning,
            )
            self.block_type = DEFAULT_BLOCK_TYPE
        try:
            imp = __import__('Cryptodome.Cipher', globals(), locals(), [self.cipher_type], -1)
        except:
            imp = __import__('Cryptodome.Cipher', globals(), locals(), [self.cipher_type])
        self.cipher_object = getattr(imp, self.cipher_type)
        if self.block_type != DEFAULT_BLOCK_TYPE:
            self.prefix = '$%s$%s$' % (self.cipher_type, self.block_type)
            self.iv = Random.new().read(self.cipher_object.block_size)
            self.cipher = self.cipher_object.new(
                self.secret_key,
                getattr(self.cipher_object, self.block_type),
                self.iv)
        else:
            self.cipher = self.cipher_object.new(self.secret_key, getattr(self.cipher_object, self.block_type))
            self.prefix = '$%s$' % self.cipher_type

        self.original_max_length = max_length = kwargs.get('max_length', 40)
        self.unencrypted_length = max_length
        # always add at least 2 to the max_length:
        #     one for the null byte, one for padding
        max_length += 2
        mod = max_length % self.cipher_object.block_size
        if mod > 0:
            max_length += self.cipher_object.block_size - mod
        if hasattr(self, 'iv'):
            max_length += len(self.iv)
        kwargs['max_length'] = max_length * 2 + len(self.prefix)

        super(BaseEncryptedField, self).__init__(*args, **kwargs)

    def _is_encrypted(self, value):
        return (
            isinstance(value, six.string_types) and
            value.startswith(self.prefix)
        )

    def _get_padding(self, value):
        # We always want at least 2 chars of padding (including zero byte),
        # so we could have up to block_size + 1 chars.
        mod = (len(value) + 2) % self.cipher_object.block_size
        return self.cipher_object.block_size - mod + 2

    def from_db_value(self, value, expression, connection, context):
        if self._is_encrypted(value):
            if self.block_type != DEFAULT_BLOCK_TYPE:
                self.iv = binascii.a2b_hex(value[len(self.prefix):])[:len(self.iv)]
                self.cipher = self.cipher_object.new(
                    self.secret_key,
                    getattr(self.cipher_object, self.block_type),
                    self.iv)
                decrypt_value = binascii.a2b_hex(value[len(self.prefix):])[len(self.iv):]
            else:
                decrypt_value = binascii.a2b_hex(value[len(self.prefix):])
            return force_unicode(
                self.cipher.decrypt(decrypt_value).split(b'\0')[0]
            )
        return value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if value is None:
            return None

        if PYTHON3 is True:
            value = bytes(value.encode('utf-8'))
        else:
            value = smart_str(value)

        if not self._is_encrypted(value):
            padding = self._get_padding(value)
            if padding > 0:
                if PYTHON3 is True:
                    value += bytes("\0".encode('utf-8')) + bytes(
                        ''.encode('utf-8')).join([
                            bytes(random.choice(
                                string.printable).encode('utf-8'))
                            for index in range(padding - 1)])
                else:
                    value += "\0" + ''.join([
                        random.choice(string.printable)
                        for index in range(padding - 1)
                    ])
            if self.block_type != DEFAULT_BLOCK_TYPE:
                self.cipher = self.cipher_object.new(
                    self.secret_key,
                    getattr(self.cipher_object, self.block_type),
                    self.iv)
                if PYTHON3 is True:
                    value = self.prefix + binascii.b2a_hex(
                        self.iv + self.cipher.encrypt(value)).decode('utf-8')
                else:
                    value = self.prefix + binascii.b2a_hex(
                        self.iv + self.cipher.encrypt(value))
            else:
                if PYTHON3 is True:
                    value = self.prefix + binascii.b2a_hex(
                        self.cipher.encrypt(value)).decode('utf-8')
                else:
                    value = self.prefix + binascii.b2a_hex(
                        self.cipher.encrypt(value))
        return value

    def deconstruct(self):
        original = super(BaseEncryptedField, self).deconstruct()
        kwargs = original[-1]
        if self.cipher_type != 'AES':
            kwargs['cipher'] = self.cipher_type
        if self.block_type is not None:
            kwargs['block_type'] = self.block_type
        if self.original_max_length != 40:
            kwargs['max_length'] = self.original_max_length
        return original[:-1] + (kwargs,)


class EncryptedTextField(BaseEncryptedField):

    def get_internal_type(self):
        return 'TextField'

    def formfield(self, **kwargs):
        defaults = {'widget': forms.Textarea}
        defaults.update(kwargs)
        return super(EncryptedTextField, self).formfield(**defaults)


class EncryptedCharField(BaseEncryptedField):

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        defaults = {'max_length': self.max_length}
        defaults.update(kwargs)
        return super(EncryptedCharField, self).formfield(**defaults)

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if value is not None and not self._is_encrypted(value):
            if len(value) > self.unencrypted_length:
                raise ValueError(
                    "Field value longer than max allowed: " +
                    str(len(value)) + " > " + str(self.unencrypted_length)
                )
        return super(EncryptedCharField, self).get_db_prep_value(
            value,
            connection=connection,
            prepared=prepared,
        )


class BaseEncryptedDateField(BaseEncryptedField):
    # Do NOT define a __metaclass__ for this - it's an abstract parent
    # for EncryptedDateField and EncryptedDateTimeField.
    # If you try to inherit from a class with a __metaclass__, you'll
    # get a very opaque infinite recursion in contribute_to_class.

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = self.max_raw_length
        super(BaseEncryptedDateField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def formfield(self, **kwargs):
        defaults = {'widget': self.form_widget, 'form_class': self.form_field}
        defaults.update(kwargs)
        return super(BaseEncryptedDateField, self).formfield(**defaults)

    def to_python(self, value):
        return self.from_db_value(value)

    def from_db_value(self, value, expression, connection, context):
        # value is either a date or a string in the format "YYYY:MM:DD"

        if value in fields.EMPTY_VALUES:
            date_value = value
        else:
            if isinstance(value, self.date_class):
                date_value = value
            else:
                date_text = super(BaseEncryptedDateField, self).from_db_value(
                    value, expression, connection, context)
                date_value = self.date_class(*map(int, date_text.split(':')))
        return date_value

    def get_db_prep_value(self, value, connection=None, prepared=False):
        # value is a date_class.
        # We need to convert it to a string in the format "YYYY:MM:DD"
        if value:
            date_text = value.strftime(self.save_format)
        else:
            date_text = None
        return super(BaseEncryptedDateField, self).get_db_prep_value(
            date_text,
            connection=connection,
            prepared=prepared
        )


class EncryptedDateField(BaseEncryptedDateField):
    form_widget = forms.DateInput
    form_field = forms.DateField
    save_format = "%Y:%m:%d"
    date_class = datetime.date
    max_raw_length = 10  # YYYY:MM:DD


class EncryptedDateTimeField(BaseEncryptedDateField):
    # FIXME:  This doesn't handle time zones, but Python doesn't really either.
    form_widget = forms.DateTimeInput
    form_field = forms.DateTimeField
    save_format = "%Y:%m:%d:%H:%M:%S:%f"
    date_class = datetime.datetime
    max_raw_length = 26  # YYYY:MM:DD:hh:mm:ss:micros


class BaseEncryptedNumberField(BaseEncryptedField):
    # Do NOT define a __metaclass__ for this - it's abstract.
    # See BaseEncryptedDateField for full explanation.
    def __init__(self, *args, **kwargs):
        if self.max_raw_length:
            kwargs['max_length'] = self.max_raw_length
        super(BaseEncryptedNumberField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return 'CharField'

    def to_python(self, value):
        return self.from_db_value(value)

    def from_db_value(self, value, expression, connection, context):
        # value is either an int or a string of an integer
        if isinstance(value, self.number_type) or value == '':
            number = value
        else:
            number_text = super(BaseEncryptedNumberField, self).from_db_value(
                value, expression, connection, context)
            number = self.number_type(number_text)
        return number

    # def get_prep_value(self, value):
    def get_db_prep_value(self, value, connection=None, prepared=False):
        number_text = self.format_string % value
        return super(BaseEncryptedNumberField, self).get_db_prep_value(
            number_text,
            connection=connection,
            prepared=prepared,
        )


class EncryptedIntField(BaseEncryptedNumberField):
    if PYTHON3 is True:
        max_raw_length = len(str(-sys.maxsize - 1))
    else:
        max_raw_length = len(str(-sys.maxint - 1))
    number_type = int
    format_string = "%d"


class EncryptedLongField(BaseEncryptedNumberField):
    max_raw_length = None  # no limit
    if PYTHON3 is True:
        number_type = int
    else:
        number_type = long
    format_string = "%d"

    def get_internal_type(self):
        return 'TextField'


class EncryptedFloatField(BaseEncryptedNumberField):
    max_raw_length = 150  # arbitrary, but should be sufficient
    number_type = float
    # If this format is too long for some architectures, change it.
    format_string = "%0.66f"


class PickleField(models.TextField):
    editable = False
    serialize = False

    def get_db_prep_value(self, value, connection=None, prepared=False):
        if PYTHON3 is True:
            # When PYTHON3, we convert data to base64 to prevent errors when
            # unpickling.
            val = codecs.encode(pickle.dumps(value), 'base64').decode()
            return val
        else:
            return pickle.dumps(value)

    def to_python(self, value):
        return self.from_db_value(value)

    def from_db_value(self, value, expression, connection, context):
        if PYTHON3 is True:
            if not isinstance(value, str):
                return value
        else:
            if not isinstance(value, basestring):
                return value

        # Tries to convert unicode objects to string, cause loads pickle from
        # unicode excepts ugly ``KeyError: '\x00'``.
        try:
            if PYTHON3 is True:
                # When PYTHON3, data are in base64 to prevent errors when
                # unpickling.
                val = pickle.loads(codecs.decode(value.encode(), "base64"))
                return val
            else:
                return pickle.loads(smart_str(value))
        # If pickle could not loads from string it's means that it's Python
        # string saved to PickleField.
        except ValueError:
            return value
        except EOFError:
            return value


class EncryptedUSPhoneNumberField(BaseEncryptedField):
    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        try:
            from localflavor.us.forms import USPhoneNumberField
        except ImportError:
            from django.contrib.localflavor.us.forms import USPhoneNumberField

        defaults = {'form_class': USPhoneNumberField}
        defaults.update(kwargs)
        return super(EncryptedUSPhoneNumberField, self).formfield(**defaults)


class EncryptedUSSocialSecurityNumberField(BaseEncryptedField):
    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        try:
            from localflavor.us.forms import USSocialSecurityNumberField
        except ImportError:
            from django.contrib.localflavor.us.forms import USSocialSecurityNumberField

        defaults = {'form_class': USSocialSecurityNumberField}
        defaults.update(kwargs)
        return super(EncryptedUSSocialSecurityNumberField, self).formfield(**defaults)


class EncryptedEmailField(BaseEncryptedField):
    description = _("E-mail address")

    def get_internal_type(self):
        return "CharField"

    def formfield(self, **kwargs):
        from django.forms import EmailField
        defaults = {'form_class': EmailField, 'max_length': self.unencrypted_length}
        defaults.update(kwargs)
        return super(EncryptedEmailField, self).formfield(**defaults)


try:
    from south.modelsinspector import add_introspection_rules
    add_introspection_rules([
        (
            [
                BaseEncryptedField, EncryptedDateField, BaseEncryptedDateField, EncryptedCharField, EncryptedTextField,
                EncryptedFloatField, EncryptedDateTimeField, BaseEncryptedNumberField, EncryptedIntField, EncryptedLongField,
                EncryptedUSPhoneNumberField, EncryptedEmailField,
            ],
            [],
            {
                'cipher': ('cipher_type', {}),
                'block_type': ('block_type', {}),
            },
        ),
    ], ["^django_fields\.fields\..+?Field"])
    add_introspection_rules([], ["^django_fields\.fields\.PickleField"])
except ImportError:
    pass
