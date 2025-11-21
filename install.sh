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
# Step 2: Create virtual environment
#-------------------------------------------------------------------------------
print_info "Setting up virtual environment..."

if [ -d "$INSTALL_DIR/venv" ]; then
    print_warning "Virtual environment already exists, skipping creation"
else
    python3 -m venv "$INSTALL_DIR/venv"
    print_success "Virtual environment created"
fi

#-------------------------------------------------------------------------------
# Step 3: Install dependencies
#-------------------------------------------------------------------------------
print_info "Installing dependencies..."

"$INSTALL_DIR/venv/bin/pip" install --upgrade pip --quiet
"$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" --quiet

print_success "Dependencies installed"

#-------------------------------------------------------------------------------
# Step 4: Create necessary directories
#-------------------------------------------------------------------------------
print_info "Creating application directories..."

mkdir -p "$HOME/.local/share/codegate/logs"
mkdir -p "$HOME/.config/autostart"

print_success "Directories created"

#-------------------------------------------------------------------------------
# Step 5: Make scripts executable
#-------------------------------------------------------------------------------
print_info "Setting permissions..."

chmod +x "$INSTALL_DIR/run_codegate.sh"

print_success "Scripts made executable"

#-------------------------------------------------------------------------------
# Step 6: Configure autostart
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
# Step 7: Create default config if needed
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
# Step 8: Test installation
#-------------------------------------------------------------------------------
print_info "Testing installation..."

if "$INSTALL_DIR/venv/bin/python3" -c "import PySide6, psutil, requests" 2>/dev/null; then
    print_success "All Python modules imported successfully"
else
    print_error "Failed to import required modules"
    exit 1
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
echo "  3. Configure blocked apps in the settings (⚙ icon)"
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
    print_success "CodeGate started! Check the system tray."
fi

exit 0
