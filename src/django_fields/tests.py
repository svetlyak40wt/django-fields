# -*- coding: utf-8 -*-
import unittest

from django.db import models

from fields import EncryptedCharField, PickleField


class EncObject(models.Model):
    password = EncryptedCharField(max_length=20)

class PickleObject(models.Model):
    name = models.CharField(max_length=16)
    data = PickleField()

class EncryptTests(unittest.TestCase):
    def testMaxFieldLength(self):
        password = 'this is a password!!'
        obj = EncObject(password = password)
        obj.save()
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)


    def testUTF8(self):
        password = u'совершенно секретно'
        obj = EncObject(password = password)
        obj.save()
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)

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
