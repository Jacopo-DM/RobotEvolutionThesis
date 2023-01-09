
# Robot Evolution Thesis

To effectively clone this repo you likely need to run:
 
* `git clone --recurse-submodules`

This will download all the submodules as well; such as [`revolve2`](https://github.com/Jacopo-DM/revolve2) and [`Basics`](https://github.com/Jacopo-DM/Basics/tree/revolve2).


## Directory Structure

```
.
├── README.md           # This document
├── basics              # Helper functions
├── charts              # DrawIO diagrams
├── exp                 # Experiments
│   ├── bo              # (ADD)
│   ├── lamarck         # (ADD)
│   ├── morphologies    # (ADD)
│   └── revdev          # (ADD)
├── revolve             # Robot evolution toolkit (submodule)
└── thesis              # LaTeX files
    ├── bibs            # Bibliography files
    └── docs            # LaTeX files

```


## `./basics`

Git submodule from: [Jacopo-DM/Basics](https://github.com/Jacopo-DM/Basics/tree/revolve2).

This directory contains various basic helper scripts and templates the author uses in his projects.

## `./exp`

This directory contains various experiments and developed code for the thesis.

## `./revolve`

Git submodule from: [Jacopo-DM/revolve2](https://github.com/Jacopo-DM/revolve2), which is a fork of [revolve2](https://github.com/ci-group/revolve2).

This is used to install `Revolve 2` in editable mode.

## `./thesis`

This directory contains the LaTeX files for the thesis.

--- 

## Python Environment Setup

Instructions on how the author set up his (mini)conda environment can be found in [`basics/shell/env.sh`](https://github.com/Jacopo-DM/Basics/blob/revolve2/utils/env.sh). 


Below you can see a copy of those instructions.
```
CONDA_SUBDIR=osx-arm64 conda create -n ENV_NAME
conda activate ENV_NAME
conda env config vars set CONDA_SUBDIR=osx-arm64
conda deactivate
conda activate ENV_NAME
```

Note this was done on a M1 Mac using the [miniforge](https://github.com/conda-forge/miniforge) distribution of `conda`.

### Mac Prerequisites

* Install [Xcode](https://developer.apple.com/xcode/) from the App Store or `Xcode Command Line Tools` by running `xcode-select --install` in a terminal.

* Install [Homebrew](https://brew.sh/) by running in a terminal:

```
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

Using `Homebrew` install `cereal` by running the following command in a terminal:

```
brew install cereal
```

### Installing Revolve 2

First you must run the following command in the terminal:

```
export CPATH=/opt/homebrew/include
```
  
Then you can install the development version of revolve2 by running the following command in the terminal:

```
revolve/dev_requirements.sh
``` 
  
This version of `dev_requirements` was edited from original `revolve2/dev_requirements.sh` to exclude `isaacgym`. 

### Check Installation 

To check that the installation was successful you can run the following command in the terminal:

```
cd path/to/root/of/this/repo
python -c "import revolve"
```

If this command runs without error then the installation was (likely) successful.

---

## Misc Prerequisites

## MyPy

To use `mypy` you must install the following packages:

```
pip install mypy
```

## Visualize


### Data Manipulation: `pandas` & `matplotlib`

```
pip install matplotlib pandas greenlet
```

#### `Plot.py` & `Fire`

The `plot.py` script uses [Fire](https://github.com/google/python-fire) to parse command line arguments, to plot the results of the optimization.

To install `Fire` run the following command in the terminal:

```
pip install fire
```

### Stubs, MyPy, & Visual Studio Code


#### SQLAlchemy

If you're using [mypy](https://mypy-lang.org/) and/or [visual studio code](https://code.visualstudio.com/) you may need to install `sqlalchemy-stubs` to avoid errors.

To do this run the following command in the terminal:

```
pip install -U sqlalchemy-stubs
```

Enable `sqlalchemy-stubs` by adding the following to your `mypy.ini` file:

```
[mypy]
plugins = sqlmypy
```

[[sqlalchemy-stubs ref.](https://github.com/dropbox/sqlalchemy-stubs)]

#### Pandas

Similarly, if you're using `visual studio code` you may need to install `pandas-stubs` to avoid errors.

```
pip install pandas-stubs
pip install pandas-stubs==1.2.0.62 
```

[[pandas-stubs ref.](https://github.com/VirtusLab/pandas-stubs)]

---

## Running The Optimization Algorithms

### Check Install

```
runner.sh
```

### Run Optimization

```
python main.py
```

### Plotting 


```
python plot.py ./database opt
```

---

## Export Your Requirements

```
pip install pipreqs
pipreqs --force .
```

---

## Lamarck 

ADD

## RevDev

ADD

## BO

ADD

## Morphology

ADD