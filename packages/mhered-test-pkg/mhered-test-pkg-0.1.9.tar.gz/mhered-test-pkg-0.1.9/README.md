# mhered-test-pkg

A simple demo package to practice creating python packages. 

[![][pypi-image]][pypi-url] [![][license-image]][license-url] [![][versions-image]][versions-url] [![][stars-image]][stars-url] [![][build-image]][build-url] [![][coverage-image]][coverage-url]

Inspired in this article: https://mathspp.com/blog/how-to-create-a-python-package-in-2022

The code implements a simple Rock, Paper, Scissors text-based game, loosely inspired in the one wrote by Al Sweigart for his great book  [Automate the boring stuff with Python](https://automatetheboringstuff.com/).

Installation:

```bash
$ pip install mhered-test-pkg
```

Usage:

```bash
$ rps
```

Alternatively

```bash
$ python3 -m mhered_test_pkg
```

## Creating a python package: Howto 

### Pick a name

Check the name is available in [PyPI](https://pypi.org/)

### Initialize `poetry`

Install `poetry` (I started from [here](https://python-poetry.org/docs/#osx--linux--bashonwindows-install-instructions) then modified the instructions):

 ```bash
$ curl -sSL https://install.python-poetry.org/ | python3 -
 ```

Create a local dedicated folder and initialize `poetry` inside

```bash
$ cd ~
$ mkdir mhered-test-pkg
$ cd mhered-test-pkg

$ poetry new .
Created package mhered_test_pkg in .

$ tree
.
├── mhered_test_pkg
│   └── __init__.py
├── pyproject.toml
├── README.rst
└── tests
    ├── __init__.py
    └── test_mhered_test_pkg.py
    
$ mv README.rst README.md
$ poetry install
```

Note: I renamed `README.rst` to `README.md` because I prefer to work in **Markdown**.

Note: Running `poetry install` creates a file `poetry.lock` with the dependencies

### Initialize git in the local folder

Create an empty github repo: **[mhered-test-pkg](https://github.com/mhered/mhered-test-pkg)** and follow the instructions to set it as the remote and push a first commit with the file structure:

```bash
$ git init
$ git add *
$ git commit -m "First commit"
$ git branch -M main
$ git remote add origin https://github.com/mhered/mhered-test-pkg.git
$ git push -u origin main
```

### Set up `pre-commit` hooks

  Add `pre-commit` as a development dependency, then commit updates:

```bash
$ poetry add -D pre-commit

$ git add poetry.lock pyproject.toml
$ git commit -m "Add pre-commit devt dependency."
```

Create a file `.pre-commit-config.yaml` in the root:

```yaml
# See https://pre-commit.com for more information
# See https://pre-commit.com/hooks.html for more hooks
repos:
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.0.1
    hooks:
      - id: check-toml
      - id: check-yaml
      - id: end-of-file-fixer
      - id: mixed-line-ending
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
  - repo: https://github.com/PyCQA/isort
    rev: 5.10.1
    hooks:
      - id: isort
        args: ["--profile", "black"]
```

Activate the `poetry` virtual environment to be able to use `pre-commit` then install the hooks and run them once: 

```bash
$ poetry shell

$ pre-commit install
$ pre-commit run all-files
```

Note: `pre-commit` is not found unless run from inside the shell - or you can use `poetry run pre-commit`

Commit the changes (including the updates to `README.md`):  

```bash
$ git add *
$ git commit -m "Run all pre-commits."
$ git push
```

Note: If some test fails, you need to add again the modified files and repeat the git commit - which is fine. But there is a strange behavior if the file was open: it seems to revert to an older version?

### Add a license

[Add a license from the github repo](https://docs.github.com/en/communities/setting-up-your-project-for-healthy-contributions/adding-a-license-to-a-repository) then pull changes to local. 

This will add [LICENSE.md](./LICENSE.md)

### Upload the stub package to TestPyPI

Declare the test repository https://test.pypi.org in `poetry` and name it  `testpypi`:

```bash
$ poetry config repositories.testpypi https://test.pypi.org/legacy/
```

[Create an account on TestPyPI](https://test.pypi.org/account/register/), go to Account Settings to get an API token and then configure `poetry` to use it:

```bash
$ poetry config http-basic.testpypi __token__ pypi-YOUR-TESTPYPI-API-TOKEN
```

Note: Be careful not to expose your API token, e.g. I wrote it to a `secrets.md` file then used `.gitignore` so as not to commit and publish it publicly.

Build and upload the package:

```bash
$ poetry build
$ poetry publish -r testpypi
```

With this our package is live in TestPyPI: https://test.pypi.org/project/mhered-test-pkg/

<img src="assets/mhered-test-pkg.png" alt="mhered-test-pkg" style="zoom: 50%;" />

Note: Build creates the `dist/` folder that should be added to `.gitignore`

```bash
$ echo dist/ >> .gitignore

$ git add .
$ git commit -m "Publish to TestPyPI"
$ git push
```

### Populate the package with code

For this example I wrote a simple Rock, Paper, Scissors game inspired and slightly refactored from the example proposed by Al Sweigart in his great book [Automate the boring stuff with Python](https://automatetheboringstuff.com/). The code goes in `mhered-test-pkg/__init__.py`.

### Changelog management

Add [scriv](https://pypi.org/project/scriv/) for changelog management, as a development dependency with the `[toml]` extra :

```
$ poetry add -D scriv[toml]
```

Configure `scriv` to use **Markdown** and add version numbering in the title by adding the following lines to the `pyproject.toml` file, refer to [scriv's readthedocs](https://scriv.readthedocs.io/en/latest/configuration.html):

```toml
[tool.scriv]
format = "md"
version = "literal: pyproject.toml: tool.poetry.version"
```

Then create the default directory for changelog fragments `changelog.d/`. Note: add an empty `.gitkeep`  file so that git tracks the empty folder.

```bash
$ mkdir changelog.d
$ touch changelog.d/.gitkeep

$ git add pyproject.toml poetry.lock changelog.d/.gitkeep
$ git commit -m "Add scriv as devt dependency."
```

Create a new `.md` fragment file in the `changelog.d` folder: 

```bash
$ scriv create
```

Edit it to add a description of the changes:

```markdown
### Added

- A first simple implementation of Rock Paper Scissors
```

Update `README.md` and commit everything:

```bash
$ git add README.md changelog.d/* __init__.py
$ git commit -m "Simple Rock Paper Scissors game"
```

### Publish the package to PyPI

Create a [PyPI](https://pypi.org/) account and API token, and configure `poetry` to use it:

```bash
$ poetry config pypi-token.pipy pypi-YOUR-PYPI-API-TOKEN
```

Build and publish:

```bash
$ poetry publish --build
```

### Do a victory lap

Install, import and uninstall the package (outside of the shell) to check it works. Note: the hyphens (`-`) in the package name turn into underscores (`_`) in the module name.

```bash
$ pip install mhered-test-pkg
Defaulting to user installation because normal site-packages is not writeable
Collecting mhered-test-pkg
  Using cached mhered_test_pkg-0.1.0-py3-none-any.whl (2.5 kB)
Installing collected packages: mhered-test-pkg
Successfully installed mhered-test-pkg-0.1.0

$ python3 -m mhered_test_pkg
ROCK, PAPER, SCISSORS
0 Wins, 0 Losses, 0 Ties
Enter your move: (r)ock (p)aper (s)cissors or (q)uit
r
ROCK versus... SCISSORS
You win!
1 Wins, 0 Losses, 0 Ties
Enter your move: (r)ock (p)aper (s)cissors or (q)uit
q
Bye!

$ pip uninstall mhered-test-pkg
ROCK, PAPER, SCISSORS
0 Wins, 0 Losses, 0 Ties
Enter your move: (r)ock (p)aper (s)cissors or (q)uit
r
ROCK versus... SCISSORS
You win!
1 Wins, 0 Losses, 0 Ties
Enter your move: (r)ock (p)aper (s)cissors or (q)uit
q
Bye!
```

###  Publish a release

Add a description, installation and usage instructions in the `README.md` and declare it in `pyproject.toml`:

```toml
readme = "README.md"
```

Make `scriv` collect the previously created changelog fragment to a new `CHANGELOG.md` file with:

```bash
$ scriv collect
```

Lets commit: 

```bash
$ git add changelog.d/20220731_143829_manolo.heredia.md CHANGELOG.md README.md pyproject.toml
$ git commit -m "Prepare release 0.1.0"
```

Tag the commit, and push it to the remote (seen [here](https://stackabuse.com/git-push-tags-to-a-remote-repo/)):

```bash
$ git tag -a v0.1.0 -m "Initial version"
$ git push origin v0.1.0
```

I discovered I hadn't configured version numbering for scriv, so I did it now, and added a new release to test it.

First modify `pyproject.toml` to increment the version to `0.1.1` and have `scriv` read the version from `tool.poetry.version`:

```toml
[tool.poetry]
name = "mhered-test-pkg"
version = "0.1.1"
description = "A simple demo package to practice how to create python packages."
authors = ["Manuel Heredia <manolo.heredia@gmail.com>"]
readme = "README.md"

[tool.poetry.dependencies]
python = "^3.8"

[tool.poetry.dev-dependencies]
pytest = "^5.2"
pre-commit = "^2.20.0"
scriv = {extras = ["toml"], version = "^0.16.0"}

[build-system]
requires = ["poetry-core>=1.0.0"]
build-backend = "poetry.core.masonry.api"

[tool.scriv]
format = "md"
version = "literal: pyproject.toml: tool.poetry.version"
```

Next add a changelog fragment:

```bash
$ scriv create
```

and edit it to describe the change

```markdown
### Fixed

- Configure `scriv` to get version number from `pyproject.toml`
```

Bump version in `mhered-test-pkg/__init__.py` `__version__ = "0.1.1"`

Add a unit test to check it is always in sync with `tool.poetry.version` in `pyproject.toml` ([there seems to be no better way](https://github.com/python-poetry/poetry/issues/144#issuecomment-877835259))

```python
import toml
from pathlib import Path
import mhered_test_pkg

def test_versions_are_in_sync():
    """ Checks if tool.poetry.version in pyproject.toml and
    	__version__ in mhered_test_pkg.__init__.py are in sync."""

    path = Path(__file__).resolve().parents[2] / "pyproject.toml"
    pyproject = toml.loads(open(str(path)).read())
    pyproject_version = pyproject["tool"]["poetry"]["version"]

    init_py_version = mhered_test_pkg.__version__
    
    assert init_py_version == pyproject_version
```

Add a new changelog fragment:

```bash
$ scriv create
```

and edit it to describe the change

```markdown
## Added

- Test to check that versions defined in `pyproject.py` and `__init__.py` are in sync
```



Update the Changelog:

```bash
$ scriv collect
```

Commit and push, tag and push:

```bash
$ git add pyproject.toml mhered_test_pkg/__init__.py tests/test_mhered_test_pkg.py CHANGELOG.md README.md

$ git commit -m "Configure versions in scriv"
$ git push

$ git tag -a v0.1.1 -m "Configure versions in scriv"
$ git push origin v0.1.1

$ scriv github-release -v  DEBUG
debug: Running command 'git tag'
debug: Command exited with 0 status. Output: 'v0.1.0\nv0.1.1\n'
debug: Running command ['git', 'config', '--get-regex', 'remote[.].*[.]url']
debug: Command exited with 0 status. Output: 'remote.origin.url https://github.com/mhered/mhered-test-pkg.git\n'
debug: Starting new HTTPS connection (1): api.github.com:443
debug: https://api.github.com:443 "GET /repos/mhered/mhered-test-pkg/releases HTTP/1.1" 200 600
warning: Version 0.1.1 has no tag. No release will be made.
warning: Version 0.1.0 has no tag. No release will be made.

```

It still does not work... to be continued.

### Troubleshooting

There is something off with the tag `v0.1.0`. Wat linked to `8ad878f` which does not show here!

```bash
$ git log --oneline
5979855 (HEAD -> main, origin/main) Update README.md
fa7a843 (tag: v0.1.1) Configure versions in scriv
74b8fcb Prepare release 0.1.0
9519229 Add victory lap to README.md
c22f560 Move __init__.py to mhered_test_pkg/
066172e Minor updates to README.md
e438080 Simple Rock Paper Scissors game
2c93077 Add scriv as devt dependency
262bb9e Publish to TestPyPI
dd9cfd9 Add .gitignore to protect API tokens
81fa08d Minor change of README.md
4d8b935 Update License in README.md
e18df98 Create LICENSE.md
9400227 Update README.md
3d3a9d8 Run all pre-commits.
8de2b5a Add pre-commit devt dependency
9743aef First commit
```

lets repair the tag `v0.1.0`:

```bash
$ git tag -d v0.1.0						# delete the old tag locally
Deleted tag 'v0.1.0' (was 8ad878f)
$ git push origin :refs/tags/v0.1.0		# delete the old tag remotely
To https://github.com/mhered/mhered-test-pkg.git
 - [deleted]         v0.1.0
$ git tag -a v0.1.0 74b8fcb				# make a new tag locally
$ git push origin v0.1.0				# push the new local tag to the remote
```

Voilá:

```bash
$ git log --oneline
5979855 (HEAD -> main, origin/main) Update README.md
fa7a843 (tag: v0.1.1) Configure versions in scriv
74b8fcb (tag: v0.1.0) Prepare release 0.1.0
9519229 Add victory lap to README.md
c22f560 Move __init__.py to mhered_test_pkg/
066172e Minor updates to README.md
e438080 Simple Rock Paper Scissors game
2c93077 Add scriv as devt dependency
262bb9e Publish to TestPyPI
dd9cfd9 Add .gitignore to protect API tokens
81fa08d Minor change of README.md
4d8b935 Update License in README.md
e18df98 Create LICENSE.md
9400227 Update README.md
3d3a9d8 Run all pre-commits.
8de2b5a Add pre-commit devt dependency
9743aef First commit
```

### Write tests

I added a couple of tests, refactored a bit the code and committed the changes.

Then, to create a release: 

- bump the  version
- edit `__init__.py` manually to sync version number
- run the tests
- create a fragment - with `--edit` option to launch the editor directly
- collect all fragments to `CHANGELOG.md`
- commit changes to `pyproject.toml README.md CHANGELOG.md mhered_test_pkg/__init__.py`
- create tag
- push commit and tag

```bash
$ git commit -a -m "Add tests"
$ poetry version patch
$ atom mhered_test_pkg/__init__.py
$ pytest
============================= test session starts =============================
platform linux -- Python 3.8.10, pytest-5.4.3, py-1.11.0, pluggy-0.13.1
rootdir: /home/mhered/mhered-test-pkg
collected 4 items                         
tests/test_mhered_test_pkg.py ....                                       [100%]
============================== 4 passed in 0.02s ==============================
$ scriv create --edit
$ scriv collect

$ git commit -m "Prepare release 0.1.2"
$ git push

$ git tag -a 0.1.2 -m "Add tests"
$ git push origin 0.1.2
```

* try to create a release with `scriv github-release`

This time `$ scriv github-release -v  DEBUG` gives an error message so I rename tag `0.1.2` to `v0.1.2`:

```bash
$ git tag v0.1.2 0.1.2^{}
$ git tag -d 0.1.2
$ git push origin :refs/tags/0.1.2
$ git log  --oneline
aa3e44a (HEAD -> main, tag: v0.1.2, origin/main) Prepare release 0.1.2
b03efa8 Add tests
d688927 Passes basic tests
5979855 Update README.md
fa7a843 (tag: v0.1.1) Configure versions in scriv
74b8fcb (tag: v0.1.0) Prepare release 0.1.0
9519229 Add victory lap to README.md
...
```

Back to normal:

```bash
$ scriv github-release -v DEBUG
debug: Running command 'git tag'
debug: Command exited with 0 status. Output: 'v0.1.0\nv0.1.1\nv0.1.2\n'
debug: Running command ['git', 'config', '--get-regex', 'remote[.].*[.]url']
debug: Command exited with 0 status. Output: 'remote.origin.url https://github.com/mhered/mhered-test-pkg.git\n'
debug: Starting new HTTPS connection (1): api.github.com:443
debug: https://api.github.com:443 "GET /repos/mhered/mhered-test-pkg/releases HTTP/1.1" 200 717
warning: Version 0.1.2 has no tag. No release will be made.
warning: Version 0.1.1 has no tag. No release will be made.
warning: Version 0.1.0 has no tag. No release will be made.
```

Apparently this is because I need to add my PAT as environment variable `GITHUB_TOKEN`, see [scriv docs](https://scriv.readthedocs.io/en/latest/commands.html#scriv-github-release). I tried though, and it does not work... I create the release manually in github.

### Automating with `tox`

`tox` automates testing, linting, formatting, test coverage, documentation, etc.

We add tox as a development dependency:

```bash
$ poetry add -D tox
```

Configuration is done in a `tox.ini` file in `toml` format, which can be initiated in its simplest form running  `$ tox-quickstart` and answering a few questions.

```toml
# tox (https://tox.readthedocs.io/) is a tool for running tests
# in multiple virtualenvs. This configuration file will run the
# test suite on all supported python versions. To use it, "pip install tox"
# and then run "tox" from this directory.

[tox]
envlist = py37

[testenv]
deps =
    pytest
commands =
    pytest
```

However this simplest version did not work. I had to do a few iteratons:

* Added `isolated_build = True` to work with `poetry`
* Added `toml` to dependencies otherwise `pytest`  cannot import it. It seems that `tox` creates its own virtual environments and you need to add all dependencies again...
* Added formatting with `black`, linting with `flake8`, `pylint`, `mccabe`, sorting of imports with [isort](https://pycqa.github.io/isort/), and testing with `pytest`. [mccabe](https://pypi.org/project/mccabe/) is a `flake8` plugin to check the code's McCabe complexity (should be <10). 
* `black --check` does not modify the files, only exits with an error if the check is not passed. What is the point?

Result:

```toml
# tox (https://tox.readthedocs.io/) is a tool for running tests
# in multiple virtualenvs. This configuration file will run the
# test suite on all supported python versions. To use it, "pip install tox"
# and then run "tox" from this directory.

[tox]
isolated_build = True
envlist = py38

[testenv]
deps =
    toml
    black
    flake8
    isort
    mccabe
    pylint
    pytest

commands =
    black --check mhered_test_pkg
    isort  --check mhered_test_pkg
    flake8 mhered_test_pkg --max-complexity 10
    pylint mhered_test_pkg
    pytest .
```

 Execute with: 

```bash
$ tox
```

Question: why use `tox` when I can use a `poetry` script or even better a `pre-commit` hook? 

### Check coverage

Installation and basic execution of [coverage](https://coverage.readthedocs.io/en/6.4.2/index.html):

```bash
$ poetry add -D coverage
$ coverage run -m pytest
$ coverage report
Name                            Stmts   Miss  Cover
---------------------------------------------------
mhered_test_pkg/__init__.py        49     38    22%
tests/__init__.py                   0      0   100%
tests/test_mhered_test_pkg.py      15      0   100%
---------------------------------------------------
TOTAL                              64     38    41%

```

We can execute the checks in a more nuanced way including all files in the package and all branching paths, and we can also generate nicer HTML reports [such as this one](./assets/sample_html_coverage_report/index.html) as follows:

```bash
$ coverage run --source=mhered_test_pkg --branch -m pytest .
$ coverage html
```

![22pc_coverage](assets/22pc_coverage.png)

To add `coverage` to `tox` modify `tox.ini` to add the relevant lines:

```toml
# tox (https://tox.readthedocs.io/) is a tool for running tests
# in multiple virtualenvs. This configuration file will run the
# test suite on all supported python versions. To use it, "pip install tox"
# and then run "tox" from this directory.

[tox]
isolated_build = True
envlist = py38

[testenv]
deps =
    toml
    black
    flake8
    isort
    mccabe
    pylint
    pytest
    coverage # development dependency

commands =
    black --check mhered_test_pkg
    isort  --check mhered_test_pkg
    flake8 mhered_test_pkg --max-complexity 10
    pylint mhered_test_pkg
    coverage run --source=mhered_test_pkg --branch -m pytest . # execute
    coverage report -m --fail-under 90 # report & fail below 90%

```

Added tests to increase coverage up to 97% - i.e. all lines of code covered except the case `"__name__" == "__main__:"` because tests import as module.

![97pc_coverage](assets/97pc_coverage.png)

In the process I learned about monkeypatching user input, using iterators to simulate a sequence of inputs, or testing for sys exit, see references in [./tests/test_mhered_test_pkg.py](./tests/test_mhered_test_pkg.py)

Usual ritual to create a release. As some of the steps modify files that need to be committed this process ends up being iterative. I try to keep it clean using profusely `$ git commit --amend`along the way:

```bash
$ scriv create --edit # describe changes in a fragment
$ poetry version patch # bump version
$ atom mhered_test_pkg/__init__.py # sync _version__
$ scriv collect # update CHANGELOG.md
$ git add . 
$ git commit
$ git tag -a v0.1.3 -m "97% test coverage"
$ git push
$ git log --oneline
91c4aa1 (HEAD -> main, tag: v0.1.3, origin/main) 0.1.3 automated with tox and 97% coverage
d6670c4 Automating with tox
028028a Update README.md
aa3e44a (tag: v0.1.2) Prepare release 0.1.2
b03efa8 Add tests
d688927 Passes basic tests
5979855 Update README.md
fa7a843 (tag: v0.1.1) Configure versions in scriv
74b8fcb (tag: v0.1.0) Prepare release 0.1.0
...
$ git push origin v0.1.3
```

### CI/CD with GitHub Actions

[GitHub Actions](https://docs.github.com/en/actions) allow automating workflows of actions that are triggered by certain events e.g. a commit pushed to the repo, a pull request or a release. They are defined in YAML files that live in the directory `.github/workflows`. 

The CI runner spawns the full environment in a Github server, including setting up the OS with`runs-on:`, installing and activating python with `uses: actions/setup-python@v2` ... `with:`  ... `python-version:`...`"3.8"`, installing dependencies (via `tox` or `poetry` commands) and downloading our repository with `uses: actions/checkout@v2`

A nice intro tutorial in Youtube:  https://www.youtube.com/watch?v=R8_veQiYBjI

```yaml
# .github/workflows/CI.yaml
name: mhered-test-pkg CI

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.8", "3.9", "3.10"]

    steps:
      - name: Checkout sources
        uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install tox tox-gh-actions

      - name: Run tox
        run: tox
      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v2
        with:
            fail_ci_if_error: true

```

Everything seems to be working including Codecov integration except PR comments.

## Automatic publishing of releases to PyPI

I wrote a new `PyPI_publish.yaml` file with the following steps: 

1. Checkout the repo
2. Set up Python 3.8
3. Install Poetry and dependencies
4. Configure Poetry with a PyPI token
5. Build and publish the package

A more straighforward solution using a pre-made GH action from PyPA to upload both to Test PyPI and PyPI is here: https://packaging.python.org/en/latest/guides/publishing-package-distribution-releases-using-github-actions-ci-cd-workflows/

Note: add the Test PyPI and PyPI credentials created earlier as repository secrets in Github as `PYPI_TOKEN` and `TEST_PYPI_TOKEN`: **Settings** --> **Secrets** --> **Actions** --> **Add new repository secret**.

```yaml
# .github/workflows/PyPI_publish.yaml
name: publish mhered-test-pkg to PyPI

on:
  release:
    types: [published]
    branches: [ main ]
  workflow_dispatch:

jobs:
  build-and-publish:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout sources
        uses: actions/checkout@v2

      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.8"

      - name: Install poetry and dependencies
        run: |
          python -m pip install --upgrade pip
          python -m pip install poetry

      - name: Configure poetry
        env:
          pypi_token: ${{ secrets.PYPI_TOKEN }}
        run: poetry config pypi-token.pypi $pypi_token

      - name: Build and publish
        run: poetry publish --build
```

New release:

```bash
$ poetry version patch
$ atom mhered_test_pkg/__init__.py
$ pytest
$ scriv create --edit
$ scriv collect
$ git add .
$ git commit -m "Add CI/CD and Codecov - release 0.1.4"
$ git push

$ git tag -a v0.1.4 -m "Add GH actions for CI/CD and Codecov integration"
$ git push origin v0.1.4
```

Did not work initially. I found three typos  in `PyPI_publish.yaml`, should be: 

- `secrets.PYPI_TOKEN` instead of `secrets.PyPI_TOKEN`
- `run: poetry config pypi-token.pypi $pypi_token` instead of `pypi_token.pypi`
-  `run: poetry publish --build` instead of `uses:` 

I also added minor updates to `README.md` and I created a few releases in the process.

```bash
$ poetry version patch
$ atom mhered_test_pkg/__init__.py
$ pytest
$ scriv create --edit
$ scriv collect
$ git add .
$ git commit -m "Commit Message - release 0.1.X"
$ git push

$ git tag -a v0.1.X -m "Release Message"
$ git push origin v0.1.X
```

Finally succeeded with `v0.1.7`

### Add badges to README.md

Piece of cake following the instructions in https://shields.io/

### Move code to `/src`

Ad adapt everywhere:

* in tests change the import statement:

```python
from src.mhered_test_pkg import ...
```

* in `tox.ini` replace `mhered_test_pkg` by `src` 

```toml
...
commands =
    black --check src
    isort  --check src
    flake8 src --max-complexity 10
    pylint src
    coverage run --source=src --branch -m pytest .
    coverage report -m --fail-under 60
    coverage xml
...
```

### Add entry points

In development, as an alternative to calling:

```bash
$ python3 ./src/mhered_test_pkg/__init__.py
```

1. We can create a `__main__.py` file:

```python
""" __main__ entry point """
from mhered_test_pkg import rock_paper_scissors

if __name__ == "__main__":
    rock_paper_scissors()
```

to allow calling the package as a module:

```bash
$ python3 -m src.mhered_test_pkg
```

And/or 

2. edit `pyproject.py` to add the following line:

```toml
[tool.poetry.scripts]
rps = "mhered_test_pkg.__init__:rock_paper_scissors
```

to create a shortcut to execute the game writing:

```bash
$ rps
```

Note that when the app is distributed the methods that work are different! - cfr. the ones described at the beginning of the `README.md`

Time to make a new release 0.1.8...

<!-- Badges: -->

[pypi-image]: https://img.shields.io/pypi/v/mhered-test-pkg
[pypi-url]: https://pypi.org/project/mhered-test-pkg/
[build-image]: https://github.com/mhered/mhered-test-pkg/actions/workflows/CI.yaml/badge.svg
[build-url]: https://github.com/mhered/mhered-test-pkg/actions/workflows/CI.yaml
[coverage-image]: https://codecov.io/gh/mhered/mhered-test-pkg/branch/main/graph/badge.svg
[coverage-url]: https://codecov.io/gh/mhered/mhered-test-pkg/
[stars-image]: https://img.shields.io/github/stars/mhered/mhered-test-pkg
[stars-url]: https://github.com/mhered/mhered-test-pkg
[versions-image]: https://img.shields.io/pypi/pyversions/mhered-test-pkg
[versions-url]: https://pypi.org/project/mhered-test-pkg/
[license-image]: https://img.shields.io/github/license/mhered/mhered-test-pkg
[license-url]: https://github.com/mhered/mhered-test-pkg/blob/main/LICENSE.md
