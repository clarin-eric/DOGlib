# Digital Object Gate library
A Python library for direct download link retrieval of resources referenced by a collection with Persistend Identifier in a registered repository. For list of registered repositories see: TBD. It provides two methods:
 
## Usage

###### sniff(pid: string) -> string 
 Checks whether entity with given PID is stored in registered repository, if it is returns repository information.
 Returns dict with information about hosting repository

 Example:
```Python 
 from DOGlib import DOG

 dog = DOG()
 dog.sniff(""))
```

```JSON
 
```
 
###### fetch(pid: string) -> dict

 Returns dict with collection's licence and description and list of download links to referenced resource.

```Python 
 from DOGlib import DOG

 dog = DOG()
 dog.sniff(""))
```

```JSON
{
 "licence": 
}
```

## Installation

























See examplary usage:
```bash
./example.py
```
