from setuptools import setup, find_packages

setup(
    url = 'http://github.com/bryanhelmig/django-fields/',
    download_url='https://github.com/bryanhelmig/django-fields/',
    install_requires = ['pycrypto', ],
    package_dir = {'': 'src'},
    packages = ['django_fields'],
    #include_package_data = True,
)


