# Digital Object Gate library
A Python library for direct download link retrieval of resources referenced by a Persistend Identifier. For list of registered (supported) repositories see: TBD. DOG currently supports following PIDs: HDL and DOI as well as URL's with CMDI content negotiation [more](https://www.clarin.eu/content/component-metadata).

## Supported repositories
Status of currently supported repositories can be found in [spreadsheet](https://docs.google.com/spreadsheets/d/1k4QiuCf2N9rsVNeqewXrhhJlZIF_3M3PVdMwyZRRCRk/edit?usp=sharing). Automatic update of status of registered repositories will come in the future.
 
## Usage
In order to use Digital Object Gate functionalities, create an instance of doglib.DOG, which loads .json configurations of registered repositories. DOG offers the following methods:

### DOGlib

#### sniff(pid: str, format='dict') -> Union\[dict, str\]
Tries to match PID with registered repositories and returns dict with information about repository, otherwise returns empty dict. If there are multiple repositories using the same identifier tries to resolve PID and match repo by host.  
By default, returns dictionary, if format=='jsons' returns a JSON string.

 Example:
```Python 
 from doglib import DOG

 dog = DOG()
 dog.sniff("https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698")
```

returns:
```JSON
{
  "name": "LINDAT/CLARIAH-CZ", 
  "host_name": "LINDAT/CLARIAH-CZ", 
  "host_netloc": "https://lindat.mff.cuni.cz"
}

```
 
#### fetch(pid: str, format='dict', dtr: bool = False) -> Union\[dict, str\]

Tries to match PID with registered repositories and returns dict/string with collection's title, license and description, and links to referenced resources within the collection, otherwise returns empty dict/string.  
By default, returns dictionary, if format=='jsons' returns a JSON string.
```Python 
 from doglib import DOG

 dog = DOG()
 dog.fetch("https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698")
```

returns:
```JSON
{
  "ref_files": 
    [
      {"resource_type": "Resource", "filename": "", "pid": "https://wiki.korpus.cz/doku.php/en:cnk:etalon"}, 
      {"resource_type": "Resource", "filename": "", "pid": "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3698/Etalon.tgz?sequence=1"},
      {"resource_type": "LandingPage", "filename": "", "pid": "https://hdl.handle.net/11234/1-3698"}
    ], 
    "description": "Etalon is a manually annotated corpus of contemporary Czech. The corpus contains 1,885,589 words (2,265,722 tokens) and is annotated in the same way as SYN2020 of the Czech National Corpus. The corpus includes fiction (ca 24%), professional and scientific literature (ca 40%) and newspapers (ca 36%). \\r\\n\\r\\nThe corpus is provided in a vertical format, where sentence boundaries are marked with a blank line. Every word form is written on a separate line, followed by five tab-separated attributes: syntactic word, lemma, sublemma, tag and verbtag. The texts are shuffled in random chunks of 100 words at maximum (respecting sentence boundaries).", 
    "license": "http://creativecommons.org/licenses/by-nc-sa/4.0/"
}

```

#### identify(pid: str, format='dict) -> Union\[dict, str\]

Tries to match PID with registered repositories and returns dict/string with collection's title, license, desciption and reverse pid, otherwise returns empty dict/string.
By default, returns dictionary, if format=='jsons' returns a JSON string.
```Python
 from doglib import DOG
 dog = DOG()
 dog.identify("https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698")
``` 

returns:
```JSON
{
  "item_title": "LINDAT / CLARIAH-CZ Data & Tools", 
  "description": "Etalon is a manually annotated corpus of contemporary Czech. The corpus contains 1,885,589 words (2,265,722 tokens) and is annotated in the same way as SYN2020 of the Czech National Corpus. The corpus includes fiction (ca 24%), professional and scientific literature (ca 40%) and newspapers (ca 36%). \r\n\r\nThe corpus is provided in a vertical format, where sentence boundaries are marked with a blank line. Every word form is written on a separate line, followed by five tab-separated attributes: syntactic word, lemma, sublemma, tag and verbtag. The texts are shuffled in random chunks of 100 words at maximum (respecting sentence boundaries).", 
  "reverse_pid": "https://hdl.handle.net/11234/1-3698@format=cmdi"}
```

#### is_host_registered(pid: str) -> bool

Checks whether PID is hosted by registered repository or not. Note that it may be slower then expected, due to some repositories using same institutional ID in their PIDs (HDl/DOI). In such cases DOG tries to resolve the PID and match the host with registered repositories.   


#### is_collection(pid: str) -> bool

Checkes whether PID is a collection hosted by registered repository. Note that this method tries to resolve the PID in order to verify whether it is a collection, therefor may be slow.

### Data Type Registry

#### expand_datatype(data_type: str) -> dict

Returns DTR MIME type taxonomy for a given MIME type
```Python
 from doglib import expand_datatype
 expand_datatype("text/xml")
```

returns:
```JSON
{'21.T11969/372ea08cab33e71c02c6': {'date': 1714003200, 'reference': '', 'children': {'21.T11969/f33c32fa8246e2ca6d5c': 'text/xml'}, 'origin': 'Typeregistry-EOSC', 'name': 'text', 'description': '', 'id': '21.T11969/372ea08cab33e71c02c6', 'type': 'TaxonomyNode', 'authors': [], 'parents': {}}, '21.T11969/f33c32fa8246e2ca6d5c': {'date': 1714003200, 'reference': '', 'children': {'21.T11969/10e5cfe3b2a481871e10': 'application/x-cmdi+xml', '21.T11969/fe61e4792b37f2bbb26e': 'application/tei+xml'}, 'origin': 'Typeregistry-EOSC', 'name': 'text/xml', 'description': '', 'id': '21.T11969/f33c32fa8246e2ca6d5c', 'type': 'TaxonomyNode', 'authors': [], 'parents': {'21.T11969/372ea08cab33e71c02c6': 'text'}}, '21.T11969/fe61e4792b37f2bbb26e': {'date': 1714003200, 'reference': '', 'children': {}, 'origin': 'Typeregistry-EOSC', 'name': 'application/tei+xml', 'description': '', 'id': '21.T11969/fe61e4792b37f2bbb26e', 'type': 'TaxonomyNode', 'authors': [], 'parents': {'21.T11969/f33c32fa8246e2ca6d5c': 'text/xml'}}, '21.T11969/10e5cfe3b2a481871e10': {'date': 1714003200, 'reference': '', 'children': {}, 'origin': 'Typeregistry-EOSC', 'name': 'application/x-cmdi+xml', 'description': '', 'id': '21.T11969/10e5cfe3b2a481871e10', 'type': 'TaxonomyNode', 'authors': [], 'parents': {'21.T11969/f33c32fa8246e2ca6d5c': 'text/xml'}}}
```

## Installation
It is recommended to install DOGlib in the virtual environment to avoid dependency clash. In order to install DOGlib enter cloned directory and install it via pip with explicit requirements.txt from the project.
Clone the repository and enter the directory:
```bash
git clone https://github.com/clarin-eric/DOGlib.git
pip install ./DOGlib
```
DOGlib utilises `lxml` which requires `libxml2` and `libxslt` system libraries. Use your system package manager, on Debian/Ubuntu:
```bash
sudo apt-get install libxml2-dev libxslt-dev
```



