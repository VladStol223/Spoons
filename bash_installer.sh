#!/bin/bash

ask_yes_no() {
    local prompt="$1"
    while true; do
        read -r -p "$prompt [y/n]: " response
        case "$response" in
            [yY]|[yY][eE][sS]) 
                return 0
                ;;
            [nN]|[nN][oO])
                return 1
                ;;
            *)
                echo "Invalid input. Please enter 'y' for yes or 'n' for no."
                ;;
        esac
    done
}

download_spoons_repo() {
    echo "Downloading Spoons repository..."

    # Directory to store the repo (set to Documents)
    DOWNLOAD_DIR="$HOME/Documents"
    REPO_URL="https://github.com/VladStol223/Spoons/archive/refs/heads/main.zip"
    
    # Download the ZIP file from GitHub
    curl -L "$REPO_URL" -o "$DOWNLOAD_DIR/spoons-main.zip"
    
    # Check if the download was successful
    if [ $? -eq 0 ]; then
        echo "Download successful."
    else
        echo "Failed to download repository."
        exit 1
    fi

    # Extract the ZIP file to the Documents directory
    echo "Extracting Spoons repository..."
    unzip "$DOWNLOAD_DIR/spoons-main.zip" -d "$DOWNLOAD_DIR"

    # Verify extraction
    if [ $? -eq 0 ]; then
        echo "Extraction successful."
        rm "$DOWNLOAD_DIR/spoons-main.zip"  # Optionally remove the ZIP file after extraction
    else
        echo "Failed to extract the ZIP file."
        exit 1
    fi
}

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
    # Ask the user if they want to proceed with the installation
    echo "Warning: Global installs can break systems which rely on certain pacakges"
    if ! ask_yes_no "Do you accpt the risk of installing pygame-ce globally?"; then
        echo "Installation cancelled by user."
        exit 1
    fi
    sudo python3 -m pip install pygame-ce --break-system-packages
    sudo python3 -m pip install requests
}

# Detect OS type
if [[ "$OSTYPE" == "darwin"* ]]; then
    install_python_mac
else
    echo "Detected Linux system. Downloading Spoons repository..."
    download_spoons_repo
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
