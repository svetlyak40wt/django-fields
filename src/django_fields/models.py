# -*- coding: utf-8 -*-

import sys

from django.db import models

if sys.version_info[0] == 3:
    PYTHON3 = True
else:
    PYTHON3 = False


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

