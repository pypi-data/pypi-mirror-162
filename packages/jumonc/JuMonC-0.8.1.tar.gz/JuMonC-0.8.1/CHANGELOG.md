# Changelog JuMonC

## [0.8.1] - 2022-08-05
### Fixed
- bug in task distribution

## [0.8.0] - 2022-06-22
### Changed
- Plugins
    - now using pluggy as plugin manager
    - [example plugin](https://gitlab.jsc.fz-juelich.de/coec/jumonc-logparser)

## [0.7.1] - 2022-05-23
### Fixed
- PyPi extra GPU was not available

## [0.7.0] - 2022-05-23
### Added
- GPU monitoring
    - only Nvidia GPUs
    - needs pynvml
    - PyPi extra target: GPU

### Fixed
- Internal MPI bug
- Sppeling mistake in cache error messages

## [0.6.0] - 2022-05-09
### Changed
- Code changed to fullfill changed CI
- using dynamic strings instead of varchar in cache DB
- removed unneeded IDs in DB, instead use composite keys

### Added
- It is now possible to use https connections with JuMonC for encrypted connections. See: [Readme Encryption](https://gitlab.jsc.fz-juelich.de/coec/jumonc#encryption)
- PyPi extras
- Cache access from REST-API
- CMD arguments to format REST-API cache output
- CMD argument to set path for DB
- DB version und version check

## [0.5.0] - 2022-04-29
### Added
- cache to retrieve old results based on a sql database

## [0.4.2] - 2022-04-19
### Changed
- Fixed error in user plugin

## [0.4.1] - 2022-04-19
### Changed
- Fixed error in disk plugin when missing (the optional dependency) psutil
