#!/usr/bin/env python

from distutils.core import setup

setup(
    name='routeros-scanner',
    version='1.7',
    description='Forensics tool for Mikrotik devices.',
    author='Noa Frumovich',
    author_email='noaf@microsoft.command',
    url='https://github.com/microsoft/routeros-scanner',
    packages=['paramiko',
    'six',
    'requests',
    'retry'],
    scripts=['main.py'],
)