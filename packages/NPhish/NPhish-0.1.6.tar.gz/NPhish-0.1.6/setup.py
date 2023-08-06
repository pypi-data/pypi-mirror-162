from setuptools import setup

long_description = open('README.md').read()

setup(name="NPhish",
version="0.1.6",
license='LICENCE',
description="Ultimate Phishing Tool in Python",
long_description = long_description,
long_description_content_type='text/markdown',
author="Nishant",
url='https://github.com/Nishant2009/NPhish/',
scripts=['NPhish'],
install_requires= ['colourfulprint'],
classifiers=[
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
], )
