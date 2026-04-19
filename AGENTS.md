# Agent Instructions for udala.tablon

This document provides guidelines and common commands for AI agents operating in the `udala.tablon` repository.

## 1. Project Context

- **Platform:** Plone 6 (Backend)
- **Language:** Python 3.10+
- **Type:** Plone Add-on Package (`udala.tablon`)
- **Package Manager:** `uv`
- **Generators:** This project uses `plonecli` and `bobtemplates.plone`. Use `make add` for generating new components.

## 2. Code Style & Standards

### Formatting and Linting
- **Python Formatting:** Managed by `ruff` (replaces Black, Flake8, and isort). Configuration is in `pyproject.toml`.
- **ZCML/XML Formatting:** Managed by `zpretty`.
- **Pre-commit Hooks:** Code must pass `pre-commit` checks.

### Imports
- **Order:** Organized automatically by `ruff`. Absolute imports are preferred.
- **Plone APIs:** Always prefer `plone.api` for content manipulation, portal tools, and user management instead of using deep internal Zope/Plone module imports.
- **Zope Component Architecture:** Use `zope.interface` and `zope.component` correctly for adapters, subscribers, and utilities.

### Types and Signatures
- **Typing:** Use Python type hints where feasible, though Plone component code might heavily rely on `zope.interface`.
- **Naming Conventions:**
  - Classes/Interfaces: `PascalCase` (e.g., `IMyBehavior`)
  - Functions/Methods/Variables: `snake_case`
  - Constants: `UPPER_SNAKE_CASE`

### Error Handling
- Use standard exceptions and avoid catching broad `Exception` unless logging it properly.
- For Plone specific errors, use appropriate standard exceptions like `Unauthorized`, `NotFound`, etc.

## 3. Common Commands

The project uses a `Makefile` heavily relying on `uv` for environment management.

### Setup
Ensure the virtual environment is built and dependencies are synced:
```bash
make sync
make install
```

### Build & Run
To run the instance locally (starts Zope/Plone):
```bash
make start
```
To run a debug console:
```bash
make console
```

### Linting & Formatting
Run all quality checks before proposing changes:
```bash
make format  # Automatically formats Python and XML/ZCML code
make lint    # Runs Ruff, Pyroma, and zpretty checks
make check   # Runs both format and lint
```
Alternatively, using `tox`:
```bash
tox -e format
tox -e lint
```

### Testing
To run the full test suite via `pytest`:
```bash
make test
```
To run tests with coverage:
```bash
make test-coverage
```

**Running a Single Test:**
You can run a single test or test file directly using the installed `pytest` binary in the virtual environment. 
```bash
.venv/bin/pytest tests/test_setup.py
.venv/bin/pytest tests/test_setup.py::test_browserlayer
```
*(Note: `tox -e test -- -t test_browserlayer` can also be used if using `zope-testrunner` via `tox`, but direct `pytest` is faster during development)*

### Generating Code
Instead of writing boilerplate (like Content Types, REST API services, Behaviors) by hand, use the make target wrapping `plonecli`:
```bash
# E.g., to add a REST API service:
make add restapi_service
```

## 4. Agent Guidelines

### General Guidelines
- **Always Run Linters:** Before declaring a task finished, run `make check` and fix any issues.
- **Verify Tests:** Ensure `make test` runs cleanly after your modifications.
- **Plone 6 Best Practices:** Do not write Plone Classic UI browser views if this is meant to be consumed by a Volto frontend; write `plone.restapi` endpoints instead.
- **Follow Existing Patterns:** Look at existing code in `src/udala/tablon` to match the established patterns and architecture for the add-on.

### Using Generators
- **Always Use Generators:** Do not create content types, behaviors, or services from scratch. Use the `plonecli` generator wrapper: `make add <template_name>`.
- **mrbob.ini:** Always use a temporary `mrbob.ini` file containing the generator configuration variables to avoid interactive prompts. Delete `mrbob.ini` after the `make add` command completes successfully.
- **Clean Git State:** Before running `make add`, ensure the git working directory is clean. If there are changes, commit them first.

### Backend Development Best Practices (Python & ZCML)
- **plone.api is the standard:** You MUST use `plone.api` for all standard operations. 
  - *Examples:* `api.content.create()`, `api.content.get()`, `api.portal.get_tool()`, `api.user.get_current()`.
  - Avoid using deep internal Zope/Plone module access directly unless absolutely necessary for advanced customizations.
- **REST API:** Extend functionality via `plone.restapi` services. Create a service class and register it via `configure.zcml` in the `services/` directory.
- **ZODB Access:** Interact with the ZODB via `plone.api` or standard accessors. Avoid raw ZODB manipulation.
- **ZCML:** Keep ZCML clean. Use `<include package=".subpackage" />` to organize configurations if the project structure gets large.

### Content Types and Schema
- **Behaviors First:** When a user requests to add fields to a content type, always check the Plone Behavior Catalog first (e.g. `plone.app.dexterity.behaviors.metadata.IDublinCore`). If a behavior provides the field, activate it in the content type's XML configuration instead of adding a custom field.
- **Content Types:** Define schemas using Python interfaces (`dexterity_type_supermodel = n`) by default, rather than XML supermodels, unless XML schemas are explicitly requested.
- **Container vs Item:** By default, new content types should be Containers (`dexterity_type_base_class = Container`) unless they are clearly leaf objects with no children (Items).

### Git Conventions
- **Commit Messages:** Follow standard conventional commits. Keep messages concise and explain the "why" rather than the "what".
- **Safety:** Do not push to the remote branch automatically unless explicitly asked. Do not run destructive git commands (like `push --force`).

