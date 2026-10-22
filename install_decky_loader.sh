#!/bin/bash
# ============================================================================
# Decky Loader (plugin store) install/update script
# Rewritten with reference to the install_plugin_store flow in steamdeck_gui:
#   - Version logic: stable/prerelease distinction and selection, smart switching of installed version
#   - Download: official GitHub source only
#   - Strict mode: set -uo pipefail (no set -e, to avoid unexpected exits when (( )) evaluates to 0)
#   - Interactive read always uses < /dev/tty
#   - File size validation
# ============================================================================

set -uo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

HOME_DIR="/home/deck"
HOMEBREW_DIR="${HOME_DIR}/homebrew"
SERVICE_DIR="${HOMEBREW_DIR}/services"
PLUGIN_DIR="${HOMEBREW_DIR}/plugins"
PLUGIN_LOADER="${SERVICE_DIR}/PluginLoader"
SERVICE_FILE="${SERVICE_DIR}/plugin_loader.service"
SERVICE_DEST="/etc/systemd/system/plugin_loader.service"
CURRENT_USER=$(whoami)

DOWNLOAD_TIMEOUT=60

for cmd in curl python3 systemctl sudo journalctl stat; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}Error: command '$cmd' not found. Please install it first.${NC}"
        read -p "Press Enter to exit..." < /dev/tty
        exit 1
    fi
done

echo -e "${CYAN}Fetching Decky Loader version information...${NC}"
releases_json=$(curl -s --connect-timeout 15 --max-time 30 "https://api.github.com/repos/SteamDeckHomebrew/decky-loader/releases")
if [ -z "$releases_json" ]; then
    echo -e "${RED}Error: unable to reach the GitHub API. Please check your network.${NC}"
    read -p "Press Enter to exit..." < /dev/tty
    exit 1
fi

versions_info=$(echo "$releases_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    stable = []
    prerelease = []
    for rel in data:
        tag = rel.get('tag_name', '')
        if tag:
            if rel.get('prerelease', False):
                prerelease.append(tag)
            else:
                stable.append(tag)
    print('STABLE:' + ','.join(stable) if stable else 'STABLE:')
    print('PRERELEASE:' + ','.join(prerelease) if prerelease else 'PRERELEASE:')
except Exception:
    print('STABLE:')
    print('PRERELEASE:')
")
if [ -z "$versions_info" ]; then
    echo -e "${RED}Error: unable to parse version information.${NC}"
    read -p "Press Enter to exit..." < /dev/tty
    exit 1
fi

stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

latest_stable=""
if [ -n "$stable_list" ]; then
    latest_stable=$(echo "$stable_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
    [ -n "$latest_stable" ] && latest_stable="v${latest_stable}"
fi

latest_prerelease=""
if [ -n "$prerelease_list" ]; then
    latest_prerelease=$(echo "$prerelease_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
    [ -n "$latest_prerelease" ] && latest_prerelease="v${latest_prerelease}"
fi

INSTALLED_VERSION=""
if [[ -f "$PLUGIN_LOADER" && -x "$PLUGIN_LOADER" ]]; then
    INSTALLED_VERSION=$(sudo journalctl -u plugin_loader --no-pager 2>/dev/null | grep -i "Starting Decky version" | tail -1 | grep -oP 'version v?\K[0-9.]+(-pre[0-9]+)?')
    if [[ -z "$INSTALLED_VERSION" ]]; then
        INSTALLED_VERSION=$("$PLUGIN_LOADER" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+(-pre\d+)?')
    fi
    if [[ -n "$INSTALLED_VERSION" ]]; then
        INSTALLED_VERSION="v${INSTALLED_VERSION}"
        echo -e "${CYAN}Currently installed version: ${INSTALLED_VERSION}${NC}"
    else
        echo -e "${YELLOW}Already installed but the version could not be determined; reinstalling.${NC}"
    fi
else
    echo -e "${YELLOW}No existing installation detected.${NC}"
fi

options=()
labels=()
if [ -n "$latest_stable" ]; then
    options+=("$latest_stable")
    labels+=("Stable $latest_stable")
fi
if [ -n "$latest_prerelease" ]; then
    options+=("$latest_prerelease")
    labels+=("Prerelease $latest_prerelease")
fi
if [ ${#options[@]} -eq 0 ]; then
    echo -e "${RED}Error: no available versions found.${NC}"
    read -p "Press Enter to exit..." < /dev/tty
    exit 1
fi

target_version=""

if [ -z "$INSTALLED_VERSION" ]; then
    while true; do
        if [ ${#options[@]} -eq 1 ]; then
            target_version="${options[0]}"
            echo -e "${GREEN}Installing the only available version: ${target_version}${NC}"
            break
        else
            echo "Select the version to install:"
            for i in "${!options[@]}"; do
                echo "$((i+1))) ${labels[$i]}"
            done
            read -p "Enter your choice [1-${#options[@]}]: " choice < /dev/tty
            if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#options[@]} ]; then
                target_version="${options[$((choice-1))]}"
                break
            else
                echo -e "${RED}Invalid choice, please try again.${NC}"
                sleep 1
            fi
        fi
    done
else
    is_prerelease=false
    if [ -n "$prerelease_list" ]; then
        inst_ver_clean=$(echo "$INSTALLED_VERSION" | sed 's/^v//')
        for tag in $(echo "$prerelease_list" | tr ',' '\n'); do
            tag_clean=$(echo "$tag" | sed 's/^v//')
            if [ "$tag_clean" = "$inst_ver_clean" ]; then
                is_prerelease=true
                break
            fi
        done
    fi

    if [ "$is_prerelease" = true ]; then
        if [ -n "$latest_stable" ]; then
            echo -e "${YELLOW}The currently installed version is the prerelease ${INSTALLED_VERSION}.${NC}"
            echo -e "${YELLOW}Switch to the stable version ${latest_stable}?${NC}"
            read -n1 -p "Press Enter or A to switch, any other key to keep the current version: " switch_choice < /dev/tty
            echo
            if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                target_version="$latest_stable"
                echo -e "${GREEN}Switching to the stable version: ${target_version}${NC}"
            else
                echo "Keeping the current version."
                read -p "Press Enter to exit..." < /dev/tty
                exit 0
            fi
        else
            echo -e "${GREEN}Already on the latest prerelease ${INSTALLED_VERSION}, and no stable version is available to switch to.${NC}"
            read -p "Press Enter to exit..." < /dev/tty
            exit 0
        fi
    else
        if [ -n "$latest_prerelease" ]; then
            stable_num=$(echo "$INSTALLED_VERSION" | sed 's/^v//')
            prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
            higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
            if [ "$higher" = "$prerelease_num" ]; then
                echo -e "${YELLOW}The currently installed version is the stable release ${INSTALLED_VERSION}.${NC}"
                echo -e "${YELLOW}A newer prerelease ${latest_prerelease} is available. Switch to it?${NC}"
                read -n1 -p "Press Enter or A to switch, any other key to keep the current version: " switch_choice < /dev/tty
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_prerelease"
                    echo -e "${GREEN}Switching to the prerelease: ${target_version}${NC}"
                else
                    echo "Keeping the current version."
                    read -p "Press Enter to exit..." < /dev/tty
                    exit 0
                fi
            else
                echo -e "${GREEN}Already on the latest stable release ${INSTALLED_VERSION}.${NC}"
                read -p "Press Enter to exit..." < /dev/tty
                exit 0
            fi
        else
            echo -e "${GREEN}Already on the latest stable release ${INSTALLED_VERSION}, and no prerelease is available.${NC}"
            read -p "Press Enter to exit..." < /dev/tty
            exit 0
        fi
    fi
fi

if [ -z "$target_version" ]; then
    echo -e "${RED}Error: target version not determined.${NC}"
    read -p "Press Enter to exit..." < /dev/tty
    exit 1
fi
echo -e "${GREEN}Target version: ${target_version}${NC}"

echo -e "${CYAN}Creating directories and fixing permissions...${NC}"
if [[ ! -d "$HOMEBREW_DIR" ]]; then
    sudo mkdir -p "$HOMEBREW_DIR"
fi
sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "$HOMEBREW_DIR" 2>/dev/null || true
mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR" 2>/dev/null || {
    sudo mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR"
    sudo chown ${CURRENT_USER}:${CURRENT_USER} "$SERVICE_DIR" "$PLUGIN_DIR"
}

echo -e "${CYAN}Downloading PluginLoader (${target_version}) ...${NC}"
TMP_FILE="${PLUGIN_LOADER}.tmp"
DOWNLOAD_URL="https://github.com/SteamDeckHomebrew/decky-loader/releases/download/${target_version}/PluginLoader"

echo -e "Downloading from github.com ..."
if curl -L --fail --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$TMP_FILE" "$DOWNLOAD_URL" && [ -s "$TMP_FILE" ]; then
    FILE_SIZE=$(stat -c%s "$TMP_FILE" 2>/dev/null || stat -f%z "$TMP_FILE" 2>/dev/null)
    if [[ -n "$FILE_SIZE" ]] && [[ "$FILE_SIZE" -gt 1000000 ]]; then
        echo -e "\n${GREEN}Download successful (size: $((FILE_SIZE/1024/1024)) MB)${NC}"
    else
        echo -e "\n${RED}Downloaded file is invalid (${FILE_SIZE:-0} bytes).${NC}"
        rm -f "$TMP_FILE"
        read -p "Press Enter to exit..." < /dev/tty
        exit 1
    fi
else
    echo -e "\n${RED}Download failed. Please check your network and retry.${NC}"
    rm -f "$TMP_FILE"
    read -p "Press Enter to exit..." < /dev/tty
    exit 1
fi

if [[ -f "$PLUGIN_LOADER" ]]; then
    sudo rm -f "$PLUGIN_LOADER"
fi
mv "$TMP_FILE" "$PLUGIN_LOADER"
chmod +x "$PLUGIN_LOADER"

echo -e "${CYAN}Enabling Steam remote debugging...${NC}"
touch "${HOME_DIR}/.steam/steam/.cef-enable-remote-debugging"
if [[ -d "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/" ]]; then
    touch "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/.cef-enable-remote-debugging"
fi

echo -e "${CYAN}Configuring the systemd service...${NC}"
cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=SteamDeck Plugin Loader
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=deck
Environment="HOMEBREW_FOLDER=${HOMEBREW_DIR}"
ExecStart=${PLUGIN_LOADER}
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

sudo cp "$SERVICE_FILE" "$SERVICE_DEST"
sudo systemctl daemon-reload
sudo systemctl enable plugin_loader
sudo systemctl restart plugin_loader

echo ""
echo -e "${GREEN}✅ Decky Loader ${target_version} installed successfully!${NC}"
echo "Service status:"
systemctl status plugin_loader --no-pager

echo -e "${YELLOW}Switch back to Game Mode and press the '...' button to open the sidebar and check whether the plugin store appears.${NC}"

read -p "Press Enter to exit..." < /dev/tty
exit 0
