# coding=utf-8
"""Python packaging."""
import os
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which path is supposed relative
    to this module."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read()


NAME = 'psykorebase'
README = read_relative_file('README')
VERSION = read_relative_file('VERSION').strip()


setup(name=NAME,
      version=VERSION,
      description='Easily perform safe (merge-based) rebases.',
      long_description=README,
      classifiers=['Development Status :: 1 - Planning',
                   'License :: OSI Approved :: BSD License',
                   'Programming Language :: Python :: 2.7',
                   ],
      keywords='git merge rebase',
      author='Benoît Bryon',
      author_email='benoit@marmelune.net',
      url='https://github.com/benoitbryon/%s' % NAME,
      license='BSD',
      packages=[NAME],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools'],
      entry_points={
          'console_scripts': [
              'psykorebase = psykorebase.cli:psykorebase',
          ]
      },
      )
