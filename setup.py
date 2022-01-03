from setuptools import find_packages, setup


setup(
    name="doglib",
    packages=find_packages(),
    version='1.0.0',
    include_package_data=True,
    package_data={"": ["*.json"]},
    description='Digital Object Gate Python library',
    author='Michał Gawor',
    install_requires=['certifi', 'pycurl>7.x.x', 'lxml>=4.6'],
)
