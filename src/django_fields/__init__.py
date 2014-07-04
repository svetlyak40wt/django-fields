from pkg_resources import get_distribution, DistributionNotFound
import os.path

try:
    _dist = get_distribution('django-fields')
except DistributionNotFound:
    __version__ = 'Please install this project with setup.py'
else:
    __version__ = _dist.version
VERSION = __version__   # synonym