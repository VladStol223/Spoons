#!/bin/bash

echo "Checking for Python installation..."

# Check if Python 3 is installed
if ! command -v python3 &>/dev/null; then
    echo "Python is not installed. Installing Python..."

    # Detect OS type
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        echo "Installing Homebrew (if not already installed)..."
        if ! command -v brew &>/dev/null; then
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
            eval "$(/opt/homebrew/bin/brew shellenv)"
        fi

        echo "Installing Python 3..."
        brew install python@3.11
        brew link python@3.11 --force
    else
        # Linux fallback
        echo "Detected Linux system. Installing via apt..."
        sudo apt update && sudo apt install -y python3 python3-pip
    fi
else
    echo "Python is already installed."
fi

# Verify Python path
PYTHON_PATH=$(which python3)
echo "Python path: $PYTHON_PATH"

# Ensure pip exists and is updated
echo "Upgrading pip..."
python3 -m ensurepip --default-pip
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing required Python packages..."
python3 -m pip install --upgrade setuptools wheel
python3 -m pip install pygame-ce pygame_gui requests

echo "Installation complete!"
echo "Press Enter to exit."
read