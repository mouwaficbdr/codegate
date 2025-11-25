#!/bin/bash
#-------------------------------------------------------------------------------
# CodeGate Installation Script
# Installs CodeGate with all dependencies and configures autostart
#-------------------------------------------------------------------------------

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Banner
echo ""
echo "╔════════════════════════════════════════╗"
echo "║     CodeGate Installation Script      ║"
echo "║   Productivity through Code Challenges ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Get script directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
print_info "Installation directory: $INSTALL_DIR"

#-------------------------------------------------------------------------------
# Step 1: Check Python version
#-------------------------------------------------------------------------------
print_info "Checking Python version..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed!"
    print_info "Please install Python 3.10 or higher:"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.10"

if printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V -C; then
    print_success "Python $PYTHON_VERSION found"
else
    print_error "Python 3.10+ required, but found $PYTHON_VERSION"
    exit 1
fi

#-------------------------------------------------------------------------------
# Step 2: Check Node.js (for JavaScript challenges)
#-------------------------------------------------------------------------------
print_info "Checking Node.js..."

if ! command -v node &> /dev/null; then
    print_warning "Node.js is not installed!"
    print_info "Node.js is required to run JavaScript challenges."
    
    read -p "Install Node.js now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing Node.js..."
        # Ubuntu/Debian
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y nodejs
        # Fedora/RHEL
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y nodejs
        # Arch
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm nodejs
        else
            print_error "Cannot auto-install Node.js on this distribution"
            print_info "Please install manually: https://nodejs.org"
            print_warning "JavaScript challenges will NOT work without Node.js"
        fi
    else
        print_warning "Skipping Node.js installation"
        print_warning "JavaScript challenges will NOT work without Node.js"
    fi
else
    NODE_VERSION=$(node --version 2>&1)
    print_success "Node.js $NODE_VERSION found"
fi

#-------------------------------------------------------------------------------
# Step 3: Check PHP (for PHP challenges)
#-------------------------------------------------------------------------------
print_info "Checking PHP..."

if ! command -v php &> /dev/null; then
    print_warning "PHP is not installed!"
    print_info "PHP is required to run PHP challenges."
    
    read -p "Install PHP now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_info "Installing PHP..."
        # Ubuntu/Debian
        if command -v apt &> /dev/null; then
            sudo apt update
            sudo apt install -y php-cli
        # Fedora/RHEL
        elif command -v dnf &> /dev/null; then
            sudo dnf install -y php-cli
        # Arch
        elif command -v pacman &> /dev/null; then
            sudo pacman -S --noconfirm php
        else
            print_error "Cannot auto-install PHP on this distribution"
            print_info "Please install manually"
            print_warning "PHP challenges will NOT work without PHP"
        fi
    else
        print_warning "Skipping PHP installation"
        print_warning "PHP challenges will NOT work without PHP"
    fi
else
    PHP_VERSION=$(php --version 2>&1 | head -n 1 | awk '{print $2}')
    print_success "PHP $PHP_VERSION found"
fi

#-------------------------------------------------------------------------------
# Step 4: Create virtual environment
#-------------------------------------------------------------------------------
print_info "Setting up virtual environment..."

# Check if venv exists AND is valid (pip must actually work)
VENV_VALID=false
if [ -d "$INSTALL_DIR/venv" ]; then
    # Test if pip can actually run
    if "$INSTALL_DIR/venv/bin/pip" --version &>/dev/null; then
        print_warning "Virtual environment already exists and is valid, skipping creation"
        VENV_VALID=true
    else
        print_warning "Virtual environment exists but appears corrupted (pip broken)"
        print_info "Removing corrupted virtual environment..."
        rm -rf "$INSTALL_DIR/venv"
    fi
fi

if [ "$VENV_VALID" = false ]; then
    print_info "Creating virtual environment..."
    python3 -m venv "$INSTALL_DIR/venv"
    print_success "Virtual environment created"
fi

#-------------------------------------------------------------------------------
# Step 5: Install dependencies
#-------------------------------------------------------------------------------
print_info "Installing dependencies..."

"$INSTALL_DIR/venv/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" --quiet

print_success "Dependencies installed"

#-------------------------------------------------------------------------------
# Step 6: Create necessary directories
#-------------------------------------------------------------------------------
print_info "Creating application directories..."

mkdir -p "$HOME/.local/share/codegate/logs"
mkdir -p "$HOME/.config/autostart"

print_success "Directories created"

#-------------------------------------------------------------------------------
# Step 7: Make scripts executable
#-------------------------------------------------------------------------------
print_info "Setting permissions..."

chmod +x "$INSTALL_DIR/run_codegate.sh"

print_success "Scripts made executable"

#-------------------------------------------------------------------------------
# Step 8: Configure autostart
#-------------------------------------------------------------------------------
print_info "Configuring autostart..."

DESKTOP_FILE="$HOME/.config/autostart/codegate.desktop"

# Update the Exec path in desktop file
cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=CodeGate
Comment=Productivity tool that requires coding challenges to unblock apps
Exec=$INSTALL_DIR/run_codegate.sh
Icon=security-high
Terminal=false
Categories=Utility;Security;
StartupNotify=false
X-GNOME-Autostart-enabled=true
Hidden=false
EOF

print_success "Autostart configured: $DESKTOP_FILE"

#-------------------------------------------------------------------------------
# Step 9: Create default config if needed
#-------------------------------------------------------------------------------
print_info "Checking configuration..."

if [ ! -f "$INSTALL_DIR/config.json" ]; then
    print_info "Creating default configuration..."
    cat > "$INSTALL_DIR/config.json" << EOF
{
    "blocked_apps": [],
    "language": "fr",
    "difficulty_mode": "Mixed",
    "custom_apps": []
}
EOF
    print_success "Default configuration created"
else
    print_warning "Configuration file already exists, keeping current settings"
fi

#-------------------------------------------------------------------------------
# Step 10: Test installation
#-------------------------------------------------------------------------------
print_info "Testing installation..."

if "$INSTALL_DIR/venv/bin/python3" -c "import PySide6, psutil, requests" 2>/dev/null; then
    print_success "All Python modules imported successfully"
else
    print_error "Failed to import required modules"
    exit 1
fi

#-------------------------------------------------------------------------------
# Step 11: Install CLI tool
#-------------------------------------------------------------------------------
print_info "Installing CLI tool..."

# Create ~/.local/bin if it doesn't exist
mkdir -p "$HOME/.local/bin"

# Copy CLI script
cp "$INSTALL_DIR/bin/codegate" "$HOME/.local/bin/codegate"
chmod +x "$HOME/.local/bin/codegate"
print_success "CLI tool installed to ~/.local/bin/codegate"

# Check if ~/.local/bin is in PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_warning "~/.local/bin is not in your PATH"
    
    # Detect shell
    SHELL_RC=""
    if [ -n "$BASH_VERSION" ]; then
        SHELL_RC="$HOME/.bashrc"
    elif [ -n "$ZSH_VERSION" ]; then
        SHELL_RC="$HOME/.zshrc"
    fi
    
    if [ -n "$SHELL_RC" ]; then
        print_info "Adding ~/.local/bin to PATH in $SHELL_RC"
        echo '' >> "$SHELL_RC"
        echo '# Added by CodeGate installer' >> "$SHELL_RC"
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$SHELL_RC"
        print_success "PATH updated in $SHELL_RC"
        print_warning "Please run: source $SHELL_RC"
        print_warning "Or restart your terminal to use 'codegate' command"
    else
        print_warning "Please manually add ~/.local/bin to your PATH"
    fi
else
    print_success "~/.local/bin already in PATH"
fi

#-------------------------------------------------------------------------------
# Installation complete
#-------------------------------------------------------------------------------
echo ""
echo "╔════════════════════════════════════════╗"
echo "║   Installation Complete! ✓             ║"
echo "╚════════════════════════════════════════╝"
echo ""
print_info "CodeGate has been installed successfully!"
echo ""
echo "Next steps:"
echo "  1. CodeGate will start automatically at next login"
echo "  2. Or start it now: $INSTALL_DIR/run_codegate.sh"
echo "  3. Open dashboard: codegate open (or click system tray icon)"
echo "  4. View status: codegate status"
echo ""
print_warning "NOTE: To uninstall, run: $INSTALL_DIR/uninstall.sh"
echo ""

# Ask if user wants to start now
read -p "Start CodeGate now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_info "Starting CodeGate..."
    "$INSTALL_DIR/run_codegate.sh" &
    sleep 2
    print_success "CodeGate started!"
    print_info "The dashboard will open for first-time setup"
    print_info "You can also control it with: codegate {open|status|quit}"
fi

exit 0
