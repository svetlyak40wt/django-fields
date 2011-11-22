# -*- coding: utf-8 -*-
from __future__ import absolute_import

import datetime
import string
import sys
import unittest

from django.db import connection
from django.db import models

from .fields import (
    EncryptedCharField, EncryptedDateField,
    EncryptedDateTimeField, EncryptedIntField,
    EncryptedLongField, EncryptedFloatField, PickleField,
    EncryptedUSPhoneNumberField, EncryptedEmailField,
)

from .models import ModelWithPrivateFields


class EncObject(models.Model):
    max_password = 20
    password = EncryptedCharField(max_length=max_password)


class EncDate(models.Model):
    important_date = EncryptedDateField()


class EncDateTime(models.Model):
    important_datetime = EncryptedDateTimeField()
    # important_datetime = EncryptedDateField()


class EncInt(models.Model):
    important_number = EncryptedIntField()


class EncLong(models.Model):
    important_number = EncryptedLongField()


class EncFloat(models.Model):
    important_number = EncryptedFloatField()


class PickleObject(models.Model):
    name = models.CharField(max_length=16)
    data = PickleField()


class EmailObject(models.Model): 
    max_email = 255
    email = EncryptedEmailField()


class USPhoneNumberField(models.Model):
    phone = EncryptedUSPhoneNumberField()


class EncryptTests(unittest.TestCase):

    def setUp(self):
        EncObject.objects.all().delete()

    def test_encryption(self):
        """
        Test that the database values are actually encrypted.
        """
        password = 'this is a password!!'  # 20 chars
        obj = EncObject(password = password)
        obj.save()
        # The value from the retrieved object should be the same...
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)
        # ...but the value in the database should not
        encrypted_password = self._get_encrypted_password(obj.id)
        self.assertNotEqual(encrypted_password, password)
        self.assertTrue(encrypted_password.startswith('$AES$'))

    def test_max_field_length(self):
        password = 'a' * EncObject.max_password
        obj = EncObject(password = password)
        obj.save()
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)

    def test_field_too_long(self):
        password = 'a' * (EncObject.max_password + 1)
        obj = EncObject(password = password)
        self.assertRaises(Exception, obj.save)

    def test_UTF8(self):
        password = u'совершенно секретно'
        obj = EncObject(password = password)
        obj.save()
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)
    
    def test_consistent_encryption(self):
        """
        The same password should not encrypt the same way twice.
        Check different lengths.
        """
        # NOTE:  This may fail occasionally because the randomly-generated padding could be the same for both values.
        # A 14-char string will only have 1 char of padding.  There's a 1/len(string.printable) chance of getting the
        # same value twice.
        for pwd_length in range(1,21):  # 1-20 inclusive
            enc_pwd_1, enc_pwd_2 = self._get_two_passwords(pwd_length)
            self.assertNotEqual(enc_pwd_1, enc_pwd_2)
    
    def test_minimum_padding(self):
        """
        There should always be at least two chars of padding.
        """
        enc_field = EncryptedCharField()
        for pwd_length in range(1,21):  # 1-20 inclusive
            password = 'a' * pwd_length  # 'a', 'aa', ...
            self.assertTrue(enc_field._get_padding(password) >= 2)

    ### Utility methods for tests ###

    def _get_encrypted_password(self, id):
        cursor = connection.cursor()
        cursor.execute("select password from django_fields_encobject where id = %s", [id,])
        passwords = map(lambda x: x[0], cursor.fetchall())
        self.assertEqual(len(passwords), 1)  # only one
        return passwords[0]

    def _get_two_passwords(self, pwd_length):
        password = 'a' * pwd_length  # 'a', 'aa', ...
        obj_1 = EncObject(password = password)
        obj_1.save()
        obj_2 = EncObject(password = password)
        obj_2.save()
        # The encrypted values in the database should be different.
        # There's a chance they'll be the same, but it's small.
        enc_pwd_1 = self._get_encrypted_password(obj_1.id)
        enc_pwd_2 = self._get_encrypted_password(obj_2.id)
        return enc_pwd_1, enc_pwd_2


class DateEncryptTests(unittest.TestCase):
    def setUp(self):
        EncDate.objects.all().delete()

    def test_BC_date(self):
        # datetime.MINYEAR is 1 -- so much for history
        func = lambda: datetime.date(0, 1, 1)
        self.assertRaises(ValueError, func)

    def test_date_encryption(self):
        today = datetime.date.today()
        obj = EncDate(important_date=today)
        obj.save()
        # The date from the retrieved object should be the same...
        obj = EncDate.objects.get(id=obj.id)
        self.assertEqual(today, obj.important_date)
        # ...but the value in the database should not
        important_date = self._get_encrypted_date(obj.id)
        self.assertTrue(important_date.startswith('$AES$'))
        self.assertNotEqual(important_date, today)

    def test_date_time_encryption(self):
        now = datetime.datetime.now()
        obj = EncDateTime(important_datetime=now)
        obj.save()
        # The datetime from the retrieved object should be the same...
        obj = EncDateTime.objects.get(id=obj.id)
        self.assertEqual(now, obj.important_datetime)
        # ...but the value in the database should not
        important_datetime = self._get_encrypted_datetime(obj.id)
        self.assertTrue(important_datetime.startswith('$AES$'))
        self.assertNotEqual(important_datetime, now)

    ### Utility methods for tests ###

    def _get_encrypted_date(self, id):
        cursor = connection.cursor()
        cursor.execute("select important_date from django_fields_encdate where id = %s", [id,])
        important_dates = map(lambda x: x[0], cursor.fetchall())
        self.assertEqual(len(important_dates), 1)  # only one
        return important_dates[0]

    def _get_encrypted_datetime(self, id):
        cursor = connection.cursor()
        cursor.execute("select important_datetime from django_fields_encdatetime where id = %s", [id,])
        important_datetimes = map(lambda x: x[0], cursor.fetchall())
        self.assertEqual(len(important_datetimes), 1)  # only one
        return important_datetimes[0]


class NumberEncryptTests(unittest.TestCase):
    def setUp(self):
        EncInt.objects.all().delete()
        EncLong.objects.all().delete()
        EncFloat.objects.all().delete()

    def test_int_encryption(self):
        self._test_number_encryption(EncInt, 'int', sys.maxint)

    def test_min_int_encryption(self):
        self._test_number_encryption(EncInt, 'int', -sys.maxint - 1)

    def test_long_encryption(self):
        self._test_number_encryption(EncLong, 'long', long(sys.maxint) * 100L)

    def test_float_encryption(self):
        value = 123.456 + sys.maxint
        self._test_number_encryption(EncFloat, 'float', value)

    def test_one_third_float_encryption(self):
        value = sys.maxint + (1.0 / 3.0)
        self._test_number_encryption(EncFloat, 'float', value)

    def _test_number_encryption(self, number_class, type_name, value):
        obj = number_class(important_number=value)
        obj.save()
        # The int from the retrieved object should be the same...
        obj = number_class.objects.get(id=obj.id)
        self.assertEqual(value, obj.important_number)
        # ...but the value in the database should not
        number = self._get_encrypted_number(type_name, obj.id)
        self.assertTrue(number.startswith('$AES$'))
        self.assertNotEqual(number, value)

    def _get_encrypted_number(self, type_name, id):
        cursor = connection.cursor()
        sql = "select important_number from django_fields_enc%s where id = %%s" % (type_name,)
        cursor.execute(sql, [id,])
        important_numbers = map(lambda x: x[0], cursor.fetchall())
        self.assertEqual(len(important_numbers), 1)  # only one
        return important_numbers[0]


class TestPickleField(unittest.TestCase):
    def setUp(self):
        PickleObject.objects.all().delete()

    def test_not_string_data(self):
        items = [
            'Item 1', 'Item 2', 'Item 3', 'Item 4', 'Item 5'
        ]

        obj = PickleObject.objects.create(name='default', data=items)
        self.assertEqual(PickleObject.objects.count(), 1)

        self.assertEqual(obj.data, items)

        obj = PickleObject.objects.get(name='default')
        self.assertEqual(obj.data, items)

    def test_string_and_unicode_data(self):
        DATA = (
            ('string', 'Simple string'),
            ('unicode', u'Simple unicode string'),
        )

        for name, data in DATA:
            obj = PickleObject.objects.create(name=name, data=data)
            self.assertEqual(obj.data, data)

        self.assertEqual(PickleObject.objects.count(), 2)

        for name, data in DATA:
            obj = PickleObject.objects.get(name=name)
            self.assertEqual(obj.data, data)

    def test_empty_string(self):
        value = ''

        obj = PickleObject.objects.create(name='default', data=value)
        self.assertEqual(PickleObject.objects.count(), 1)

        self.assertEqual(obj.data, value)


class EncryptEmailTests(unittest.TestCase):

    def setUp(self):
        EmailObject.objects.all().delete()

    def test_encryption(self):
        """
        Test that the database values are actually encrypted.
        """
        email = 'test@example.com'  # 16 chars
        obj = EmailObject(email = email)
        obj.save()
        # The value from the retrieved object should be the same...
        obj = EmailObject.objects.get(id=obj.id)
        self.assertEqual(email, obj.email)
        # ...but the value in the database should not
        encrypted_email = self._get_encrypted_email(obj.id)
        self.assertNotEqual(encrypted_email, email)
        self.assertTrue(encrypted_email.startswith('$AES$'))

    def test_max_field_length(self):
        email = 'a' * EmailObject.max_email
        obj = EmailObject(email = email)
        obj.save()
        obj = EmailObject.objects.get(id=obj.id)
        self.assertEqual(email, obj.email)

    def test_UTF8(self):
        email = u'совершенно@секретно.com'
        obj = EmailObject(email = email)
        obj.save()
        obj = EmailObject.objects.get(id=obj.id)
        self.assertEqual(email, obj.email)
    
    def test_consistent_encryption(self):
        """
        The same password should not encrypt the same way twice.
        Check different lengths.
        """
        # NOTE:  This may fail occasionally because the randomly-generated padding could be the same for both values.
        # A 14-char string will only have 1 char of padding.  There's a 1/len(string.printable) chance of getting the
        # same value twice.
        for email_length in range(1,21):  # 1-20 inclusive
            enc_email_1, enc_email_2 = self._get_two_emails(email_length)
            self.assertNotEqual(enc_email_1, enc_email_2)
    
    def test_minimum_padding(self):
        """
        There should always be at least two chars of padding.
        """
        enc_field = EncryptedCharField()
        for pwd_length in range(1,21):  # 1-20 inclusive
            email = 'a' * pwd_length  # 'a', 'aa', ...
            self.assertTrue(enc_field._get_padding(email) >= 2)

    ### Utility methods for tests ###

    def _get_encrypted_email(self, id):
        cursor = connection.cursor()
        cursor.execute("select email from django_fields_emailobject where id = %s", [id,])
        emails = map(lambda x: x[0], cursor.fetchall())
        self.assertEqual(len(emails), 1)  # only one
        return emails[0]

    def _get_two_emails(self, email_length):
        email = 'a' * email_length  # 'a', 'aa', ...
        obj_1 = EmailObject(email = email)
        obj_1.save()
        obj_2 = EmailObject(email = email)
        obj_2.save()
        # The encrypted values in the database should be different.
        # There's a chance they'll be the same, but it's small.
        enc_email_1 = self._get_encrypted_email(obj_1.id)
        enc_email_2 = self._get_encrypted_email(obj_2.id)
        return enc_email_1, enc_email_2


class TestModelWithPrivateFields(ModelWithPrivateFields):
    """This model is for the unittests against ModelWithPrivateFields.
    """
    __state = models.CharField(max_length=255, editable=False)
    __state_changed_at = models.DateTimeField(editable=False, blank=True, null=True)

    def get_state(self):
        return self.__state

    def set_state(self, value):
        self.__state = value
        self.__state_changed_at = datetime.datetime.now()

    state = property(get_state, set_state)
    del get_state, set_state



class PrivateFieldsTests(unittest.TestCase):
    def test_private_fields(self):
        obj1 = TestModelWithPrivateFields(state='blah')

        self.assert_(obj1._TestModelWithPrivateFields__state_changed_at is None)
        obj1.save()

        obj2 = TestModelWithPrivateFields.objects.create(state='minor')
        self.assert_(obj2._TestModelWithPrivateFields__state_changed_at is None)

        self.assertEqual(1, TestModelWithPrivateFields.objects.filter(state='blah').count())
        self.assertEqual(2, TestModelWithPrivateFields.objects.all().count())

        obj1.state = 'blah2' # this has a side effect:
        self.assert_(obj1._TestModelWithPrivateFields__state_changed_at is not None)
        obj1.save()

        sql = unicode(TestModelWithPrivateFields.objects.filter(state='blah').query)
        self.assert_('_TestModelWithPrivateFields__' not in sql, '_TestModelWithPrivateFields__ is in the "' + sql + '"')


