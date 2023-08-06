# Opvia Scripts

[![CI](https://github.com/opvia/opvia-scripts/actions/workflows/ci.yml/badge.svg)](https://github.com/opvia/opvia-scripts/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/opvia/opvia-scripts/branch/main/graph/badge.svg?token=NSNITDCIUW)](https://codecov.io/gh/opvia/opvia-scripts)

This repo is used to build custom cards on the Opvia platform.

## Developing

Install [Poetry](https://python-poetry.org/) and `poetry install` the project

PRs made to this repo require approval from another developer. There should be reasonable tests for all functionality. Tests should protect backwards-compatibility of all of our changes.

New changes should be accompanied by appropriate updates to the [docs](docs/), covering:
- Relevant class and function definitions for custom card writers
- Simple examples covering installed script functionality
- Independently readable in-app scripting versions of the same examples

### Useful Commands

Note: if Poetry is managing a virtual environment for you, you may need to use `poetry run poe` instead of `poe`

- `poe autoformat` - Autoformat code
- `poe lint` - Linting
- `poe test` - Run Tests
- `poe docs` - Build docs

### Release

Release a new version by manually running the release action on GitHub with a 'major', 'minor', or 'patch' version bump selected.
This will create an push a new semver tag of the format `v1.2.3`.

Pushing this tag will trigger an action to release a new version of your library to PyPI.

Optionally create a release from this new tag to let users know what changed.
