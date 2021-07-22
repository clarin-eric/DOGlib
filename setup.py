from setuptools import find_packages, setup

setup(
    name="doglib",
    package_dir={"": "src"},
    packages=find_packages("src"),
    version='0.1.0',
    package_data={"src": ["*.json"]},
    include_package_data=True,
    description='Digital Object Gate Python library',
    author='Michał Gawor',
)
