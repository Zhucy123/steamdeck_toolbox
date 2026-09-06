#!/bin/bash
# ============================================================================
# Decky Loader (插件商店) 安装/更新脚本
# 参考 steamdeck_gui 的 install_plugin_store 流程重写：
#   - 版本逻辑：正式版/预发布版区分与选择、已安装版本智能切换
#   - 下载：交互式镜像选择（与原程序 download_with_mirrors 一致）
#   - 严格模式：set -uo pipefail（不用 set -e，避免 (( )) 算术值 0 触发意外退出）
#   - 交互 read 统一 < /dev/tty
#   - 文件大小校验
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

MIRRORS=(
    "gh.ddlc.top"
    "ghproxy.net"
    "mirror.ghproxy.com"
    "github.com"
)
DOWNLOAD_TIMEOUT=60

for cmd in curl python3 systemctl sudo journalctl stat; do
    if ! command -v $cmd &> /dev/null; then
        echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
        read -p "按回车键退出..." < /dev/tty
        exit 1
    fi
done

echo -e "${CYAN}正在获取 Decky Loader 版本信息...${NC}"
releases_json=$(curl -s --connect-timeout 15 --max-time 30 "https://api.github.com/repos/SteamDeckHomebrew/decky-loader/releases")
if [ -z "$releases_json" ]; then
    echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
    read -p "按回车键退出..." < /dev/tty
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
    echo -e "${RED}错误: 无法解析版本信息。${NC}"
    read -p "按回车键退出..." < /dev/tty
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
        echo -e "${CYAN}当前已安装版本: ${INSTALLED_VERSION}${NC}"
    else
        echo -e "${YELLOW}已安装但无法获取版本，将重新安装。${NC}"
    fi
else
    echo -e "${YELLOW}未检测到现有安装。${NC}"
fi

options=()
labels=()
if [ -n "$latest_stable" ]; then
    options+=("$latest_stable")
    labels+=("正式版 $latest_stable")
fi
if [ -n "$latest_prerelease" ]; then
    options+=("$latest_prerelease")
    labels+=("预发布版 $latest_prerelease")
fi
if [ ${#options[@]} -eq 0 ]; then
    echo -e "${RED}错误: 未找到任何可用版本。${NC}"
    read -p "按回车键退出..." < /dev/tty
    exit 1
fi

target_version=""

if [ -z "$INSTALLED_VERSION" ]; then
    while true; do
        if [ ${#options[@]} -eq 1 ]; then
            target_version="${options[0]}"
            echo -e "${GREEN}将安装唯一版本: ${target_version}${NC}"
            break
        else
            echo "请选择要安装的版本："
            for i in "${!options[@]}"; do
                echo "$((i+1))) ${labels[$i]}"
            done
            read -p "请输入选择 [1-${#options[@]}]: " choice < /dev/tty
            if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#options[@]} ]; then
                target_version="${options[$((choice-1))]}"
                break
            else
                echo -e "${RED}无效选择，请重新输入。${NC}"
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
            echo -e "${YELLOW}当前已安装预发布版 ${INSTALLED_VERSION}。${NC}"
            echo -e "${YELLOW}是否切换为正式版 ${latest_stable}？${NC}"
            read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice < /dev/tty
            echo
            if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                target_version="$latest_stable"
                echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
            else
                echo "保持当前版本。"
                read -p "按回车键退出..." < /dev/tty
                exit 0
            fi
        else
            echo -e "${GREEN}已是最新预发布版 ${INSTALLED_VERSION}，且没有正式版可切换。${NC}"
            read -p "按回车键退出..." < /dev/tty
            exit 0
        fi
    else
        if [ -n "$latest_prerelease" ]; then
            stable_num=$(echo "$INSTALLED_VERSION" | sed 's/^v//')
            prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
            higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
            if [ "$higher" = "$prerelease_num" ]; then
                echo -e "${YELLOW}当前已安装正式版 ${INSTALLED_VERSION}。${NC}"
                echo -e "${YELLOW}发现更高预发布版 ${latest_prerelease}，是否切换？${NC}"
                read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice < /dev/tty
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_prerelease"
                    echo -e "${GREEN}将切换至预发布版: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    read -p "按回车键退出..." < /dev/tty
                    exit 0
                fi
            else
                echo -e "${GREEN}已是最新正式版 ${INSTALLED_VERSION}。${NC}"
                read -p "按回车键退出..." < /dev/tty
                exit 0
            fi
        else
            echo -e "${GREEN}已是最新正式版 ${INSTALLED_VERSION}，且没有预发布版。${NC}"
            read -p "按回车键退出..." < /dev/tty
            exit 0
        fi
    fi
fi

if [ -z "$target_version" ]; then
    echo -e "${RED}错误: 未确定目标版本。${NC}"
    read -p "按回车键退出..." < /dev/tty
    exit 1
fi
echo -e "${GREEN}目标版本: ${target_version}${NC}"

echo -e "${CYAN}创建目录并修复权限...${NC}"
if [[ ! -d "$HOMEBREW_DIR" ]]; then
    sudo mkdir -p "$HOMEBREW_DIR"
fi
sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "$HOMEBREW_DIR" 2>/dev/null || true
mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR" 2>/dev/null || {
    sudo mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR"
    sudo chown ${CURRENT_USER}:${CURRENT_USER} "$SERVICE_DIR" "$PLUGIN_DIR"
}

echo -e "${CYAN}开始下载 PluginLoader (${target_version}) ...${NC}"
TMP_FILE="${PLUGIN_LOADER}.tmp"
DOWNLOAD_URL="https://github.com/SteamDeckHomebrew/decky-loader/releases/download/${target_version}/PluginLoader"

DOWNLOAD_SUCCESS=false
while [ "$DOWNLOAD_SUCCESS" != "true" ]; do
    clear
    echo -e "${CYAN}下载 PluginLoader${NC}\n"
    echo "请选择下载镜像源（输入编号，0 取消）："
    for i in "${!MIRRORS[@]}"; do
        echo "  $((i+1)). ${MIRRORS[$i]}"
    done
    read -p "请输入选择: " mirror_choice < /dev/tty
    [[ -z "$mirror_choice" ]] && echo -e "${RED}输入无效${NC}" && sleep 1 && continue
    [[ "$mirror_choice" == "0" ]] && echo "操作已取消。" && read -p "按回车键退出..." < /dev/tty && exit 1
    if [[ "$mirror_choice" =~ ^[0-9]+$ ]] && [ "$mirror_choice" -ge 1 ] && [ "$mirror_choice" -le ${#MIRRORS[@]} ]; then
        mirror="${MIRRORS[$((mirror_choice-1))]}"
        if [[ "$mirror" == "github.com" ]]; then
            FULL_URL="https://github.com/${DOWNLOAD_URL#https://github.com/}"
        else
            FULL_URL="https://${mirror}/${DOWNLOAD_URL}"
        fi
        echo -e "尝试从 ${mirror} 下载..."
        if curl -L --fail --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$TMP_FILE" "$FULL_URL" && [ -s "$TMP_FILE" ]; then
            FILE_SIZE=$(stat -c%s "$TMP_FILE" 2>/dev/null || stat -f%z "$TMP_FILE" 2>/dev/null)
            if [[ -n "$FILE_SIZE" ]] && [[ "$FILE_SIZE" -gt 1000000 ]]; then
                echo -e "\n${GREEN}下载成功 (大小: $((FILE_SIZE/1024/1024)) MB)${NC}"
                DOWNLOAD_SUCCESS=true
            else
                echo -e "\n${RED}下载文件无效 (${FILE_SIZE:-0} 字节)，请重新选择镜像源。${NC}"
                rm -f "$TMP_FILE"
                sleep 1
            fi
        else
            echo -e "\n${RED}下载失败，请重新选择镜像源。${NC}"
            rm -f "$TMP_FILE"
            sleep 1
        fi
    else
        echo -e "${RED}无效编号，请重新输入。${NC}"
        sleep 1
    fi
done

if [[ -f "$PLUGIN_LOADER" ]]; then
    sudo rm -f "$PLUGIN_LOADER"
fi
mv "$TMP_FILE" "$PLUGIN_LOADER"
chmod +x "$PLUGIN_LOADER"

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
echo -e "${GREEN}✅ Decky Loader ${target_version} 安装完成！${NC}"
echo "服务状态："
systemctl status plugin_loader --no-pager

echo -e "${YELLOW}请切换回游戏模式，按 '...' 键打开侧边栏检查插件商店是否出现。${NC}"

read -p "按回车键退出..." < /dev/tty
exit 0
