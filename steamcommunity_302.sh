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
    echo -e "${CYAN}            Steam社区302 安装/卸载工具 v$VERSION           ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
}

install_steamcommunity_302() {
    show_header
    echo -e "${YELLOW}════════════════ 安装Steam社区302 ════════════════${NC}"
    echo ""

    echo -e "${CYAN}正在准备安装Steam社区302工具...${NC}"
    echo "该工具用于解决Steam社区访问问题。"
    echo ""

    local install_dir="$HOME/SteamCommunity302"
    local install_dir2="$HOME/Steamcommunity_302"
    local desktop_file="$DESKTOP_DIR/Steamcommunity-302.desktop"

    local installed=false
    if [ -d "$install_dir" ] || [ -d "$install_dir2" ] || [ -f "$desktop_file" ]; then
        installed=true
    fi

    if [ "$installed" = true ]; then
        echo -e "${GREEN}检测到可能已安装Steam社区302${NC}"
        echo ""
        echo "请选择要执行的操作："
        echo "1. 重新安装Steam社区302"
        echo "2. 卸载Steam社区302"
        echo "3. 退出"
        echo ""

        read -p "请输入选择 [1-3]: " choice < /dev/tty

        case $choice in
            1)
                echo "开始重新安装Steam社区302..."
                echo "正在清理旧版本..."
                if [ -d "$install_dir" ]; then
                    rm -rf "$install_dir"
                    echo -e "${GREEN}✓ 已删除安装目录: $install_dir${NC}"
                fi
                if [ -d "$install_dir2" ]; then
                    rm -rf "$install_dir2"
                    echo -e "${GREEN}✓ 已删除安装目录: $install_dir2${NC}"
                fi
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 已删除桌面快捷方式${NC}"
                fi
                echo -e "${GREEN}✓ 旧版本清理完成，开始新安装${NC}"
                echo ""
                ;;
            2)
                echo "正在卸载Steam社区302..."
                if [ -d "$install_dir" ]; then
                    rm -rf "$install_dir"
                    echo -e "${GREEN}✓ 已删除安装目录: $install_dir${NC}"
                fi
                if [ -d "$install_dir2" ]; then
                    rm -rf "$install_dir2"
                    echo -e "${GREEN}✓ 已删除安装目录: $install_dir2${NC}"
                fi
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 已删除桌面快捷方式${NC}"
                fi
                echo -e "${GREEN}✓ Steam社区302已卸载完成${NC}"
                read -p "按回车键退出..." < /dev/tty
                exit 0
                ;;
            3)
                echo "退出。"
                read -p "按回车键退出..." < /dev/tty
                exit 0
                ;;
            *)
                echo "无效选择，退出。"
                read -p "按回车键退出..." < /dev/tty
                exit 1
                ;;
        esac
    fi

    echo "即将下载并安装Steam社区302工具..."
    echo "该工具需要从dogfight360.com下载。"
    echo ""

    read -p "是否继续安装？(y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消。"
        read -p "按回车键退出..." < /dev/tty
        exit 0
    fi

    echo ""
    echo -e "${CYAN}开始安装Steam社区302...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    mkdir -p "$install_dir"
    cd "$install_dir"

    echo "步骤1: 下载Steam社区302工具..."
    echo "下载地址: https://www.dogfight360.com/blog/wp-content/uploads/2025/12/steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"
    echo ""

    if ! command -v wget &> /dev/null; then
        echo -e "${YELLOW}未找到wget，正在尝试安装...${NC}"
        sudo pacman -S --noconfirm wget 2>/dev/null || {
            echo -e "${RED}无法安装wget，请手动安装后再试。${NC}"
            echo "安装命令: sudo pacman -S wget"
            read -p "按回车键退出..." < /dev/tty
            exit 1
        }
    fi

    local download_url="https://www.dogfight360.com/blog/wp-content/uploads/2025/12/steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"
    local filename="steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"

    echo "正在下载文件..."
    wget --show-progress "$download_url"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 下载失败，请检查网络连接${NC}"
        echo "可以尝试手动下载后放置到 $install_dir 目录"
        read -p "按回车键退出..." < /dev/tty
        exit 1
    fi

    echo -e "${GREEN}✓ 下载完成${NC}"
    echo ""

    echo "步骤2: 解压文件..."
    tar -xzf "$filename"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 解压失败${NC}"
        read -p "按回车键退出..." < /dev/tty
        exit 1
    fi

    echo -e "${GREEN}✓ 解压完成${NC}"
    echo ""

    rm -f "$filename"
    echo "步骤3: 清理压缩包..."
    echo -e "${GREEN}✓ 已清理压缩包${NC}"
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
            echo -e "${RED}✗ 找不到解压后的文件${NC}"
            read -p "按回车键退出..." < /dev/tty
            exit 1
        fi
    fi

    cd "$extracted_dir"
    local extracted_path="$(pwd)"
    echo "步骤4: 文件位置: $extracted_path"
    echo -e "${GREEN}✓ 文件准备就绪${NC}"
    echo ""

    echo "步骤5: 设置执行权限..."
    [ -f "Steamcommunity_302" ] && chmod +x "Steamcommunity_302"
    [ -f "steamcommunity_302" ] && chmod +x "steamcommunity_302"
    [ -f "steamcommunity_302.cli" ] && chmod +x "steamcommunity_302.cli"
    [ -f "steamcommunity_302.caddy" ] && chmod +x "steamcommunity_302.caddy"
    echo -e "${GREEN}✓ 已设置执行权限${NC}"
    echo ""

    echo "步骤6: 创建运行脚本..."
    local run_script="run运行.sh"
    cat > "$run_script" << 'EOF'
#!/bin/bash
clear
echo ""
[ -f "Steamcommunity_302" ] && sudo ./Steamcommunity_302
[ -f "steamcommunity_302" ] && sudo ./steamcommunity_302
EOF

    chmod +x "$run_script"
    echo -e "${GREEN}✓ 运行脚本已创建: $run_script${NC}"
    echo ""

    echo "步骤7: 创建桌面快捷方式..."

    local steam_icon="applications-internet"
    if [ -f "/usr/share/icons/hicolor/48x48/apps/steam.png" ]; then
        steam_icon="steam"
    fi

    cat > "$desktop_file" << EOF
[Desktop Entry]
Name=Steamcommunity 302
Comment=Steam社区302访问工具
Exec=$extracted_path/$run_script
Terminal=true
Type=Application
Categories=Network;Utility;
Icon=$steam_icon
Path=$extracted_path
EOF

    chmod +x "$desktop_file"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    echo ""

    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ Steam社区302 安装完成！${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW}使用说明：${NC}"
    echo "1. 双击桌面上的 'Steamcommunity 302' 图标启动程序"
    echo "2. 首次使用时，请进入设置保存设置后再启动服务"
    echo "3. 运行程序需要管理员权限，首次运行时需要输入密码"
    echo ""
    echo -e "${YELLOW}文件位置：${NC}"
    echo "安装目录: $install_dir"
    echo "运行脚本: $extracted_path/$run_script"
    echo "桌面快捷方式: $desktop_file"
    echo ""
    echo -e "${YELLOW}注意：${NC}"
    echo "1. 本工具安装在 $install_dir 目录"
    echo "2. 如需卸载，请重新运行此脚本并选择卸载选项"
    echo "3. 卸载时会同时清理桌面快捷方式和安装文件"
    echo ""

    read -p "按回车键退出..." < /dev/tty
    exit 0
}

install_steamcommunity_302
