import os
import sys
import django

from django.conf import settings
from django.test.utils import get_runner


def runtests():
    os.environ['DJANGO_SETTINGS_MODULE'] = 'example.settings'
    django.setup()
    TestRunner = get_runner(settings)
    test_runner = TestRunner()
    failures = test_runner.run_tests(["django_fields.tests"])
    sys.exit(bool(failures))

if __name__ == '__main__':
    runtests()
