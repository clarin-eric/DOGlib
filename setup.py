from setuptools import find_packages, setup

setup(
    name="doglib",
    packages=["doglib"],
    version='0.1.0',
    package_data={"doglib": ["*.json"]},
    include_package_data=True,
    description='Digital Object Gate Python library',
    author='Michał Gawor',
)
