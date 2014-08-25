from setuptools import setup

import swift3_gatekeeper

setup(name='swift3_gatekeeper',
      version=swift3_gatekeeper.version,
      description='Middleware to filter S3 relational user-metadata in swift',
      license='Apache License (2.0)',
      author='a2company',
      author_email='admin@a2company.co.kr',
      packages=['swift3_gatekeeper'],
      install_requires=['swift >= 1.13.0', 'swift3 >= 1.7.0'],
      entry_points={'paste.filter_factory':
                        ['swift3_gatekeeper='
                         'swift3_gatekeeper.middleware:filter_factory']})