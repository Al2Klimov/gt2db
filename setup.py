# SPDX-License-Identifier: AGPL-3.0-or-later

from setuptools import setup, find_packages

setup(name='gt2db', version='1.0', packages=find_packages(), install_requires=['psycopg2', 'pytrends', 'sdnotify'])
