import unittest

from django.db import models
from fields import EncryptedCharField

class EncObject(models.Model):
    password = EncryptedCharField(max_length=20)

class EncryptTests(unittest.TestCase):
    def testMaxFieldLength(self):
        password = 'this is a password!!'
        obj = EncObject(password = password)
        obj.save()
        obj = EncObject.objects.get(id=obj.id)
        self.assertEqual(password, obj.password)

