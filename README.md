# Cumination Repository

<img src="https://user-images.githubusercontent.com/46063764/103461711-a9eb6280-4d20-11eb-983b-516b022cbbf5.png" width="300" align="right">

Kodi repository for the Cumination addon and supporting modules.

## Quick links

- Setup guide: [`docs/guides/SETUP.md`](docs/guides/SETUP.md)
- Testing guide: [`docs/testing/TESTING_GUIDE.md`](docs/testing/TESTING_GUIDE.md)
- Test runner docs: [`docs/testing/test_runner.md`](docs/testing/test_runner.md)
- Logo tooling docs: [`docs/logos/LOGO_SCRIPTS_README.md`](docs/logos/LOGO_SCRIPTS_README.md)
- Fork/PR workflow: [`docs/guides/fork_pr_workflow.md`](docs/guides/fork_pr_workflow.md)

## Repository layout

- `plugin.video.cumination/` – main addon code.
- `repository.dobbelina/` – Kodi repository metadata and packaging files.
- `script.module.resolveurl/`, `script.module.resolveurl.xxx/`, `script.video.F4mProxy/` – bundled dependencies/modules.
- `tests/` – pytest suite and fixtures.
- `scripts/` – maintenance, debugging, smoke-test, and logo-processing scripts.
- `docs/` – project documentation, grouped by topic (`guides/`, `testing/`, `logos/`, `development/`, etc.).

## Development setup

Follow [`docs/guides/SETUP.md`](docs/guides/SETUP.md) for Linux/Windows setup.

## Common commands

From repository root:

```bash
# Run all tests
python run_tests.py

# Run tests with coverage
python run_tests.py --coverage

# Run logo validation
python scripts/validate_logos.py

# Run logo processing workflow
python scripts/process_logos.py
```

## Notes

- Historical test/checklist documents are stored in `docs/testing/`.
- Most operational scripts have been consolidated under `scripts/` to keep the repository root focused on core project files.

## Credits

All credit to the fantastic people at reddit who have provided fixes, especially jdoedev, 12asdfg12, and camilt, plus Whitecream and holisticdioxide as the original addon authors.

## Badges

![GitHub closed issues](https://img.shields.io/github/issues-closed/dobbelina/repository.dobbelina)
![GitHub last commit (by committer)](https://img.shields.io/github/last-commit/dobbelina/repository.dobbelina)
[![Latest Version](https://img.shields.io/badge/dynamic/xml?color=blue&label=latest%20addon%20version&query=%2Faddon%2F@version&url=https%3A%2F%2Fraw.githubusercontent.com%2Fdobbelina%2Frepository.dobbelina%2Fmaster%2Fplugin.video.cumination%2Faddon.xml)](https://github.com/dobbelina/repository.dobbelina)

<div align="center">

[![Visitors](https://api.visitorbadge.io/api/daily?path=https%3A%2F%2Fgithub.com%2Fdobbelina%2Frepository.dobbelina&label=Visitors%20Today&countColor=%23eca90b&style=flat)](https://visitorbadge.io/status?path=https%3A%2F%2Fgithub.com%2Fdobbelina%2Frepository.dobbelina)

</div>
