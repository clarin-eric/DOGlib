from setuptools import find_packages, setup

setup(
    name='doglib',
    packages=find_packages(include=['doglib']),
    version='0.1.0',
    description='Digital Object Gate Python library',
    author='Michał Gawor',
    install_requires=['certifi==2021.5.30', 'pycurl==7.43.0.6'],
    test_requires=['lxml==4.6.3'],
)
