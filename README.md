# Robot Evolution Thesis

## README.md

This file

## Basics 

Git submodule from: [Jacopo-DM/Basics](https://github.com/Jacopo-DM/Basics)

This directory contains various basic helper scripts and templates JMDM uses in his projects.

## Revolve

Git submodule from: [Jacopo-DM/revolve2](https://github.com/Jacopo-DM/revolve2), which is a fork of [revolve2](https://github.com/ci-group/revolve2).

This is used to install `Revolve 2` in editable mode.

### Python Environment Setup

Instructions on how JMDM set up his (mini)conda environment can be found in `basics/shell/env.sh`.

### Mac Pre-requisites

* Install `Xcode` from the App Store or `Xcode Command Line Tools` by running `xcode-select --install` in a terminal 
* Install `Homebrew` by running `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"` in a terminal

Using `Homebrew` install `cereal` by running the following command in a terminal:

* `brew install cereal`

### Installing Revolve 2

First you must run the following command in the terminal:

* `export CPATH=/opt/homebrew/include`
  
Then you can install the development version of revolve2 by running the following command in the terminal:

* `revolve/dev_requirements.sh` 
  
This version of `dev_requirements` was edited from original `revolve2/dev_requirements.sh` to exclude `isaacgym`. 

<!-- ## Lamarck 

This repository contains the code for the `Lamarck` project, which is a project to evolve robots using the `Revolve 2` framework, using the `Lamarckian` evolution paradigm for the neural networks.

## Morphology

This repository contains the code for the `Morphology` project, which is a project to evolve robots using the `Revolve 2` framework, explores the automatic generation of robot morphologies for baseline experiments. -->

## Directory Structure

```
.
├── LICENSE
├── README.md
├── basics
├── lamarck
└── revolve
```
