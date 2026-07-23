#!/bin/bash
VERSION="1.3.9"

rm -f /home/deck/steamdeck_toolbox.sh
rm -f /home/deck/Desktop/SteamDeck工具箱.desktop

TOOLBOX_URL="https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_gui.py"
TOOLBOX_NAME="$HOME/steamdeck_gui.py"
ICON_DIR="$HOME/emoji_icons"
REPO_ZIP_URL="https://gitee.com/Zhucy2100/steamdeck_toolbox/repository/archive/master.zip"
TEMP_ZIP="/tmp/steamdeck_toolbox_master.zip"
TEMP_EXTRACT="/tmp/steamdeck_toolbox_extract"

echo "正在检查系统只读状态..."
sudo steamos-readonly disable 2>/dev/null || true

if pacman -Q vte3 &> /dev/null; then
    echo "✅ vte3 已安装。"
else
    echo "未找到 vte3（终端组件），正在尝试安装..."
    if [ ! -f /etc/pacman.d/gnupg/pubring.gpg ]; then
        echo "正在初始化 Pacman 密钥..."
        sudo pacman-key --init
        sudo pacman-key --populate archlinux
    fi
    if sudo pacman -S --noconfirm vte3; then
        echo "✅ vte3 安装成功！"
    else
        echo "⚠️ vte3 安装失败，GUI 将使用纯文本模式（功能仍可用）。"
    fi
fi

if ! command -v unzip &> /dev/null; then
    echo "未找到 unzip，正在安装..."
    sudo pacman -S --noconfirm unzip || {
        echo "❌ unzip 安装失败，无法解压 emoji_icons。"
        exit 1
    }
fi

echo "正在准备下载 emoji_icons 文件夹..."

echo "正在下载仓库压缩包..."
if ! curl -L --progress-bar "$REPO_ZIP_URL" -o "$TEMP_ZIP"; then
    echo "❌ 下载仓库压缩包失败，请检查网络。"
    exit 1
fi

rm -rf "$TEMP_EXTRACT"
mkdir -p "$TEMP_EXTRACT"

echo "正在解压..."
if ! unzip -q "$TEMP_ZIP" -d "$TEMP_EXTRACT"; then
    echo "❌ 解压失败，请检查 unzip 是否正常工作。"
    rm -f "$TEMP_ZIP"
    exit 1
fi

EXTRACTED_DIR=$(find "$TEMP_EXTRACT" -maxdepth 1 -type d -name "steamdeck_toolbox-master" | head -1)
if [ -z "$EXTRACTED_DIR" ]; then
    echo "❌ 未找到解压后的仓库目录。"
    rm -rf "$TEMP_EXTRACT" "$TEMP_ZIP"
    exit 1
fi

if [ -d "$ICON_DIR" ]; then
    echo "检测到已存在的 emoji_icons，正在覆盖..."
    rm -rf "$ICON_DIR"
fi

if [ -d "$EXTRACTED_DIR/emoji_icons" ]; then
    cp -r "$EXTRACTED_DIR/emoji_icons" "$ICON_DIR"
    echo "✅ emoji_icons 文件夹已下载到 $ICON_DIR"
else
    echo "❌ 仓库中未找到 emoji_icons 文件夹。"
    rm -rf "$TEMP_EXTRACT" "$TEMP_ZIP"
    exit 1
fi

rm -rf "$TEMP_EXTRACT" "$TEMP_ZIP"

echo "正在从 Gitee 下载 Steam Deck GUI 工具箱..."

if curl -L --progress-bar "$TOOLBOX_URL" -o "$TOOLBOX_NAME"; then
    chmod +x "$TOOLBOX_NAME"
    echo "下载完成，正在启动..."
    exec python3 "$TOOLBOX_NAME"
else
    echo "❌ 下载失败，请检查网络后重试"
    exit 1
fi