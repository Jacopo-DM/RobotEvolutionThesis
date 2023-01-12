<<readme
RUN COMMANDS MANUALLY! THIS SCRIPT IS NOT MEANT TO BE RUN!

Developed and used on macOS 12.6 (Monterey) with Apple M1 chip; other OSes and chips may not work.

Using 'miniforge' instead of 'miniconda' because it's more less likely to break
(https://github.com/conda-forge/miniforge#miniforge)

Author:     jmdm
Date:       2022-12-30

readme

# if script is run exit
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # echo in red and exit
    echo "\033[0;31mThis script is not meant to be run!\033[0m"
    exit 1
fi

# == Set Up The Conda Environment == #
CONDA_SUBDIR=osx-arm64 conda create -n ENV_NAME
conda activate ENV_NAME
conda env config vars set CONDA_SUBDIR=osx-arm64
conda deactivate
conda activate ENV_NAME