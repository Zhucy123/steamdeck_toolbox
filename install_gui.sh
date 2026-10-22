#!/bin/bash

TOOLBOX_URL="https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/steamdeck_gui.py"
TOOLBOX_NAME="$HOME/steamdeck_gui.py"

# Automatically restore SteamOS read-only mode when the script exits (including on error),
# so that system updates are not affected.
cleanup() {
    if command -v steamos-readonly &>/dev/null; then
        if sudo -n steamos-readonly status 2>/dev/null | grep -q "disabled"; then
            if sudo -n steamos-readonly enable 2>/dev/null; then
                echo "✅ Read-only mode restored"
            else
                echo "⚠️ Please run manually: sudo steamos-readonly enable"
            fi
        fi
    fi
}
trap cleanup EXIT

echo "Checking system read-only status..."
sudo steamos-readonly disable 2>/dev/null || true

if pacman -Q vte3 &> /dev/null; then
    echo "✅ vte3 is already installed."
else
    echo "vte3 (terminal component) not found, attempting to install..."
    # Note: SteamOS uses both the archlinux and holo keyrings.
    # 889B5EBD... belongs to holo-keyring. When only archlinux is populated, that key
    # is not imported and the later --lsign-key necessarily reports "unable to sign
    # locally", so both keyrings must be populated.
    if [ ! -f /etc/pacman.d/gnupg/pubring.gpg ]; then
        echo "Initializing Pacman keys..."
        sudo pacman-key --init || {
            echo "❌ Failed to initialize the pacman keyring, cannot install vte3."
            exit 1
        }
    fi
    sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null || true
    sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null || true
    echo "Populating official Arch and SteamOS Holo keys..."
    sudo pacman-key --populate archlinux || {
        echo "❌ Failed to populate the archlinux keyring."
        exit 1
    }
    if [ -f /usr/share/pacman/keyrings/holo.gpg ]; then
        sudo pacman-key --populate holo || {
            echo "❌ Failed to populate the holo keyring."
            exit 1
        }
    fi
    echo "Trusting the SteamOS packager key..."
    if ! sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF; then
        echo "⚠️ Key signing failed, refreshing keyrings and retrying..."
        sudo pacman-key --refresh-keys 2>/dev/null || true
        sudo pacman-key --populate archlinux holo 2>/dev/null || true
        sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || {
            echo "❌ Key signing still failed, cannot install vte3."
            echo "   You can try manually: sudo pacman-key --init && sudo pacman-key --populate archlinux holo"
            exit 1
        }
    fi
    sudo pacman -Sy --noconfirm 2>/dev/null || true
    if sudo pacman -S --needed --noconfirm vte3; then
        echo "✅ vte3 installed successfully!"
    else
        echo "⚠️ vte3 installation failed. The GUI will use plain-text mode (features still work)."
    fi
fi

echo "Downloading the Steam Deck GUI toolbox from GitHub..."

if curl -L --progress-bar "$TOOLBOX_URL" -o "$TOOLBOX_NAME"; then
    # Validate the downloaded content to avoid an error page or an incomplete file
    if ! grep -q 'BASH_SCRIPT = ' "$TOOLBOX_NAME" || ! grep -q '^VERSION = ' "$TOOLBOX_NAME"; then
        echo "❌ Download validation failed (not a valid toolbox script). Please check your network and retry."
        rm -f "$TOOLBOX_NAME"
        exit 1
    fi
    chmod +x "$TOOLBOX_NAME"
    echo "Download complete!"
    echo "✅ Installation successful!"
    echo ""

    DESKTOP_FILE="$HOME/Desktop/Deck Toolbox.desktop"
    if [ -f "$DESKTOP_FILE" ]; then
        echo "Desktop shortcut already exists."
    else
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Deck Toolbox
Exec=$(command -v python3) "$TOOLBOX_NAME"
Icon=input-gamepad-symbolic
Terminal=false
StartupNotify=true
Categories=Utility;
EOF
        chmod +x "$DESKTOP_FILE"
        echo "✅ Desktop shortcut created: Deck Toolbox.desktop"
    fi

    echo "Click or double-click the 'Deck Toolbox' icon on the desktop to launch the program."
    echo ""
    exit 0
else
    echo "❌ Download failed. Please check your network and retry."
    exit 1
fi
