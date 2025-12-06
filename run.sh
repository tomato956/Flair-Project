#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Define virtual environment path
VENV_DIR="${SCRIPT_DIR}/.venv"

# Determine OS and set Python executable path
PYTHON_EXEC=""
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
    PYTHON_EXEC="${VENV_DIR}/bin/python"
elif [ "$(uname -s)" == "Linux" ]; then
    PYTHON_EXEC="${VENV_DIR}/bin/python"
elif [ "$(uname -s)" == "Darwin" ]; then
    PYTHON_EXEC="${VENV_DIR}/bin/python"
elif [[ "$(uname -s)" == CYGWIN* || "$(uname -s)" == MINGW32* || "$(uname -s)" == MSYS* || "$(uname -s)" == MINGW* ]]; then
    PYTHON_EXEC="${VENV_DIR}/Scripts/python.exe"
else
    echo "Unsupported OS"
    exit 1
fi

# Check if virtual environment exists, if not, create it and install dependencies
# For WSL, we don't try to create a Linux venv if it's already a Windows venv
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV_DIR"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to create virtual environment."
        exit 1
    fi
    echo "Virtual environment created."
fi

# Install dependencies if not already installed
if [ ! -f "${VENV_DIR}/.installed_requirements" ]; then
    echo "Installing dependencies..."
    # Ensure pip is up-to-date
    "$PYTHON_EXEC" -m pip install --upgrade pip
    REQUIREMENTS_PATH="${SCRIPT_DIR}/requirements.txt"

    "$PYTHON_EXEC" -m pip install -r "${REQUIREMENTS_PATH}"
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install dependencies."
        exit 1
    fi
    touch "${VENV_DIR}/.installed_requirements"
    echo "Dependencies installed."
else
    echo "Dependencies already installed."
fi

# Check if the python executable exists after potential venv creation
if [ ! -f "$PYTHON_EXEC" ]; then
    echo "Error: Python executable not found at $PYTHON_EXEC"
    echo "Please ensure the virtual environment is set up correctly."
    exit 1
fi

# Path to the main application script
FLAIR_SCRIPT="${SCRIPT_DIR}/maincode/Flair.py"


echo "Starting Flair application..."
# Run the Flair application in the background
# For Windows (including WSL calling Windows Python), the GUI will appear on the Windows desktop.
# For native Linux/macOS, it will appear on the X server.
if grep -qEi "(Microsoft|WSL)" /proc/version &>/dev/null; then
    # For WSL, we will use the Linux Python executable from the virtual environment.
    PYTHON_EXEC="${VENV_DIR}/bin/python"
    FLAIR_SCRIPT="${SCRIPT_DIR}/maincode/Flair.py"
    "$PYTHON_EXEC" "$FLAIR_SCRIPT" &
else
    "$PYTHON_EXEC" "$FLAIR_SCRIPT"
fi
