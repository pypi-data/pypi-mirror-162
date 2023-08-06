"""
mfacopy
===

Multi-factor authentication on your command line.

"""
from setuptools import setup

setup(
    name='mfacopy',
    version='0.0.3',
    url='https://github.com/sunskblue/mfacopy',
    author='sunskblue',
    author_email='961370624@qq.com',
    description='Multi-factor authentication on your command line',
    long_description=__doc__,
    packages=['mfacopy'],
    entry_points={
        'console_scripts': ['mfacopy = mfacopy.cli:cli']
    },
    install_requires=[
        'click == 8.1.3',
        'keyring == 23.8.2',
        'onetimepass == 1.0.1'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.4',
        'Topic :: Utilities'
    ]
)
