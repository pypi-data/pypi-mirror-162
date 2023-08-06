import os
from setuptools import setup, find_packages
from os import environ

url = '{GITHUB_SERVER_URL}/{GITHUB_REPOSITORY}'
version = environ['GITHUB_REF'].split('/')[-1]

setup(
    name='afip-ws',
    version=version,
    author='Gaston Michel',
    author_email='michel.z.gaston@gmail.com',
    description='Python library to easily interact with AFIP Web Services',
    url=url.format(**environ),
    long_description_content_type='text/markdown',
    long_description=open('README.md').read(),
    packages=find_packages('./afip'),
    install_requires=open('requirements.txt').readlines(),
    keywords=['afip', 'ws', 'python'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: Unix',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows'
    ]
)
