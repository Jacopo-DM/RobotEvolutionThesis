#!/usr/bin/env python3

"""
Author:     jmdm
Date:       2022-12-30
OS:         macOS 12.6 (Monterey)
Hardware:   M1 chip

This code is provided "As Is"
"""


# Default libraries
import logging
import os
import sys

# Local libraries
try:
    from .data import ShellColours as Clr
except ImportError:
    from data import ShellColours as Clr


# Global constants
LOGGING_LEVEL = logging.INFO
PY_VERSION = (3, 10)


def setup_logging() -> None:
    """Setup logging"""

    # Set logging level and format
    logging.basicConfig(
        level=LOGGING_LEVEL,
        format="[%(levelname)-8s] \t %(message)s",
        datefmt="%H:%M",
    )

    # Add color to logging levels
    logging.addLevelName(logging.DEBUG, f"{Clr.gray_em}DEBUG{Clr.end}")
    logging.addLevelName(logging.INFO, f"{Clr.green_em}INFO{Clr.end}")
    logging.addLevelName(logging.WARNING, f"{Clr.yellow_em}WARN{Clr.end}")
    logging.addLevelName(logging.ERROR, f"{Clr.red_em}ERROR{Clr.end}")


def check_os() -> None:
    """Check operating system"""

    # Check which operating system is being used
    logging.debug("Checking system...")
    system = sys.platform
    os_match = {
        "darwin": "MacOS",
        "linux": "Linux",
        "linux2": "Linux",
        "win32": "Windows",
    }
    os_name = os_match.get(system, "Unknown")
    if os_name != "Unknown":
        if os_name != "MacOS":
            logging.warning(f"Code was developed on {Clr.yellow}MacOS{Clr.end}")
        logging.info(f"Operating system is {Clr.green}{os_name}{Clr.end}")
    else:
        logging.error(f"System {Clr.red}{sys.platform}{Clr.end} is not supported!")
        logging.error("Exiting...\n")
        raise NotImplementedError

    # Log number of cores
    logging.info(f"Number of cores is {Clr.green}{os.cpu_count()}{Clr.end}")


def check_python_version() -> None:
    """Check python version"""

    # Check python version matches minimum
    logging.debug("Checking python version...")
    py_maj = sys.version_info.major
    py_min = sys.version_info.minor

    # Check major version
    if py_maj != PY_VERSION[0]:
        logging.error(
            f"{Clr.red}Python major version must be {PY_VERSION[0]}, got: {py_maj}{Clr.end}"
        )
        logging.error("Exiting...")
        sys.exit(1)
    else:
        # Check minor version if major version is the same
        if py_min < PY_VERSION[1]:
            logging.error(
                f"{Clr.red}Python version must be {PY_VERSION[0]}.{PY_VERSION[1]} or higher, got: {py_maj}.{py_min}{Clr.end}"
            )
            logging.error("Exiting...")
            sys.exit(1)

    # Log python version
    logging.info(
        f"Python version: {Clr.green}{sys.version_info.major}.{sys.version_info.minor}{Clr.end}"
    )


def check_requirements() -> None:
    """Check requirements.txt exists and required packages are installed"""

    # Check if requirements.txt exists
    logging.debug("Checking if requirements.txt exists...")
    if not os.path.exists("requirements.txt"):
        logging.warning(f"requirements.txt {Clr.yellow}not found{Clr.end}")
        logging.debug("Skipping check for required packages...")
    elif os.stat("requirements.txt").st_size == 0:
        logging.warning(f"requirements.txt {Clr.yellow}is empty{Clr.end}")
        logging.debug("Skipping check for required packages...")
    elif os.path.getsize("requirements.txt") <= 1:
        logging.warning(f"requirements.txt {Clr.yellow}is empty{Clr.end}")
        logging.debug("Skipping check for required packages...")
    else:
        # Check that required packages are installed
        logging.debug("Checking required packages...")

        # get imports from requirements.txt
        with open("requirements.txt", "r") as f:
            requirements = f.readlines()
            # remove version numbers
            requirements = [r.split("==")[0] for r in requirements]
            # warn version numbers are ignored
            logging.debug(f"{Clr.yellow}Version numbers are ignored{Clr.end}")
        try:
            # check if all packages are installed
            for r in requirements:
                __import__(r)
                # if no error is raised, the package is installed
                logging.info(f"Package {r} is {Clr.green}installed{Clr.end}")
        except ModuleNotFoundError as e:
            logging.error("Required packages are not installed")

            # Log required packages
            logging.error("Required packages:")
            for r in requirements:
                logging.error(f"\t{Clr.red}{r}{Clr.end}")

            # logging warning, install using pip install -r requirements.txt
            logging.warning(
                f"Install using {Clr.yellow}pip install -r requirements.txt{Clr.end}"
            )
            logging.error("Exiting...\n")
            raise

    # Log success
    logging.info(f"{Clr.green}Environment is ready{Clr.end}")


def setup() -> None:
    """Check if environment is ready to run code"""

    # Setup logging module
    setup_logging()

    # Check which system is being used
    check_os()

    # Check which python version is being used
    check_python_version()

    # Check if required packages are installed
    check_requirements()


if __name__ == "__main__":
    setup()
