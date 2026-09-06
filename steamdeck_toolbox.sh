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
    if [ ! -f /etc/pacman.d/gnupg/pubring.gpg ]; then
        echo "正在初始化 Pacman 密钥..."
        sudo pacman-key --init || {
            echo "❌ pacman keyring 初始化失败，无法安装 vte3。"
            exit 1
        }
        echo "正在填充 Arch Linux 官方密钥..."
        sudo pacman-key --populate archlinux || {
            echo "❌ pacman keyring 填充失败。"
            exit 1
        }
    fi
    echo "正在信任 SteamOS 打包者密钥..."
    if ! sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF; then
        echo "⚠️ 密钥签署失败，正在修复 keyring 权限并重试..."
        sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null || true
        sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null || true
        sudo pacman-key --init
        sudo pacman-key --populate archlinux
        sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || {
            echo "❌ 密钥签署仍失败，无法安装 vte3。"
            echo "   可尝试手动执行: sudo pacman-key --init && sudo pacman-key --populate archlinux"
            exit 1
        }
    fi
    if sudo pacman -S --noconfirm vte3; then
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
