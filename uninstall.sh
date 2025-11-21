#!/bin/bash
#-------------------------------------------------------------------------------
# CodeGate Uninstallation Script
# Removes CodeGate and cleans up all configuration
#-------------------------------------------------------------------------------

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Banner
echo ""
echo "╔════════════════════════════════════════╗"
echo "║   CodeGate Uninstallation Script      ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Get install directory
INSTALL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Confirm uninstallation
echo -e "${YELLOW}This will remove CodeGate and all its data.${NC}"
read -p "Are you sure you want to uninstall? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Uninstallation cancelled"
    exit 0
fi

#-------------------------------------------------------------------------------
# Step 1: Stop running processes
#-------------------------------------------------------------------------------
print_info "Stopping CodeGate processes..."

# Stop watchdog
if [ -f "$HOME/.local/share/codegate/watchdog.pid" ]; then
    WATCHDOG_PID=$(cat "$HOME/.local/share/codegate/watchdog.pid")
    if kill -0 "$WATCHDOG_PID" 2>/dev/null; then
        kill "$WATCHDOG_PID" 2>/dev/null || true
        print_success "Watchdog stopped (PID: $WATCHDOG_PID)"
    fi
    rm -f "$HOME/.local/share/codegate/watchdog.pid"
fi

# Kill any remaining CodeGate processes
pkill -f "codegate" 2>/dev/null || true
sleep 1

print_success "All processes stopped"

#-------------------------------------------------------------------------------
# Step 2: Remove autostart
#-------------------------------------------------------------------------------
print_info "Removing autostart configuration..."

if [ -f "$HOME/.config/autostart/codegate.desktop" ]; then
    rm -f "$HOME/.config/autostart/codegate.desktop"
    print_success "Autostart removed"
fi

#-------------------------------------------------------------------------------
# Step 3: Clean up data directory
#-------------------------------------------------------------------------------
print_info "Cleaning up data directory..."

if [ -d "$HOME/.local/share/codegate" ]; then
    # Ask if user wants to keep logs
    read -p "Keep log files? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        rm -rf "$HOME/.local/share/codegate"
        print_success "Data directory removed"
    else
        print_warning "Logs kept in: $HOME/.local/share/codegate/logs"
    fi
fi

#-------------------------------------------------------------------------------
# Step 4: Remove virtual environment
#-------------------------------------------------------------------------------
print_info "Removing virtual environment..."

if [ -d "$INSTALL_DIR/venv" ]; then
    rm -rf "$INSTALL_DIR/venv"
    print_success "Virtual environment removed"
fi

#-------------------------------------------------------------------------------
# Step 5: Clean up config files
#-------------------------------------------------------------------------------
print_info "Cleaning up configuration..."

# Ask if user wants to keep config
read -p "Keep configuration file? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    rm -f "$INSTALL_DIR/config.json"
    rm -f "$INSTALL_DIR/.config_checksum"
    rm -f "$INSTALL_DIR/config.json.backup"
    rm -f "$INSTALL_DIR/.config.json.backup_checksum"
    print_success "Configuration removed"
else
    print_warning "Configuration kept: $INSTALL_DIR/config.json"
fi

#-------------------------------------------------------------------------------
# Complete
#-------------------------------------------------------------------------------
echo ""
echo "╔════════════════════════════════════════╗"
echo "║   Uninstallation Complete! ✓           ║"
echo "╚════════════════════════════════════════╝"
echo ""
print_info "CodeGate has been uninstalled"
print_warning "To completely remove, delete: $INSTALL_DIR"
echo ""

exit 0
