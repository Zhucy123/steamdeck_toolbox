#!/bin/bash
trap 'echo -e "\n${YELLOW}用户取消操作，退出工具箱。${NC}"; exit 0' INT TERM

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

INSTALL_DIR="$HOME/Applications"
DESKTOP_DIR="$HOME/Desktop"
BACKUP_DIR="$HOME/backups"
TEMP_DIR="/tmp/steamdeck_toolbox"
MAIN_LAUNCHER="$DESKTOP_DIR/SteamDeck工具箱.desktop"
SCRIPT_PATH="$(realpath "$0")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
SCRIPT_NAME="$(basename "$SCRIPT_PATH")"

VERSION="1.3.1"
REPO_URL="https://gitee.com/Zhucy2100/steamdeck_toolbox"

SYSTEM_TYPE=""

auto_update_check() {
    local temp_dir="/tmp/steamdeck_toolbox_update"
    local target_script="/home/deck/steamdeck_toolbox.sh"

    echo -e "${CYAN}正在检查工具箱更新...${NC}"

    rm -rf "$temp_dir"

    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}未找到 git，尝试安装...${NC}"
        sudo pacman -Sy --noconfirm git &> /dev/null || {
            echo -e "${RED}无法安装 git，跳过更新检查${NC}"
            return 1
        }
    fi

    if ! git clone --depth=1 "$REPO_URL" "$temp_dir" &> /dev/null; then
        echo -e "${YELLOW}⚠ 无法连接仓库，跳过更新检查。${NC}"
        rm -rf "$temp_dir"
        return 1
    fi

    local remote_script="$temp_dir/steamdeck_toolbox.sh"
    if [ ! -f "$remote_script" ]; then
        echo -e "${YELLOW}⚠ 远程仓库中未找到脚本文件，跳过更新。${NC}"
        rm -rf "$temp_dir"
        return 1
    fi

    local remote_version=$(grep -E '^VERSION="[0-9]+\.[0-9]+\.[0-9]+"' "$remote_script" | head -1 | sed -E 's/VERSION="([0-9]+\.[0-9]+\.[0-9]+)"/\1/')
    if [ -z "$remote_version" ]; then
        remote_version=$(grep -E 'VERSION="[0-9]+\.[0-9]+\.[0-9]+"' "$remote_script" | head -1 | sed -E 's/.*VERSION="([0-9]+\.[0-9]+\.[0-9]+)".*/\1/')
    fi

    if [ -z "$remote_version" ]; then
        echo -e "${YELLOW}⚠ 无法解析远程版本号，跳过更新。${NC}"
        rm -rf "$temp_dir"
        return 1
    fi

    if [ "$remote_version" = "$VERSION" ]; then
        echo -e "${GREEN}✓ 已是最新版本${NC}"
        rm -rf "$temp_dir"
        sleep 1
        return 0
    fi

    echo -e "${YELLOW}发现新版本: ${remote_version} (当前版本: ${VERSION})${NC}"
    echo -e "${CYAN}正在自动更新...${NC}"

    local backup_script="${SCRIPT_PATH}.bak"
    cp "$SCRIPT_PATH" "$backup_script" 2>/dev/null

    if cp "$remote_script" "$SCRIPT_PATH"; then
        chmod +x "$SCRIPT_PATH"
        echo -e "${GREEN}✓ 当前脚本已更新${NC}"
    else
        echo -e "${RED}✗ 更新当前脚本失败，尝试恢复备份...${NC}"
        [ -f "$backup_script" ] && cp "$backup_script" "$SCRIPT_PATH"
        rm -rf "$temp_dir"
        echo -e "${YELLOW}按回车键继续使用当前版本...${NC}"
        read -p "" < /dev/tty
        return 1
    fi

    if [ "$SCRIPT_PATH" != "$target_script" ]; then
        if cp "$remote_script" "$target_script"; then
            chmod +x "$target_script"
            echo -e "${GREEN}✓ 已同步更新到 $target_script${NC}"
        else
            echo -e "${YELLOW}⚠ 无法写入 $target_script，请检查权限${NC}"
        fi
    fi

    rm -rf "$temp_dir"

    echo ""
    echo -e "${GREEN}工具箱已从 v$VERSION 更新至 v$remote_version${NC}"
    echo -e "${YELLOW}请重启工具箱以使更新生效。${NC}"
    echo -e "${YELLOW}按回车键关闭本窗口，然后重新打开工具箱。${NC}"
    read -p "" < /dev/tty
    exit 0
}

init_dirs() {
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$TEMP_DIR"
}

detect_system_type() {
    local has_clover=0

    if [ -d "/boot/efi/EFI/CLOVER" ] || [ -d "/boot/efi/EFI/Clover" ]; then
        has_clover=1
    fi

    if command -v efibootmgr &> /dev/null; then
        if efibootmgr 2>/dev/null | grep -i "CLOVER" &> /dev/null; then
            has_clover=1
        fi
    fi

    if [ -f "/boot/efi/EFI/CLOVER/CLOVERX64.efi" ] || \
       [ -f "/boot/efi/EFI/CLOVER/config.plist" ] || \
       [ -f "/boot/efi/EFI/Clover/CLOVERX64.efi" ] || \
       [ -f "/boot/efi/EFI/Clover/config.plist" ]; then
        has_clover=1
    fi

    local has_windows=0
    if [ -d "/boot/efi/EFI/Microsoft" ] || \
       [ -f "/boot/efi/EFI/Microsoft/Boot/bootmgfw.efi" ] || \
       [ -d "/boot/efi/EFI/Boot" ] && [ -f "/boot/efi/EFI/Boot/bootx64.efi" ]; then
        has_windows=1
    fi

    if [ $has_clover -eq 1 ] || [ $has_windows -eq 1 ]; then
        SYSTEM_TYPE="dual"
    else
        SYSTEM_TYPE="single"
    fi

    if [ -z "$SYSTEM_TYPE" ]; then
        local boot_entries=0
        if command -v efibootmgr &> /dev/null; then
            boot_entries=$(efibootmgr 2>/dev/null | grep -c "Boot[0-9A-F][0-9A-F][0-9A-F][0-9A-F]")
            if [ $boot_entries -gt 2 ]; then
                SYSTEM_TYPE="dual"
            else
                SYSTEM_TYPE="single"
            fi
        else
            SYSTEM_TYPE="single"
        fi
    fi
}

show_header() {
    clear
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                     Steam Deck 工具箱 - 版本: $VERSION                               ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

create_desktop_shortcuts() {
    if [ ! -f "$MAIN_LAUNCHER" ]; then
        cat > "$MAIN_LAUNCHER" << EOF
[Desktop Entry]
Type=Application
Name=SteamDeck 工具箱
Comment=Steam Deck 系统优化与软件管理工具 v$VERSION
Exec=konsole -e /bin/bash -c 'cd "$SCRIPT_DIR" && ./"$SCRIPT_NAME" && echo "" && echo "程序执行完毕，按回车键关闭窗口..." && read'
Icon=utilities-terminal
Terminal=false
StartupNotify=true
Categories=Utility;
EOF
        chmod +x "$MAIN_LAUNCHER"
    fi
}

show_main_menu() {
    while true; do
        clear

        echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
        echo -e "${CYAN}                     Steam Deck 工具箱 - 版本: $VERSION                               ${NC}"
        echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""

if [ "$SYSTEM_TYPE" == "dual" ]; then
    echo -e "${GREEN}当前系统: 双系统${NC}"
    echo ""
    echo -e "${CYAN}请选择要执行的功能：${NC}"
    echo ""
echo -e "${GREEN} 1. 关于支持与维护的说明    12. 校准摇杆              23. 清理Steam缓存${NC}"
echo -e "${GREEN} 2. 安装国内源              13. 设置管理员密码        24. 更新已安装应用${NC}"
echo -e "${GREEN} 3. 调整虚拟内存大小        14. 安装AnyDesk           25. 卸载已安装应用${NC}"
echo -e "${GREEN} 4. 修复磁盘写入错误        15. 安装ToDesk            26. 安装小黄鸭软件${NC}"
echo -e "${GREEN} 5. 修复引导                16. 安装WPS Office        27. 安装Steam社区302${NC}"
echo -e "${GREEN} 6. 修复互通盘              17. 安装QQ                28. 安装LSFG-VK插件${NC}"
echo -e "${GREEN} 7. 清理hosts缓存           18. 安装微信              29. 安装Framegen插件${NC}"
echo -e "${GREEN} 8. 安装UU加速器插件        19. 安装QQ音乐            30. 安装/重装Clover引导${NC}"
echo -e "${GREEN} 9. 安装迅游加速器插件      20. 安装百度网盘          31. 远程无法连接点我${NC}"
echo -e "${GREEN}10. 安装ToMoon              21. 安装Edge浏览器${NC}"
echo -e "${GREEN}11. 安装＆卸载插件商店      22. 安装Google浏览器${NC}"
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""

    read -p "请输入选项 (输入1-31的数字): " choice < /dev/tty

    if [[ ! "$choice" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}无效选择，请输入数字！${NC}"
        sleep 1
        continue
    fi

    if [ $choice -lt 1 ] || [ $choice -gt 31 ]; then
        echo -e "${RED}无效选择，请选择1到31之间的数字！${NC}"
        sleep 1
        continue
    fi

    case $choice in
        1) show_about ;;
        2) install_chinese_source ;;
        3) adjust_swap ;;
        4) fix_disk_write_error ;;
        5) fix_boot ;;
        6) fix_shared_disk ;;
        7) clear_hosts_cache ;;
        8) install_uu_accelerator ;;
        9) install_xunyou_accelerator ;;
        10) install_tomoon ;;
        11) install_remove_plugin_store ;;
        12) calibrate_joystick ;;
        13) set_admin_password ;;
        14) install_anydesk ;;
        15) install_todesk ;;
        16) install_wps_office ;;
        17) install_qq ;;
        18) install_wechat ;;
        19) install_qqmusic ;;
        20) install_baidunetdisk ;;
        21) install_edge ;;
        22) install_chrome ;;
        23) steamdeck_cache_manager ;;
        24) update_installed_apps ;;
        25) uninstall_apps ;;
        26) install_yellow_duck_software ;;
        27) install_steamcommunity_302 ;;
        28) install_decky_lsfg_vk ;;
        29) install_decky_framegen ;;
        30) clover_install_or_reinstall ;;
        31) remote_connection_fix ;;
        *)
            echo -e "${RED}无效选择，请重新输入！${NC}"
            sleep 1
            continue
            ;;
    esac
else
    echo -e "${YELLOW}当前系统: 单系统${NC}"
    echo ""
    echo -e "${CYAN}请选择要执行的功能：${NC}"
    echo ""
echo -e "${GREEN} 1. 关于支持与维护的说明  11. 设置管理员密码      21. 清理Steam缓存${NC}"
echo -e "${GREEN} 2. 安装国内源            12. 安装AnyDesk         22. 更新已安装应用${NC}"
echo -e "${GREEN} 3. 调整虚拟内存大小      13. 安装ToDesk          23. 卸载已安装应用${NC}"
echo -e "${GREEN} 4. 修复磁盘写入错误      14. 安装WPS Office      24. 安装小黄鸭软件${NC}"
echo -e "${GREEN} 5. 清理hosts缓存         15. 安装QQ              25. 安装Steam社区302${NC}"
echo -e "${GREEN} 6. 安装UU加速器插件      16. 安装微信            26. 安装LSFG-VK插件${NC}"
echo -e "${GREEN} 7. 安装迅游加速器插件    17. 安装QQ音乐          27. 安装Framegen插件${NC}"
echo -e "${GREEN} 8. 安装ToMoon            18. 安装百度网盘        28. 安装/重装Clover引导${NC}"
echo -e "${GREEN} 9. 安装＆卸载插件商店    19. 安装Edge浏览器      29. 远程无法连接点我${NC}"
echo -e "${GREEN}10. 校准摇杆              20. 安装Google浏览器${NC}"
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""

    read -p "请输入选项 (输入1-29的数字): " choice < /dev/tty

    if [[ ! "$choice" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}无效选择，请输入数字！${NC}"
        sleep 1
        continue
    fi

    if [ $choice -lt 1 ] || [ $choice -gt 29 ]; then
        echo -e "${RED}无效选择，请选择1到29之间的数字！${NC}"
        sleep 1
        continue
    fi

    case $choice in
        1) show_about ;;
        2) install_chinese_source ;;
        3) adjust_swap ;;
        4) fix_disk_write_error ;;
        5) clear_hosts_cache ;;
        6) install_uu_accelerator ;;
        7) install_xunyou_accelerator ;;
        8) install_tomoon ;;
        9) install_remove_plugin_store ;;
        10) calibrate_joystick ;;
        11) set_admin_password ;;
        12) install_anydesk ;;
        13) install_todesk ;;
        14) install_wps_office ;;
        15) install_qq ;;
        16) install_wechat ;;
        17) install_qqmusic ;;
        18) install_baidunetdisk ;;
        19) install_edge ;;
        20) install_chrome ;;
        21) steamdeck_cache_manager ;;
        22) update_installed_apps ;;
        23) uninstall_apps ;;
        24) install_yellow_duck_software ;;
        25) install_steamcommunity_302 ;;
        26) install_decky_lsfg_vk ;;
        27) install_decky_framegen ;;
        28) clover_install_or_reinstall ;;
        29) remote_connection_fix ;;
        *)
            echo -e "${RED}无效选择，请重新输入！${NC}"
            sleep 1
            continue
            ;;
    esac
fi
    done
}

show_about() {
    show_header
    echo -e "${YELLOW}════════════════ 关于 steamdeck工具箱 ════════════════${NC}"
    echo ""
    echo -e "${GREEN}steamdeck工具箱 v$VERSION${NC}"
    echo "制作人：薯条＆DeepSeek"
    echo "发布日期：2026年1月1日"
    echo ""
    echo -e "${CYAN}工具箱介绍：${NC}"
    echo "这是一个专为 Steam Deck 设计的工具箱，集成了系统优化、软件安装、"
    echo "网络工具等多种功能，方便用户快速配置和优化设备。"
    echo "感谢DeepSeek提供的大量技术支持"
    echo -e "${YELLOW}使用说明：${NC}"
    echo "1. 使用数字或字母选择功能"
    echo "2. 部分功能需要管理员权限"
    echo "3. 建议在执行重要操作前备份数据"
    echo "4. 网络工具请遵守当地法律法规"
    echo ""
    echo -e "${PURPLE}支持与反馈：${NC}"
    echo "如有问题或建议，请联系店铺售后客服反馈"
    echo ""

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_chinese_source() {
    show_header
    echo -e "${YELLOW}════════════════ 安装国内源 ════════════════${NC}"

    echo "正在配置国内源..."
    echo ""

    echo -e "${CYAN}步骤1: 禁用SteamOS只读模式${NC}"
    sudo steamos-readonly disable 2>/dev/null || true
    echo -e "${GREEN}✓ 已禁用只读模式${NC}"

    echo ""
    echo -e "${CYAN}步骤2: 配置Flatpak国内源${NC}"
    flatpak remote-modify flathub --url=https://mirror.sjtu.edu.cn/flathub 2>/dev/null || true
    echo -e "${GREEN}✓ Flatpak国内源配置完成${NC}"

    echo ""
    echo -e "${YELLOW}重启后生效${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

adjust_swap() {
    show_header
    echo -e "${YELLOW}════════════════ 调整虚拟内存大小 ════════════════${NC}"
    echo ""

    echo -e "${CYAN} 当前系统状态${NC}"
    echo "--------------------------------------------"

    # 直接获取内存和交换信息，避免管道子 shell
    if command -v free &> /dev/null; then
        # 获取物理内存行
        mem_line=$(LANG=C free -h | grep '^Mem:')
        swap_line=$(LANG=C free -h | grep '^Swap:')
        if [ -n "$mem_line" ]; then
            mem_total=$(echo "$mem_line" | awk '{print $2}')
            mem_used=$(echo "$mem_line" | awk '{print $3}')
            echo -e "物理内存: ${GREEN}${mem_total}${NC} | 已用: ${YELLOW}${mem_used}${NC}"
        else
            echo -e "${YELLOW}无法获取物理内存信息${NC}"
        fi
        if [ -n "$swap_line" ]; then
            swap_total=$(echo "$swap_line" | awk '{print $2}')
            swap_used=$(echo "$swap_line" | awk '{print $3}')
            echo -e "交换空间: ${GREEN}${swap_total}${NC} | 已用: ${YELLOW}${swap_used}${NC}"
        else
            echo -e "${YELLOW}无法获取交换空间信息${NC}"
        fi
    else
        echo -e "${YELLOW}未找到 free 命令，无法获取内存信息${NC}"
    fi

    echo ""

    echo -e "${CYAN} 活动交换设备${NC}"
    echo "--------------------------------------------"
    if command -v swapon &> /dev/null; then
        swapon_output=$(swapon --show 2>/dev/null)
        if [ -n "$swapon_output" ] && [ "$(echo "$swapon_output" | wc -l)" -gt 1 ]; then
            echo "$swapon_output" | while read -r line; do
                if [[ ! $line == NAME* ]]; then
                    # 使用 awk 解析列（NAME, TYPE, SIZE, USED, PRIO）
                    device=$(echo "$line" | awk '{print $1}')
                    type=$(echo "$line" | awk '{print $2}')
                    size=$(echo "$line" | awk '{print $3}')
                    used=$(echo "$line" | awk '{print $4}')
                    echo -e "${GREEN}${device}${NC} (${CYAN}${type}${NC}): ${size} | 已用: ${YELLOW}${used}${NC}"
                fi
            done
        else
            echo "未找到活动交换空间"
        fi
    else
        echo "未找到 swapon 命令"
    fi
    echo ""

    echo -e "${CYAN} 请选择要执行的操作${NC}"
    echo "============================================"

    echo -e "${GREEN}[1] 一键应用CryoByte33推荐方案${NC}"
    echo -e "    ${YELLOW}★ 推荐选项${NC} - 16GB Swap + 游戏专用优化参数    为现代大型游戏提供最佳兼容性与性能"
    echo ""

    echo -e "${GREEN}[2] 调整传统Swap文件大小${NC}"
    echo -e "    手动设置位于 /home/swapfile 的交换文件，适用于需要精确控制或大容量后备的情况"
    echo ""

    echo -e "${GREEN}[3] 配置ZRAM (内存压缩交换)${NC}"
    echo -e "    配置不依赖存储的快速内存交换，响应快、不损耗存储，适合日常使用"
    echo ""

    echo -e "${GREEN}[4] 清理所有Swap配置并重新开始${NC}"
    echo -e "    ${RED}重置选项${NC} - 停用并删除现有配置，切换方案或排除故障时使用"
    echo "============================================"
    echo ""

    read -p "请输入选项 [1-4]: " main_choice < /dev/tty

    case $main_choice in
        1)
            apply_cryo_recommendation
            ;;
        2)
            adjust_swapfile
            ;;
        3)
            configure_zram
            ;;
        4)
            cleanup_swap
            ;;
        *)
            echo -e "${RED}无效选择，请重新输入${NC}"
            echo ""
            read -p "按回车键返回主菜单..." < /dev/tty
            return
            ;;
    esac
}

apply_cryo_recommendation() {
    echo ""
    echo -e "${YELLOW}═══════════════ 应用CryoByte33推荐方案 ═══════════════${NC}"
    echo ""
    echo -e "${CYAN}方案概述${NC}"
    echo "----------------------------------------"
    echo "此方案专为Steam Deck游戏优化，包含："
    echo "• 16GB交换文件 (确保大型游戏兼容性)"
    echo "• 优化的内核参数 (减少不必要的交换)"
    echo "• 针对btrfs文件系统的正确配置"
    echo ""
    echo -e "${YELLOW}注意：${NC}这将需要约16GB的可用磁盘空间"
    echo "现有交换配置将被替换"
    echo ""

    read -p "是否继续？(输入 y 确认，其他键取消): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}操作已取消${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN} 开始应用优化配置...${NC}"
    echo "════════════════════════════════════════════"

    echo -e "\n${CYAN}步骤1/3: 创建16GB交换文件${NC}"
    echo "----------------------------------------"

    local swap_size_gb=16
    local block_count=$((swap_size_gb * 1024))

    echo "• 停用现有交换文件..."
    sudo swapoff /home/swapfile 2>/dev/null
    sudo swapoff -a 2>/dev/null

    echo "• 删除旧文件..."
    sudo rm -f /home/swapfile

    echo "• 创建新文件 (针对btrfs文件系统)..."
    sudo touch /home/swapfile
    sudo chattr +C /home/swapfile 2>/dev/null || echo -e "${YELLOW}  提示: chattr +C 可能失败，继续执行...${NC}"

    echo "• 填充16GB数据 (这需要几分钟)..."
    sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$block_count conv=fsync status=progress 2>/dev/null

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 创建文件失败，请检查磁盘空间${NC}"
        return
    fi

    echo "• 设置权限并格式化..."
    sudo chmod 600 /home/swapfile
    sudo mkswap /home/swapfile

    echo "• 启用交换文件..."
    sudo swapon /home/swapfile

    sudo sed -i '\|/home/swapfile|d' /etc/fstab 2>/dev/null
    echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null

    echo -e "${GREEN}✓ 16GB交换文件创建完成${NC}"

    echo -e "\n${CYAN}步骤2/3: 优化内核参数${NC}"
    echo "----------------------------------------"

    sudo tee /etc/sysctl.d/99-cryo-optimizations.conf > /dev/null <<'EOF'
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.page-cluster=0
vm.dirty_background_ratio=3
vm.dirty_ratio=50
EOF

    sudo sysctl --system --load=/etc/sysctl.d/99-cryo-optimizations.conf

    echo -e "${GREEN}✓ 内核参数优化完成${NC}"

    echo -e "\n${CYAN}步骤3/3: 配置ZRAM${NC}"
    echo "----------------------------------------"

    echo "• 停用ZRAM (避免与交换文件冲突)..."
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null

    echo -e "${GREEN}✓ ZRAM已停用${NC}"

    echo -e "\n${CYAN}════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✅ CryoByte33推荐方案已成功应用！${NC}"
    echo -e "${CYAN}════════════════════════════════════════════${NC}"
    echo ""
    echo -e "${YELLOW} 应用的项目：${NC}"
    echo "• 16GB交换文件 (位于 /home/swapfile)"
    echo "• 优化的内核参数 (swappiness=1, vfs_cache_pressure=50等)"
    echo "• ZRAM已停用，避免双重交换"
    echo ""
    echo -e "${YELLOW} 建议操作：${NC}"
    echo "1. 重启系统使所有设置完全生效"
    echo "2. 游戏时可在性能设置中调整交换文件使用策略"
    echo "3. 如需恢复原状，可使用本工具的[清理所有Swap配置]选项"
    echo ""

    echo -e "${CYAN} 验证当前状态：${NC}"
    echo "----------------------------------------"
    if command -v swapon &> /dev/null; then
        swapon --show | grep -E "(NAME|/home/swapfile)"
    fi
    echo -e "交换倾向性 (swappiness): ${GREEN}$(cat /proc/sys/vm/swappiness 2>/dev/null || echo 'N/A')${NC}"
    echo ""

    read -p "按回车键返回主菜单..." < /dev/tty
}

adjust_swapfile() {
    echo ""
    echo -e "${YELLOW}️  调整传统Swap文件大小${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if [ -f "/home/swapfile" ]; then
        current_size=$(sudo du -h /home/swapfile 2>/dev/null | cut -f1)
        echo -e "现有文件大小: ${GREEN}$current_size${NC}"
    else
        echo -e "现有文件: ${YELLOW}未找到${NC}"
    fi

    echo ""
    echo -e "${CYAN}磁盘空间信息 (/) ${NC}"
    df -h / | tail -1
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    echo "选择新的大小:"
    echo " 1.  1GB (轻度使用)"
    echo " 2.  4GB (基础游戏)"
    echo " 3.  8GB (推荐，平衡型)"
    echo " 4. 16GB (大型游戏/多任务)"
    echo " 5. 32GB (虚拟机/专业用途)"
    echo " 6. 自定义大小"
    echo ""

    read -p "请选择 [1-6]: " size_choice < /dev/tty

    case $size_choice in
        1) swap_size_gb=1;;
        2) swap_size_gb=4;;
        3) swap_size_gb=8;;
        4) swap_size_gb=16;;
        5) swap_size_gb=32;;
        6)
            read -p "请输入大小 (单位GB，数字): " custom_size < /dev/tty
            if [[ "$custom_size" =~ ^[0-9]+$ ]]; then
                swap_size_gb=$custom_size
            else
                echo -e "${RED}输入无效。${NC}"
                return
            fi
            ;;
        *) echo -e "${RED}无效选择。${NC}"; return;;
    esac

    echo ""
    echo -e "${YELLOW}即将创建 ${swap_size_gb}GB 的Swap文件。${NC}"
    echo "这会花费几分钟，并且需要临时磁盘空间。"
    read -p "是否继续? (y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    echo -e "${CYAN}开始创建Swap文件...${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo "1. 停用现有的Swap文件..."
    sudo swapoff /home/swapfile 2>/dev/null

    echo "2. 删除旧文件..."
    sudo rm -f /home/swapfile

    echo "3. 创建空文件并禁用Copy-on-Write (针对btrfs)..."
    sudo touch /home/swapfile
    sudo chattr +C /home/swapfile 2>/dev/null || echo -e "${YELLOW}⚠  警告: chattr +C 失败，但继续执行。${NC}"

    echo "4. 填充文件 (${swap_size_gb}GB)..."
    block_count=$((swap_size_gb * 1024))
    sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$block_count status=progress conv=fsync 2>/dev/null

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 创建文件失败，可能磁盘空间不足。${NC}"
        sudo rm -f /home/swapfile
        return
    fi

    echo "5. 设置文件权限..."
    sudo chmod 600 /home/swapfile

    echo "6. 格式化..."
    sudo mkswap /home/swapfile

    echo "7. 启用Swap文件..."
    sudo swapon /home/swapfile

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Swap文件已创建并启用。${NC}"

        if ! grep -q "/home/swapfile" /etc/fstab 2>/dev/null; then
            echo "8. 添加到 /etc/fstab (永久生效)..."
            echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null
        else
            echo "8. /etc/fstab 中已存在配置。"
        fi

        echo ""
        echo -e "${CYAN}✅ 创建成功！验证:${NC}"
        ls -lh /home/swapfile
        swapon --show | grep /home/swapfile
    else
        echo -e "${RED}✗ 启用失败。文件可能包含空洞或不兼容。${NC}"
        echo "建议: 使用本工具的选项4清理后，再尝试选项1（CryoByte33推荐）。"
    fi

    echo ""
    read -p "按回车键返回主菜单..." < /dev/tty
}

configure_zram() {
    echo ""
    echo -e "${YELLOW}羅 配置ZRAM (内存压缩交换)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    echo "ZRAM将部分内存作为压缩的交换空间，速度快且不磨损存储。"
    echo ""
    echo "选择ZRAM大小 (基于你的16GB物理内存):"
    echo " 1. 2GB (保守，节省内存)"
    echo " 2. 4GB (平衡推荐)"
    echo " 3. 8GB (积极，提升大型游戏体验)"
    echo ""

    read -p "请选择 [1-3]: " zram_choice < /dev/tty

    case $zram_choice in
        1) zram_size_gb=2;;
        2) zram_size_gb=4;;
        3) zram_size_gb=8;;
        *) echo -e "${RED}无效选择。${NC}"; return;;
    esac

    echo ""
    echo -e "${CYAN}安装并配置ZRAM...${NC}"

    if ! command -v systemctl &> /dev/null; then
        echo -e "${RED}系统不支持systemd。${NC}"
        return
    fi

    echo "1. 安装 systemd-zram-generator..."
    sudo pacman -S --noconfirm systemd-zram-generator 2>/dev/null || {
        echo -e "${YELLOW}无法通过pacman安装，尝试其他方法...${NC}"
    }

    echo "2. 创建配置文件..."
    sudo tee /etc/systemd/zram-generator.conf > /dev/null <<EOF
[zram0]
zram-size = min(ram, ${zram_size_gb}G)
compression-algorithm = lz4
swap-priority = 100
EOF

    echo "3. 启用服务..."
    sudo systemctl daemon-reload
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl start systemd-zram-setup@zram0
    sudo systemctl enable systemd-zram-setup@zram0

    echo "4. 等待ZRAM初始化..."
    sleep 2

    if swapon --show | grep -q zram; then
        echo -e "${GREEN}✓ ZRAM 已启用。${NC}"
        swapon --show | grep zram
    else
        echo -e "${YELLOW}⚠  ZRAM可能未启动，尝试重启后生效。${NC}"
    fi

    echo ""
    echo -e "${YELLOW}提示：${NC}你现在同时启用了ZRAM和传统Swap。"
    echo "如需仅使用ZRAM，可在主菜单使用选项4清理传统Swap。"

    read -p "按回车键返回主菜单..." < /dev/tty
}

cleanup_swap() {
    echo ""
    echo -e "${YELLOW}粒 清理所有Swap配置${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "这将："
    echo " • 停用并删除 /home/swapfile"
    echo " • 从 /etc/fstab 移除Swap条目"
    echo " • 停用并禁用ZRAM服务"
    echo ""

    read -p "确定要清理吗？此操作不可逆。(y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        return
    fi

    echo -e "${CYAN}正在清理...${NC}"

    sudo swapoff -a

    sudo rm -f /home/swapfile

    sudo sed -i '\|/home/swapfile|d' /etc/fstab

    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null
    sudo systemctl daemon-reload

    echo -e "${GREEN}✅ 已清理所有Swap配置。${NC}"
    echo "你可以重新启动本功能来配置新的Swap方案。"

    read -p "按回车键返回主菜单..." < /dev/tty
}

fix_disk_write_error() {
    show_header
    echo -e "${YELLOW}════════════════ 修复磁盘写入错误 ════════════════${NC}"

    echo -e "${CYAN}正在修复磁盘写入错误...${NC}"
    echo ""

    echo "步骤1: 检查并禁用SteamOS只读模式"

    if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
        echo "检测到只读模式已启用，正在禁用..."
        sudo steamos-readonly disable 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 已禁用只读模式${NC}"
        else
            echo -e "${YELLOW}⚠️  禁用只读模式时出现警告${NC}"
        fi
    else
        echo "只读模式未启用或已处于读写模式"
        echo -e "${GREEN}✓ 系统已处于读写模式${NC}"
    fi

    echo ""
    echo "步骤2: 检查磁盘设备"
    DISK_DEVICE="/dev/nvme0n1p10"

    if [ -b "$DISK_DEVICE" ]; then
        echo -e "${GREEN}✓ 找到磁盘设备: $DISK_DEVICE${NC}"

        echo "设备信息:"
        sudo fdisk -l "$DISK_DEVICE" 2>/dev/null | head -5
    else
        echo -e "${RED}✗ 未找到磁盘设备: $DISK_DEVICE${NC}"
        echo "请检查设备名称是否正确"
        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤3: 检查分区挂载状态"

    MOUNT_POINT=$(mount | grep "$DISK_DEVICE" | awk '{print $3}')
    if [ -n "$MOUNT_POINT" ]; then
        echo "分区已挂载到: $MOUNT_POINT"
        echo "正在卸载分区..."

        if sudo umount "$DISK_DEVICE" 2>/dev/null; then
            echo -e "${GREEN}✓ 分区卸载成功${NC}"
        else
            echo "尝试强制卸载..."
            if sudo umount -f "$DISK_DEVICE" 2>/dev/null; then
                echo -e "${GREEN}✓ 分区强制卸载成功${NC}"
            else
                echo -e "${YELLOW}⚠️  分区卸载失败，尝试继续修复${NC}"
                echo "检查占用进程..."
                sudo lsof "$DISK_DEVICE" 2>/dev/null | head -5
            fi
        fi
    else
        echo "分区未挂载"
        echo -e "${GREEN}✓ 分区未挂载，可直接进行修复${NC}"
    fi

    echo ""
    echo "步骤4: 修复NTFS文件系统"
    echo "正在修复 $DISK_DEVICE..."

    if mount | grep -q "$DISK_DEVICE"; then
        echo -e "${YELLOW}⚠️  分区仍处于挂载状态，尝试强制修复${NC}"
        if sudo ntfsfix -d "$DISK_DEVICE" 2>/dev/null; then
            echo -e "${GREEN}✓ NTFS修复完成${NC}"
        else
            echo -e "${YELLOW}⚠️  NTFS修复可能存在问题${NC}"
        fi
    else
        if sudo ntfsfix "$DISK_DEVICE" 2>/dev/null; then
            echo -e "${GREEN}✓ NTFS修复完成${NC}"
        else
            echo -e "${YELLOW}⚠️  NTFS修复可能存在问题${NC}"
        fi
    fi

    echo ""
    echo "步骤5: 重新挂载分区"

    if [ -n "$MOUNT_POINT" ] && [ ! -d "$MOUNT_POINT" ]; then
        sudo mkdir -p "$MOUNT_POINT" 2>/dev/null
    fi

    if [ -n "$MOUNT_POINT" ] && [ -d "$MOUNT_POINT" ]; then
        echo "尝试重新挂载到原位置: $MOUNT_POINT"
        if sudo mount "$DISK_DEVICE" "$MOUNT_POINT" 2>/dev/null; then
            echo -e "${GREEN}✓ 分区重新挂载完成${NC}"
        else
            echo "尝试自动挂载..."
            if sudo mount "$DISK_DEVICE" 2>/dev/null; then
                NEW_MOUNT_POINT=$(mount | grep "$DISK_DEVICE" | awk '{print $3}')
                echo -e "${GREEN}✓ 分区自动挂载完成: $NEW_MOUNT_POINT${NC}"
            else
                echo -e "${YELLOW}⚠️  分区重新挂载失败${NC}"
                echo "您可以稍后手动挂载分区"
            fi
        fi
    else
        echo "尝试自动挂载..."
        if sudo mount "$DISK_DEVICE" 2>/dev/null; then
            NEW_MOUNT_POINT=$(mount | grep "$DISK_DEVICE" | awk '{print $3}')
            if [ -n "$NEW_MOUNT_POINT" ]; then
                echo -e "${GREEN}✓ 分区自动挂载完成: $NEW_MOUNT_POINT${NC}"
            else
                echo -e "${GREEN}✓ 分区挂载完成${NC}"
            fi
        else
            echo "分区未挂载，您可以在需要时手动挂载"
            echo -e "${GREEN}✓ 分区修复完成，可随时挂载使用${NC}"
        fi
    fi

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ 磁盘写入错误修复流程已完成${NC}"
    echo ""
    echo -e "${YELLOW}提示：${NC}"
    echo "1. 如果问题仍然存在，请重启后再次尝试"
    echo "2. 建议备份重要数据后再进行磁盘操作"
    echo "3. 如需更彻底的修复，建议使用Windows系统下的磁盘检查工具"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

fix_boot() {
    show_header
    echo -e "${YELLOW}════════════════ 修复引导 ════════════════${NC}"

    echo -e "${CYAN}正在运行引导修复脚本...${NC}"

    cat > "$TEMP_DIR/fix_boot.sh" << 'EOF'
#!/bin/bash

echo "========================================"
echo "  Clover启动顺序自动设置脚本"
echo "========================================"
echo ""

if [ "$EUID" -ne 0 ]; then
    echo "⚠️ 检测到需要管理员权限，正在提升权限..."
    echo "   如需修改启动顺序，请输入您的用户密码（输入时不会显示）"
    echo ""
    sudo "$0" "$@"
    exit $?
fi

if ! command -v efibootmgr &> /dev/null; then
    echo "❌ 错误：未找到efibootmgr命令。"
    echo "   请确保系统已安装efibootmgr工具。"
    exit 1
fi

echo "1. 正在扫描UEFI启动项..."
echo "----------------------------------------"

BACKUP_FILE="/tmp/boot_backup_$(date +%Y%m%d_%H%M%S).txt"
CURRENT_BOOT_ORDER=$(efibootmgr | grep "BootOrder")
echo "当前启动顺序: $CURRENT_BOOT_ORDER"
efibootmgr -v > "$BACKUP_FILE"
echo "启动项备份已保存到: $BACKUP_FILE"

echo ""
echo "2. 正在查找Clover启动项..."
echo "----------------------------------------"

CLOVER_ENTRY=$(efibootmgr -v | grep -i "CLOVER" | head -1)

if [ -z "$CLOVER_ENTRY" ]; then
    echo "❌ 未找到Clover启动项！可能的原因："
    echo "   • Clover尚未安装或安装不正确"
    echo "   • Clover的EFI文件不在标准位置"
    echo "   • 启动项名称不包含'CLOVER'关键字"
    echo ""
    echo "当前所有启动项列表："
    efibootmgr | grep "Boot[0-9A-F][0-9A-F][0-9A-F][0-9A-F]"
    echo ""
    echo "⚠️ 建议：请确保Clover已正确安装到ESP分区，然后重试。"
    exit 1
fi

CLOVER_BOOTNUM=$(echo "$CLOVER_ENTRY" | grep -o 'Boot[0-9A-F]\{4\}' | head -1 | sed 's/Boot//')

echo "✅ 找到Clover启动项："
echo "   启动编号: Boot$CLOVER_BOOTNUM"
echo "   描述: $CLOVER_ENTRY"

echo ""
echo "3. 正在分析当前启动顺序..."
echo "----------------------------------------"

CURRENT_ORDER=$(efibootmgr | grep "BootOrder" | cut -d: -f2 | tr -d ' ')

if [ -z "$CURRENT_ORDER" ]; then
    echo "⚠️  无法获取当前启动顺序，将创建新顺序。"
    NEW_ORDER="$CLOVER_BOOTNUM"
else
    if [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM,"* ]] || [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM" ]]; then
        echo "✅ Clover已在启动顺序的首位，无需修改。"
        echo "   当前顺序: $CURRENT_ORDER"
        exit 0
    fi

    NEW_ORDER="$CLOVER_BOOTNUM,$(echo "$CURRENT_ORDER" | tr ',' '\n' | grep -v "^$CLOVER_BOOTNUM$" | tr '\n' ',' | sed 's/,$//')"
fi

echo "当前顺序: $CURRENT_ORDER"
echo "新顺序: $NEW_ORDER"

echo ""
echo "4. 确认设置"
echo "----------------------------------------"
echo "脚本将执行以下操作："
echo "  • 将Clover (Boot$CLOVER_BOOTNUM) 设为第一启动项"
echo "  • 其他启动项顺序保持不变"
echo ""

read -p "是否继续？(输入 y 确认，其他键取消): " -n 1 -r CONFIRM < /dev/tty
echo ""

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "❌ 操作已取消。"
    exit 0
fi

echo ""
echo "5. 正在设置启动顺序..."
echo "----------------------------------------"

efibootmgr -o "$NEW_ORDER"

echo ""
echo "6. 验证设置结果"
echo "----------------------------------------"

RESULT=$(efibootmgr | grep "BootOrder")
echo "最终启动顺序: $RESULT"

if echo "$RESULT" | grep -q "^BootOrder: $CLOVER_BOOTNUM,"; then
    echo ""
    echo "✅ 设置成功！Clover (Boot$CLOVER_BOOTNUM) 现在是第一启动项。"
    echo ""
    echo "下次重启时将首先进入Clover引导菜单。"
    echo "要测试设置，请重启Steam Deck。"
else
    echo ""
    echo "⚠️  设置可能未完全生效。"
    echo "   请手动运行 'efibootmgr -v' 检查设置。"
fi

echo ""
echo "========================================"
echo "脚本执行完成"
echo "========================================"
echo "提示：如需恢复原设置，可参考备份文件: $BACKUP_FILE"
EOF

    chmod +x "$TEMP_DIR/fix_boot.sh"
    "$TEMP_DIR/fix_boot.sh"

    echo ""

    read -p "按回车键返回主菜单..." < /dev/tty
}

fix_shared_disk() {
    show_header
    echo -e "${YELLOW}════════════════ 修复互通盘 ════════════════${NC}"

    echo -e "${CYAN}正在修复互通盘...${NC}"

    echo "步骤1: 禁用SteamOS只读模式"
    sudo steamos-readonly disable
    echo -e "${GREEN}✓ 已禁用只读模式${NC}"

    echo "步骤2: 修改UDisks2权限文件"
    UDISKS2_FILE="/usr/share/polkit-1/actions/org.freedesktop.UDisks2.policy"

    if [ -f "$UDISKS2_FILE" ]; then
        sudo cp "$UDISKS2_FILE" "$UDISKS2_FILE.backup.$(date +%Y%m%d)"

        sudo sed -i '181s/<allow_active>[^<]*<\/allow_active>/<allow_active>yes<\/allow_active>/' "$UDISKS2_FILE"

        if grep -q "<allow_active>yes</allow_active>" "$UDISKS2_FILE"; then
            echo -e "${GREEN}✓ UDisks2权限文件修改成功${NC}"
        else
            echo -e "${YELLOW}⚠️  UDisks2权限文件可能未修改成功，请手动检查${NC}"
        fi
    else
        echo -e "${RED}✗ 未找到UDisks2权限文件: $UDISKS2_FILE${NC}"
    fi

    echo "步骤3: 检查并添加fstab配置"
    FSTAB_FILE="/etc/fstab"
    FSTAB_ENTRY="LABEL=Game  /run/media/deck/Game  ntfs   defaults,nofail,uid=1000,gid=1000,umask=022   0 0"

    if [ -f "$FSTAB_FILE" ]; then
        if grep -q "LABEL=Game" "$FSTAB_FILE"; then
            echo -e "${GREEN}✓ fstab中已存在Game盘配置${NC}"
        else
            sudo cp "$FSTAB_FILE" "$FSTAB_FILE.backup.$(date +%Y%m%d)"

            echo "$FSTAB_ENTRY" | sudo tee -a "$FSTAB_FILE" > /dev/null
            echo -e "${GREEN}✓ 已添加Game盘配置到fstab${NC}"
        fi
    else
        echo -e "${RED}✗ 未找到fstab文件: $FSTAB_FILE${NC}"
    fi

    echo "步骤4: 创建目录并尝试挂载"
    GAME_DIR="/run/media/deck/Game"

    sudo mkdir -p "$GAME_DIR"
    sudo chown deck:deck "$GAME_DIR"

    if [ -d "$GAME_DIR" ]; then
        echo -e "${GREEN}✓ 已创建Game目录: $GAME_DIR${NC}"

        if mountpoint -q "$GAME_DIR"; then
            echo "卸载已挂载的Game盘..."
            sudo umount "$GAME_DIR"
        fi

        echo "尝试挂载Game盘..."
        if sudo mount -L "Game" "$GAME_DIR" 2>/dev/null; then
            echo -e "${GREEN}✓ Game盘已成功挂载${NC}"
            echo ""
            echo -e "${CYAN}Game盘信息：${NC}"
            echo "挂载点: $GAME_DIR"
            echo "文件系统类型: $(lsblk -o NAME,FSTYPE,LABEL | grep -i game || echo '未知')"
            echo ""
            echo -e "${YELLOW}提示：${NC}"
            echo "1. Game盘现在可以在文件管理器中访问"
            echo "2. 路径: /run/media/deck/Game"
            echo "3. 重启后会自动挂载"
        else
            echo -e "${YELLOW}⚠️  Game盘挂载失败${NC}"
            echo "可能的原因："
            echo "1. Game盘不存在或标签不正确"
            echo "2. 分区未格式化"
            echo "3. 需要重启后生效"
            echo ""
            echo "您可以尝试重启后再次检查"
        fi
    else
        echo -e "${YELLOW}⚠️  无法创建或访问Game目录${NC}"
    fi

    echo ""
    echo -e "${GREEN}✓ 修复互通盘已完成${NC}"
    echo ""
    echo -e "${YELLOW}提示：如果没看到GAME盘，请去steam-设置-存储空间，添加一下GAME盘${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

clear_hosts_cache() {
    show_header
    echo -e "${YELLOW}════════════════ 清理hosts缓存 ════════════════${NC}"

    echo -e "${CYAN}正在清理hosts缓存...${NC}"

    echo "备份原hosts文件..."
    sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d_%H%M%S)

    echo "清空hosts文件内容..."
    sudo sh -c 'echo "" > /etc/hosts'

    echo -e "${GREEN}✓ hosts缓存已清理完成${NC}"
    echo -e "${YELLOW}注意：/etc/hosts文件已被清空，如果需要默认配置，请手动恢复备份${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_uu_accelerator() {
    show_header
    echo -e "${YELLOW}════════════════ 安装UU加速器插件 ════════════════${NC}"

    echo -e "${CYAN}正在安装UU加速器插件...${NC}"
    echo "安装命令: curl -s uudeck.com | sudo sh"

    if curl -s uudeck.com | sudo sh; then
        echo ""
        echo -e "${GREEN}✓ UU加速器插件安装完成${NC}"
    else
        echo ""
        echo -e "${RED}✗ UU加速器插件安装失败${NC}"
    fi

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_xunyou_accelerator() {
    show_header
    echo -e "${YELLOW}════════════════ 安装迅游加速器插件 ════════════════${NC}"

    echo -e "${CYAN}正在安装迅游加速器插件...${NC}"
    echo "安装命令: curl -s sd.xunyou.com | sudo sh"

    if curl -s sd.xunyou.com | sudo sh; then
        echo ""
        echo -e "${GREEN}✓ 迅游加速器插件安装完成${NC}"
    else
        echo ""
        echo -e "${RED}✗ 迅游加速器插件安装失败${NC}"
    fi

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_tomoon() {
    show_header
    echo -e "${YELLOW}════════════════ 安装/卸载 ToMoon 插件 ════════════════${NC}"
    echo ""

    local GITHUB_REPO="YukiCoco/ToMoon"
    local API_URL="https://api.github.com/repos/${GITHUB_REPO}/releases/latest"
    local PLUGIN_DIR="/home/deck/homebrew/plugins"
    local TARGET_DIR="${PLUGIN_DIR}/tomoon"
    local TEMP_DIR="/tmp/tomoon_install"
    local MIRRORS=(
        "https://ghproxy.net/"
        "https://gh.ddlc.top/"
        "https://mirror.ghproxy.com/"
        "https://gh.api.99988866.xyz/"
        "https://download.fastgit.org/"
        "https://hub.gitmirror.com/"
        "https://git.xfj0.xyz/"
        "https://github.com/"
    )
    local DOWNLOAD_TIMEOUT=60
    local MAX_RETRY_PER_MIRROR=1

    for cmd in curl sudo unzip; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            read -p "按回车键返回主菜单..." < /dev/tty
            return 1
        fi
    done

    echo "请选择要执行的操作："
    echo "1. 安装/更新 ToMoon 插件"
    echo "2. 卸载 ToMoon 插件"
    echo ""

    read -p "请输入选择 [1-2] (输入其他键返回): " action_choice < /dev/tty

    case $action_choice in
        1)
            echo -e "${CYAN}正在从 GitHub 获取最新版本信息...${NC}"
            local latest_version=$(curl -s "$API_URL" | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//; s/".*//')

            if [ -z "$latest_version" ]; then
                echo -e "${RED}错误: 无法从 GitHub API 获取最新版本，请检查网络连接。${NC}"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo -e "${GREEN}最新版本: ${latest_version}${NC}"

            local installed_version="未安装"
            local is_installed=false
            if [ -f "$TARGET_DIR/bin/tomoon" ]; then
                is_installed=true
                if [ -f "$TARGET_DIR/package.json" ]; then
                    installed_version=$(grep -o '"version": *"[^"]*"' "$TARGET_DIR/package.json" | head -1 | sed 's/.*"version": *"//; s/".*//')
                    if [ -n "$installed_version" ]; then
                        echo -e "${CYAN}已安装版本: ${installed_version}${NC}"
                        if [ "$installed_version" = "${latest_version#v}" ]; then
                            echo -e "${GREEN}已经是最新版本，无需更新。${NC}"
                            read -p "按回车键返回主菜单..." < /dev/tty
                            return 0
                        else
                            echo -e "${YELLOW}发现新版本，将进行更新。${NC}"
                        fi
                    else
                        echo -e "${YELLOW}已安装但无法获取版本，将覆盖安装。${NC}"
                    fi
                else
                    echo -e "${YELLOW}已安装但 package.json 缺失，将覆盖安装。${NC}"
                fi
            else
                echo "未检测到 ToMoon 插件安装，将进行全新安装。"
            fi

            if [ ! -f "/etc/systemd/system/plugin_loader.service" ]; then
                echo -e "${YELLOW}⚠ 警告: 未检测到 Decky Loader 插件商店。${NC}"
                echo "ToMoon 插件需要先安装 Decky Loader 才能正常工作。"
                read -p "是否继续安装？(y/N): " -n 1 -r < /dev/tty
                echo ""
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    echo "安装已取消。"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 1
                fi
            fi

            echo -e "${CYAN}准备安装/更新 ToMoon 插件...${NC}"
            read -p "是否继续？(y/N): " -n 1 -r < /dev/tty
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "操作已取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            rm -rf "$TEMP_DIR"
            mkdir -p "$TEMP_DIR"
            cd "$TEMP_DIR"

            local zip_filename="tomoon-${latest_version}.zip"
            local download_path="https://github.com/${GITHUB_REPO}/releases/download/${latest_version}/${zip_filename}"
            local DOWNLOAD_SUCCESS=false

            for mirror in "${MIRRORS[@]}"; do
                local full_url="${mirror}${download_path}"
                echo -e "尝试从 ${mirror} 下载..."

                local retry_count=0
                while [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; do
                    if [[ $retry_count -gt 0 ]]; then
                        echo -e "${YELLOW}重试下载 (第 ${retry_count} 次重试)...${NC}"
                    fi

                    curl -L --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$zip_filename" "$full_url"
                    local curl_exit=$?

                    if [[ $curl_exit -eq 0 ]] && [[ -f "$zip_filename" ]]; then
                        local file_size=$(stat -c%s "$zip_filename" 2>/dev/null || stat -f%z "$zip_filename" 2>/dev/null)
                        if [[ -n "$file_size" ]] && [[ "$file_size" -gt 10000 ]]; then
                            echo -e "\n${GREEN}下载成功 (大小: $((file_size/1024)) KB)${NC}"
                            DOWNLOAD_SUCCESS=true
                            break 2
                        else
                            echo -e "\n${RED}下载文件无效 (${file_size} 字节)，尝试下一个镜像...${NC}"
                            rm -f "$zip_filename"
                            break
                        fi
                    else
                        echo -e "\n${RED}下载失败 (退出码: $curl_exit)${NC}"
                        rm -f "$zip_filename"
                        ((retry_count++))
                        if [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; then
                            echo "将进行重试..."
                            sleep 2
                        else
                            echo "该镜像重试次数用完，切换到下一个镜像。"
                        fi
                    fi
                done
            done

            if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
                echo -e "${RED}所有镜像均下载失败，安装中止。${NC}"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo -e "${CYAN}正在解压...${NC}"
            if ! unzip -q "$zip_filename"; then
                echo -e "${RED}解压失败，文件可能已损坏。${NC}"
                rm -rf "$TEMP_DIR"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            sudo mkdir -p "$PLUGIN_DIR"

            if [ -d "$TARGET_DIR" ]; then
                echo "检测到旧版本目录，正在删除..."
                sudo rm -rf "$TARGET_DIR"
            fi

            # 智能查找解压后的插件目录
            local extracted_dir=""
            extracted_dir=$(find "$TEMP_DIR" -maxdepth 2 -type f \( -name "tomoon" -o -name "package.json" \) -exec dirname {} \; | head -1)
            if [ -z "$extracted_dir" ]; then
                extracted_dir=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "tomoon*" | head -1)
            fi
            if [ -z "$extracted_dir" ]; then
                local subdirs=($(find "$TEMP_DIR" -maxdepth 1 -type d ! -path "$TEMP_DIR"))
                if [ ${#subdirs[@]} -eq 1 ]; then
                    extracted_dir="${subdirs[0]}"
                fi
            fi
            if [ -z "$extracted_dir" ]; then
                if [ -f "$TEMP_DIR/package.json" ] || [ -d "$TEMP_DIR/bin" ]; then
                    extracted_dir="$TEMP_DIR"
                fi
            fi

            if [ -z "$extracted_dir" ] || [ ! -d "$extracted_dir" ]; then
                echo -e "${RED}错误: 解压后未找到 ToMoon 插件目录。${NC}"
                echo "解压后的文件列表："
                ls -la "$TEMP_DIR"
                rm -rf "$TEMP_DIR"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo -e "${CYAN}正在安装插件到 ${TARGET_DIR}...${NC}"
            sudo mv "$extracted_dir" "$TARGET_DIR"

            sudo chown -R deck:deck "$TARGET_DIR"

            rm -rf "$TEMP_DIR"

            echo ""
            echo -e "${GREEN}✅ ToMoon 插件 (${latest_version}) 安装/更新完成！${NC}"
            echo "请切换回游戏模式，在 Decky 侧边栏中查看 ToMoon 是否出现。"
            ;;

        2)
            echo -e "${CYAN}正在卸载 ToMoon 插件...${NC}"
            echo "这将删除目录: ${TARGET_DIR}"

            read -p "确定要卸载吗？(y/N): " -n 1 -r < /dev/tty
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "卸载已取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 0
            fi

            if [ -d "$TARGET_DIR" ]; then
                if sudo rm -rf "$TARGET_DIR"; then
                    echo -e "${GREEN}✅ ToMoon 插件已卸载。${NC}"
                else
                    echo -e "${RED}卸载失败，请检查权限。${NC}"
                fi
            else
                echo -e "${YELLOW}未检测到 ToMoon 插件安装。${NC}"
            fi
            ;;

        *)
            echo "返回主菜单..."
            return
            ;;
    esac

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_remove_plugin_store() {
    show_header
    echo -e "${YELLOW}════════════════ 安装＆卸载插件商店 ════════════════${NC}"

    echo "请选择操作："
    echo "1. 安装插件商店"
    echo "2. 卸载插件商店"
    echo ""

    read -p "请输入选择 [1-2]: " plugin_choice < /dev/tty

    case $plugin_choice in
        1)
            echo -e "${CYAN}正在从 GitHub 安装最新版 Decky Loader...${NC}"

            HOME_DIR="/home/deck"
            HOMEBREW_DIR="${HOME_DIR}/homebrew"
            SERVICE_DIR="${HOMEBREW_DIR}/services"
            PLUGIN_DIR="${HOMEBREW_DIR}/plugins"
            PLUGIN_LOADER="${SERVICE_DIR}/PluginLoader"
            SERVICE_FILE="${SERVICE_DIR}/plugin_loader.service"
            SERVICE_DEST="/etc/systemd/system/plugin_loader.service"
            CURRENT_USER=$(whoami)
            MIRRORS=(
                "https://ghproxy.net/"
                "https://gh.ddlc.top/"
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
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 1
                fi
            done

            echo "正在获取最新版本信息..."
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
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi
            echo -e "${GREEN}最新版本: ${LATEST_VERSION}${NC}"

            INSTALLED_VERSION=""
            if [[ -f "$PLUGIN_LOADER" && -x "$PLUGIN_LOADER" ]]; then
                INSTALLED_VERSION=$(sudo journalctl -u plugin_loader --no-pager 2>/dev/null | grep -i "Starting Decky version" | tail -1 | grep -oP 'version v?\K[0-9.]+(-pre[0-9]+)?')
                if [[ -z "$INSTALLED_VERSION" ]]; then
                    INSTALLED_VERSION=$("$PLUGIN_LOADER" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+(-pre\d+)?')
                fi
                if [[ -n "$INSTALLED_VERSION" ]]; then
                    echo -e "${CYAN}当前已安装版本: ${INSTALLED_VERSION}${NC}"
                    if [[ "$INSTALLED_VERSION" == "$LATEST_VERSION" ]]; then
                        echo -e "${GREEN}已经是最新版本，无需安装。${NC}"
                        read -p "按回车键返回主菜单..." < /dev/tty
                        return 0
                    else
                        echo -e "${YELLOW}发现新版本，将进行更新。${NC}"
                    fi
                else
                    echo -e "${YELLOW}已安装但无法获取版本，将覆盖安装。${NC}"
                fi
            else
                echo "未检测到现有安装，将进行全新安装。"
            fi

            echo "创建目录并修复权限..."
            if [[ ! -d "$HOMEBREW_DIR" ]]; then
                sudo mkdir -p "$HOMEBREW_DIR"
            fi
            sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "$HOMEBREW_DIR" 2>/dev/null || true
            mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR" 2>/dev/null || {
                sudo mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR"
                sudo chown ${CURRENT_USER}:${CURRENT_USER} "$SERVICE_DIR" "$PLUGIN_DIR"
            }

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
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo "启用 Steam 远程调试..."
            touch "${HOME_DIR}/.steam/steam/.cef-enable-remote-debugging"
            if [[ -d "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/" ]]; then
                touch "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/.cef-enable-remote-debugging"
            fi

            echo "配置 systemd 服务..."
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

            echo "服务状态："
            systemctl status plugin_loader --no-pager

            echo ""
            echo -e "${GREEN}✓ Decky Loader ${LATEST_VERSION} 安装/更新完成${NC}"
            echo "请切换回游戏模式，按 '...' 键打开侧边栏检查。"
            ;;

        2)
            echo -e "${CYAN}正在卸载插件商店...${NC}"
            echo "卸载命令: sudo rm -rf /home/deck/homebrew"
            echo "警告：这将删除整个 /home/deck/homebrew 目录，包括所有插件和插件商店。"
            echo ""

            read -p "确定要卸载插件商店吗？(y/N): " -n 1 -r < /dev/tty
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "卸载已取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return
            fi

            echo "正在执行卸载..."
            if sudo rm -rf /home/deck/homebrew; then
                echo ""
                echo -e "${GREEN}✓ 插件商店卸载完成${NC}"
            else
                echo ""
                echo -e "${RED}✗ 插件商店卸载失败${NC}"
            fi
            ;;

        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac

    read -p "按回车键返回主菜单..." < /dev/tty
}

calibrate_joystick() {
    show_header
    echo -e "${YELLOW}════════════════ 校准摇杆 ════════════════${NC}"

    echo -e "${CYAN}正在校准摇杆...${NC}"

    if thumbstick_cal; then
        echo ""
        echo -e "${GREEN}✓ 摇杆校准完成${NC}"
    else
        echo ""
        echo -e "${RED}✗ 摇杆校准失败${NC}"
        echo "请确保系统中已安装摇杆校准工具"
    fi

    read -p "按回车键返回主菜单..." < /dev/tty
}

set_admin_password() {
    show_header
    echo -e "${YELLOW}════════════════ 设置管理员密码 ════════════════${NC}"

    echo -e "${CYAN}正在检查是否已设置管理员密码...${NC}"

    if sudo -n true 2>/dev/null; then
        echo -e "${GREEN}✓ 管理员密码已经设置${NC}"
        echo "无需重复设置"
    else
        echo -e "${YELLOW}检测到未设置管理员密码或密码已过期${NC}"
        echo ""
        echo "现在开始设置管理员密码..."
        echo "请按照提示输入您要设置的密码"
        echo ""

        sudo passwd

        if [ $? -eq 0 ]; then
            echo ""
            echo -e "${GREEN}✓ 管理员密码设置完成${NC}"
            echo "请妥善保管您的密码"
        else
            echo ""
            echo -e "${RED}✗ 管理员密码设置失败${NC}"
            echo "请检查输入是否正确"
        fi
    fi

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_anydesk() {
    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    local ANYDESK_BIN_DIR="$HOME/.local/bin"
    local ANYDESK_DESKTOP_DIR="$HOME/.local/share/applications"
    local ANYDESK_EXECUTABLE="$ANYDESK_INSTALL_DIR/anydesk"
    local ANYDESK_SYMLINK="$ANYDESK_BIN_DIR/anydesk"
    local ANYDESK_DESKTOP_FILE="$ANYDESK_DESKTOP_DIR/anydesk.desktop"
    local ANYDESK_DOWNLOAD_DIR="$HOME/Downloads"
    local ANYDESK_FLATPAK_PKG="com.anydesk.Anydesk"

    anydesk_show_header() {
        clear
        echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
        echo -e "${CYAN}           AnyDesk 管理脚本                        ${NC}"
        echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
        echo ""
    }

anydesk_delete_desktop_shortcuts() {
    for desktop_path in "$HOME/Desktop" "$HOME/桌面"; do
        [ -d "$desktop_path" ] || continue
        find "$desktop_path" -maxdepth 1 -type f -iname "*anydesk*.desktop" -exec rm -f {} \; -print | while read -r file; do
            echo -e "${GREEN}✓ 已删除桌面快捷方式: $file${NC}"
        done
    done
}

    anydesk_get_latest_version_info() {
        local page_content
        page_content=$(wget -qO- --referer='' --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
            "https://anydesk.com.cn/zhs/downloads/linux" 2>/dev/null)

        if [ -z "$page_content" ]; then
            echo -e "${RED}✗ 无法访问官网，请检查网络连接${NC}"
            return 1
        fi

        LATEST_VERSION=$(echo "$page_content" | grep -oP 'v?\d+\.\d+\.\d+' | head -1 | sed 's/^v//')
        if [ -z "$LATEST_VERSION" ]; then
            LATEST_VERSION=$(echo "$page_content" | grep -oP '\d+\.\d+\.\d+\s*\([\d.]+ MB\)' | head -1 | grep -oP '\d+\.\d+\.\d+')
        fi

        if [ -z "$LATEST_VERSION" ]; then
            echo -e "${RED}✗ 无法解析版本号，请检查官网页面结构${NC}"
            return 1
        fi

        DOWNLOAD_URL="https://download.anydesk.com/linux/anydesk-${LATEST_VERSION}-amd64.tar.gz"
        if ! wget --spider -q --referer='' --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
            "$DOWNLOAD_URL" 2>/dev/null; then
            echo -e "${YELLOW}⚠ 下载链接无效，尝试备用链接...${NC}"
            DOWNLOAD_URL="https://anydesk.com/downloads/linux/anydesk-${LATEST_VERSION}-amd64.tar.gz"
            if ! wget --spider -q --referer='' --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" \
                "$DOWNLOAD_URL" 2>/dev/null; then
                echo -e "${RED}✗ 无法访问下载链接，请检查网络或稍后重试${NC}"
                return 1
            fi
        fi

        echo -e "${GREEN}✓ 最新版本: ${LATEST_VERSION}${NC}"
        return 0
    }

    anydesk_get_installed_version() {
        if [ -x "$ANYDESK_EXECUTABLE" ]; then
            INSTALLED_VERSION=$("$ANYDESK_EXECUTABLE" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+' | head -1)
            [ -z "$INSTALLED_VERSION" ] && INSTALLED_VERSION=$(echo "$ANYDESK_EXECUTABLE" | grep -oP '\d+\.\d+\.\d+' | head -1)
            echo "$INSTALLED_VERSION"
        else
            echo ""
        fi
    }

    anydesk_uninstall_flatpak() {
        echo "正在卸载 Flatpak 版本 ($ANYDESK_FLATPAK_PKG)..."
        if flatpak uninstall "$ANYDESK_FLATPAK_PKG" -y; then
            echo -e "${GREEN}✓ Flatpak 版本卸载成功${NC}"
            local OLD_DESKTOP="$ANYDESK_DESKTOP_DIR/com.anydesk.Anydesk.desktop"
            if [ -f "$OLD_DESKTOP" ]; then
                rm -f "$OLD_DESKTOP"
                echo -e "${GREEN}✓ 已删除旧脚本创建的快捷方式: $OLD_DESKTOP${NC}"
            fi
            anydesk_delete_desktop_shortcuts
            return 0
        else
            echo -e "${RED}✗ Flatpak 卸载失败${NC}"
            return 1
        fi
    }

    anydesk_uninstall_portable() {
        echo ""
        echo -e "${YELLOW}即将卸载便携版 AnyDesk...${NC}"
        echo "将删除："
        echo "  - $ANYDESK_INSTALL_DIR"
        echo "  - $ANYDESK_SYMLINK"
        echo "  - $ANYDESK_DESKTOP_FILE"
        echo "  - 桌面上的 AnyDesk 快捷方式（如果存在）"
        read -p "确认卸载？[y/N] " confirm < /dev/tty
        [[ ! "$confirm" =~ ^[Yy]$ ]] && echo "取消卸载" && return

        pkill -f "$ANYDESK_EXECUTABLE" 2>/dev/null
        pkill -f "anydesk" 2>/dev/null

        [ -d "$ANYDESK_INSTALL_DIR" ] && rm -rf "$ANYDESK_INSTALL_DIR" && echo -e "${GREEN}✓ 已删除安装目录${NC}"
        [ -L "$ANYDESK_SYMLINK" ] && rm -f "$ANYDESK_SYMLINK" && echo -e "${GREEN}✓ 已删除软链接${NC}"
        [ -f "$ANYDESK_DESKTOP_FILE" ] && rm -f "$ANYDESK_DESKTOP_FILE" && echo -e "${GREEN}✓ 已删除桌面快捷方式（应用目录）${NC}"
        anydesk_delete_desktop_shortcuts
        rm -f "$ANYDESK_DOWNLOAD_DIR"/anydesk-*.tar.gz 2>/dev/null

        echo -e "${GREEN}✓ 便携版卸载完成${NC}"
    }

    anydesk_download_and_install() {
        local version=$1
        local url=$2
        local tarball="anydesk-${version}-amd64.tar.gz"

        echo ""
        echo "步骤1: 创建安装目录"
        mkdir -p "$ANYDESK_INSTALL_DIR" "$ANYDESK_BIN_DIR" "$ANYDESK_DESKTOP_DIR"

        echo ""
        echo "步骤2: 下载 AnyDesk ${version}"
        echo "下载地址: $url"
        echo "开始下载..."
        cd "$ANYDESK_DOWNLOAD_DIR" || return 1
        if ! wget --progress=bar:force -O "$tarball" \
            --referer='' --user-agent="Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36" "$url"; then
            echo -e "${RED}✗ 下载失败${NC}"
            return 1
        fi
        echo -e "${GREEN}✓ 下载完成${NC}"

        echo ""
        echo "步骤3: 解压"
        if ! tar -xzf "$tarball" -C "$ANYDESK_INSTALL_DIR" --strip-components=1 2>/dev/null; then
            echo -e "${RED}✗ 解压失败${NC}"
            return 1
        fi
        echo -e "${GREEN}✓ 解压完成${NC}"

        echo ""
        echo "步骤4: 设置权限"
        chmod +x "$ANYDESK_EXECUTABLE" && echo -e "${GREEN}✓ 权限设置完成${NC}" || { echo -e "${RED}✗ 设置权限失败${NC}"; return 1; }

        echo ""
        echo "步骤5: 创建软链接"
        ln -sf "$ANYDESK_EXECUTABLE" "$ANYDESK_SYMLINK" && echo -e "${GREEN}✓ 软链接创建完成: $ANYDESK_SYMLINK${NC}"

        echo ""
        echo "步骤6: 创建桌面快捷方式"
        cat > "$ANYDESK_DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AnyDesk
Exec=$ANYDESK_EXECUTABLE
Icon=$ANYDESK_INSTALL_DIR/icons/hicolor/256x256/apps/anydesk.png
Type=Application
Categories=Network;RemoteAccess;
Comment=AnyDesk远程控制软件
Terminal=false
StartupNotify=true
EOF
        chmod +x "$ANYDESK_DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已创建（在应用菜单中）${NC}"

        cp "$ANYDESK_DESKTOP_FILE" "$DESKTOP_DIR/"
        echo -e "${GREEN}✓ 桌面快捷方式已复制到桌面${NC}"

        echo ""
        echo "步骤7: 清理下载文件"
        rm -f "$ANYDESK_DOWNLOAD_DIR/$tarball"
        echo -e "${GREEN}✓ 清理完成${NC}"

        echo ""
        echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
        echo -e "${GREEN}✓ AnyDesk ${version} 安装完成！${NC}"
        echo -e "${GREEN}✓ 安装路径: $ANYDESK_INSTALL_DIR${NC}"
        echo -e "${GREEN}✓ 可执行文件: $ANYDESK_EXECUTABLE${NC}"
        echo -e "${GREEN}✓ 您可以在应用菜单中找到 AnyDesk${NC}"
        echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
        return 0
    }

    anydesk_install_update() {
        anydesk_show_header
        echo -e "${YELLOW}══════════════ 安装 / 更新 AnyDesk ══════════════${NC}"
        echo ""

        echo "正在获取最新版本信息..."
        if ! anydesk_get_latest_version_info; then
            read -p "按回车键返回主菜单..." < /dev/tty
            return
        fi

        PORTABLE_VER=$(anydesk_get_installed_version)
        if [ -n "$PORTABLE_VER" ]; then
            echo -e "${GREEN}✓ 当前便携版版本: $PORTABLE_VER${NC}"
            if [ "$PORTABLE_VER" = "$LATEST_VERSION" ]; then
                echo -e "${GREEN}✓ 已是最新版本！${NC}"
                echo ""
                echo "请选择："
                echo "1. 重新安装（覆盖）"
                echo "2. 卸载便携版"
                echo ""
                read -p "请输入选择 [1-2] 输入其他键返回: " choice < /dev/tty
                case $choice in
                    1) echo "正在重新安装..." && anydesk_download_and_install "$LATEST_VERSION" "$DOWNLOAD_URL" ;;
                    2) anydesk_uninstall_portable ;;
                    *) echo "返回主菜单..." ;;
                esac
                read -p "按回车键返回主菜单..." < /dev/tty
                return
            else
                echo -e "${YELLOW}⚠ 发现新版本: $LATEST_VERSION (当前: $PORTABLE_VER)${NC}"
                read -p "是否更新？[Y/n] " update_choice < /dev/tty
                if [[ "$update_choice" =~ ^[Nn]$ ]]; then
                    echo "取消更新"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return
                fi
                [ -d "$ANYDESK_INSTALL_DIR" ] && rm -rf "$ANYDESK_INSTALL_DIR"
                [ -L "$ANYDESK_SYMLINK" ] && rm -f "$ANYDESK_SYMLINK"
                [ -f "$ANYDESK_DESKTOP_FILE" ] && rm -f "$ANYDESK_DESKTOP_FILE"
                echo "正在更新..."
                anydesk_download_and_install "$LATEST_VERSION" "$DOWNLOAD_URL"
                read -p "按回车键返回主菜单..." < /dev/tty
                return
            fi
        fi

        echo "未检测到便携版，检查 Flatpak 版本..."
        if flatpak list 2>/dev/null | grep -q "$ANYDESK_FLATPAK_PKG"; then
            echo -e "${YELLOW}检测到 Flatpak 版本 ($ANYDESK_FLATPAK_PKG)${NC}"
            echo "将在安装便携版前自动卸载 Flatpak 版本。"
            read -p "按回车继续，或按 Ctrl+C 取消..." < /dev/tty
            anydesk_uninstall_flatpak
            echo "继续安装便携版..."
        else
            echo -e "${GREEN}✓ 未检测到 Flatpak 版本${NC}"
        fi

        echo "开始安装最新便携版..."
        anydesk_download_and_install "$LATEST_VERSION" "$DOWNLOAD_URL"
        read -p "按回车键返回主菜单..." < /dev/tty
    }

    anydesk_uninstall_menu() {
        anydesk_show_header
        echo -e "${YELLOW}════════════════ 卸载 AnyDesk ══════════════════${NC}"
        echo ""

        PORTABLE_INSTALLED=false
        FLATPAK_INSTALLED=false
        [ -x "$ANYDESK_EXECUTABLE" ] && PORTABLE_INSTALLED=true
        flatpak list 2>/dev/null | grep -q "$ANYDESK_FLATPAK_PKG" && FLATPAK_INSTALLED=true

        if [ "$PORTABLE_INSTALLED" = false ] && [ "$FLATPAK_INSTALLED" = false ]; then
            echo "未检测到任何已安装的 AnyDesk 版本。"
            read -p "按回车键返回主菜单..." < /dev/tty
            return
        fi

        echo "检测到以下已安装版本："
        valid_choices=""
        if [ "$PORTABLE_INSTALLED" = true ]; then
            echo "  1) 便携版 (官网版本)  -> 卸载此版本"
            valid_choices="1"
        fi
        if [ "$FLATPAK_INSTALLED" = true ]; then
            [ -n "$valid_choices" ] && valid_choices="${valid_choices}/"
            valid_choices="${valid_choices}2"
            echo "  2) Flatpak 版本 (Discover) -> 卸载此版本"
        fi
        if [ "$PORTABLE_INSTALLED" = true ] && [ "$FLATPAK_INSTALLED" = true ]; then
            valid_choices="${valid_choices}/3"
            echo "  3) 同时卸载两者"
        fi
        echo ""
        read -p "请选择要卸载的版本 [${valid_choices}] 或输入其他键返回: " choice < /dev/tty

        case $choice in
            1)
                if [ "$PORTABLE_INSTALLED" = true ]; then
                    anydesk_uninstall_portable
                else
                    echo "便携版未安装。"
                fi
                ;;
            2)
                if [ "$FLATPAK_INSTALLED" = true ]; then
                    anydesk_uninstall_flatpak
                else
                    echo "Flatpak 版本未安装。"
                fi
                ;;
            3)
                if [ "$PORTABLE_INSTALLED" = true ] && [ "$FLATPAK_INSTALLED" = true ]; then
                    anydesk_uninstall_portable
                    anydesk_uninstall_flatpak
                else
                    echo "两个版本未同时安装，无法执行此操作。"
                fi
                ;;
            *)
                echo "返回主菜单..."
                ;;
        esac
        read -p "按回车键返回主菜单..." < /dev/tty
    }

    while true; do
        anydesk_show_header
        echo "请选择操作："
        echo "  1) 安装 / 更新 AnyDesk"
        echo "  2) 卸载 AnyDesk"
        echo ""
        read -p "请输入选择 [1-2]（其他任意键返回主菜单）: " main_choice < /dev/tty
        case $main_choice in
            1) anydesk_install_update ;;
            2) anydesk_uninstall_menu ;;
            *) echo "返回主菜单..." ; break ;;
        esac
    done
}

install_todesk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装ToDesk ════════════════${NC}"

    echo -e "${CYAN}正在安装ToDesk...${NC}"

    echo "禁用SteamOS只读模式..."
    sudo steamos-readonly disable

    echo "执行安装命令: curl -L todesk.lanbai.top | sh"
    curl -L todesk.lanbai.top | sh

    echo ""
    echo -e "${GREEN}✓ ToDesk安装脚本已执行${NC}"
    echo ""
    echo -e "${YELLOW}请在桌面上运行'todesk安装'或'todesk重新安装'的文件来完成安装${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_wps_office() {
    show_header
    echo -e "${YELLOW}════════════════ 安装WPS Office ════════════════${NC}"

    echo "正在检查是否已安装WPS Office..."

    INSTALLED_WPS=""
    for PACKAGE in com.wps.Office cn.wps.wps-office com.kingsoft.wps org.wps.Office; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_WPS="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_WPS" ]; then
        echo -e "${GREEN}✓ 检测到已安装WPS Office${NC}"
        echo "已安装的包名: $INSTALLED_WPS"
        echo ""

        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载WPS Office"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " wps_choice < /dev/tty

        case $wps_choice in
            1)
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_DIR/WPS_Office.desktop" << EOF
[Desktop Entry]
Name=WPS Office
Exec=flatpak run $INSTALLED_WPS
Icon=$INSTALLED_WPS
Type=Application
Categories=Office;
Comment=WPS Office Suite
EOF

                chmod +x "$DESKTOP_DIR/WPS_Office.desktop"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                echo "正在卸载WPS Office..."
                if flatpak uninstall "$INSTALLED_WPS" -y; then
                    echo -e "${GREEN}✓ WPS Office卸载完成${NC}"
                    rm -f "$DESKTOP_DIR/WPS_Office.desktop"
                else
                    echo -e "${RED}✗ WPS Office卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN}未检测到WPS Office，开始安装...${NC}"
    echo ""

    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤3: 搜索WPS Office包"
    echo "正在搜索可用的WPS Office包..."

    if flatpak search wps 2>/dev/null | grep -i wps; then
        echo -e "${GREEN}✓ 找到WPS Office包${NC}"
        WPS_PACKAGE=$(flatpak search wps 2>/dev/null | grep -i "wps" | head -1 | awk '{print $1}')
    else
        WPS_PACKAGE=""
    fi

    echo ""
    echo "步骤4: 安装WPS Office"

    INSTALL_SUCCESS=false

    PACKAGE_NAMES=("com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps" "org.wps.Office")

    for PACKAGE in "${PACKAGE_NAMES[@]}"; do
        echo "尝试安装包: $PACKAGE"
        if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
            echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
            INSTALL_SUCCESS=true
            FINAL_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到WPS Office包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装WPS Office。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤5: 创建桌面快捷方式"
    cat > "$DESKTOP_DIR/WPS_Office.desktop" << EOF
[Desktop Entry]
Name=WPS Office
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=Office;
Comment=WPS Office Suite
EOF

    chmod +x "$DESKTOP_DIR/WPS_Office.desktop"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ WPS Office 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到WPS Office快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到WPS Office${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_qq() {
    show_header
    echo -e "${YELLOW}════════════════ 安装QQ ════════════════${NC}"

    APP_NAME="QQ"
    DESKTOP_FILE="$DESKTOP_DIR/QQ.desktop"

    echo "正在检查是否已安装QQ..."

    INSTALLED_PACKAGE=""
    for PACKAGE in com.qq.QQ com.tencent.qq linuxqq; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        echo -e "${GREEN}✓ 检测到已安装QQ${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载QQ"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice < /dev/tty

        case $app_choice in
            1)
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=QQ
Exec=flatpak run $INSTALLED_PACKAGE
Icon=$INSTALLED_PACKAGE
Type=Application
Categories=Network;InstantMessaging;
Comment=腾讯QQ即时通讯工具
EOF

                chmod +x "$DESKTOP_FILE"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                echo "正在卸载QQ..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ QQ卸载完成${NC}"
                    rm -f "$DESKTOP_FILE"
                else
                    echo -e "${RED}✗ QQ卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN}未检测到QQ，开始安装...${NC}"
    echo ""

    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤3: 安装QQ"

    INSTALL_SUCCESS=false

    PACKAGE_NAMES=("com.qq.QQ" "com.tencent.qq" "io.github.msojocs.qq")

    for PACKAGE in "${PACKAGE_NAMES[@]}"; do
        echo "尝试安装包: $PACKAGE"
        if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
            echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
            INSTALL_SUCCESS=true
            FINAL_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到QQ包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装QQ。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤4: 创建桌面快捷方式"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=QQ
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=Network;InstantMessaging;
Comment=腾讯QQ即时通讯工具
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ QQ 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到QQ快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到QQ${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_wechat() {
    show_header
    echo -e "${YELLOW}════════════════ 安装微信 ════════════════${NC}"

    APP_NAME="微信"
    DESKTOP_FILE="$DESKTOP_DIR/WeChat.desktop"

    echo "正在检查是否已安装微信..."

    INSTALLED_PACKAGE=""
    for PACKAGE in com.tencent.WeChat com.qq.weixin com.tencent.wechat io.github.msojocs.wechat; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        echo -e "${GREEN}✓ 检测到已安装微信${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载微信"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice < /dev/tty

        case $app_choice in
            1)
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=微信
Exec=flatpak run $INSTALLED_PACKAGE
Icon=$INSTALLED_PACKAGE
Type=Application
Categories=Network;InstantMessaging;
Comment=微信即时通讯工具
EOF

                chmod +x "$DESKTOP_FILE"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                echo "正在卸载微信..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ 微信卸载完成${NC}"
                    rm -f "$DESKTOP_FILE"
                else
                    echo -e "${RED}✗ 微信卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN}未检测到微信，开始安装...${NC}"
    echo ""

    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤3: 安装微信"

    INSTALL_SUCCESS=false

    PACKAGE_NAMES=("com.tencent.WeChat" "com.qq.weixin" "com.tencent.wechat" "io.github.msojocs.wechat")

    for PACKAGE in "${PACKAGE_NAMES[@]}"; do
        echo "尝试安装包: $PACKAGE"
        if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
            echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
            INSTALL_SUCCESS=true
            FINAL_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到微信包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装微信。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤4: 创建桌面快捷方式"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=微信
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=Network;InstantMessaging;
Comment=微信即时通讯工具
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ 微信 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到微信快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到微信${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_qqmusic() {
    show_header
    echo -e "${YELLOW}════════════════ 安装QQ音乐 ════════════════${NC}"

    APP_NAME="QQ音乐"
    DESKTOP_FILE="$DESKTOP_DIR/com.qq.QQmusic.desktop"

    echo "正在检查是否已安装QQ音乐..."

    INSTALLED_PACKAGE=""
    for PACKAGE in com.qq.music com.qq.QQmusic; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        echo -e "${GREEN}✓ 检测到已安装QQ音乐${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载QQ音乐"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice < /dev/tty

        case $app_choice in
            1)
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=QQ音乐
Exec=flatpak run $INSTALLED_PACKAGE
Icon=$INSTALLED_PACKAGE
Type=Application
Categories=AudioVideo;Music;
Comment=QQ音乐播放器
EOF

                chmod +x "$DESKTOP_FILE"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                echo "正在卸载QQ音乐..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ QQ音乐卸载完成${NC}"
                    rm -f "$DESKTOP_FILE"
                else
                    echo -e "${RED}✗ QQ音乐卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN}未检测到QQ音乐，开始安装...${NC}"
    echo ""

    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤3: 安装QQ音乐"

    INSTALL_SUCCESS=false

    PACKAGE_NAMES=("com.qq.QQmusic" "com.tencent.QQmusic")

    for PACKAGE in "${PACKAGE_NAMES[@]}"; do
        echo "尝试安装包: $PACKAGE"
        if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
            echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
            INSTALL_SUCCESS=true
            FINAL_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到QQ音乐包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装QQ音乐。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤4: 创建桌面快捷方式"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=QQ音乐
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=AudioVideo;Music;
Comment=QQ音乐播放器
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ QQ音乐 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到QQ音乐快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到QQ音乐${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_baidunetdisk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装百度网盘 ════════════════${NC}"

    APP_NAME="百度网盘"
    DESKTOP_FILE="$DESKTOP_DIR/com.baidu.NetDisk.desktop"

    echo "正在检查是否已安装百度网盘..."

    INSTALLED_PACKAGE=""
    for PACKAGE in com.baidu.NetDisk com.baidu.pan; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        echo -e "${GREEN}✓ 检测到已安装百度网盘${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载百度网盘"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice < /dev/tty

        case $app_choice in
            1)
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=百度网盘
Exec=flatpak run $INSTALLED_PACKAGE
Icon=$INSTALLED_PACKAGE
Type=Application
Categories=Network;FileTransfer;
Comment=百度网盘客户端
EOF

                chmod +x "$DESKTOP_FILE"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                echo "正在卸载百度网盘..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ 百度网盘卸载完成${NC}"
                    rm -f "$DESKTOP_FILE"
                else
                    echo -e "${RED}✗ 百度网盘卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN}未检测到百度网盘，开始安装...${NC}"
    echo ""

    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤3: 安装百度网盘"

    INSTALL_SUCCESS=false

    PACKAGE_NAMES=("com.baidu.NetDisk" "com.baidu.pan")

    for PACKAGE in "${PACKAGE_NAMES[@]}"; do
        echo "尝试安装包: $PACKAGE"
        if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
            echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
            INSTALL_SUCCESS=true
            FINAL_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到百度网盘包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装百度网盘。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤4: 创建桌面快捷方式"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=百度网盘
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=Network;FileTransfer;
Comment=百度网盘客户端
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ 百度网盘 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到百度网盘快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到百度网盘${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_edge() {
    show_header
    echo -e "${YELLOW}════════════════ 安装Edge浏览器 ════════════════${NC}"

    APP_NAME="Edge浏览器"
    DESKTOP_FILE="$DESKTOP_DIR/Microsoft_Edge.desktop"

    echo "正在检查是否已安装Edge浏览器..."

    INSTALLED_PACKAGE=""
    for PACKAGE in com.microsoft.Edge org.mozilla.firefox; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        echo -e "${GREEN}✓ 检测到已安装Edge浏览器${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载Edge浏览器"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice < /dev/tty

        case $app_choice in
            1)
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Microsoft Edge
Exec=flatpak run $INSTALLED_PACKAGE
Icon=$INSTALLED_PACKAGE
Type=Application
Categories=Network;WebBrowser;
Comment=Microsoft Edge浏览器
EOF

                chmod +x "$DESKTOP_FILE"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                echo "正在卸载Edge浏览器..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ Edge浏览器卸载完成${NC}"
                    rm -f "$DESKTOP_FILE"
                else
                    echo -e "${RED}✗ Edge浏览器卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN}未检测到Edge浏览器，开始安装...${NC}"
    echo ""

    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤3: 安装Edge浏览器"

    INSTALL_SUCCESS=false

    PACKAGE_NAMES=("com.microsoft.Edge" "org.mozilla.firefox" "com.google.Chrome")

    for PACKAGE in "${PACKAGE_NAMES[@]}"; do
        echo "尝试安装包: $PACKAGE"
        if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
            echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
            INSTALL_SUCCESS=true
            FINAL_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到Edge浏览器包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装Edge浏览器。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤4: 创建桌面快捷方式"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Microsoft Edge
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=Network;WebBrowser;
Comment=Microsoft Edge浏览器
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Edge浏览器 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到Edge浏览器快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到Edge浏览器${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_chrome() {
    show_header
    echo -e "${YELLOW}════════════════ 安装Google浏览器 ════════════════${NC}"

    APP_NAME="Google浏览器"
    DESKTOP_FILE="$DESKTOP_DIR/Google_Chrome.desktop"

    echo "正在检查是否已安装Google浏览器..."

    INSTALLED_PACKAGE=""
    for PACKAGE in com.google.Chrome org.chromium.Chromium; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        echo -e "${GREEN}✓ 检测到已安装Google浏览器${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载Google浏览器"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice < /dev/tty

        case $app_choice in
            1)
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Google Chrome
Exec=flatpak run $INSTALLED_PACKAGE
Icon=$INSTALLED_PACKAGE
Type=Application
Categories=Network;WebBrowser;
Comment=Google Chrome浏览器
EOF

                chmod +x "$DESKTOP_FILE"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                echo "正在卸载Google浏览器..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ Google浏览器卸载完成${NC}"
                    rm -f "$DESKTOP_FILE"
                else
                    echo -e "${RED}✗ Google浏览器卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${CYAN}未检测到Google浏览器，开始安装...${NC}"
    echo ""

    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    echo ""
    echo "步骤3: 安装Google浏览器"

    INSTALL_SUCCESS=false

    PACKAGE_NAMES=("com.google.Chrome" "org.chromium.Chromium")

    for PACKAGE in "${PACKAGE_NAMES[@]}"; do
        echo "尝试安装包: $PACKAGE"
        if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
            echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
            INSTALL_SUCCESS=true
            FINAL_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到Google浏览器包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装Google浏览器。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo ""
    echo "步骤4: 创建桌面快捷方式"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=Google Chrome
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=Network;WebBrowser;
Comment=Google Chrome浏览器
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ Google浏览器 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到Google浏览器快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到Google浏览器${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..." < /dev/tty
}

steamdeck_cache_manager() {
    show_header
    echo -e "${YELLOW}════════════════ Steam Deck 缓存管理器 ════════════════${NC}"
    echo ""

    echo "正在启动 Steam Deck 缓存管理器..."
    echo "该功能需要图形界面支持，请确保您在桌面模式下运行。"
    echo ""

    if [ -z "$DISPLAY" ]; then
        echo -e "${RED}错误：未检测到图形界面环境。${NC}"
        echo "请确保在桌面模式下运行此功能。"
        echo ""
        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    if ! command -v zenity &> /dev/null; then
        echo -e "${YELLOW}未找到zenity工具，正在尝试安装...${NC}"

        if command -v pacman &> /dev/null; then
            echo "正在安装zenity..."
            sudo pacman -Sy --noconfirm zenity
        elif command -v apt &> /dev/null; then
            echo "正在安装zenity..."
            sudo apt update && sudo apt install -y zenity
        else
            echo -e "${RED}无法自动安装zenity，请手动安装zenity后再试。${NC}"
            echo "安装命令: sudo pacman -S zenity 或 sudo apt install zenity"
            echo ""
            read -p "按回车键返回主菜单..." < /dev/tty
            return
        fi

        if ! command -v zenity &> /dev/null; then
            echo -e "${RED}✗ Zenity安装失败！${NC}"
            echo ""
            read -p "按回车键返回主菜单..." < /dev/tty
            return
        fi
    fi

    echo -e "${GREEN}✓ 环境检查完成，启动缓存管理器...${NC}"
    echo ""

    exec_steamdeck_cache_manager
}

exec_steamdeck_cache_manager() {
    local live=1
    local tmp_dir="$TEMP_DIR/steamdeck_cache_manager"
    local steamapps_dir="/home/deck/.local/share/Steam/steamapps"
    local cache_type="shadercache"

    function create_temp_dirs() {
        mkdir -p "$tmp_dir"
        echo "临时目录: $tmp_dir"
    }

    function check_environment() {
        if [ ! -d "$steamapps_dir" ]; then
            zenity --error --width=400 \
                --text="找不到Steam目录: $steamapps_dir\n请确保Steam已安装且正在运行。"
            return 1
        fi

        if [ ! -d "$steamapps_dir/shadercache" ] && [ ! -d "$steamapps_dir/compatdata" ]; then
            zenity --warning --width=400 \
                --text="在 $steamapps_dir 中找不到缓存目录。\n可能您的缓存位置不同或尚未生成缓存。"
        fi
        return 0
    }

    function find_steam_libraries() {
        local libraries=()

        if [ -d "$steamapps_dir" ]; then
            libraries+=("$steamapps_dir")
        fi

        if [ -f "$steamapps_dir/libraryfolders.vdf" ]; then
            while read -r line; do
                if [[ "$line" =~ \"path\"[[:space:]]*\"([^\"]*)\" ]]; then
                    local path="${BASH_REMATCH[1]}"
                    if [ -d "$path" ]; then
                        local library_path="$path/steamapps"
                        if [ -d "$library_path" ] && [ "$library_path" != "$steamapps_dir" ]; then
                            libraries+=("$library_path")
                        fi
                    fi
                fi
            done < "$steamapps_dir/libraryfolders.vdf"
        fi

        echo "${libraries[@]}"
    }

    function get_game_install_info() {
        local app_id="$1"
        local libraries=($(find_steam_libraries))

        for lib in "${libraries[@]}"; do
            local manifest="$lib/appmanifest_${app_id}.acf"
            if [ -f "$manifest" ]; then
                local game_name=$(grep '"name"' "$manifest" | cut -d'"' -f4)
                local install_dir=$(grep '"installdir"' "$manifest" | cut -d'"' -f4)

                if [ -n "$game_name" ] && [ -n "$install_dir" ]; then
                    local game_path="$lib/common/$install_dir"
                    if [ -d "$game_path" ]; then
                        echo "$game_name|$game_path"
                        return 0
                    fi
                fi
            fi
        done

        echo "Unknown|Unknown"
        return 1
    }

    function get_delete_list() {
        local cache_type="$1"

        rm -f "$tmp_dir/delete_list.txt" 2>/dev/null

        if [ ! -d "$steamapps_dir/$cache_type" ]; then
            echo "FALSE|0|0|No $cache_type directory found|N/A|$steamapps_dir/$cache_type" > "$tmp_dir/delete_list.txt"
            return
        fi

        local count=0
        for cache_dir in "$steamapps_dir/$cache_type"/*; do
            if [ -d "$cache_dir" ]; then
                local app_id=$(basename "$cache_dir")

                if [[ ! "$app_id" =~ ^[0-9]+$ ]]; then
                    continue
                fi

                local size=$(du -sm "$cache_dir" 2>/dev/null | cut -f1)
                if [ -z "$size" ] || [ "$size" -eq 0 ]; then
                    continue
                fi

                local game_info=$(get_game_install_info "$app_id")
                local game_name=$(echo "$game_info" | cut -d'|' -f1)
                local game_path=$(echo "$game_info" | cut -d'|' -f2)

                local status="Unknown"
                if [ "$game_name" != "Unknown" ] && [ -d "$game_path" ]; then
                    status="Installed"
                elif [ "$game_name" != "Unknown" ]; then
                    status="Uninstalled"
                fi

                echo "FALSE|$size|$app_id|$game_name|$status|$cache_dir" >> "$tmp_dir/delete_list.txt"
                count=$((count+1))
            fi
        done

        if [ $count -eq 0 ]; then
            echo "FALSE|0|0|No $cache_type found|N/A|$steamapps_dir/$cache_type" > "$tmp_dir/delete_list.txt"
        fi
    }

    function get_move_list() {
        local cache_type="$1"

        rm -f "$tmp_dir/move_list.txt" 2>/dev/null

        if [ ! -d "$steamapps_dir/$cache_type" ]; then
            echo "FALSE|0|0|No $cache_type directory found|N/A|N/A" > "$tmp_dir/move_list.txt"
            return
        fi

        local libraries=($(find_steam_libraries))
        local count=0

        for lib in "${libraries[@]}"; do
            if [ "$lib" == "$steamapps_dir" ]; then
                continue
            fi

            for manifest in "$lib"/appmanifest_*.acf; do
                if [ -f "$manifest" ]; then
                    local app_id=$(basename "$manifest" | sed 's/appmanifest_\(.*\)\.acf/\1/')
                    local game_name=$(grep '"name"' "$manifest" | cut -d'"' -f4)
                    local install_dir=$(grep '"installdir"' "$manifest" | cut -d'"' -f4)

                    if [ -n "$app_id" ] && [ -n "$game_name" ] && [ -n "$install_dir" ]; then
                        local cache_dir="$steamapps_dir/$cache_type/$app_id"
                        if [ -d "$cache_dir" ] && [ ! -L "$cache_dir" ]; then
                            local size=$(du -sm "$cache_dir" 2>/dev/null | cut -f1)
                            if [ -n "$size" ] && [ "$size" -gt 0 ]; then
                                local game_path="$lib/common/$install_dir"

                                echo "FALSE|$size|$app_id|$game_name|$game_path" >> "$tmp_dir/move_list.txt"
                                count=$((count+1))
                            fi
                        fi
                    fi
                fi
            done
        done

        if [ $count -eq 0 ]; then
            echo "FALSE|0|0|No $cache_type to move|N/A" > "$tmp_dir/move_list.txt"
        fi
    }

    function show_delete_dialog() {
        local cache_type="$1"
        local title="选择要删除的$cache_type"

        if [ "$cache_type" = "compatdata" ]; then
            title="⚠  警告：选择要删除的兼容数据（将破坏游戏配置！）"
        fi

        local zenity_items=()
        while IFS='|' read -r check size app_id game_name status path; do
            if [ "$size" != "0" ] && [ "$app_id" != "0" ]; then
                zenity_items+=("$check" "$size" "$app_id" "$game_name" "$status" "$path")
            fi
        done < "$tmp_dir/delete_list.txt"

        if [ ${#zenity_items[@]} -eq 0 ]; then
            zenity --info --width=400 --text="没有找到可删除的$cache_type。"
            echo "empty"
            return
        fi

        local selected=$(zenity --list \
            --title="$title" \
            --width=1200 --height=600 \
            --print-column=6 \
            --separator="|" \
            --ok-label="删除选中的$cache_type" \
            --extra-button="切换缓存类型" \
            --checklist \
            --column="选择" \
            --column="大小(MB)" \
            --column="应用ID" \
            --column="游戏名称" \
            --column="状态" \
            --column="路径" \
            "${zenity_items[@]}")

        echo "$selected"
    }

    function show_move_dialog() {
        local cache_type="$1"

        local zenity_items=()
        while IFS='|' read -r check size app_id game_name game_path; do
            if [ "$size" != "0" ] && [ "$app_id" != "0" ]; then
                zenity_items+=("$check" "$size" "$app_id" "$game_name" "$game_path")
            fi
        done < "$tmp_dir/move_list.txt"

        if [ ${#zenity_items[@]} -eq 0 ]; then
            zenity --info --width=400 --text="没有找到可移动的$cache_type。"
            echo "empty"
            return
        fi

        local selected=$(zenity --list \
            --title="选择要移动到游戏安装目录的$cache_type" \
            --width=1200 --height=600 \
            --print-column=3 \
            --separator="|" \
            --ok-label="移动选中的$cache_type" \
            --extra-button="切换缓存类型" \
            --checklist \
            --column="选择" \
            --column="大小(MB)" \
            --column="应用ID" \
            --column="游戏名称" \
            --column="游戏安装目录" \
            "${zenity_items[@]}")

        echo "$selected"
    }

    function perform_delete() {
        local cache_type="$1"
        local selected_items="$2"

        if [ -z "$selected_items" ] || [ "$selected_items" = "empty" ]; then
            return 1
        fi

        IFS='|' read -ra selected_array <<< "$selected_items"

        if [ ${#selected_array[@]} -eq 0 ]; then
            zenity --error --width=400 --text="没有选择任何$cache_type！"
            return 1
        fi

        if [ "$cache_type" = "compatdata" ]; then
            zenity --question --width=500 \
                --text="⚠  严重警告！\n\n删除兼容数据将：\n• 删除游戏存档和设置\n• 删除Wine前缀配置\n• 可能导致游戏无法启动\n\n仅当您知道自己在做什么时才继续！\n确定要删除选中的兼容数据吗？"

            if [ $? -ne 0 ]; then
                return 1
            fi
        else
            zenity --question --width=400 \
                --text="确定要删除选中的着色器缓存吗？\n游戏下次运行时需要重新编译着色器，可能导致首次加载变慢。"

            if [ $? -ne 0 ]; then
                return 1
            fi
        fi

        (
            local total=${#selected_array[@]}
            local current=0

            for item in "${selected_array[@]}"; do
                ((current++))
                local percentage=$((current * 100 / total))

                echo "# 正在删除: $(basename "$item")"
                echo "$percentage"

                if [ $live -eq 1 ]; then
                    rm -rf "$item" 2>/dev/null
                fi

                sleep 0.5
            done

            if [ $live -eq 1 ]; then
                echo "# $cache_type 删除完成！"
            else
                echo "# 模拟运行 - 实际未删除任何文件"
            fi
        ) | zenity --progress \
            --title="删除$cache_type" \
            --percentage=0 \
            --auto-close \
            --width=400

        return $?
    }

    function perform_move() {
        local cache_type="$1"
        local selected_items="$2"

        if [ -z "$selected_items" ] || [ "$selected_items" = "empty" ]; then
            return 1
        fi

        IFS='|' read -ra selected_array <<< "$selected_items"

        if [ ${#selected_array[@]} -eq 0 ]; then
            zenity --error --width=400 --text="没有选择任何$cache_type！"
            return 1
        fi

        (
            local total=${#selected_array[@]}
            local current=0

            for app_id in "${selected_array[@]}"; do
                ((current++))
                local percentage=$((current * 100 / total))

                local game_info=$(get_game_install_info "$app_id")
                local game_name=$(echo "$game_info" | cut -d'|' -f1)
                local game_path=$(echo "$game_info" | cut -d'|' -f2)

                echo "# 正在移动 $app_id ($game_name)"
                echo "$percentage"

                if [ $live -eq 1 ]; then
                    local source_dir="$steamapps_dir/$cache_type/$app_id"
                    local target_dir="$game_path/$cache_type"

                    mkdir -p "$target_dir" 2>/dev/null

                    if cp -r "$source_dir" "$target_dir/" 2>/dev/null; then
                        rm -rf "$source_dir" 2>/dev/null

                        ln -s "$target_dir/$app_id" "$source_dir" 2>/dev/null
                    fi
                fi

                sleep 1
            done

            if [ $live -eq 1 ]; then
                echo "# $cache_type 移动完成！"
            else
                echo "# 模拟运行 - 实际未移动任何文件"
            fi
        ) | zenity --progress \
            --title="移动$cache_type" \
            --percentage=0 \
            --auto-close \
            --width=400

        return $?
    }

    function show_main_menu() {
        local choice=$(zenity --list \
            --title="Steam Deck 缓存管理器" \
            --width=500 --height=350 \
            --text="选择要执行的操作：" \
            --column="操作" \
            --column="描述" \
            "删除着色器缓存" "删除选中的着色器缓存文件" \
            "删除兼容数据" "删除选中的兼容数据（危险！）" \
            "移动着色器缓存" "将着色器缓存移动到游戏目录" \
            "移动兼容数据" "将兼容数据移动到游戏目录" \
            "切换模式" "切换实际执行/模拟运行" \
            "退出" "退出程序")

        echo "$choice"
    }

    function show_status() {
        local mode_text=""
        if [ $live -eq 1 ]; then
            mode_text="实际执行模式"
        else
            mode_text="模拟运行模式"
        fi

        local shader_size="N/A"
        local compat_size="N/A"

        if [ -d "$steamapps_dir/shadercache" ]; then
            shader_size=$(du -sh "$steamapps_dir/shadercache" 2>/dev/null | cut -f1)
        fi

        if [ -d "$steamapps_dir/compatdata" ]; then
            compat_size=$(du -sh "$steamapps_dir/compatdata" 2>/dev/null | cut -f1)
        fi

        echo "=== Steam Deck 缓存管理器 ==="
        echo "模式: $mode_text"
        echo "着色器缓存大小: $shader_size"
        echo "兼容数据大小: $compat_size"
        echo "临时目录: $tmp_dir"
        echo "============================="
    }

    function cache_manager_main() {
        check_environment || return 1

        create_temp_dirs

        while true; do
            local choice=$(show_main_menu)

            if [ $? -ne 0 ] || [ -z "$choice" ]; then
                echo "退出程序"
                return 0
            fi

            case "$choice" in
                "删除着色器缓存")
                    echo "正在获取着色器缓存列表..."
                    get_delete_list "shadercache"
                    local selected=$(show_delete_dialog "shadercache")

                    if [ "$selected" = "切换缓存类型" ]; then
                        echo "切换到兼容数据删除..."
                        get_delete_list "compatdata"
                        selected=$(show_delete_dialog "compatdata")
                        perform_delete "compatdata" "$selected"
                    elif [ -n "$selected" ] && [ "$selected" != "empty" ]; then
                        perform_delete "shadercache" "$selected"
                    fi
                    ;;

                "删除兼容数据")
                    echo "正在获取兼容数据列表..."
                    get_delete_list "compatdata"
                    local selected=$(show_delete_dialog "compatdata")

                    if [ "$selected" = "切换缓存类型" ]; then
                        echo "切换到着色器缓存删除..."
                        get_delete_list "shadercache"
                        selected=$(show_delete_dialog "shadercache")
                        perform_delete "shadercache" "$selected"
                    elif [ -n "$selected" ] && [ "$selected" != "empty" ]; then
                        perform_delete "compatdata" "$selected"
                    fi
                    ;;

                "移动着色器缓存")
                    echo "正在获取可移动的着色器缓存列表..."
                    get_move_list "shadercache"
                    local selected=$(show_move_dialog "shadercache")

                    if [ "$selected" = "切换缓存类型" ]; then
                        echo "切换到兼容数据移动..."
                        get_move_list "compatdata"
                        selected=$(show_move_dialog "compatdata")
                        perform_move "compatdata" "$selected"
                    elif [ -n "$selected" ] && [ "$selected" != "empty" ]; then
                        perform_move "shadercache" "$selected"
                    fi
                    ;;

                "移动兼容数据")
                    echo "正在获取可移动的兼容数据列表..."
                    get_move_list "compatdata"
                    local selected=$(show_move_dialog "compatdata")

                    if [ "$selected" = "切换缓存类型" ]; then
                        echo "切换到着色器缓存移动..."
                        get_move_list "shadercache"
                        selected=$(show_move_dialog "shadercache")
                        perform_move "shadercache" "$selected"
                    elif [ -n "$selected" ] && [ "$selected" != "empty" ]; then
                        perform_move "compatdata" "$selected"
                    fi
                    ;;

                "切换模式")
                    if [ $live -eq 1 ]; then
                        live=0
                        zenity --info --width=300 --text="已切换到模拟运行模式\n（不会实际修改文件）"
                    else
                        live=1
                        zenity --info --width=300 --text="已切换到实际执行模式"
                    fi
                    ;;

                "退出")
                    echo "退出程序"
                    return 0
                    ;;
            esac
        done
    }

    cache_manager_main

    echo ""
    echo "缓存管理器操作完成。"
    read -p "按回车键返回主菜单..." < /dev/tty
}

# ==================== 修改后的更新全部应用 ====================
update_installed_apps() {
    show_header
    echo -e "${YELLOW}════════════════ 更新全部应用 ════════════════${NC}"
    echo ""
    read -p "是否更新所有已安装的 Flatpak 应用？(y/N): " confirm < /dev/tty
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}正在更新所有应用...${NC}"
        flatpak update -y
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 所有应用更新完成${NC}"
        else
            echo -e "${RED}✗ 更新过程中出现错误${NC}"
        fi
    else
        echo "取消更新。"
    fi
    read -p "按回车键返回主菜单..." < /dev/tty
}

# ==================== 修改后的卸载已安装应用（移除 AnyDesk） ====================
uninstall_apps() {
    show_header
    echo -e "${YELLOW}════════════════ 卸载已安装应用 ════════════════${NC}"
    echo ""

    echo "请选择要卸载的应用："
    echo "1. WPS Office"
    echo "2. QQ"
    echo "3. 微信"
    echo "4. QQ音乐"
    echo "5. 百度网盘"
    echo "6. Edge浏览器"
    echo "7. Google浏览器"
    echo ""

    read -p "请输入选择 [1-7] (输入其他键返回主菜单): " app_choice < /dev/tty

    case $app_choice in
        1)
            uninstall_app_by_name "WPS Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps" "org.wps.Office" "$DESKTOP_DIR/WPS_Office.desktop"
            ;;
        2)
            uninstall_app_by_name "QQ" "com.qq.QQ" "com.tencent.qq" "io.github.msojocs.qq" "$DESKTOP_DIR/QQ.desktop"
            ;;
        3)
            uninstall_app_by_name "微信" "com.tencent.WeChat" "com.qq.weixin" "com.tencent.wechat" "io.github.msojocs.wechat" "$DESKTOP_DIR/WeChat.desktop"
            ;;
        4)
            uninstall_app_by_name "QQ音乐" "com.qq.QQmusic" "com.tencent.QQmusic" "$DESKTOP_DIR/com.qq.QQmusic.desktop"
            ;;
        5)
            uninstall_app_by_name "百度网盘" "com.baidu.NetDisk" "com.baidu.pan" "$DESKTOP_DIR/com.baidu.NetDisk.desktop"
            ;;
        6)
            uninstall_app_by_name "Edge浏览器" "com.microsoft.Edge" "org.mozilla.firefox" "com.google.Chrome" "$DESKTOP_DIR/Microsoft_Edge.desktop"
            ;;
        7)
            uninstall_app_by_name "Google浏览器" "com.google.Chrome" "org.chromium.Chromium" "$DESKTOP_DIR/Google_Chrome.desktop"
            ;;
        *)
            echo "返回主菜单..."
            return
            ;;
    esac

    read -p "按回车键返回主菜单..." < /dev/tty
}

uninstall_app_by_name() {
    local app_name="$1"
    shift
    local packages=("$@")

    local desktop_file="${!#}"
    set -- "${@:1:$(($#-1))}"

    echo ""
    echo -e "${CYAN}正在检查是否已安装$app_name...${NC}"

    local installed_package=""
    for package in "${packages[@]}"; do
        if flatpak list | grep -q "$package"; then
            installed_package="$package"
            break
        fi
    done

    if [ -n "$installed_package" ]; then
        echo "找到已安装的包: $installed_package"
        echo ""
        echo -e "${YELLOW}警告：您即将卸载 $app_name${NC}"
        read -p "是否继续？(输入 y 确认，其他键取消): " -n 1 -r < /dev/tty
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "操作已取消。"
            return
        fi

        echo "正在卸载$app_name..."

        if flatpak uninstall "$installed_package" -y 2>/dev/null; then
            echo -e "${GREEN}✓ $app_name 卸载完成${NC}"

            if [ -f "$desktop_file" ]; then
                rm -f "$desktop_file"
                echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
            fi
        else
            echo -e "${RED}✗ $app_name 卸载失败${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  未检测到已安装的$app_name${NC}"
        echo "无需卸载。"

        if [ -f "$desktop_file" ]; then
            echo "检测到残留的桌面快捷方式。"
            read -p "是否删除桌面快捷方式？(输入 y 确认，其他键取消): " -n 1 -r < /dev/tty
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -f "$desktop_file"
                echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
            fi
        fi
    fi

    read -p "按回车键返回..." < /dev/tty
}

install_yellow_duck_software() {
    show_header
    echo -e "${YELLOW}════════════════ 安装小黄鸭软件 ════════════════${NC}"

    local temp_dir="$TEMP_DIR/yellow_duck_software"
    mkdir -p "$temp_dir"

    cat > "$temp_dir/install_lossless_scaling.sh" << 'EOF'
#!/bin/bash

check_lossless_scaling() {
    echo "检测小黄鸭软件安装状态..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    local LOSS_DIR="/home/deck/.local/share/Steam/steamapps/common/Lossless Scaling"

    if [[ -d "$LOSS_DIR" ]]; then
        echo "✅ 检测到已安装小黄鸭软件。"
        echo "   安装目录: $LOSS_DIR"
        echo ""

        read -p "是否要卸载小黄鸭软件？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "开始卸载小黄鸭软件..."
            if sudo rm -rf "$LOSS_DIR"; then
                echo "✅ 小黄鸭软件已成功卸载。"
                echo ""
                echo "卸载完成，脚本退出。"
            else
                echo "❌ 卸载失败，请检查权限。"
            fi
            exit 0
        else
            echo "脚本退出。"
            exit 0
        fi
    else
        echo "未检测到小黄鸭软件，准备从Gitee仓库安装..."
        return 1
    fi
}

check_zip_tools() {
    echo "检查必要的解压工具..."

    local missing_tools=()

    if ! command -v zip &> /dev/null; then
        missing_tools+=("zip")
    fi

    if ! command -v unzip &> /dev/null; then
        missing_tools+=("unzip")
    fi

    if [[ ${#missing_tools[@]} -gt 0 ]]; then
        echo "需要安装以下工具: ${missing_tools[*]}"
        read -p "是否现在安装？(y/N): " -n 1 -r < /dev/tty
        echo ""

        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "正在安装必要的工具..."
            sudo pacman -S --needed --noconfirm "${missing_tools[@]}"

            for tool in "${missing_tools[@]}"; do
                if ! command -v "$tool" &> /dev/null; then
                    echo "❌ 安装 $tool 失败，请手动安装后再运行脚本。"
                    exit 1
                fi
            done
            echo "✅ 工具安装完成。"
        else
            echo "❌ 需要解压工具才能继续，请手动安装后重试。"
            exit 1
        fi
    else
        echo "✅ 解压工具已就绪。"
    fi
    echo ""
}

clone_from_gitee() {
    local CLONE_DIR="$HOME/lossless-scaling-repo"
    local GITEE_REPO="https://gitee.com/Zhucy2100/lossless-scaling.git"

    if [[ -d "$CLONE_DIR" ]]; then
        echo "清理旧仓库目录..."
        rm -rf "$CLONE_DIR"
    fi

    echo "开始从Gitee克隆仓库..."
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "仓库地址: $GITEE_REPO"
    echo ""

    if git clone --depth=1 --progress "$GITEE_REPO" "$CLONE_DIR" 2>&1; then
        echo ""
        echo "✅ 从Gitee克隆成功！"
        echo "仓库位置: $CLONE_DIR"
        return 0
    else
        echo ""
        echo "❌ 从Gitee克隆失败！"
        echo "可能的原因:"
        echo "1. 网络连接问题"
        echo "2. 仓库地址不存在或已更改"
        echo "3. Gitee服务器暂时不可用"
        echo ""
        echo "请检查网络连接后重试。"
        exit 1
    fi
}

validate_split_files() {
    local CLONE_DIR="$1"
    local split_files=(
        "Lossless Scaling.zip.001"
        "Lossless Scaling.zip.002"
        "Lossless Scaling.zip.003"
        "Lossless Scaling.zip.004"
        "Lossless Scaling.zip.005"
        "Lossless Scaling.zip.006"
        "Lossless Scaling.zip.007"
    )

    echo "验证分卷压缩文件（共7个分卷）..."

    local missing_files=()
    for file in "${split_files[@]}"; do
        if [[ ! -f "$CLONE_DIR/$file" ]]; then
            missing_files+=("$file")
        fi
    done

    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo "❌ 缺少必要的分卷文件:"
        for file in "${missing_files[@]}"; do
            echo "   - $file"
        done
        echo ""
        echo "当前目录内容:"
        ls -la "$CLONE_DIR"
        return 1
    fi

    echo "✅ 找到所有7个分卷文件:"
    for file in "${split_files[@]}"; do
        local file_size=$(stat -c%s "$CLONE_DIR/$file" 2>/dev/null || stat -f%z "$CLONE_DIR/$file" 2>/dev/null)
        if [[ $file_size -gt 0 ]]; then
            local size_mb=$(echo "scale=2; $file_size / 1024 / 1024" | bc)
            echo "   - $file (${size_mb} MB)"
        else
            echo "   - $file (大小未知)"
        fi
    done

    echo "✅ 所有分卷文件验证通过。"
    echo ""
    return 0
}

extract_split_files() {
    local CLONE_DIR="$1"
    local TARGET_DIR="/home/deck/.local/share/Steam/steamapps/common"

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "步骤: 合并并解压7个分卷文件"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""

    echo "检查目标目录: $TARGET_DIR"
    if [[ ! -d "$TARGET_DIR" ]]; then
        echo "创建目标目录..."
        mkdir -p "$TARGET_DIR"
        sudo chown deck:deck "$TARGET_DIR"
    fi

    cd "$CLONE_DIR" || {
        echo "❌ 无法进入目录: $CLONE_DIR"
        return 1
    }

    echo "正在合并7个分卷文件..."
    echo "注意：合并过程可能需要一些时间，请耐心等待..."

    if ls "Lossless Scaling.zip."* > /dev/null 2>&1; then
        echo "找到分卷文件，开始合并..."
        if cat "Lossless Scaling.zip."* > "Lossless-Scaling-Combined.zip"; then
            echo "✅ 7个分卷文件合并完成。"

            echo "验证合并后的文件..."
            if unzip -tq "Lossless-Scaling-Combined.zip" > /dev/null 2>&1; then
                echo "✅ ZIP文件完整性验证通过。"
            else
                echo "⚠️  ZIP文件完整性验证失败，但继续解压..."
            fi

            echo ""
            echo "正在解压到目标目录: $TARGET_DIR"

            if unzip -o "Lossless-Scaling-Combined.zip" -d "$TARGET_DIR" 2>&1 | tail -20; then
                echo ""
                echo "✅ 解压完成！"

                echo "清理临时文件..."
                rm -f "Lossless-Scaling-Combined.zip"

                local EXTRACTED_DIR="$TARGET_DIR/Lossless Scaling"
                if [[ -d "$EXTRACTED_DIR" ]]; then
                    echo "解压目录: $EXTRACTED_DIR"

                    sudo chown -R deck:deck "$EXTRACTED_DIR"
                    sudo chmod -R 755 "$EXTRACTED_DIR"

                    local exe_files=$(find "$EXTRACTED_DIR" -name "*.exe" -o -name "*.EXE" | head -5)
                    if [[ -n "$exe_files" ]]; then
                        echo "找到的可执行文件:"
                        echo "$exe_files" | while read -r file; do
                            echo "  - $(basename "$file")"
                        done
                    fi

                    local total_size=$(du -sh "$EXTRACTED_DIR" 2>/dev/null | cut -f1)
                    echo "安装总大小: $total_size"

                    return 0
                else
                    echo "❌ 解压后未找到 'Lossless Scaling' 目录"
                    echo "当前目录内容:"
                    ls -la "$TARGET_DIR"
                    return 1
                fi
            else
                echo ""
                echo "❌ 解压失败！"
                echo "可能的原因:"
                echo "1. ZIP文件损坏"
                echo "2. 磁盘空间不足"
                echo "3. 文件权限问题"
                return 1
            fi
        else
            echo "❌ 分卷文件合并失败！"
            echo "请检查分卷文件是否完整。"
            return 1
        fi
    else
        echo "❌ 未找到分卷文件！"
        echo "当前目录内容:"
        ls -la
        return 1
    fi
}

cleanup_repository() {
    local CLONE_DIR="$1"

    echo ""
    echo "清理克隆的仓库..."
    if [[ -d "$CLONE_DIR" ]]; then
        if rm -rf "$CLONE_DIR"; then
            echo "✅ 仓库目录已清理。"
        else
            echo "⚠️  警告: 仓库目录清理失败，可手动删除: $CLONE_DIR"
        fi
    fi
}

show_installation_complete() {
    local INSTALL_DIR="/home/deck/.local/share/Steam/steamapps/common/Lossless Scaling"

    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo " 小黄鸭软件安装完成！"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "安装目录: $INSTALL_DIR"
    echo ""
    echo "使用说明:"
    echo "1. 打开 Steam，进入库页面"
    echo "2. 点击左下角 '添加游戏' → '添加非Steam游戏'"
    echo "3. 浏览到安装目录，选择 Lossless Scaling 可执行文件"
    echo "4. 在游戏模式中，可以通过 Steam 库启动小黄鸭软件"
    echo ""
    echo "注意:"
    echo "• 首次运行可能需要配置 Proton 兼容层"
    echo "• 建议使用 Proton GE 或 Proton Experimental"
    echo "• 在 Steam Deck 性能设置中，可以为该程序分配更多显存"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

main() {
    clear
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Steam Deck 小黄鸭软件安装助手 (Gitee版)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "使用国内Gitee仓库，下载速度更快"
    echo ""

    if check_lossless_scaling; then
        return
    fi

    check_zip_tools

    echo ""
    echo "即将安装小黄鸭软件 (Lossless Scaling)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "安装说明:"
    echo "• 使用国内Gitee仓库，下载速度快"
    echo "• 需要约 175 MB 磁盘空间"
    echo "• 需要合并7个分卷文件，请耐心等待"
    echo "• 仓库地址: https://gitee.com/Zhucy2100/lossless-scaling"
    echo ""

    read -p "是否继续安装？(y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "安装已取消。"
        exit 0
    fi

    clone_from_gitee
    local CLONE_DIR="$HOME/lossless-scaling-repo"

    if ! validate_split_files "$CLONE_DIR"; then
        cleanup_repository "$CLONE_DIR"
        exit 1
    fi

    if ! extract_split_files "$CLONE_DIR"; then
        cleanup_repository "$CLONE_DIR"
        exit 1
    fi

    cleanup_repository "$CLONE_DIR"

    show_installation_complete

    echo ""
    read -p "按回车键退出..." < /dev/tty
}

main
EOF

    chmod +x "$temp_dir/install_lossless_scaling.sh"
    echo "正在启动小黄鸭软件安装助手..."
    echo ""
    "$temp_dir/install_lossless_scaling.sh"

    rm -rf "$temp_dir"

    echo ""
    read -p "按回车键返回主菜单..." < /dev/tty
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
        echo "3. 返回主菜单"
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
                read -p "按回车键返回主菜单..." < /dev/tty
                return
                ;;
            3)
                echo "返回主菜单..."
                return
                ;;
            *)
                echo "无效选择，返回主菜单..."
                return
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
        read -p "按回车键返回主菜单..." < /dev/tty
        return
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
            read -p "按回车键返回主菜单..." < /dev/tty
            return
        }
    fi

    local download_url="https://www.dogfight360.com/blog/wp-content/uploads/2025/12/steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"
    local filename="steamcommunity_302_Linux_AMD64_V14.0.01.tar.gz"

    echo "正在下载文件..."
    wget --show-progress "$download_url"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 下载失败，请检查网络连接${NC}"
        echo "可以尝试手动下载后放置到 $install_dir 目录"
        read -p "按回车键返回主菜单..." < /dev/tty
        return
    fi

    echo -e "${GREEN}✓ 下载完成${NC}"
    echo ""

    echo "步骤2: 解压文件..."
    tar -xzf "$filename"

    if [ $? -ne 0 ]; then
        echo -e "${RED}✗ 解压失败${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return
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
            read -p "按回车键返回主菜单..." < /dev/tty
            return
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
    echo "2. 如需卸载，请重新运行此功能并选择卸载选项"
    echo "3. 卸载时会同时清理桌面快捷方式和安装文件"
    echo ""

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_decky_lsfg_vk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装/卸载 LSFG-VK 插件 ════════════════${NC}"
    echo ""

    local GITHUB_REPO="xXJSONDeruloXx/decky-lsfg-vk"
    local PLUGIN_DIR="/home/deck/homebrew/plugins"
    local TARGET_DIR="${PLUGIN_DIR}/Decky-LSFG-VK"
    local TEMP_DIR="/tmp/decky_lsfg_vk_install"
    local MIRRORS=(
        "https://ghproxy.net/"
        "https://gh.ddlc.top/"
        "https://mirror.ghproxy.com/"
        "https://gh.api.99988866.xyz/"
        "https://download.fastgit.org/"
        "https://hub.gitmirror.com/"
        "https://git.xfj0.xyz/"
        "https://github.com/"
    )
    local DOWNLOAD_TIMEOUT=60
    local MAX_RETRY_PER_MIRROR=1

    for cmd in curl sudo unzip; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            read -p "按回车键返回主菜单..." < /dev/tty
            return 1
        fi
    done

    echo "请选择要执行的操作："
    echo "1. 安装/更新 LSFG-VK 插件"
    echo "2. 卸载 LSFG-VK 插件"
    echo ""

    read -p "请输入选择 [1-2] (输入其他键返回): " action_choice < /dev/tty

    case $action_choice in
        1)
            echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
            local releases_json=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases")
            local versions_info=$(echo "$releases_json" | grep -E '("tag_name":|"prerelease":)' | paste -d ' ' - - | sed 's/.*"tag_name": "\([^"]*\)".*"prerelease": \([^,]*\).*/\1|\2/')
            local stable_versions=()
            local prerelease_versions=()
            while IFS='|' read -r tag prerelease; do
                [ -z "$tag" ] && continue
                if [[ "$prerelease" == "true" ]]; then
                    prerelease_versions+=("$tag")
                else
                    stable_versions+=("$tag")
                fi
            done <<< "$versions_info"

            local latest_stable=""
            local latest_prerelease=""
            if [ ${#stable_versions[@]} -gt 0 ]; then
                latest_stable=$(printf '%s\n' "${stable_versions[@]}" | sed 's/^v//' | sort -V | tail -1)
                latest_stable="v${latest_stable}"
            fi
            if [ ${#prerelease_versions[@]} -gt 0 ]; then
                latest_prerelease=$(printf '%s\n' "${prerelease_versions[@]}" | sed 's/^v//' | sort -V | tail -1)
                latest_prerelease="v${latest_prerelease}"
            fi

            # 比较预发布版本是否高于正式版，若不是则忽略预发布
            if [ -n "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                local stable_num=$(echo "$latest_stable" | sed 's/^v//')
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                if [[ "$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)" != "$prerelease_num" ]]; then
                    latest_prerelease=""
                fi
            fi

            local installed_version=""
            if [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/package.json" ]; then
                installed_version=$(grep -o '"version": *"[^"]*"' "$TARGET_DIR/package.json" | head -1 | sed 's/.*"version": *"//; s/".*//')
                if [ -n "$installed_version" ]; then
                    installed_version="v${installed_version}"
                    echo -e "${CYAN}已安装版本: ${installed_version}${NC}"
                fi
            fi

            local target_version=""
            if [ -n "$installed_version" ]; then
                if [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                    echo -e "${GREEN}已安装最新正式版 ${installed_version}${NC}"
                    echo -e "${YELLOW}发现更高版本的预发布版: ${latest_prerelease}${NC}"
                    read -p "是否升级到预发布版？(y/N): " upgrade < /dev/tty
                    if [[ $upgrade =~ ^[Yy]$ ]]; then
                        target_version="$latest_prerelease"
                    else
                        echo "保持当前版本。"
                        read -p "按回车键返回主菜单..." < /dev/tty
                        return 0
                    fi
                elif [ -n "$latest_prerelease" ] && [ "$installed_version" = "$latest_prerelease" ] && [ -n "$latest_stable" ]; then
                    echo -e "${GREEN}已安装最新预发布版 ${installed_version}${NC}"
                    echo -e "${YELLOW}当前正式版为: ${latest_stable}${NC}"
                    read -p "是否切换到正式版？(y/N): " switch < /dev/tty
                    if [[ $switch =~ ^[Yy]$ ]]; then
                        target_version="$latest_stable"
                    else
                        echo "保持当前版本。"
                        read -p "按回车键返回主菜单..." < /dev/tty
                        return 0
                    fi
                elif [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ] && [ -z "$latest_prerelease" ]; then
                    echo -e "${GREEN}已经是最新版本 (正式版 ${installed_version})，无需更新。${NC}"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 0
                elif [ -n "$latest_prerelease" ] && [ "$installed_version" = "$latest_prerelease" ] && [ -z "$latest_stable" ]; then
                    echo -e "${GREEN}已经是最新版本 (预发布版 ${installed_version})，无需更新。${NC}"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 0
                else
                    echo -e "${YELLOW}已安装版本 ${installed_version} 不是最新版本。${NC}"
                    if [ -n "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                        echo "请选择要安装的版本："
                        echo "1. 正式版 ${latest_stable}"
                        echo "2. 预发布版 ${latest_prerelease}"
                        read -p "请输入选择 [1-2] (默认正式版): " choice < /dev/tty
                        case $choice in
                            2) target_version="$latest_prerelease" ;;
                            *) target_version="$latest_stable" ;;
                        esac
                    elif [ -n "$latest_stable" ]; then
                        target_version="$latest_stable"
                        echo "将安装正式版 ${target_version}"
                    elif [ -n "$latest_prerelease" ]; then
                        target_version="$latest_prerelease"
                        echo "将安装预发布版 ${target_version}"
                    else
                        echo -e "${RED}错误: 无法找到任何版本。${NC}"
                        read -p "按回车键返回主菜单..." < /dev/tty
                        return 1
                    fi
                fi
            else
                echo "未检测到已安装版本。"
                if [ -n "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                    echo "请选择要安装的版本："
                    echo "1. 正式版 ${latest_stable}"
                    echo "2. 预发布版 ${latest_prerelease}"
                    read -p "请输入选择 [1-2] (默认正式版): " choice < /dev/tty
                    case $choice in
                        2) target_version="$latest_prerelease" ;;
                        *) target_version="$latest_stable" ;;
                    esac
                elif [ -n "$latest_stable" ]; then
                    target_version="$latest_stable"
                    echo "将安装正式版 ${target_version}"
                elif [ -n "$latest_prerelease" ]; then
                    target_version="$latest_prerelease"
                    echo -e "${YELLOW}注意: 当前只有预发布版本 ${target_version}${NC}"
                else
                    echo -e "${RED}错误: 无法找到任何版本。${NC}"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 1
                fi
            fi

            if [ -z "$target_version" ]; then
                echo "未选择任何版本，操作取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 0
            fi

            echo -e "${GREEN}将安装版本: ${target_version}${NC}"

            if [ ! -f "/etc/systemd/system/plugin_loader.service" ]; then
                echo -e "${YELLOW}⚠ 警告: 未检测到 Decky Loader 插件商店。${NC}"
                echo "LSFG-VK 插件需要先安装 Decky Loader 才能正常工作。"
                read -p "是否继续安装？(y/N): " -n 1 -r < /dev/tty
                echo ""
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    echo "安装已取消。"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 1
                fi
            fi

            echo -e "${CYAN}准备安装/更新 LSFG-VK 插件...${NC}"
            read -p "是否继续？(y/N): " -n 1 -r < /dev/tty
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "操作已取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            rm -rf "$TEMP_DIR"
            mkdir -p "$TEMP_DIR"
            cd "$TEMP_DIR"

            local zip_filename="Decky.LSFG-VK.zip"
            local download_path="https://github.com/${GITHUB_REPO}/releases/download/${target_version}/${zip_filename}"
            local DOWNLOAD_SUCCESS=false

            for mirror in "${MIRRORS[@]}"; do
                local full_url="${mirror}${download_path}"
                echo -e "尝试从 ${mirror} 下载..."

                local retry_count=0
                while [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; do
                    if [[ $retry_count -gt 0 ]]; then
                        echo -e "${YELLOW}重试下载 (第 ${retry_count} 次重试)...${NC}"
                    fi

                    curl -L --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$zip_filename" "$full_url"
                    local curl_exit=$?

                    if [[ $curl_exit -eq 0 ]] && [[ -f "$zip_filename" ]]; then
                        local file_size=$(stat -c%s "$zip_filename" 2>/dev/null || stat -f%z "$zip_filename" 2>/dev/null)
                        if [[ -n "$file_size" ]] && [[ "$file_size" -gt 10000 ]]; then
                            echo -e "\n${GREEN}下载成功 (大小: $((file_size/1024)) KB)${NC}"
                            DOWNLOAD_SUCCESS=true
                            break 2
                        else
                            echo -e "\n${RED}下载文件无效 (${file_size} 字节)，尝试下一个镜像...${NC}"
                            rm -f "$zip_filename"
                            break
                        fi
                    else
                        echo -e "\n${RED}下载失败 (退出码: $curl_exit)${NC}"
                        rm -f "$zip_filename"
                        ((retry_count++))
                        if [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; then
                            echo "将进行重试..."
                            sleep 2
                        else
                            echo "该镜像重试次数用完，切换到下一个镜像。"
                        fi
                    fi
                done
            done

            if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
                echo -e "${RED}所有镜像均下载失败，安装中止。${NC}"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo -e "${CYAN}正在解压...${NC}"
            if ! unzip -q "$zip_filename"; then
                echo -e "${RED}解压失败，文件可能已损坏。${NC}"
                rm -rf "$TEMP_DIR"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            sudo mkdir -p "$PLUGIN_DIR"

            if [ -d "$TARGET_DIR" ]; then
                echo "检测到旧版本目录，正在删除..."
                sudo rm -rf "$TARGET_DIR"
            fi

            local extracted_dir=""
            extracted_dir=$(find "$TEMP_DIR" -maxdepth 2 -type f \( -name "plugin.py" -o -name "plugin.json" -o -name "lsfg-vk" \) -exec dirname {} \; 2>/dev/null | head -1)
            if [ -z "$extracted_dir" ]; then
                extracted_dir=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "*LSFG*" -o -name "*lsfg*" | head -1)
            fi
            if [ -z "$extracted_dir" ]; then
                local subdirs=($(find "$TEMP_DIR" -maxdepth 1 -type d ! -path "$TEMP_DIR"))
                if [ ${#subdirs[@]} -eq 1 ]; then
                    extracted_dir="${subdirs[0]}"
                fi
            fi
            if [ -z "$extracted_dir" ]; then
                if [ -f "$TEMP_DIR/plugin.py" ] || [ -d "$TEMP_DIR/bin" ]; then
                    extracted_dir="$TEMP_DIR"
                fi
            fi

            if [ -z "$extracted_dir" ] || [ ! -d "$extracted_dir" ]; then
                echo -e "${RED}错误: 解压后未找到 LSFG-VK 插件目录。${NC}"
                echo "解压后的文件列表："
                ls -la "$TEMP_DIR"
                rm -rf "$TEMP_DIR"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo -e "${CYAN}正在安装插件到 ${TARGET_DIR}...${NC}"
            sudo mv "$extracted_dir" "$TARGET_DIR"

            sudo chown -R deck:deck "$TARGET_DIR"

            rm -rf "$TEMP_DIR"

            echo ""
            echo -e "${GREEN}✅ LSFG-VK 插件 (${target_version}) 安装/更新完成！${NC}"
            echo "请切换回游戏模式，在 Decky 侧边栏中查看 LSFG-VK 是否出现。"
            ;;

        2)
            echo -e "${CYAN}正在卸载 LSFG-VK 插件...${NC}"
            echo "这将删除目录: ${TARGET_DIR}"

            read -p "确定要卸载吗？(y/N): " -n 1 -r < /dev/tty
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "卸载已取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 0
            fi

            if [ -d "$TARGET_DIR" ]; then
                if sudo rm -rf "$TARGET_DIR"; then
                    echo -e "${GREEN}✅ LSFG-VK 插件已卸载。${NC}"
                else
                    echo -e "${RED}卸载失败，请检查权限。${NC}"
                fi
            else
                echo -e "${YELLOW}未检测到 LSFG-VK 插件安装。${NC}"
            fi
            ;;

        *)
            echo "返回主菜单..."
            return
            ;;
    esac

    read -p "按回车键返回主菜单..." < /dev/tty
}

install_decky_framegen() {
    show_header
    echo -e "${YELLOW}════════════════ 安装/卸载 Framegen 插件 ════════════════${NC}"
    echo ""

    local GITHUB_REPO="xXJSONDeruloXx/Decky-Framegen"
    local PLUGIN_DIR="/home/deck/homebrew/plugins"
    local TARGET_DIR="${PLUGIN_DIR}/Decky-Framegen"
    local TEMP_DIR="/tmp/decky_framegen_install"
    local MIRRORS=(
        "https://ghproxy.net/"
        "https://gh.ddlc.top/"
        "https://mirror.ghproxy.com/"
        "https://gh.api.99988866.xyz/"
        "https://download.fastgit.org/"
        "https://hub.gitmirror.com/"
        "https://git.xfj0.xyz/"
        "https://github.com/"
    )
    local DOWNLOAD_TIMEOUT=60
    local MAX_RETRY_PER_MIRROR=1

    for cmd in curl sudo unzip; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            read -p "按回车键返回主菜单..." < /dev/tty
            return 1
        fi
    done

    echo "请选择要执行的操作："
    echo "1. 安装/更新 Framegen 插件"
    echo "2. 卸载 Framegen 插件"
    echo ""

    read -p "请输入选择 [1-2] (输入其他键返回): " action_choice < /dev/tty

    case $action_choice in
        1)
            echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
            local releases_json=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases")
            local versions_info=$(echo "$releases_json" | grep -E '("tag_name":|"prerelease":)' | paste -d ' ' - - | sed 's/.*"tag_name": "\([^"]*\)".*"prerelease": \([^,]*\).*/\1|\2/')
            local stable_versions=()
            local prerelease_versions=()
            while IFS='|' read -r tag prerelease; do
                [ -z "$tag" ] && continue
                if [[ "$prerelease" == "true" ]]; then
                    prerelease_versions+=("$tag")
                else
                    stable_versions+=("$tag")
                fi
            done <<< "$versions_info"

            local latest_stable=""
            local latest_prerelease=""
            if [ ${#stable_versions[@]} -gt 0 ]; then
                latest_stable=$(printf '%s\n' "${stable_versions[@]}" | sed 's/^v//' | sort -V | tail -1)
                latest_stable="v${latest_stable}"
            fi
            if [ ${#prerelease_versions[@]} -gt 0 ]; then
                latest_prerelease=$(printf '%s\n' "${prerelease_versions[@]}" | sed 's/^v//' | sort -V | tail -1)
                latest_prerelease="v${latest_prerelease}"
            fi

            if [ -n "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                local stable_num=$(echo "$latest_stable" | sed 's/^v//')
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                if [[ "$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)" != "$prerelease_num" ]]; then
                    latest_prerelease=""
                fi
            fi

            local installed_version=""
            if [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/package.json" ]; then
                installed_version=$(grep -o '"version": *"[^"]*"' "$TARGET_DIR/package.json" | head -1 | sed 's/.*"version": *"//; s/".*//')
                if [ -n "$installed_version" ]; then
                    installed_version="v${installed_version}"
                    echo -e "${CYAN}已安装版本: ${installed_version}${NC}"
                fi
            fi

            local target_version=""
            if [ -n "$installed_version" ]; then
                if [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                    echo -e "${GREEN}已安装最新正式版 ${installed_version}${NC}"
                    echo -e "${YELLOW}发现更高版本的预发布版: ${latest_prerelease}${NC}"
                    read -p "是否升级到预发布版？(y/N): " upgrade < /dev/tty
                    if [[ $upgrade =~ ^[Yy]$ ]]; then
                        target_version="$latest_prerelease"
                    else
                        echo "保持当前版本。"
                        read -p "按回车键返回主菜单..." < /dev/tty
                        return 0
                    fi
                elif [ -n "$latest_prerelease" ] && [ "$installed_version" = "$latest_prerelease" ] && [ -n "$latest_stable" ]; then
                    echo -e "${GREEN}已安装最新预发布版 ${installed_version}${NC}"
                    echo -e "${YELLOW}当前正式版为: ${latest_stable}${NC}"
                    read -p "是否切换到正式版？(y/N): " switch < /dev/tty
                    if [[ $switch =~ ^[Yy]$ ]]; then
                        target_version="$latest_stable"
                    else
                        echo "保持当前版本。"
                        read -p "按回车键返回主菜单..." < /dev/tty
                        return 0
                    fi
                elif [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ] && [ -z "$latest_prerelease" ]; then
                    echo -e "${GREEN}已经是最新版本 (正式版 ${installed_version})，无需更新。${NC}"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 0
                elif [ -n "$latest_prerelease" ] && [ "$installed_version" = "$latest_prerelease" ] && [ -z "$latest_stable" ]; then
                    echo -e "${GREEN}已经是最新版本 (预发布版 ${installed_version})，无需更新。${NC}"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 0
                else
                    echo -e "${YELLOW}已安装版本 ${installed_version} 不是最新版本。${NC}"
                    if [ -n "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                        echo "请选择要安装的版本："
                        echo "1. 正式版 ${latest_stable}"
                        echo "2. 预发布版 ${latest_prerelease}"
                        read -p "请输入选择 [1-2] (默认正式版): " choice < /dev/tty
                        case $choice in
                            2) target_version="$latest_prerelease" ;;
                            *) target_version="$latest_stable" ;;
                        esac
                    elif [ -n "$latest_stable" ]; then
                        target_version="$latest_stable"
                        echo "将安装正式版 ${target_version}"
                    elif [ -n "$latest_prerelease" ]; then
                        target_version="$latest_prerelease"
                        echo "将安装预发布版 ${target_version}"
                    else
                        echo -e "${RED}错误: 无法找到任何版本。${NC}"
                        read -p "按回车键返回主菜单..." < /dev/tty
                        return 1
                    fi
                fi
            else
                echo "未检测到已安装版本。"
                if [ -n "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                    echo "请选择要安装的版本："
                    echo "1. 正式版 ${latest_stable}"
                    echo "2. 预发布版 ${latest_prerelease}"
                    read -p "请输入选择 [1-2] (默认正式版): " choice < /dev/tty
                    case $choice in
                        2) target_version="$latest_prerelease" ;;
                        *) target_version="$latest_stable" ;;
                    esac
                elif [ -n "$latest_stable" ]; then
                    target_version="$latest_stable"
                    echo "将安装正式版 ${target_version}"
                elif [ -n "$latest_prerelease" ]; then
                    target_version="$latest_prerelease"
                    echo -e "${YELLOW}注意: 当前只有预发布版本 ${target_version}${NC}"
                else
                    echo -e "${RED}错误: 无法找到任何版本。${NC}"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 1
                fi
            fi

            if [ -z "$target_version" ]; then
                echo "未选择任何版本，操作取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 0
            fi

            echo -e "${GREEN}将安装版本: ${target_version}${NC}"

            if [ ! -f "/etc/systemd/system/plugin_loader.service" ]; then
                echo -e "${YELLOW}⚠ 警告: 未检测到 Decky Loader 插件商店。${NC}"
                echo "Framegen 插件需要先安装 Decky Loader 才能正常工作。"
                read -p "是否继续安装？(y/N): " -n 1 -r < /dev/tty
                echo ""
                if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                    echo "安装已取消。"
                    read -p "按回车键返回主菜单..." < /dev/tty
                    return 1
                fi
            fi

            echo -e "${CYAN}准备安装/更新 Framegen 插件...${NC}"
            read -p "是否继续？(y/N): " -n 1 -r < /dev/tty
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "操作已取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            rm -rf "$TEMP_DIR"
            mkdir -p "$TEMP_DIR"
            cd "$TEMP_DIR"

            local zip_filename="Decky-Framegen.zip"
            local download_path="https://github.com/${GITHUB_REPO}/releases/download/${target_version}/${zip_filename}"
            local DOWNLOAD_SUCCESS=false

            for mirror in "${MIRRORS[@]}"; do
                local full_url="${mirror}${download_path}"
                echo -e "尝试从 ${mirror} 下载..."

                local retry_count=0
                while [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; do
                    if [[ $retry_count -gt 0 ]]; then
                        echo -e "${YELLOW}重试下载 (第 ${retry_count} 次重试)...${NC}"
                    fi

                    curl -L --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$zip_filename" "$full_url"
                    local curl_exit=$?

                    if [[ $curl_exit -eq 0 ]] && [[ -f "$zip_filename" ]]; then
                        local file_size=$(stat -c%s "$zip_filename" 2>/dev/null || stat -f%z "$zip_filename" 2>/dev/null)
                        if [[ -n "$file_size" ]] && [[ "$file_size" -gt 10000 ]]; then
                            echo -e "\n${GREEN}下载成功 (大小: $((file_size/1024)) KB)${NC}"
                            DOWNLOAD_SUCCESS=true
                            break 2
                        else
                            echo -e "\n${RED}下载文件无效 (${file_size} 字节)，尝试下一个镜像...${NC}"
                            rm -f "$zip_filename"
                            break
                        fi
                    else
                        echo -e "\n${RED}下载失败 (退出码: $curl_exit)${NC}"
                        rm -f "$zip_filename"
                        ((retry_count++))
                        if [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; then
                            echo "将进行重试..."
                            sleep 2
                        else
                            echo "该镜像重试次数用完，切换到下一个镜像。"
                        fi
                    fi
                done
            done

            if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
                echo -e "${RED}所有镜像均下载失败，安装中止。${NC}"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo -e "${CYAN}正在解压...${NC}"
            if ! unzip -q "$zip_filename"; then
                echo -e "${RED}解压失败，文件可能已损坏。${NC}"
                rm -rf "$TEMP_DIR"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            sudo mkdir -p "$PLUGIN_DIR"

            if [ -d "$TARGET_DIR" ]; then
                echo "检测到旧版本目录，正在删除..."
                sudo rm -rf "$TARGET_DIR"
            fi

            local extracted_dir=""
            extracted_dir=$(find "$TEMP_DIR" -maxdepth 2 -type f \( -name "plugin.py" -o -name "main.py" -o -name "plugin.json" \) -exec dirname {} \; 2>/dev/null | head -1)
            if [ -z "$extracted_dir" ]; then
                extracted_dir=$(find "$TEMP_DIR" -maxdepth 1 -type d -name "*Framegen*" -o -name "*framegen*" | head -1)
            fi
            if [ -z "$extracted_dir" ]; then
                local subdirs=($(find "$TEMP_DIR" -maxdepth 1 -type d ! -path "$TEMP_DIR"))
                if [ ${#subdirs[@]} -eq 1 ]; then
                    extracted_dir="${subdirs[0]}"
                fi
            fi
            if [ -z "$extracted_dir" ]; then
                if [ -f "$TEMP_DIR/plugin.py" ] || [ -f "$TEMP_DIR/main.py" ]; then
                    extracted_dir="$TEMP_DIR"
                fi
            fi

            if [ -z "$extracted_dir" ] || [ ! -d "$extracted_dir" ]; then
                echo -e "${RED}错误: 解压后未找到 Framegen 插件目录。${NC}"
                echo "解压后的文件列表："
                ls -la "$TEMP_DIR"
                rm -rf "$TEMP_DIR"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 1
            fi

            echo -e "${CYAN}正在安装插件到 ${TARGET_DIR}...${NC}"
            sudo mv "$extracted_dir" "$TARGET_DIR"

            sudo chown -R deck:deck "$TARGET_DIR"

            rm -rf "$TEMP_DIR"

            echo ""
            echo -e "${GREEN}✅ Framegen 插件 (${target_version}) 安装/更新完成！${NC}"
            echo "请切换回游戏模式，在 Decky 侧边栏中查看 Framegen 是否出现。"
            ;;

        2)
            echo -e "${CYAN}正在卸载 Framegen 插件...${NC}"
            echo "这将删除目录: ${TARGET_DIR}"

            read -p "确定要卸载吗？(y/N): " -n 1 -r < /dev/tty
            echo ""
            if [[ ! $REPLY =~ ^[Yy]$ ]]; then
                echo "卸载已取消。"
                read -p "按回车键返回主菜单..." < /dev/tty
                return 0
            fi

            if [ -d "$TARGET_DIR" ]; then
                if sudo rm -rf "$TARGET_DIR"; then
                    echo -e "${GREEN}✅ Framegen 插件已卸载。${NC}"
                else
                    echo -e "${RED}卸载失败，请检查权限。${NC}"
                fi
            else
                echo -e "${YELLOW}未检测到 Framegen 插件安装。${NC}"
            fi
            ;;

        *)
            echo "返回主菜单..."
            return
            ;;
    esac

    read -p "按回车键返回主菜单..." < /dev/tty
}

clover_install_or_reinstall() {
    show_header
    echo -e "${YELLOW}════════════════ 安装/重装 Clover 引导 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}此操作将安装或重新安装 Clover 图形化引导管理器。${NC}"
    echo -e "${YELLOW}重要：请先在 Windows 中进行以下配置（如已有 Windows且初次安装引导）（如果是重装引导则忽略此步骤）：${NC}"
    echo "  1. 以管理员身份打开命令提示符或 PowerShell"
    echo "  2. 执行命令：bcdedit.exe -set \"{globalsettings}\" highestmode on"
    echo "  3. 执行命令：reg add \"HKEY_LOCAL_MACHINE\\System\\CurrentControlSet\\Control\\TimeZoneInformation\" /v RealTimeIsUniversal /d 1 /t REG_DWORD /f"
    echo ""

    echo "========================================="
    echo "   Steam Deck Clover 安装助手"
    echo "========================================="
    echo "请选择克隆镜像源："
    echo "1) GitHub 官方（原始，可能较慢）"
    echo "2) ghproxy.net 镜像"
    echo "3) gh.ddlc.top 镜像"
    read -p "请输入数字 [1-3] (默认 1): " choice < /dev/tty

    case "$choice" in
        2) BASE_URL="https://ghproxy.net/https://github.com" ;;
        3) BASE_URL="https://gh.ddlc.top/https://github.com" ;;
        *) BASE_URL="https://github.com" ;;
    esac

    REPO_FULL_PATH="ryanrudolfoba/SteamDeck-Clover-dualboot"
    REPO_URL="${BASE_URL}/${REPO_FULL_PATH}"
    TARGET_DIR="$HOME/SteamDeck-Clover-dualboot"

    if [ -d "$TARGET_DIR" ]; then
        echo -e "${YELLOW}目录 $TARGET_DIR 已存在。${NC}"
        read -p "是否删除旧文件夹并重新克隆？(y/N): " -n 1 -r < /dev/tty
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$TARGET_DIR"
        else
            echo "操作已取消。"
            read -p "按回车键返回主菜单..." < /dev/tty
            return 0
        fi
    fi

    echo -e "${CYAN}正在克隆仓库...${NC}"
    if ! git clone "$REPO_URL" "$TARGET_DIR"; then
        echo -e "${RED}克隆失败，请检查网络连接或更换镜像源。${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    fi

    cd "$TARGET_DIR" || { echo -e "${RED}无法进入目录${NC}"; return 1; }

    echo -e "${CYAN}正在生成优化版 install-Clover.sh...${NC}"
    cat > install-Clover.sh << 'CLOVER_SCRIPT_EOF'
#!/bin/bash

clear

echo "Clover 双系统启动安装脚本 - Steam Deck 专用"
echo "项目地址: https://github.com/ryanrudolfoba/SteamDeck-Clover-dualboot"
echo "作者 YT: 10MinuteSteamDeckGamer"
echo "正在进行初步检查..."

CLOVER=$(efibootmgr | grep -i Clover | colrm 9 | colrm 1 4)
REFIND=$(efibootmgr | grep -i rEFInd | colrm 9 | colrm 1 4)
ESP=$(df /dev/nvme0n1p1 --output=avail | tail -n1)
CLOVER_VERSION=5172
CLOVER_EFI=\\EFI\\clover\\cloverx64.efi
BOARD_NAME=$(cat /sys/class/dmi/id/board_name)
PRODUCT_NAME=$(cat /sys/class/dmi/id/product_name)

if [ "$BOARD_NAME" = "Jupiter" ] || [ "$BOARD_NAME" = "Galileo" ]; then
    echo "检测到支持的设备 - Steam Deck $BOARD_NAME，无需修改 config.plist。"
elif [ "$PRODUCT_NAME" = "83L3" ] || [ "$PRODUCT_NAME" = "83Q2" ] || [ "$PRODUCT_NAME" = "83Q3" ]; then
    echo "检测到 Legion Go S，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1200<\/string>' custom/config.plist
elif [ "$PRODUCT_NAME" = "83N6" ]; then
    echo "不支持的设备 - Legion Go S 83N6，退出。"
    exit
elif [ "$PRODUCT_NAME" = "83E1" ]; then
    echo "检测到 Legion Go，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>2560x1600<\/string>' custom/config.plist
elif [ "$BOARD_NAME" = "RC71L" ]; then
    echo "检测到 ROG Ally，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' custom/config.plist
elif [ "$BOARD_NAME" = "RC72LA" ]; then
    echo "检测到 ROG Ally X，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' custom/config.plist
elif [ "$PRODUCT_NAME" = "ONEXPLAYER 2 PRO ARP23P" ]; then
    echo "检测到 Onexplayer 2 Pro，正在应用专用配置。"
    sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>2560x1600<\/string>' custom/config.plist
else
    echo "不支持的设备！退出。"
    exit
fi

if grep -qi bazzite /etc/os-release; then
    OS=bazzite
    EFI_PATH=/boot/efi/EFI
    BOOTX64=$EFI_PATH/BOOT/BOOTX64.EFI
    echo "检测到操作系统: Bazzite"
else
    grep -qi SteamOS /etc/os-release || { echo "既不是 SteamOS 也不是 Bazzite！退出。"; exit; }
    OS=SteamOS
    EFI_PATH=/esp/efi
    BOOTX64=$EFI_PATH/boot/bootx64.efi
    echo "检测到操作系统: SteamOS"
fi

if blkid /dev/nvme0n1p1 | grep -qi microsoft; then
    echo "检测到不支持的双系统配置（Windows 安装在 SteamOS 之前）。请确保 SteamOS 安装在 Windows 之前！"
    exit
else
    echo "双系统配置检查通过。"
fi

if [ "$(passwd --status $(whoami) | tr -s " " | cut -d " " -f 2)" == "P" ]; then
    read -s -p "请输入当前 sudo 密码: " current_password ; echo < /dev/tty
    echo "正在验证 sudo 密码..."
    if ! echo -e "$current_password\n" | sudo -S ls &> /dev/null; then
        echo "sudo 密码错误！请重新运行脚本并输入正确密码。"
        exit
    fi
    echo "sudo 密码正确。"
else
    echo "未设置 sudo 密码！请先设置密码再运行脚本。"
    passwd
    exit
fi

mkdir -p ~/temp-ESP
if ! echo -e "$current_password\n" | sudo -S mount /dev/nvme0n1p1 ~/temp-ESP; then
    echo "挂载 ESP 分区失败！"
    rmdir ~/temp-ESP
    exit
fi
echo "ESP 分区已挂载。"
if [ $ESP -ge 15000 ]; then
    echo "ESP 分区剩余空间: $ESP KB，空间充足。"
    echo -e "$current_password\n" | sudo -S umount ~/temp-ESP
    rmdir ~/temp-ESP
else
    echo "ESP 分区剩余空间: $ESP KB，空间不足！请清理后重试。"
    echo -e "$current_password\n" | sudo -S du -hd2 /esp
    echo -e "$current_password\n" | sudo -S umount ~/temp-ESP
    rmdir ~/temp-ESP
    exit
fi

if efibootmgr | grep -qi refind; then
    echo "检测到 rEFInd，正在尽力卸载..."
    for rEFInd_boot in $REFIND; do
        echo -e "$current_password\n" | sudo -S efibootmgr -b $rEFInd_boot -B &> /dev/null
    done
    echo -e "$current_password\n" | sudo -S systemctl disable bootnext-refind.service &> /dev/null
    echo -e "$current_password\n" | sudo -S systemctl disable rEFInd_bg_randomizer.service
    echo -e "$current_password\n" | sudo -S rm -rf $EFI_PATH/refind &> /dev/null
    echo -e "$current_password\n" | sudo -S steamos-readonly disable
    echo -e "$current_password\n" | sudo -S rm /etc/systemd/system/bootnext-refind.service &> /dev/null
    echo -e "$current_password\n" | sudo -S rm -f /etc/systemd/system/rEFInd_bg_randomizer.service
    echo -e "$current_password\n" | sudo -S pacman-key --init
    echo -e "$current_password\n" | sudo -S pacman-key --populate archlinux
    echo -e "$current_password\n" | sudo -S pacman -R --noconfirm SteamDeck_rEFInd
    echo -e "$current_password\n" | sudo -S steamos-readonly enable
    rm -rf ~/.local/SteamDeck_rEFInd ~/.SteamDeck_rEFInd ~/Desktop/SteamDeck_rEFInd.desktop
    if efibootmgr | grep -qi refind; then
        echo "rEFInd 卸载失败，请手动卸载后重试。"
        exit
    fi
    echo "rEFInd 已成功卸载。"
else
    echo "未检测到 rEFInd，继续安装 Clover。"
fi

echo "正在使用多镜像源下载 Clover ISO（支持重试）..."
MIRRORS=(
    "https://ghproxy.net/https://github.com"
    "https://gh.ddlc.top/https://github.com"
    "https://mirror.ghproxy.com/https://github.com"
    "https://github.com"
)
CLOVER_FILE="Clover-${CLOVER_VERSION}-X64.iso.7z"
DOWNLOAD_SUCCESS=0

for mirror in "${MIRRORS[@]}"; do
    CLOVER_URL="${mirror}/CloverHackyColor/CloverBootloader/releases/download/${CLOVER_VERSION}/${CLOVER_FILE}"
    for attempt in 1 2; do
        echo "尝试从 ${mirror} 下载 (尝试 ${attempt}/2)..."
        if curl -# -L --fail --connect-timeout 10 --max-time 60 -o "${CLOVER_FILE}" "${CLOVER_URL}"; then
            echo "✅ 下载成功！"
            DOWNLOAD_SUCCESS=1
            break 2
        else
            echo "⚠️ 下载失败 (尝试 ${attempt}/2)"
            rm -f "${CLOVER_FILE}"
            [ $attempt -eq 1 ] && echo "将进行第2次重试..." && sleep 2
        fi
    done
done

if [ ${DOWNLOAD_SUCCESS} -eq 0 ]; then
    echo "❌ 下载 Clover 失败！所有镜像源均不可用，请检查网络后重试。"
    exit 1
fi

CLOVER_BASE=$(basename -s .7z "${CLOVER_FILE}")

if ! 7z x "${CLOVER_FILE}" -aoa "${CLOVER_BASE}" &> /dev/null; then
    echo "解压 Clover ISO 失败！"
    exit
fi
echo "Clover ISO 解压成功。"

mkdir -p ~/temp-clover
if ! echo -e "$current_password\n" | sudo -S mount "${CLOVER_BASE}" ~/temp-clover &> /dev/null; then
    echo "挂载 Clover ISO 失败！"
    echo -e "$current_password\n" | sudo -S umount ~/temp-clover
    rmdir ~/temp-clover
    exit
fi
echo "Clover ISO 已挂载。"

echo -e "$current_password\n" | sudo -S cp -Rf ~/temp-clover/efi/clover $EFI_PATH
echo -e "$current_password\n" | sudo -S cp custom/config.plist $EFI_PATH/clover/config.plist
echo -e "$current_password\n" | sudo -S cp -Rf custom/themes/* $EFI_PATH/clover/themes
echo -e "$current_password\n" | sudo -S rm -rf $EFI_PATH/clover/themes/{bgm,cesium,christmas,glass,purple_swirl,theme-sample.plist}

if [ "$PRODUCT_NAME" = "83N6" ] || [ "$PRODUCT_NAME" = "83L3" ] || [ "$PRODUCT_NAME" = "83Q2" ] || [ "$PRODUCT_NAME" = "83Q3" ] || [ "$PRODUCT_NAME" = "83E1" ] || [ "$BOARD_NAME" = "RC71L" ] || [ "$BOARD_NAME" = "RC72LA" ] || [ "$PRODUCT_NAME" = "ONEXPLAYER 2 PRO ARP23P" ]; then
    echo "非 Steam Deck 设备，正在安装 Xbox 360 UEFI 驱动..."
    if echo -e "$current_password\n" | sudo -S cp custom/UsbXbox360Dxe.efi $EFI_PATH/clover/drivers/uefi; then
        echo "Xbox 360 驱动安装成功。"
    else
        echo "Xbox 360 驱动安装失败！"
        exit
    fi
else
    echo "Steam Deck 无需安装 Xbox 360 驱动。"
fi

echo -e "$current_password\n" | sudo -S umount ~/temp-clover
rmdir ~/temp-clover
rm -f "Clover-${CLOVER_VERSION}-X64.iso"*

for entry in $CLOVER; do
    echo -e "$current_password\n" | sudo -S efibootmgr -b $entry -B &> /dev/null
done

echo -e "$current_password\n" | sudo -S efibootmgr -c -d /dev/nvme0n1 -p 1 -L "Clover - GUI Boot Manager" -l "$CLOVER_EFI" &> /dev/null

if [ -e "$BOOTX64.orig" ]; then
    echo "$BOOTX64.orig 已存在，无需备份。"
else
    echo "备份 $BOOTX64 为 $BOOTX64.orig"
    echo -e "$current_password\n" | sudo -S cp "$BOOTX64" "$BOOTX64.orig"
    echo -e "$current_password\n" | sudo -S cp "$EFI_PATH/clover/cloverx64.efi" "$BOOTX64"
    echo "已替换 bootx64.efi 为 Clover EFI。"
fi

if [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig" ]; then
    if [ -e "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" ]; then
        echo -e "$current_password\n" | sudo -S mv "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/bootmgfw.efi"
        echo "已禁用 Windows EFI 直接启动。"
    else
        echo "Windows EFI 已禁用。"
    fi
else
    echo -e "$current_password\n" | sudo -S cp "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig"
    echo -e "$current_password\n" | sudo -S mv "$EFI_PATH/Microsoft/Boot/bootmgfw.efi" "$EFI_PATH/Microsoft/bootmgfw.efi"
    echo "已禁用 Windows EFI 直接启动。"
fi

echo -e "$current_password\n" | sudo -S efibootmgr -n $CLOVER &> /dev/null
echo -e "$current_password\n" | sudo -S efibootmgr -o $CLOVER &> /dev/null

if efibootmgr | grep -q "Clover - GUI"; then
    echo "Clover 已成功安装到 EFI 系统分区！"
else
    echo "哎呀，出错了，Clover 未安装成功。"
    exit
fi

mkdir -p ~/1Clover-tools
rm -f ~/1Clover-tools/*
cp custom/Clover-Toolbox.sh ~/1Clover-tools
echo -e "$current_password\n" | sudo -S cp custom/clover-bootmanager.service custom/clover-bootmanager.sh /etc/systemd/system
cp -R custom/logos ~/1Clover-tools
cp -R custom/efi ~/1Clover-tools

chmod +x ~/1Clover-tools/Clover-Toolbox.sh
echo -e "$current_password\n" | sudo -S chmod +x /etc/systemd/system/clover-bootmanager.sh

echo -e "$current_password\n" | sudo -S systemctl daemon-reload
echo -e "$current_password\n" | sudo -S systemctl enable --now clover-bootmanager.service
echo -e "$current_password\n" | sudo -S /etc/systemd/system/clover-bootmanager.sh

if [ "$OS" = "SteamOS" ]; then
    mkdir -p ~/.local/share/kservices5/ServiceMenus
    cp custom/open_as_root.desktop ~/.local/share/kservices5/ServiceMenus
    echo -e "$current_password\n" | sudo -S cp custom/clover-whitelist.conf /etc/atomic-update.conf.d
else
    if ! blkid /dev/nvme0n1p1 | grep -qi esp; then
        echo -e "$current_password\n" | sudo -S fatlabel /dev/nvme0n1p1 esp
        echo "ESP 分区标签已设置。"
    fi
    echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\fedora\\shimx64\.efi<\/string>' $EFI_PATH/clover/config.plist
fi

echo "Clover 安装完成于 $OS！"
CLOVER_SCRIPT_EOF

    chmod +x install-Clover.sh || {
        echo -e "${RED}无法设置 install-Clover.sh 执行权限。${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    }

    echo -e "${CYAN}即将运行 Clover 安装脚本，请根据提示输入 sudo 密码（如果需要）...${NC}"
    sleep 1

    LOG_FILE="/tmp/clover_install.log"
    ./install-Clover.sh 2>&1 | tee "$LOG_FILE"
    INSTALL_EXIT=$?

    if grep -q "Not enough space on the ESP partition!" "$LOG_FILE"; then
        echo -e "${RED}安装失败：ESP分区空间不足，请清理后重试。${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    elif [ $INSTALL_EXIT -eq 0 ] && grep -q "Clover 安装完成" "$LOG_FILE"; then
        echo -e "${GREEN}Clover 安装/重装成功！${NC}"
    else
        echo -e "${RED}安装/重装失败，请检查上方输出。${NC}"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    fi

    # 处理桌面快捷方式
    SHORTCUT="$HOME/Desktop/引导文件配置.desktop"
    if [ -f "$SHORTCUT" ]; then
        echo -e "${GREEN}桌面快捷方式“引导文件配置”已存在，无需创建。${NC}"
    else
        cat > "$SHORTCUT" << 'EOF'
[Desktop Entry]
Type=Application
Name=引导文件配置
Exec=konsole -e bash -c '/home/deck/1Clover-tools/Clover-Toolbox.sh; read -p "按回车键关闭..." -n1'
Icon=kdiamond
Terminal=false
Categories=Utility;
EOF
        chmod +x "$SHORTCUT"
        echo -e "${GREEN}已创建桌面快捷方式“引导文件配置”。${NC}"
    fi

    # 覆盖 Clover-Toolbox.sh 为汉化版（带完整中文菜单和卸载清理）
    cat > ~/1Clover-tools/Clover-Toolbox.sh << 'TOOLBOX_EOF'
#!/bin/bash

# 检查 Bazzite 或 SteamOS
grep -i bazzite /etc/os-release &> /dev/null
if [ $? -eq 0 ]
then
	OS=bazzite
	EFI_PATH=/boot/efi/EFI
	BOOTX64=$EFI_PATH/BOOT/BOOTX64.EFI
else
	grep -i SteamOS /etc/os-release &> /dev/null
	if [ $? -eq 0 ]
	then
		OS=SteamOS
		EFI_PATH=/esp/efi
		BOOTX64=$EFI_PATH/boot/bootx64.efi
	else
		exit
	fi
fi

current_password=$(zenity --password --title "sudo 密码验证")
echo -e "$current_password\n" | sudo -S ls &> /dev/null
if [ $? -ne 0 ]
then
	echo "sudo 密码错误！" | \
		zenity --text-info --title "Clover 工具箱" --width 400 --height 200
	exit
fi

while true
do
Choice=$(zenity --width 750 --height 450 --list --radiolist --multiple \
	--title "Clover 工具箱 - https://github.com/ryanrudolfoba/SteamDeck-clover-dualboot" \
	--column "选择" \
	--column "选项" \
	--column "说明 - 请仔细阅读" \
	FALSE 状态 "提交错误报告时请选用此项" \
	FALSE Batocera "选择 Batocera v39 (及更新) 或 v38 (及更旧) 的配置" \
	FALSE 主题 "选择固定主题或随机主题" \
	FALSE 超时 "设置默认超时时间 (1/5/10/15 秒) 后自动启动默认系统" \
	FALSE 服务 "禁用/启用 Clover EFI 条目和 systemd 服务" \
	FALSE 默认启动 "设置默认启动的操作系统" \
	FALSE 新Logo "替换 BGRT 启动标志" \
	FALSE 恢复Logo "恢复默认的 BGRT 启动标志" \
	FALSE 分辨率 "设置屏幕分辨率 (DeckHD 或 DeckSight 屏幕改装)" \
	FALSE 自定义 "替换 Clover EFI 为隐藏 OPTIONS 按钮的自定义版本" \
	FALSE 卸载 "卸载 Clover 并恢复所有更改" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

if [ $? -eq 1 ] || [ "$Choice" == "退出" ]
then
	echo "用户按下了取消/退出。"
	exit

elif [ "$Choice" == "状态" ]
then
	zenity --warning --title "Clover 工具箱" --text "$(fold -w 120 -s ~/1Clover-tools/status.txt)" --width 1000 --height 400

elif [ "$Choice" == "Batocera" ]
then
Batocera_Choice=$(zenity --width 550 --height 220 --list --radiolist --multiple --title "Clover 工具箱" --column "选择" \
	--column "选项" --column "说明 - 请仔细阅读" \
	FALSE v39 "为 Batocera v39 及更新版本设置 Clover 配置" \
	FALSE v38 "为 Batocera v38 及更旧版本设置 Clover 配置" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Batocera_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Batocera_Choice" == "v39" ]
	then
		# 为 Batocera v39 及更新版本更新 config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<string>os_batocera<\/string>/!b;n;n;c\\t\t\t\t\t<string>\\efi\\batocera\\grubx64\.efi<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "已为 Batocera v39 及更新版本更新 Clover 配置！" --width 450 --height 75

	elif [ "$Batocera_Choice" == "v38" ]
	then
		# 为 Batocera v38 及更旧版本更新 config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<string>os_batocera<\/string>/!b;n;n;c\\t\t\t\t\t<string>\\efi\\boot\\bootx64\.efi<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "已为 Batocera v38 及更旧版本更新 Clover 配置！" --width 450 --height 75

	fi

elif [ "$Choice" == "主题" ]
then
Theme_Choice=$(zenity --title "Clover 工具箱"	--width 200 --height 325 --list \
	--column "主题名称" $(echo -e "$current_password\n" | sudo -S ls $EFI_PATH/clover/themes) )

	if [ $? -eq 1 ]
	then
		echo "用户按了取消。返回主菜单。"
	else
		echo -e "$current_password\n" | sudo -S sed -i '/<key>Theme<\/key>/!b;n;c\\t\t<string>'$Theme_Choice'<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "主题已更改为 $Theme_Choice！" --width 400 --height 75
	fi

elif [ "$Choice" == "超时" ]
then
Timeout_Choice=$(zenity --width 500 --height 300 --list --radiolist --multiple \
	--title "Clover 工具箱" --column "选择" --column "选项" --column "说明 - 请仔细阅读" \
	FALSE 1 "设置默认超时时间为 1 秒" \
	FALSE 5 "设置默认超时时间为 5 秒" \
	FALSE 10 "设置默认超时时间为 10 秒" \
	FALSE 15 "设置默认超时时间为 15 秒" \
 	FALSE 60 "设置默认超时时间为 60 秒" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Timeout_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"
	else
		# 修改 config.plist 中的 Default Timeout
		echo -e "$current_password\n" | sudo -S sed -i '/<key>Timeout<\/key>/!b;n;c\\t\t<integer>'$Timeout_Choice'<\/integer>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "默认超时时间已设置为 $Timeout_Choice 秒！" --width 400 --height 75
	fi

elif [ "$Choice" == "服务" ]
then
Service_Choice=$(zenity --width 650 --height 250 --list --radiolist --multiple --title "Clover 工具箱" \
	--column "选择" --column "选项" --column "说明 - 请仔细阅读" \
	FALSE 禁用 "禁用 Clover EFI 条目和 systemd 服务" \
	FALSE 启用 "启用 Clover EFI 条目和 systemd 服务" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Service_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Service_Choice" == "禁用" ]
	then
		# 从备份恢复 Windows EFI 条目
		echo -e "$current_password\n" | sudo -S cp $EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig $EFI_PATH/Microsoft/Boot/bootmgfw.efi

		# 将 Windows 设为下一次启动项
		Windows=$(efibootmgr | grep -i Windows | colrm 9 | colrm 1 4)
		echo -e "$current_password\n" | sudo -S efibootmgr -n $Windows &> /dev/null

		# 禁用 Clover systemd 服务
		echo -e "$current_password\n" | sudo -S systemctl disable --now clover-bootmanager
		zenity --warning --title "Clover 工具箱" --text "Clover systemd 服务已禁用。Windows 现已激活！" --width 500 --height 75

	elif [ "$Service_Choice" == "启用" ]
	then
		# 启用 Clover systemd 服务
		sudo systemctl enable --now clover-bootmanager
		echo -e "$current_password\n" | sudo -S /etc/systemd/system/clover-bootmanager.sh
		zenity --warning --title "Clover 工具箱" --text "Clover systemd 服务已启用。Windows 已禁用！" --width 500 --height 75
	fi

elif [ "$Choice" == "默认启动" ]
then
Boot_Choice=$(zenity --width 550 --height 300 --list --radiolist --multiple --title "Clover 工具箱" --column "选择" \
	--column "选项" --column "说明 - 请仔细阅读" \
	FALSE Windows "将 Windows 设为默认启动系统" \
	FALSE SteamOS "将 SteamOS 设为默认启动系统" \
	FALSE Bazzite "将 Bazzite 设为默认启动系统" \
	FALSE 上次系统 "将上一次启动的系统设为默认" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Boot_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Boot_Choice" == "Windows" ]
	then
		# 修改 config.plist 中的 Default Loader 为 Windows
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\microsoft\\bootmgfw\.efi<\/string>' $EFI_PATH/clover/config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "Windows 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "SteamOS" ]
	then
		# 修改 config.plist 中的 Default Loader
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\steamos\\steamcl\.efi<\/string>' $EFI_PATH/clover/config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "SteamOS 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "Bazzite" ]
	then
		# 修改 config.plist 中的 Default Loader
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\EFI\\FEDORA\\shimx64\.efi<\/string>' $EFI_PATH/clover/config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "Bazzite 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "上次系统" ]
	then
		# 修改 config.plist 中的 Default Volume
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>LastBootedVolume<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "上一次使用的系统现在是 Clover 中的默认启动项！" --width 425 --height 75
	fi

elif [ "$Choice" == "新Logo" ]
then
Logo_Choice=$(zenity --title "Clover 工具箱" --width 200 --height 350 --list \
	--column "Logo 名称" $(ls -l ~/1Clover-tools/logos/*.png | sed s/^.*\\/\//) )
	if [ $? -eq 1 ]
	then
		echo "用户按了取消。返回主菜单。"
	else
		echo -e "$current_password\n" | sudo -S cp ~/1Clover-tools/logos/$Logo_Choice $EFI_PATH/steamos/steamos.png
		zenity --warning --title "Clover 工具箱" --text "BGRT 标志已更改为 $Logo_Choice！" --width 400 --height 75
	fi

elif [ "$Choice" == "恢复Logo" ]
then
	echo -e "$current_password\n" | sudo -S rm $EFI_PATH/steamos/steamos.png &> /dev/null
	zenity --warning --title "Clover 工具箱" --text "BGRT 标志已恢复为默认！" --width 400 --height 75

elif [ "$Choice" == "分辨率" ]
then
Resolution_Choice=$(zenity --width 550 --height 250 --list --radiolist --multiple --title "Clover 工具箱" \
	--column "选择" --column "选项" --column "说明 - 请仔细阅读" \
	FALSE 默认 "使用默认屏幕分辨率 1280x800" \
	FALSE DeckHD "使用 DeckHD 屏幕分辨率 1920x1200" \
	FALSE DeckSight "使用 DeckSight 屏幕分辨率 1920x1080" \
	TRUE 退出 "***** 退出 Clover 工具箱 *****")

	if [ $? -eq 1 ] || [ "$Resolution_Choice" == "退出" ]
	then
		echo "用户按了取消。返回主菜单。"

	elif [ "$Resolution_Choice" == "默认" ]
	then
		# 修改 config.plist 中的屏幕分辨率为 1280x800
		echo -e "$current_password\n" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1280x800<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1280x800。" --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckHD" ]
	then
		# 修改 config.plist 中的屏幕分辨率为 1920x1200
		echo -e "$current_password\n" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1200<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1920x1200。" --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckSight" ]
	then
		# 修改 config.plist 中的屏幕分辨率为 1920x1080
		echo -e "$current_password\n" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1920x1080。" --width 400 --height 75

	fi

elif [ "$Choice" == "自定义" ]
then
	echo -e "$current_password\n" | sudo -S cp ~/1Clover-tools/efi/custom_clover_5157.efi $EFI_PATH/clover/cloverx64.efi
	zenity --warning --title "Clover 工具箱" --text "自定义 Clover EFI 已安装！" --width 400 --height 75

elif [ "$Choice" == "卸载" ]
then
	# 从备份恢复 Windows EFI 条目
	echo -e "$current_password\n" | sudo -S mv $EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig $EFI_PATH/Microsoft/Boot/bootmgfw.efi
	if [ $? -eq 0 ]
	then
		echo -e "$current_password\n" | sudo -S rm $EFI_PATH/Microsoft/bootmgfw.efi
	else
		echo -e "$current_password\n" | sudo -S mv $EFI_PATH/Microsoft/bootmgfw.efi $EFI_PATH/Microsoft/Boot/bootmgfw.efi
	fi
	echo -e "$current_password\n" | sudo -S mv $BOOTX64.orig $BOOTX64

	# 从 EFI 系统分区移除 Clover
	echo -e "$current_password\n" | sudo -S rm -rf $EFI_PATH/clover

	for entry in $(efibootmgr | grep "Clover - GUI" | colrm 9 | colrm 1 4)
	do
		echo -e "$current_password\n" | sudo -S efibootmgr -b $entry -B &> /dev/null
	done

	# 移除自定义 BGRT 标志
	echo -e "$current_password\n" | sudo -S rm $EFI_PATH/steamos/steamos.png &> /dev/null

	echo -e "$current_password\n" | sudo -S steamos-readonly disable

	# 删除 systemd 服务
	echo -e "$current_password\n" | sudo -S systemctl stop clover-bootmanager.service
	echo -e "$current_password\n" | sudo -S rm /etc/systemd/system/clover-bootmanager*
	echo -e "$current_password\n" | sudo -S systemctl daemon-reload

	echo -e "$current_password\n" | sudo -S rm -f /etc/atomic-update.conf.d/clover-whitelist.conf

	echo -e "$current_password\n" | sudo -S steamos-readonly enable

	# 删除 dolphin 右键扩展
	rm ~/.local/share/kservices5/ServiceMenus/open_as_root.desktop

	rm -rf ~/SteamDeck-Clover-dualboot
	rm -rf ~/1Clover-tools/

	# 删除桌面上的“引导文件配置”快捷方式（如果存在）
	rm -f ~/Desktop/引导文件配置.desktop

	zenity --warning --title "Clover 工具箱" --text "Clover 已卸载，Windows EFI 条目已激活！" --width 600 --height 75
	exit
fi
done
TOOLBOX_EOF

    chmod +x ~/1Clover-tools/Clover-Toolbox.sh
    echo -e "${GREEN}✓ 已更新 Clover-Toolbox.sh 为汉化版。${NC}"

    echo -e "${YELLOW}建议重启 Steam Deck 以使引导生效。${NC}"
    echo ""
    read -p "按回车键返回主菜单..." < /dev/tty
}

remote_connection_fix() {
    show_header
    echo -e "${YELLOW}════════════════ 远程无法连接点我 ════════════════${NC}"
    echo ""
    echo "请选择要切换的显示服务器模式："
    echo "1. 切换为 X11（无法连接远程时选择此项）"
    echo "2. 切换为默认模式"
    echo ""
    read -p "请输入选择 [1-2] (其他键返回): " choice < /dev/tty

    case $choice in
        1)
            echo -e "${CYAN}正在切换至 X11 会话...${NC}"
            steamos-session-select plasma-x11-persistent
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ 已切换为 X11，请注销后重新登录生效。${NC}"
            else
                echo -e "${RED}✗ 切换失败，请检查系统是否支持该命令。${NC}"
            fi
            ;;
        2)
            echo -e "${CYAN}正在切换至默认模式...${NC}"
            steamos-session-select
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ 已切换为默认模式，请注销后重新登录生效。${NC}"
            else
                echo -e "${RED}✗ 切换失败，请检查系统是否支持该命令。${NC}"
            fi
            ;;
        *)
            echo "返回主菜单..."
            ;;
    esac
    read -p "按回车键返回主菜单..." < /dev/tty
}

main() {
    init_dirs
    detect_system_type

    auto_update_check

    create_desktop_shortcuts

    show_main_menu
}

main "$@"
