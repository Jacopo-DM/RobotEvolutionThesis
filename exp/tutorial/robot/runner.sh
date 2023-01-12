<<readme

Runs mypy on selected files in the project.

Author:     jmdm
Date:       2023-01-05
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

Remeber to:
- cd path/to/root
- chmod +x runner.sh

readme

function run_mypy {
    echo "\033[1;36m--- $1 ---033[0m"
    mypy --config-file mypy.ini $1
    echo "\033[1;36m--- end ---\033[0m"
    echo ""
}

function run_python {
    echo "\033[1;36m--- $1 ---\033[0m"
    python $1
    echo "\033[1;36m--- end ---\033[0m"
    echo ""
}

# Create list of files
mypy_files=(
    "utils/data.py"
    "utils/setup.py"
    "main.py"
)

python_files=(
    "utils/setup.py"
)

# Run mypy on each file
echo "\033[1;35m=== mypy ===\033[0m\n"
for file in "${mypy_files[@]}"
do
    run_mypy $file
done

# Run python on each file
echo "\033[1;35m=== python ===\033[0m\n"
for file in "${python_files[@]}"
do
    run_python $file
done