from doglib import DOG

if __name__ == "__main__":
    dog = DOG()

    url = 'https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698'
    print("The URL:")
    print(url)
    print("\n")
    ret = dog.sniff(url)
    print("This is sniff() output")
    print(ret)
    print("\n")
    ret = dog.fetch(url)
    print("This is fetch() output")
    print(ret)
    print("\n")
    ret = dog.identify(url)
    print("This is identify() output")
    print(ret)
    print("\n")
