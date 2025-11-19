#!/bin/bash

install_python_mac() {
    echo "Detected Darwin system. Installing via Homebrew..."
    echo "Installing Homebrew (if not already installed)..."
    if ! command -v brew &>/dev/null; then
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        eval "$(/opt/homebrew/bin/brew shellenv)"
    fi

    echo "Installing Python 3..."
    brew install python@3.11
    brew link python@3.11 --force
}

install_python_linux() {
    sudo apt update && sudo apt install -y python3 python3-pip
    sudo python3 -m pip install pygame-ce requests
}

# Detect OS type
if [[ "$OSTYPE" == "darwin"* ]]; then
    install_python_mac
else
    echo "Detected Linux system. Installing via apt..."
    install_python_linux
    echo "Creating .desktop entry in /home/$SUDO_USER/.local/share/applications/" 
    sudo tee ./spoons.desktop >/dev/null <<-EOL
[Desktop Entry]
Type=Application
Terminal=false
Exec=python3 main.pyw
Path=/home/$SUDO_USER/Documents/Spoons-main/
Name=Spoons
Comment=Get your shit together
Icon=/home/$SUDO_USER/Documents/Spoons-main/images/hubIcons/default/addSpoonsIcon.png
EOL

    sudo mv ./spoons.desktop /home/$SUDO_USER/.local/share/applications/
    sudo chmod +x /home/$SUDO_USER/.local/share/applications/spoons.desktop
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
python3 -m pip install --upgrade setuptools wheel #idk what this is lol
python3 -m pip install pygame-ce requests

echo "Installation complete!"
echo "Press Enter to exit."
read
