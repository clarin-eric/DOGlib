from doglib import DOG
from repos import RegRepo
from pid import PID, HDL

"""
Examples of DOGlib supported repositories
"""


if __name__ == "__main__":
    dog = DOG()

    # url = 'https://collections.clarin.eu/details/1033'
    # pid = PID(url)
    # print(pid.get_pid_type())
    # ret = dog.sniff(url)
    # print(ret)
    # ret = dog.fetch(url)
    # print(ret)

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3422'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3422'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3422'
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)

    url = 'http://hdl.handle.net/11022/1007-0000-0000-8DEE-6'
    pid = PID(url)
    hdl = HDL(url)
    print(hdl)
    print(pid.get_pid_type())
    ret = dog.sniff(url)
    print(ret)
    ret = dog.fetch(url)
    print(ret)
