# gidgetlab-kit

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white)](https://github.com/pre-commit/pre-commit)
[![pipeline](https://gitlab.com/beenje/gidgetlab-kit/badges/main/pipeline.svg)](https://gitlab.com/beenje/gidgetlab-kit/-/commits/main)
[![coverage](https://gitlab.com/beenje/gidgetlab-kit/badges/main/coverage.svg)](https://gitlab.com/beenje/gidgetlab-kit/-/commits/main)

`gidgetlab-kit` is a Python package that provides several high level functions that can be used when
working with [gidgetlab](https://gidgetlab.readthedocs.io), as well as a `gidgetlab` cli tool to interact
with GitLab.

It inlcudes some useful commands:

```bash
$ gidgetlab --help
Usage: gidgetlab [OPTIONS] COMMAND [ARGS]...

Options:
  --version                       Show the current version and exit.
  --url TEXT                      GitLab URL  [env var: GL_URL; default:
                                  https://gitlab.com]

  --access-token TEXT             GitLab access token  [env var:
                                  GL_ACCESS_TOKEN; default: ]

  --verify / --no-verify          Verify SSL cerificate or disable
                                  verification  [default: True]

  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.

  --help                          Show this message and exit.

Commands:
  clone              Clone or pull all projects from group (including...
  commit-file        Add or update a file to a list of projects Example:
                     The...

  get                Get one or several items from the given endpoint
  list-projects      List all projects from group (including subgroups)
  trigger-pipelines  Trigger the pipeline for all or a subset of projects...
```

## Installation

Only Python 3.8 and above is tested. Create a virtualenv and run:

```bash
pip3 install gidgetlab-kit
```

To use the cli tool, [pipx](https://pipxproject.github.io/pipx/) is recommended.

## License

MIT
