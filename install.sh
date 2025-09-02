#!/bin/bash

# Cookie Creator Utility Installation Script
# This script helps you set up the Cookie Creator Utility

echo "======================================"
echo "Cookie Creator Utility Installation"
echo "======================================"
echo

# Check if Python 3.7+ is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required but not installed."
    echo "Please install Python 3.7 or higher and try again."
    exit 1
fi

PYTHON_VERSION=$(python3 -c "import sys; print('.'.join(map(str, sys.version_info[:2])))")
echo "Python version detected: $PYTHON_VERSION"

# Check Python version
if python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)"; then
    echo "✓ Python version is compatible"
else
    echo "✗ Python 3.7 or higher is required"
    exit 1
fi

echo
echo "Installing Cookie Creator Utility..."

# Install in development mode
pip3 install -e .

if [ $? -eq 0 ]; then
    echo "✓ Base installation completed"
else
    echo "✗ Installation failed"
    exit 1
fi

echo
read -p "Do you want to install yt-dlp integration support? (y/N): " install_ytdlp

if [[ $install_ytdlp =~ ^[Yy]$ ]]; then
    echo "Installing yt-dlp integration..."
    pip3 install -e .[ytdlp]
    
    if [ $? -eq 0 ]; then
        echo "✓ yt-dlp integration installed"
    else
        echo "✗ yt-dlp installation failed"
    fi
fi

echo
read -p "Do you want to install development dependencies? (y/N): " install_dev

if [[ $install_dev =~ ^[Yy]$ ]]; then
    echo "Installing development dependencies..."
    pip3 install -e .[dev]
    
    if [ $? -eq 0 ]; then
        echo "✓ Development dependencies installed"
    else
        echo "✗ Development dependencies installation failed"
    fi
fi

echo
echo "======================================"
echo "Installation completed!"
echo "======================================"
echo
echo "You can now use the utility in the following ways:"
echo
echo "1. Interactive mode:"
echo "   cookie-util"
echo
echo "2. Command line mode:"
echo "   cookie-util --url https://example.com"
echo
echo "3. Python module:"
echo "   python3 -m cookie_creator.cookie_creator"
echo
echo "4. In your Python scripts:"
echo "   from cookie_creator import CookieCreator"
echo
echo "For examples, run:"
echo "   python3 examples.py"
echo
echo "For help, run:"
echo "   cookie-util --help"
echo