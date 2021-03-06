from setuptools import setup, find_packages
import sys, os

version = '1.0.0'

setup(
    name='ckanext-odm_audit',
    version=version,
    description="OD Mekong CKAN's audit extension",
    long_description='''
    ''',
    classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='',
    author='Alex Corbi',
    author_email='alex@open-steps.org',
    url='http://www.open-steps.org',
    license='AGPL3',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    namespace_packages=['ckanext'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        # -*- Extra requirements: -*-
    ],
    entry_points='''
        [ckan.plugins]
        odm_audit=ckanext.odm_audit.plugin:OdmAuditPlugin
    ''',
)
