from setuptools import find_packages, setup

setup(
    name="doglib",
    packages=find_packages(),
    version='0.1.0',
    include_package_data=True,
    package_data={"": ["*.json"]},
    description='Digital Object Gate Python library',
    author='Michał Gawor',
)
