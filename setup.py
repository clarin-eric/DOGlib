from setuptools import find_packages, setup


install_requires = ["certifi", 
                    "lxml>=4.6", 
                    "pycurl>=7"]

setup(
    name="doglib",
    packages=find_packages(),
    version='0.1.0',
    include_package_data=True,
    install_requires = install_requires,
    package_data={"": ["*.json"]},
    description='Digital Object Gate Python library',
    author='Michał Gawor',
)
