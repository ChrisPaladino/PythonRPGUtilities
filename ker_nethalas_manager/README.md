# Ker Nethalas Manager

Personal Python desktop companion prototype for Ker Nethalas.

## Quick start

1. Create/select a Python 3.12 environment.
2. Install package and dev tools:
   - `pip install -e .[dev]`
3. Run tests:
   - `pytest`
4. Start desktop shell:
   - `python -m ker_nethalas.interfaces.pyqt_main`

## Windows launchers

From the repository root, you can use:

- `run_app.bat` - Launch the desktop app.
- `run_tests.bat` - Run unit tests.
- `validate_content.bat` - Validate all JSON content tables.

## Current status

- Project scaffold and rules kernel started.
- Core check/opposed-check behavior implemented with unit tests.
- Initial combat helper functions implemented for baseline test cases.
