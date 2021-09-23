from doglib import DOG
if __name__ == "__main__":
    dog = DOG()

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698'
    print(f"Processed PID:\n{url}")
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    input()


    url = 'http://hdl.handle.net/11022/1007-0000-0000-8DEE-6'
    print(f"Processed PID:\n{url}")
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    url = 'https://b2share.eudat.eu/records/5399170dc1b8415a90af3f52a6362227'
    print(f"Processed PID:\n{url}")
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")

    input("END")
