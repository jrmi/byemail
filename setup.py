from setuptools import setup
from importlib import import_module

VERSION = import_module("byemail").__version__
URL = import_module("byemail").__url__

setup(name='byemail',
      version=VERSION,
      description='byemail',
      classifiers=[
          'Development Status :: 4 - Beta',
          'License :: OSI Approved :: Apache Software License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3 :: Only',
          'Operating System :: POSIX :: Linux',
          'Topic :: Internet',
          'Programming Language :: Python',
      ],
      keywords='mail asyncio smtp webmail',
      url=URL,

      author='Jeremie Pardou',
      author_email='jeremie.pardou@mhcomm.fr',

      license='Apache Software License',
      packages=['byemail'],

      entry_points={
          'console_scripts': [
              'byemail = byemail.commands:run.start',
          ]
      },

      test_suite='nose.collector',
      install_requires=['begins'],
      extras_require={
      },
      tests_require=['nose', 'nose-cover3'],
)