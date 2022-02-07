import os
import sys

PACKAGE_PARENT = '..'
SCRIPT_DIR = os.path.dirname(os.path.realpath(os.path.join(os.getcwd(), os.path.expanduser(__file__))))
sys.path.append(os.path.normpath(os.path.join(SCRIPT_DIR, PACKAGE_PARENT)))

from doglib import DOG

"""
Examples of DOGlib supported repositories
"""


if __name__ == "__main__":
    dog = DOG()

    url = 'https://archive.mpi.nl/objects/tla:1839_00_0000_0000_0018_A640_9/datastreams/CMD/content?asOfDateTime=2018-03-02T11:00:00.000Z'
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = 'https://archive.mpi.nl/tla/islandora/object/tla:1839_00_0000_0000_0018_A640_9?asOfDateTime=2018-03-02T11:00:00.000Z'
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = 'http://hdl.handle.net/1839/00-0000-0000-0018-A640-9'
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = "https://collections.clarin.eu/details/1030"
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = "http://hdl.handle.net/1839/00-0000-0000-0018-A640-9@view"
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = "http://hdl.handle.net/hdl:11022/0000-0000-20E0-E"
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = "http://hdl.handle.net/11022/1007-0000-0000-8DEE-6"
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698'
    print("The URL")
    print(url)
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")
