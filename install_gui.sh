#!/bin/bash

TOOLBOX_URL="https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/steamdeck_gui.py"
TOOLBOX_NAME="$HOME/steamdeck_gui.py"

# 脚本退出（含出错）时自动恢复 SteamOS 只读模式，避免系统更新受影响
cleanup() {
    if command -v steamos-readonly &>/dev/null; then
        if sudo -n steamos-readonly status 2>/dev/null | grep -q "disabled"; then
            if sudo -n steamos-readonly enable 2>/dev/null; then
                echo "✅ 已恢复只读模式"
            else
                echo "⚠️ 请手动执行: sudo steamos-readonly enable"
            fi
        fi
    fi
}
trap cleanup EXIT

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
    # 下载内容校验，防止拿到错误页/不完整文件
    if ! grep -q 'BASH_SCRIPT = ' "$TOOLBOX_NAME" || ! grep -q '^VERSION = ' "$TOOLBOX_NAME"; then
        echo "❌ 下载内容校验失败（不是有效的工具箱脚本），请检查网络后重试"
        rm -f "$TOOLBOX_NAME"
        exit 1
    fi
    chmod +x "$TOOLBOX_NAME"
    echo "下载完成！"
    echo "✅ 安装成功！"
    echo ""

    DESKTOP_FILE="$HOME/Desktop/Deck工具箱.desktop"
    if [ -f "$DESKTOP_FILE" ]; then
        echo "桌面快捷方式已存在。"
    else
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Deck工具箱
Exec=$(command -v python3) "$TOOLBOX_NAME"
Icon=input-gamepad-symbolic
Terminal=false
StartupNotify=true
Categories=Utility;
EOF
        chmod +x "$DESKTOP_FILE"
        echo "✅ 已创建桌面快捷方式：Deck工具箱.desktop"
    fi

    echo "请单击或双击桌面上的 'Deck工具箱' 图标来启动程序。"
    echo ""
    exit 0
else
    echo "❌ 下载失败，请检查网络后重试"
    exit 1
fi
