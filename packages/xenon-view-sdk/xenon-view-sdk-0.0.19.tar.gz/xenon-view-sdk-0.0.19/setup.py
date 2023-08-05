'''
Created on September 20, 2021

@author: lwoydziak
'''
import pathlib

from setuptools import setup, find_packages

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / 'README.md').read_text()

setup(name='xenon-view-sdk',
      version='0.0.19',
      maintainer='Luke Woydziak',
      maintainer_email='lwoydziak@gmail.com',
      url='https://github.com/xenonview-com/view-python-sdk',
      download_url='https://github.com/xenonview-com/view-python-sdk/tarball/1.0',
      platforms=['any'],
      description='Python access to Xenon View.',
      long_description=README,
      long_description_content_type='text/markdown',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Natural Language :: English',
          'Operating System :: Unix',
          'Programming Language :: Python',
          'Programming Language :: Unix Shell',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      packages=find_packages(include=[
          'xenon_view_sdk'
      ]),
      install_requires=[
          'singleton3',
          'requests',
          'pytz'
      ],
      python_requires='>=3',

      )
