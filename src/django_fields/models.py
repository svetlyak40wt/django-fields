# -*- coding: utf-8 -*-

import re
from django.db import models


class PrivateFieldsMetaclass(models.base.ModelBase):
    """Metaclass to set right default db_column values
    for mangled private fields.

    For example, python transforms field __secret_state of the model
    Machine, to the _Machine__secret_state and you don't want
    database column has this ugly name. There are two possibilities:

    * to specify column name via arguments to django Field class, or…
    * to use this PrivateFieldsMetaclass which will say django:
      "Hey, for this field `_Machine__secret_state` use db_column
      `secret_state`, please!"

    """
    def __new__(cls, name, bases, attrs):
        super_new = super(PrivateFieldsMetaclass, cls).__new__

        prefix = '_' + name + '__'
        for key, value in attrs.iteritems():
            if key.startswith(prefix) and hasattr(value, 'db_column') and value.db_column is None:
                value.db_column = key[len(prefix):]

        result = super_new(cls, name, bases, attrs)
        return result


class ModelWithPrivateFields(models.Model):
    """This abstract base class allows you to use "private" fields in django models for better encapsulation.

    It does two things:

    * adds a one more item into the Django's internal name map for the model class;
    * mangles constructor kwargs so that short names could be used.

    The first thing needs to make `filter`, `get` and other methods accept short field names.
    For example, let you want to use this class:

        class TestModel(ModelWithPrivateFields):
            __state = models.CharField(max_length=255, editable=False)

    Then you will not be able to execute `TestModel.objects.filter(state='blah')` and
    Django will not allow you to run `TestModel.objects.filter(_TestModel__state='blah')`
    because it will see `__` in the param and try to make join using missing field `_TestModel`.

    Monkey patching of the `init_name_map` method, resolves this problem.

    Another obstacle is that you can't pass short field names into the class's constructor like that:
    `obj = TestModel(state='blah')`, because Django does not know about `state` attribute, but is
    aware of `_TestModel__state`. That is why `PrivateFieldsMetaclass` mangles such keyword attributes
    in the `__init__` method.

    """
    __metaclass__ = PrivateFieldsMetaclass

    def __init__(self, *args, **kwargs):
        new_kwargs = {}
        prefix = '_' + self.__class__.__name__ + '__'

        field_names = set(f.name for f in self._meta.fields)

        for key, value in kwargs.iteritems():
            if prefix + key in field_names:
                key = prefix + key
            new_kwargs[key] = value

        _init_name_map_orig = self._meta.init_name_map

        def init_name_map(self):
            cache = _init_name_map_orig()

            for key, value in cache.items():
                match = re.match(r'^_.+__(.*)', key)
                if match is not None:
                    cache[match.group(1)] = value
            return cache
        init_name_map.patched = True

        if not getattr(self._meta.init_name_map, 'patched', False):
            self._meta.init_name_map = type(_init_name_map_orig)(init_name_map, type(self._meta))

        super(ModelWithPrivateFields, self).__init__(*args, **new_kwargs)

    class Meta:
        abstract = True

