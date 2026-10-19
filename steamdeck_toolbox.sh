#!/bin/bash
VERSION="1.3.9"

rm -f /home/deck/steamdeck_toolbox.sh
rm -f /home/deck/Desktop/SteamDeck工具箱.desktop

TOOLBOX_URL="https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_gui.py"
TOOLBOX_NAME="$HOME/steamdeck_gui.py"

echo "正在检查系统只读状态..."
sudo steamos-readonly disable 2>/dev/null || true

if pacman -Q vte3 &> /dev/null; then
    echo "✅ vte3 已安装。"
else
    echo "未找到 vte3（终端组件），正在尝试安装..."
    # 注意：SteamOS 同时使用 archlinux 与 holo 两个钥匙环。
    # 889B5EBD... 属于 holo-keyring，只 populate archlinux 时该密钥不会被导入，
    # 后续 --lsign-key 必然报“无法在本地签署”，因此两个钥匙环都必须导入。
    if [ ! -f /etc/pacman.d/gnupg/pubring.gpg ]; then
        echo "正在初始化 Pacman 密钥..."
        sudo pacman-key --init || {
            echo "❌ pacman keyring 初始化失败，无法安装 vte3。"
            exit 1
        }
    fi
    sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null || true
    sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null || true
    echo "正在填充 Arch 官方与 SteamOS Holo 密钥..."
    sudo pacman-key --populate archlinux || {
        echo "❌ archlinux 钥匙环填充失败。"
        exit 1
    }
    if [ -f /usr/share/pacman/keyrings/holo.gpg ]; then
        sudo pacman-key --populate holo || {
            echo "❌ holo 钥匙环填充失败。"
            exit 1
        }
    fi
    echo "正在信任 SteamOS 打包者密钥..."
    if ! sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF; then
        echo "⚠️ 密钥签署失败，刷新钥匙环后重试..."
        sudo pacman-key --refresh-keys 2>/dev/null || true
        sudo pacman-key --populate archlinux holo 2>/dev/null || true
        sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || {
            echo "❌ 密钥签署仍失败，无法安装 vte3。"
            echo "   可尝试手动执行: sudo pacman-key --init && sudo pacman-key --populate archlinux holo"
            exit 1
        }
    fi
    sudo pacman -Sy --noconfirm 2>/dev/null || true
    if sudo pacman -S --needed --noconfirm vte3; then
        echo "✅ vte3 安装成功！"
    else
        echo "⚠️ vte3 安装失败，GUI 将使用纯文本模式（功能仍可用）。"
    fi
fi

echo "正在从 Gitee 下载 Steam Deck GUI 工具箱..."

if curl -L --progress-bar "$TOOLBOX_URL" -o "$TOOLBOX_NAME"; then
    chmod +x "$TOOLBOX_NAME"
    echo "下载完成，正在启动..."
    exec python3 "$TOOLBOX_NAME"
else
    echo "❌ 下载失败，请检查网络后重试"
    exit 1
fi
