from doglib import DOG
from repos import RegRepo
from pid import DOI, URL

"""
Examples of DOGlib supported repositories
"""


if __name__ == "__main__":
    dog = DOG()

    url = 'https://collections.clarin.eu/details/1033'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3422'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = '11304/a287e5b9-feca-4ad6-bc16-14675d574088'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)
