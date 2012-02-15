#!/bin/bash

set -e

if [ ! -e 'env' ]; then
    python virtualenv.py env
    env/bin/pip install -U -r requirements.txt
fi

env/bin/python src/example/manage.py test $@
