#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='routeros_scanner',
    version='1.8',
    description='Forensics tool for Mikrotik devices.',
    author='Noa Frumovich',
    author_email='noaf@microsoft.command',
    url='https://github.com/microsoft/routeros-scanner',
    packages=['paramiko',
    'six',
    'requests',
    'retry'],
    scripts=['src/routeros_scanner/main.py'],
)