
# Robot Evolution Thesis

To effectively clone this repo you likely need to run:
 
* `git clone --recurse-submodules`

This will download all the submodules as well; such as [`revolve2`](https://github.com/Jacopo-DM/revolve2) and [`Basics`](https://github.com/Jacopo-DM/Basics#basics).


## Directory Structure

```
.
├── LICENSE
├── README.md               # This document
├── basics                  # Helper functions (submodule)
├── charts                  # DrawIO diagrams
├── lamarck                 # (ToDo)
├── morphologies            # (ToDo)
├── revolve                 # Robot evolution toolkit (submodule)
└── thesis                  # LaTeX files
```

## Basics 

Git submodule from: [Jacopo-DM/Basics](https://github.com/Jacopo-DM/Basics)

This directory contains various basic helper scripts and templates the author uses in his projects.

## Revolve

Git submodule from: [Jacopo-DM/revolve2](https://github.com/Jacopo-DM/revolve2), which is a fork of [revolve2](https://github.com/ci-group/revolve2).

This is used to install `Revolve 2` in editable mode.

### Python Environment Setup

Instructions on how the author set up his (mini)conda environment can be found in [`basics/shell/env.sh`](https://github.com/Jacopo-DM/Basics/blob/main/shell/env.sh). 

Note this was done on a M1 Mac. 

### Mac Pre-requisites

* Install [`Xcode`](https://developer.apple.com/xcode/) from the App Store or `Xcode Command Line Tools` by running `xcode-select --install` in a terminal 

* Install [`Homebrew`](https://brew.sh/) by running `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` in a terminal

Using `Homebrew` install `cereal` by running the following command in a terminal:

* `brew install cereal`

### Installing Revolve 2

First you must run the following command in the terminal:

* `export CPATH=/opt/homebrew/include`
  
Then you can install the development version of revolve2 by running the following command in the terminal:

* `revolve/dev_requirements.sh` 
  
This version of `dev_requirements` was edited from original `revolve2/dev_requirements.sh` to exclude `isaacgym`. 

### Check Installation 

To check that the installation was successful you can run the following command in the terminal:

* `python -c "import revolve`

If this command runs without error then the installation was successful.

### SQLAlchemy & MyPy

If you're using `mypy` and/or `visual studio code` you may need to install `sqlalchemy-stubs` to avoid errors.

To do this run the following command in the terminal:

```
pip install -U sqlalchemy-stubs
```

Enable `sqlalchemy-stubs` by adding the following to your `mypy.ini` file:

```
[mypy]
plugins = sqlmypy
```

([ref.](https://github.com/dropbox/sqlalchemy-stubs)])


## Running The Optimization Algorithms

### Plotting 

```
pip install fire
python plot.py ./database simpleopt
```

#### Visual Studio Code Errors

```
pip install pandas-stubs==1.2.0.62
```

## Lamarck 

TO FILL IN
## Morphology

TO FILL IN
