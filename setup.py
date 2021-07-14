from setuptools import find_packages, setup

setup(
    name='doglib',
    packages=find_packages(include=['doglib']),
    version='0.1.0',
    package_data={'doglib': ['*.json', 'repo_configs/*.json']}
    include_package_data=True,
    description='Digital Object Gate Python library',
    author='Michał Gawor',
)
