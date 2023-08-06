
see [`BACKLOG`](./BACKLOG.md)
for open development tasks and limitations.


# CHANGELOG


## version v0.0.3 - 20220806

- `-venv` cmd-line parameter in addition to `-cwd` parameter
  - `-venv` specifies the venv folder, and 
  `-cwd` is working directory folder
- pip update after ensurepip added
- BUG fix: bash return code handling
- `tools` uninstall option
- `req` sub-cmd for handling requirements.txt installation
- `pypi` sub-cmd for printing helping information (just for copy&paste as of now)
- `build` clean only for wiping build related folders without starting the building process
- fix in cdvenv
- added run freeze scripts
- 


## version v0.0.2 - 20220801

- `drop` sub-cmd for removing a venv
- more verbose info
- `binst` sub-cmd for build and installing
- `clean` sub-cmd for wiping build related folders
- `qtest` sub-cmd for running black, flake8, and unit-tests
- better trace / debug log messages
- 


## version v0.0.1 - 20220731

- first release
- 
