# Digital Object Gate library
A Python library for direct download link retrieval of resources referenced by a Persistend Identifier. For list of registered (supported) repositories see: TBD. DOG currently supports following PIDs: HDL and DOI as well as URL's with CMDI content negotiation (![more](https://www.clarin.eu/content/component-metadata)).
 
## Usage

#### sniff(pid: string) -> string 
Tries to match PID with registered repositories and returns dict with information about repository, otherwise returns empty dict. If there are multiple repositories using the same identifier tries to resolve PID and match repo by host.

 Example:
```Python 
 from DOGlib import DOG

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
 
#### fetch(pid: string) -> dict

 Tries to match PID with registered repositories and returns dict with collection's license and description, and links to referenced resources within the collection, otherwise returns empty dict
```Python 
 from DOGlib import DOG

 dog = DOG()
 dog.fetch("https://lindat.mff.cuni.cz/repository/xmlui/handle/11234/1-3698")
```

returns:
```JSON
{
  "description": "Etalon is a manually annotated corpus of contemporary Czech. The corpus contains 1,885,589 words (2,265,722 tokens) and is annotated in the same way as SYN2020 of the Czech National Corpus. The corpus includes fiction (ca 24%), professional and scientific literature (ca 40%) and newspapers (ca 36%). \r\n\r\nThe corpus is provided in a vertical format, where sentence boundaries are marked with a blank line. Every word form is written on a separate line, followed by five tab-separated attributes: syntactic word, lemma, sublemma, tag and verbtag. The texts are shuffled in random chunks of 100 words at maximum (respecting sentence boundaries).'",
  "license": "",
  "ref_resources": [
    {
      "filename": "",
      "pid": "https://wiki.korpus.cz/doku.php/en:cnk:etalon"
    },
    {
      "filename": "http://radio.makon.cz/",
      "pid": "https://lindat.mff.cuni.cz/repository/xmlui/bitstream/handle/11234/1-3698/Etalon.tgz?sequence=1"
    }
  ]
}
```

## Installation

via PIP:
```bash
pip install requirements.txt
```

Conda:
```bash
conda env create -f environment.yml
conda activate DOG
```






















See examplary usage:
```bash
./example.py
```
