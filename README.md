# python-app-template

A basic python app template for all my python projects.

To setup a new python app with all the good stuff, run `script/setup_new_app`.

This script can do the following:

- Create a new local directory for the new app
- Copy relevant files from this repo for a greenfield app
  - Note: does not copy the README.md or LICENSE, since github can easily set that up if needed
- [Optional] Run the intial python environment setup (eg. `script/bootstrap`)
- [Optional] Setup git (assuming the repo already exists in github.com)
- [Optional] Create an initial pull request with a commit of all the changes

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
