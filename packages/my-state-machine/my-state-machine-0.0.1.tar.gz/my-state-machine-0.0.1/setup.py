#!/usr/bin/python
# coding = utf-8

from setuptools import setup

setup(
    name='my-state-machine',
    version='0.0.1',
    description='Simple State Machine',
    long_description='''You can use this library to build a state machine.
    ''',
    author='Wenhan Zhang',
    license='MIT License',
    platforms='any',
    packages=['my_state_machine'],
    install_requires = [
        'Pillow>=9.1.0'
    ]
)