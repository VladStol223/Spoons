#!/bin/bash

echo "Checking for Python installation..."

# Check if Python is installed
if ! command -v python3 &>/dev/null; then
    echo "Python is not installed. Installing Python..."
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        brew install python3
    else
        # Linux
        sudo apt update && sudo apt install -y python3 python3-pip
    fi
else
    echo "Python is already installed."
fi

# Ensure pip is installed and upgraded
echo "Upgrading pip..."
python3 -m ensurepip --default-pip
python3 -m pip install --upgrade pip

# Install dependencies
echo "Installing required Python packages..."
python3 -m pip install pygame requests

echo "Installation complete!"