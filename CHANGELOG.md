# Changelog

## [1.0.11] - TBD

### Added features
- FetchResult dataclass expanded with "author" and "title" field, logic for JSON and XML TBD 
- pilot FAIR signposting support, SignposterParser as optional for repositories supporting signposting  
- jsonpath-rw for json parsing. Planned to apply to JSON parser as well
- remove `requests` from dependencies, rely solely on `PyCurl`
- dependency bump: certifi -> 2025.8.3, lxml -> 6.0.1, pycurl -> 7.45.6
- add `wheel` 0.45.1 to dependency tree as jsonpath-rw uses legacy setuptools
- better try-catch for signposting

### Bugfixes
- dynamic versioning in UI
- sniff api call


## [1.0.10] - 15.10.2024

### Bugfixes
- prune CMU
- minor bugfixes


## [1.0.9] - 26.09.2024

### Added features
- HTML parser
- ADS config registration
- replaced dict type hints on parser methods with well-typed dataclasses


## [1.0.8] - 12.08.2024

### Added features
- registered repository status


## [1.0.7] - 24.06.2024

### Changed features
- Data Type Registry integration. doglib.expand_datatype() returning MIME type taxonomy from DTR 
- better README 


## [1.0.6] - 11.04.2024

### Changed features
- DOGlib distribution as a wheel for internal CLARIN use
- Data Type Registry integration adjusted for taxonomies from latest development instace of DTR
- GPL3.0 license file


## [1.0.5] - 4.04.2024

### Changed features
- First DTR integration release


## [1.0.4] - 3.07.2023

### Changed features
- Standarise on Poetry backend build, setuptools is legacy
- Fetch now always returns List instance not comprehension (DOGapp issue with context type filtering in Django templates)
- Minor changes and improvements
- Fixed inconsistent output format for cases where no resource type is linked


## [1.0.3] - 4.05.2023

### Changed features
- Added ```resolve_identifier_conflicts``` bool flag for clashing repo identifiers resolution


## [1.0.2] - 23.01.2023

### Changed features
- Allow PID instance as argument to sniff fetch and identify and pid_factory
- CI migrated from Travis to GitActions
- added is_pid(Union[str, PID]) -> bool to core functionalities
- remove EKUT from testing due to Forbidden access to the repository for over a month


## [1.0.1] - 3.10.2022

### Changed features
- Fixed tests failing silently
- Fixed repositories serving CMDI via OAI-PMH endpoint (e.g. ACDH-CH)
- Added static testing along with logic for procuring static resources and the resources
- Changed SCM from setup.py to pyproject.toml
- Fixed CI


## [1.0.0] - 16.05.2022

First release of Digital Object Gate
- Support for repositories serving CMDI metadata via content negotiation
- Support for repositories serving metadata via OAI-OMH endpoint 
- Support for Invinio repositories (B2SHARE, Zenodo)
- Support for Europeana

