#!/bin/bash
VERSION="1.3.9"

rm -f /home/deck/steamdeck_toolbox.sh
rm -f "/home/deck/Desktop/SteamDeck Toolbox.desktop"

TOOLBOX_URL="https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/steamdeck_gui.py"
TOOLBOX_NAME="$HOME/steamdeck_gui.py"

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
    chmod +x "$TOOLBOX_NAME"
    echo "Download complete, launching..."
    exec python3 "$TOOLBOX_NAME"
else
    echo "❌ Download failed. Please check your network and retry."
    exit 1
fi
