"""A setuptools based setup module.
See:
https://packaging.python.org/en/latest/distributing.html
"""

# To use a consistent encoding
from codecs import open
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
# with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
#     long_description = f.read()

setup(
    name='StackItDecklist',
    version='1.4.0',
    description='Generates visual decklists for various TCGs',
    url='https://github.com/poppu-mtg/StackIt',
    author='Guillaume Robert-Demolaize & Katelyn Gigante',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Games/Entertainment :: Board Games',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='mtg tcg',

    packages=find_packages(exclude=['contrib', 'docs', 'tests']),

    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'lxml',
        'pillow',
        'requests',
        'pyYAML',
        'watchdog',
        'cachecontrol[filecache]',
        'appdirs'
        ],

    # extras_require={
    #     'dev': ['check-manifest'],
    #     'test': ['coverage'],
    # },

    package_data={
        'StackIt': [
            'resources/StackIt-Logo.png'
            'resources/*/*.ttf',
            'resources/*/*.otf',
            'resources/*/*.png',
            'resources/*/*.dat',
            ],
    },

    scripts=['StackIt.py'],
)
