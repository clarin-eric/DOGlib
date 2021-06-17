from doglib import DOG
from repos import RegRepo
from pid import PID, HDL

"""
Examples of DOGlib supported repositories
"""


if __name__ == "__main__":
    dog = DOG()


    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698'
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = 'https://collections.clarin.eu/details/1030'
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = "https://zenodo.org/record/1639549#.YIu0fxKxXs0"
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = "http://hdl.handle.net/hdl:11022/0000-0000-20E0-E"
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = "http://hdl.handle.net/11022/1007-0000-0000-8DEE-6"
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698'
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")
