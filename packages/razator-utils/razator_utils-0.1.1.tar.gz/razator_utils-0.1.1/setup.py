#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

try: # for pip >= 10
    # noinspection PyProtectedMember
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

## workaround derived from: https://github.com/pypa/pip/issues/7645#issuecomment-578210649
parsed_requirements = parse_requirements(
    'requirements/prod.txt',
    session='workaround'
)

parsed_test_requirements = parse_requirements(
    'requirements/test.txt',
    session='workaround'
)

requirements = [str(ir.requirement) for ir in parsed_requirements]
test_requirements = [str(tr.requirement) for tr in parsed_test_requirements]

setup(
    author="Ryan Scott",
    author_email='ryan.t.scott73@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="A pypi package for personal use. Containing common functions I use.",
    install_requires=requirements,
    license="GNU General Public License v3",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='razator_utils',
    name='razator_utils',
    packages=find_packages(include=['razator_utils', 'razator_utils.*']),
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/razator73/razator_utils',
    version='0.1.1',
    zip_safe=False,
)
