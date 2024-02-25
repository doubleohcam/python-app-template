# [beta] python-app-template

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

A basic python app template for all my python projects.

To setup a new python app with all the good stuff, run `script/setup_new_app`.

This script will do the following:

- Create a new local directory for the new app
- Copy relevant files from this repo for a greenfield app
  - Note: does not copy the README.md or LICENSE, since github can easily set that up if needed
- [_Optional_] Run the intial python environment setup (eg. `script/bootstrap`)
- [_Optional_] Setup git (assuming the repo already exists in github.com)
- [_Optional_] Create an initial pull request with a commit of all the changes
