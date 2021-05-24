from doglib import DOG
from repos import RegRepo
from pid import PID, HDL

"""
Examples of DOGlib supported repositories
"""


if __name__ == "__main__":
    dog = DOG()

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3422'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = 'http://hdl.handle.net/11022/1007-0000-0000-8DEE-6'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = "https://b2share.eudat.eu/records/5399170dc1b8415a90af3f52a6362227"
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = "hdl:11304/d91121d1-f31c-410f-96e1-4d9f5839e74f"
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = "10.23728/b2share.5399170dc1b8415a90af3f52a6362227"
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = "https://zenodo.org/record/1639549#.YIu0fxKxXs0"
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = "http://hdl.handle.net/hdl:11022/0000-0000-20E0-E"
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = "http://hdl.handle.net/11022/1007-0000-0000-8DEE-6"
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = 'https://collections.clarin.eu/details/1017'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)
