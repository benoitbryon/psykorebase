# -*- coding: utf-8 -*-
"""Python packaging."""
import os
from setuptools import setup


def read_relative_file(filename):
    """Returns contents of the given file, which is relative to this module."""
    with open(os.path.join(os.path.dirname(__file__), filename)) as f:
        return f.read().strip()


NAME = 'psykorebase'
README = read_relative_file('README.rst')
CHANGELOG = read_relative_file('CHANGELOG.rst')
VERSION = read_relative_file('VERSION')
REQUIRES = ['six']
ENTRY_POINTS = {
    'console_scripts': [
        'psykorebase = psykorebase.cli:psykorebase',
        'git-psykorebase = psykorebase.cli:psykorebase',
    ]
}


def run_setup():
    """Actually run setup()."""
    setup(name=NAME,
          version=VERSION,
          description='Easily perform safe (merge-based) rebases.',
          long_description=README + '\r\n' + CHANGELOG,
          classifiers=['Development Status :: 1 - Planning',
                       'License :: OSI Approved :: BSD License',
                       'Programming Language :: Python :: 2.7',
                       'Programming Language :: Python :: 3.4'],
          keywords='git merge rebase',
          author='Benoît Bryon',
          author_email='benoit@marmelune.net',
          url='https://github.com/benoitbryon/%s' % NAME,
          license='BSD',
          packages=[NAME],
          include_package_data=True,
          zip_safe=False,
          install_requires=REQUIRES,
          entry_points=ENTRY_POINTS)


if __name__ == '__main__':  # Don't trigger setup() on import.
    run_setup()
