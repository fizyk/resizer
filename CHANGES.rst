CHANGELOG
=========

.. towncrier release notes start

pyverter 0.1.1 (2026-08-23)
===========================

Miscellaneous
-------------

- Update license configuration in pyproject.toml to use SPDX expression and license-files.


pyverter 0.1.0 (2026-08-23)
===========================

Features
--------

- Add tests for resizer (`#2 <https://github.com/fizyk/pyverter/issues/2>`_)
- Implemented multiprocessing - now images will be converted faster. (`#4 <https://github.com/fizyk/pyverter/issues/4>`_)
- Build a package structure and define an entrypoint script. This will make the resizer properly installable. (`#9 <https://github.com/fizyk/pyverter/issues/9>`_)
- List images and error encountered while processing them (`#27 <https://github.com/fizyk/pyverter/issues/27>`_)
- Print size change in summary (`#28 <https://github.com/fizyk/pyverter/issues/28>`_)
- Migrate to python 3.12 (`#40 <https://github.com/fizyk/pyverter/issues/40>`_)


Miscellaneous
-------------

- Lint and typecheck code. (`#1 <https://github.com/fizyk/pyverter/issues/1>`_)
- Added dependabot configuration and automerge workflow (`#3 <https://github.com/fizyk/pyverter/issues/3>`_)
- Add towncrier and tbump configuration and dependency to (`#5 <https://github.com/fizyk/pyverter/issues/5>`_)
- Drop dpi related code as they do not really matter. (`#10 <https://github.com/fizyk/pyverter/issues/10>`_)
- Removed resizer editable installation from Pipfile. It breaks dependabot. (`#15 <https://github.com/fizyk/pyverter/issues/15>`_)
- Freeze Pillow and click requirements in Pipfile (`#19 <https://github.com/fizyk/pyverter/issues/19>`_)
- Adjust progressbar typing for mypy and new click. (`#38 <https://github.com/fizyk/pyverter/issues/38>`_)
- Update code formatting with black 24.1 (`#55 <https://github.com/fizyk/pyverter/issues/55>`_)
- Extend pre-commit with pyproject-fmt to format pyproject.toml (`#337 <https://github.com/fizyk/pyverter/issues/337>`_)
- Migrate development environment and CI to uv (`#338 <https://github.com/fizyk/pyverter/issues/338>`_)
- Add release-schedule workflow. (`#343 <https://github.com/fizyk/pyverter/issues/343>`_)
- Migrated the Automerge workflow to `fizyk/actions-reuse` version 5.4.1. (`#348 <https://github.com/fizyk/pyverter/issues/348>`_)
- Configure Dependabot to update pre-commit dependencies. (`#351 <https://github.com/fizyk/pyverter/issues/351>`_)
- `#352 <https://github.com/fizyk/pyverter/issues/352>`_
- Settle on pyverter as the package name
- Update workflows for actions-reuse 3
- Use pre-commit for maintaining code style and linting
