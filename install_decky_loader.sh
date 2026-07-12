#!/bin/bash

set -e

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

MIRRORS=(
    "https://gh.ddlc.top/"
    "https://ghproxy.net/"
    "https://mirror.ghproxy.com/"
    "https://gh.api.99988866.xyz/"
    "https://download.fastgit.org/"
    "https://hub.gitmirror.com/"
    "https://git.xfj0.xyz/"
    "https://github.com/"
)
DOWNLOAD_TIMEOUT=60
MAX_RETRY_PER_MIRROR=1

for cmd in curl python3 systemctl sudo journalctl stat; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
        read -p "按回车键退出..."
        exit 1
    fi
done

echo -e "${CYAN}正在获取 Decky Loader 最新版本...${NC}"
LATEST_VERSION=$(curl -s "https://api.github.com/repos/SteamDeckHomebrew/decky-loader/releases" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tag = data[0]['tag_name']
    if tag.startswith('v'):
        tag = tag[1:]
    print(tag)
except:
    print('')
")
if [[ -z "$LATEST_VERSION" ]]; then
    echo -e "${RED}错误: 无法获取最新版本号，请检查网络。${NC}"
    read -p "按回车键退出..."
    exit 1
fi
echo -e "${GREEN}最新版本: ${LATEST_VERSION}${NC}"

INSTALLED_VERSION=""
if [[ -f "$PLUGIN_LOADER" && -x "$PLUGIN_LOADER" ]]; then
    INSTALLED_VERSION=$(sudo journalctl -u plugin_loader --no-pager 2>/dev/null | grep -i "Starting Decky version" | tail -1 | grep -oP 'version v?\K[0-9.]+(-pre[0-9]+)?')
    if [[ -z "$INSTALLED_VERSION" ]]; then
        INSTALLED_VERSION=$("$PLUGIN_LOADER" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+(-pre\d+)?')
    fi
fi

if [[ -n "$INSTALLED_VERSION" ]]; then
    echo -e "${CYAN}已安装版本: ${INSTALLED_VERSION}${NC}"
    if [[ "$INSTALLED_VERSION" == "$LATEST_VERSION" ]]; then
        echo -e "${GREEN}✅ 已是最新版本，无需安装。${NC}"
        read -p "按回车键退出..."
        exit 0
    else
        echo -e "${YELLOW}发现新版本，将进行更新安装...${NC}"
    fi
else
    echo -e "${YELLOW}未检测到现有安装，将进行全新安装。${NC}"
fi

echo -e "${CYAN}创建目录并修复权限...${NC}"
if [[ ! -d "$HOMEBREW_DIR" ]]; then
    sudo mkdir -p "$HOMEBREW_DIR"
fi
sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "$HOMEBREW_DIR" 2>/dev/null || true
mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR" 2>/dev/null || {
    sudo mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR"
    sudo chown ${CURRENT_USER}:${CURRENT_USER} "$SERVICE_DIR" "$PLUGIN_DIR"
}

echo -e "${CYAN}开始下载 PluginLoader ...${NC}"
DOWNLOAD_SUCCESS=false
TMP_FILE="${PLUGIN_LOADER}.tmp"
DOWNLOAD_PATH="https://github.com/SteamDeckHomebrew/decky-loader/releases/download/v${LATEST_VERSION}/PluginLoader"

for mirror in "${MIRRORS[@]}"; do
    FULL_URL="${mirror}${DOWNLOAD_PATH}"
    echo -e "尝试从 ${mirror} 下载..."

    retry_count=0
    while [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; do
        if [[ $retry_count -gt 0 ]]; then
            echo -e "${YELLOW}重试下载 (第 ${retry_count} 次重试)...${NC}"
        fi

        curl -L --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$TMP_FILE" "$FULL_URL"
        curl_exit=$?

        if [[ $curl_exit -eq 0 ]] && [[ -f "$TMP_FILE" ]]; then
            FILE_SIZE=$(stat -c%s "$TMP_FILE" 2>/dev/null || stat -f%z "$TMP_FILE" 2>/dev/null)
            if [[ -n "$FILE_SIZE" ]] && [[ "$FILE_SIZE" -gt 1000000 ]]; then
                echo -e "\n${GREEN}下载成功 (大小: $((FILE_SIZE/1024/1024)) MB)${NC}"
                if [[ -f "$PLUGIN_LOADER" ]]; then
                    sudo rm -f "$PLUGIN_LOADER"
                fi
                mv "$TMP_FILE" "$PLUGIN_LOADER"
                chmod +x "$PLUGIN_LOADER"
                DOWNLOAD_SUCCESS=true
                break 2
            else
                echo -e "\n${RED}下载文件无效 (${FILE_SIZE} 字节)，尝试下一个镜像...${NC}"
                rm -f "$TMP_FILE"
                break
            fi
        else
            echo -e "\n${RED}下载失败 (退出码: $curl_exit)${NC}"
            rm -f "$TMP_FILE"
            ((retry_count++))
            if [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; then
                echo "将进行重试..."
                sleep 2
            else
                echo "该镜像重试次数用完，切换到下一个镜像。"
            fi
        fi
    done

    if [[ "$DOWNLOAD_SUCCESS" == "true" ]]; then
        break
    fi
done

if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
    echo -e "${RED}所有镜像均下载失败，安装中止。${NC}"
    read -p "按回车键退出..."
    exit 1
fi

echo -e "${CYAN}启用 Steam 远程调试...${NC}"
touch "${HOME_DIR}/.steam/steam/.cef-enable-remote-debugging"
if [[ -d "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/" ]]; then
    touch "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/.cef-enable-remote-debugging"
fi

echo -e "${CYAN}配置 systemd 服务...${NC}"
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
echo -e "${GREEN}✅ Decky Loader ${LATEST_VERSION} 安装完成！${NC}"
echo "服务状态："
systemctl status plugin_loader --no-pager

echo -e "${YELLOW}请切换回游戏模式，按 '...' 键打开侧边栏检查插件商店是否出现。${NC}"

read -p "按回车键退出..."
exit 0