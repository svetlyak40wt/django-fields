# -*- coding: utf-8 -*-
import datetime
import string
import sys
import unittest

from django.db import connection
from django.db import models

from fields import EncryptedCharField, EncryptedDateField, EncryptedDateTimeField, EncryptedIntField, EncryptedLongField, EncryptedFloatField, PickleField


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


class EncryptTests(unittest.TestCase):

    def setUp(self):
        EncObject.objects.all().delete()

    def testEncryption(self):
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

    def testMaxFieldLength(self):
        password = 'a' * EncObject.max_password
        obj = EncObject(password = password)
        obj.save()
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)

    def testFieldTooLong(self):
        password = 'a' * (EncObject.max_password + 1)
        obj = EncObject(password = password)
        self.assertRaises(Exception, obj.save)

    def testUTF8(self):
        password = u'совершенно секретно'
        obj = EncObject(password = password)
        obj.save()
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)
    
    def testConsistentEncryption(self):
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
    
    def testMinimumPadding(self):
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

    def testBCDate(self):
        # datetime.MINYEAR is 1 -- so much for history
        func = lambda: datetime.date(0, 1, 1)
        self.assertRaises(ValueError, func)

    def testDateEncryption(self):
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

    def testDateTimeEncryption(self):
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

    def testIntEncryption(self):
        self._testNumberEncryption(EncInt, 'int', sys.maxint)

    def testMinIntEncryption(self):
        self._testNumberEncryption(EncInt, 'int', -sys.maxint - 1)

    def testLongEncryption(self):
        self._testNumberEncryption(EncLong, 'long', long(sys.maxint) * 100L)

    def testFloatEncryption(self):
        value = 123.456 + sys.maxint
        self._testNumberEncryption(EncFloat, 'float', value)

    def testOneThirdFloatEncryption(self):
        value = sys.maxint + (1.0 / 3.0)
        self._testNumberEncryption(EncFloat, 'float', value)

    def _testNumberEncryption(self, number_class, type_name, value):
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
