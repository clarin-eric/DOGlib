# Changelog


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

