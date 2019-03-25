from setuptools import setup, find_packages

version = '0.3.0'

setup(
    name='django-fields',
    version=version,
    description='Django-fields is an application which includes different kinds of models fields.',
    keywords='django apps tools collection',
    license='New BSD License',
    author='Alexander Artemenko',
    author_email='svetlyak.40wt@gmail.com',
    url='http://github.com/svetlyak40wt/django-fields/',
    install_requires=[
        'django',
        'pycryptodome',
    ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Plugins',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    package_dir={'': 'src'},
    packages=['django_fields'],
    include_package_data=True,
    test_suite="runtests.runtests",
)
