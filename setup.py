from setuptools import setup
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

install_dependencies = [
    'python-libnmap==0.7.0',
    'robotframework==3.0.4',
]

setup(
    name='RoboNmap',
    version='1.1',
    packages=[''],
    package_dir={'': 'robotnmap'},
    url='',
    license='MIT License',
    author='Kostas Tripitiris',
    install_requires=install_dependencies,
    description='''RobotNmap - Robot Framework Library 
    for Nmap Port and Volnerability Scanner''',
    long_description=long_description,
    long_description_content_type='text/markdown'
)
