#!/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

VERSION="1.0.0"
DESKTOP_DIR="$HOME/Desktop"
TEMP_DIR="/tmp/steamcommunity_install"

show_header() {
    clear
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}         Steam Community 302 Install/Uninstall Tool v$VERSION         ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
}

install_steamcommunity_302() {
    show_header
    echo -e "${YELLOW}════════════════ Install Steam Community 302 ════════════════${NC}"
    echo ""

    echo -e "${CYAN}Preparing to install the Steam Community 302 tool...${NC}"
    echo "This tool fixes Steam Community access issues."
    echo ""

    local install_dir="$HOME/SteamCommunity302"
    local install_dir2="$HOME/Steamcommunity_302"
    local desktop_file="$DESKTOP_DIR/Steamcommunity-302.desktop"

    local installed=false
    if [ -d "$install_dir" ] || [ -d "$install_dir2" ] || [ -f "$desktop_file" ]; then
        installed=true
    fi

    if [ "$installed" = true ]; then
        echo -e "${GREEN}An existing Steam Community 302 installation may be present${NC}"
        echo ""
        echo "Select an action:"
        echo "1. Reinstall Steam Community 302"
        echo "2. Uninstall Steam Community 302"
        echo "3. Exit"
        echo ""

        read -p "Enter your choice [1-3]: " choice < /dev/tty

        case $choice in
            1)
                echo "Reinstalling Steam Community 302..."
                echo "Cleaning up the old version..."
                if [ -d "$install_dir" ]; then
                    rm -rf "$install_dir"
                    echo -e "${GREEN}✓ Removed install directory: $install_dir${NC}"
                fi
                if [ -d "$install_dir2" ]; then
                    rm -rf "$install_dir2"
                    echo -e "${GREEN}✓ Removed install directory: $install_dir2${NC}"
                fi
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ Removed desktop shortcut${NC}"
                fi
                echo -e "${GREEN}✓ Old version cleaned up, starting the new installation${NC}"
                echo ""
                ;;
            2)
                echo "Uninstalling Steam Community 302..."
                if [ -d "$install_dir" ]; then
                    rm -rf "$install_dir"
                    echo -e "${GREEN}✓ Removed install directory: $install_dir${NC}"
                fi
                if [ -d "$install_dir2" ]; then
                    rm -rf "$install_dir2"
                    echo -e "${GREEN}✓ Removed install directory: $install_dir2${NC}"
                fi
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ Removed desktop shortcut${NC}"
                fi
                echo -e "${GREEN}✓ Steam Community 302 has been uninstalled${NC}"
                read -p "Press Enter to exit..." < /dev/tty
                exit 0
                ;;
            3)
                echo "Exiting."
                read -p "Press Enter to exit..." < /dev/tty
                exit 0
                ;;
            *)
                echo "Invalid choice, exiting."
                read -p "Press Enter to exit..." < /dev/tty
                exit 1
                ;;
        esac
    fi

    echo "About to download and install the Steam Community 302 tool..."
    echo "This tool must be downloaded from dogfight360.com."
    echo ""

    read -p "Continue with the installation? (y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Installation cancelled."
        read -p "Press Enter to exit..." < /dev/tty
        exit 0
    fi

    echo ""
    echo -e "${CYAN}Installing Steam Community 302...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    mkdir -p "$install_dir"
    cd "$install_dir"

    echo "Step 1: Downloading the Steam Community 302 tool..."
    echo "Download URL: https://www.dogfight360.com/blog/wp-content/uploads/2025/12/steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"
    echo ""

    if ! command -v wget &> /dev/null; then
        echo -e "${YELLOW}wget not found, attempting to install it...${NC}"
        sudo pacman -S --noconfirm wget 2>/dev/null || {
            echo -e "${RED}Unable to install wget. Please install it manually and try again.${NC}"
            echo "Install command: sudo pacman -S wget"
            read -p "Press Enter to exit..." < /dev/tty
            exit 1
        }
    fi

    local download_url="https://www.dogfight360.com/blog/wp-content/uploads/2025/12/steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"
    local filename="steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"

    echo "Downloading file..."
    wget --show-progress "$download_url"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Download failed. Please check your network connection.${NC}"
        echo "You can also download it manually and place it in $install_dir"
        read -p "Press Enter to exit..." < /dev/tty
        exit 1
    fi

    echo -e "${GREEN}✓ Download complete${NC}"
    echo ""

    echo "Step 2: Extracting files..."
    tar -xzf "$filename"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ Extraction failed${NC}"
        read -p "Press Enter to exit..." < /dev/tty
        exit 1
    fi

    echo -e "${GREEN}✓ Extraction complete${NC}"
    echo ""

    rm -f "$filename"
    echo "Step 3: Cleaning up the archive..."
    echo -e "${GREEN}✓ Archive removed${NC}"
    echo ""

    local extracted_dir=""
    for dir in *steamcommunity* *Steamcommunity*; do
        if [ -d "$dir" ]; then
            extracted_dir="$dir"
            break
        fi
    done

    if [ -z "$extracted_dir" ]; then
        if [ -f "Steamcommunity_302" ] || [ -f "steamcommunity_302" ]; then
            extracted_dir="."
        else
            echo -e "${RED}✗ Extracted files not found${NC}"
            read -p "Press Enter to exit..." < /dev/tty
            exit 1
        fi
    fi

    cd "$extracted_dir"
    local extracted_path="$(pwd)"
    echo "Step 4: File location: $extracted_path"
    echo -e "${GREEN}✓ Files ready${NC}"
    echo ""

    echo "Step 5: Setting executable permissions..."
    [ -f "Steamcommunity_302" ] && chmod +x "Steamcommunity_302"
    [ -f "steamcommunity_302" ] && chmod +x "steamcommunity_302"
    [ -f "steamcommunity_302.cli" ] && chmod +x "steamcommunity_302.cli"
    [ -f "steamcommunity_302.caddy" ] && chmod +x "steamcommunity_302.caddy"
    echo -e "${GREEN}✓ Executable permissions set${NC}"
    echo ""

    echo "Step 6: Creating the run script..."
    local run_script="run.sh"
    cat > "$run_script" << 'EOF'
#!/bin/bash
clear
echo ""
[ -f "Steamcommunity_302" ] && sudo ./Steamcommunity_302
[ -f "steamcommunity_302" ] && sudo ./steamcommunity_302
EOF

    chmod +x "$run_script"
    echo -e "${GREEN}✓ Run script created: $run_script${NC}"
    echo ""

    echo "Step 7: Creating the desktop shortcut..."

    local steam_icon="applications-internet"
    if [ -f "/usr/share/icons/hicolor/48x48/apps/steam.png" ]; then
        steam_icon="steam"
    fi

    cat > "$desktop_file" << EOF
[Desktop Entry]
Name=Steamcommunity 302
Comment=Steam Community 302 access tool
Exec=$extracted_path/$run_script
Terminal=true
Type=Application
Categories=Network;Utility;
Icon=$steam_icon
Path=$extracted_path
EOF

    chmod +x "$desktop_file"
    echo -e "${GREEN}✓ Desktop shortcut created${NC}"
    echo ""

    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Steam Community 302 installed successfully!${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}Usage:${NC}"
    echo "1. Double-click the 'Steamcommunity 302' icon on the desktop to launch the program"
    echo "2. On first use, open the settings, save them, and then start the service"
    echo "3. The program requires administrator privileges; you will be asked for your password on first run"
    echo ""
    echo -e "${YELLOW}File locations:${NC}"
    echo "Install directory: $install_dir"
    echo "Run script: $extracted_path/$run_script"
    echo "Desktop shortcut: $desktop_file"
    echo ""
    echo -e "${YELLOW}Notes:${NC}"
    echo "1. This tool is installed in $install_dir"
    echo "2. To uninstall, run this script again and choose the uninstall option"
    echo "3. Uninstalling also removes the desktop shortcut and the installed files"
    echo ""

    read -p "Press Enter to exit..." < /dev/tty
    exit 0
}

install_steamcommunity_302
