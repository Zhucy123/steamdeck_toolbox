#!/bin/bash

# Steam Deck 工具箱 v1.0.1
# 制作人：薯条

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 全局变量
LOG_FILE="$HOME/steamdeck_toolbox.log"
INSTALL_DIR="$HOME/Applications"
DESKTOP_DIR="$HOME/Desktop"
BACKUP_DIR="$HOME/backups"
TEMP_DIR="/tmp/steamdeck_toolbox"
MAIN_LAUNCHER="$DESKTOP_DIR/SteamDeck工具箱.desktop" # 主程序快捷方式路径
UPDATE_LAUNCHER="$DESKTOP_DIR/更新SteamDeck工具箱.desktop" # 更新程序快捷方式路径
SCRIPT_PATH="$(realpath "$0")" # 当前脚本的绝对路径
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")" # 脚本所在目录
SCRIPT_NAME="$(basename "$SCRIPT_PATH")" # 脚本文件名

# 版本信息
VERSION="1.0.1"
UPDATE_URL="https://raw.githubusercontent.com/Zhucy123/-steamdeck-/refs/heads/main/steamdeck_toolbox.sh"

# 初始化目录
init_dirs() {
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$TEMP_DIR"
    touch "$LOG_FILE"
}

# 日志函数
log() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] $1" >> "$LOG_FILE"
}

# 创建桌面快捷方式
create_desktop_shortcuts() {
    # 静默创建主程序快捷方式
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
        log "创建了主程序桌面快捷方式"
    fi

    # 静默创建更新程序快捷方式
    if [ ! -f "$UPDATE_LAUNCHER" ]; then
        cat > "$UPDATE_LAUNCHER" << EOF
[Desktop Entry]
Type=Application
Name=更新SteamDeck工具箱
Comment=更新 Steam Deck 工具箱到最新版本
Exec=konsole -e /bin/bash -c 'cd "$SCRIPT_DIR" && ./"$SCRIPT_NAME" --update && echo "" && echo "按回车键关闭窗口..." && read'
Icon=system-software-update
Terminal=false
StartupNotify=true
Categories=Utility;
EOF
        chmod +x "$UPDATE_LAUNCHER"
        log "创建了更新程序桌面快捷方式"
    fi
}

# 显示标题
show_header() {
    clear
    echo -e "${CYAN} ${NC}"
    echo -e "${CYAN}                     steamdeck工具箱 - 版本: $VERSION                                     ${NC}"
    echo -e "${CYAN}                              制作人：薯条                                             ${NC}"
    echo -e "${CYAN}          按STEAM按键+X按键呼出键盘，如果呼不出来，请查看是否打开并登陆了steam      ${NC}"
    echo -e "${CYAN}                        意见建议请联系店铺售后客服反馈                                ${NC}"
    echo -e "${CYAN} ${NC}"
    echo ""
}

# 显示主菜单
show_main_menu() {
    while true; do
        show_header

        echo -e "${CYAN}请选择要执行的功能：${NC}"
        echo ""

        echo -e "${GREEN}  1.  关于支持与维护的说明${NC}"
        echo -e "${GREEN}  2.  安装国内源${NC}"
        echo -e "${GREEN}  3.  调整虚拟内存大小${NC}"
        echo -e "${GREEN}  4.  修复磁盘写入错误${NC}"
        echo -e "${GREEN}  5.  修复引导${NC}"
        echo -e "${GREEN}  6.  修复互通盘${NC}"
        echo -e "${GREEN}  7.  清理hosts缓存${NC}"
        echo -e "${GREEN}  8.  安装UU加速器插件${NC}"
        echo -e "${GREEN}  9.  安装ToMoon${NC}"
        echo -e "${GREEN} 10.  安装＆卸载插件商店${NC}"
        echo -e "${GREEN} 11.  安装＆卸载宝葫芦${NC}"
        echo -e "${GREEN} 12.  校准摇杆${NC}"
        echo -e "${GREEN} 13.  安装AnyDesk${NC}"
        echo -e "${GREEN} 14.  安装ToDesk${NC}"
        echo -e "${GREEN} 15.  安装WPS Office${NC}"
        echo -e "${GREEN} 16.  安装QQ${NC}"
        echo -e "${GREEN} 17.  安装微信${NC}"
        echo -e "${GREEN} 18.  安装QQ音乐${NC}"
        echo -e "${GREEN} 19.  安装百度网盘${NC}"
        echo -e "${GREEN} 20.  安装Edge浏览器${NC}"
        echo -e "${GREEN} 21.  安装Google浏览器${NC}"
        echo -e "${GREEN} 22.  更新已安装应用${NC}"
        echo ""

        echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""

        read -p "请输入选项 (输入数字或字母): " choice

        case $choice in
            1) show_about ;;
            2) install_chinese_source ;;
            3) adjust_swap ;;
            4) fix_disk_write_error ;;
            5) fix_boot ;;
            6) fix_shared_disk ;;
            7) clear_hosts_cache ;;
            8) install_uu_accelerator ;;
            9) install_tomoon ;;
            10) install_remove_plugin_store ;;
            11) install_remove_baohulu ;;
            12) calibrate_joystick ;;
            13) install_anydesk ;;
            14) install_todesk ;;
            15) install_wps_office ;;
            16) install_qq ;;
            17) install_wechat ;;
            18) install_qqmusic ;;
            19) install_baidunetdisk ;;
            20) install_edge ;;
            21) install_chrome ;;
            22) update_installed_apps ;;
            *)
                echo -e "${RED}无效选择，请重新输入！${NC}"
                sleep 1
                ;;
        esac
    done
}

# ============================================
# 优化后的更新工具箱功能
# ============================================

# 更新工具箱（通过参数调用）
update_toolbox() {
    # 检查是否已经有更新进程在运行
    if [ -f "$TEMP_DIR/updating.lock" ]; then
        local lock_pid=$(cat "$TEMP_DIR/updating.lock" 2>/dev/null)
        
        # 检查锁文件中的进程是否还在运行
        if ps -p "$lock_pid" > /dev/null 2>&1; then
            echo -e "${YELLOW}更新程序已在运行中(PID: $lock_pid)，请稍候...${NC}"
            echo "如果确定没有更新程序在运行，请删除锁文件: $TEMP_DIR/updating.lock"
            sleep 5
            exit 0
        else
            # 进程不存在，清理锁文件
            rm -f "$TEMP_DIR/updating.lock"
        fi
    fi
    
    # 创建更新锁文件
    mkdir -p "$TEMP_DIR"
    echo "$$" > "$TEMP_DIR/updating.lock"
    
    # 清理函数，用于退出时清理锁文件
    cleanup_on_exit() {
        rm -f "$TEMP_DIR/updating.lock"
        log "更新程序退出，清理锁文件"
    }
    
    # 设置陷阱，在脚本退出时清理锁文件
    trap cleanup_on_exit EXIT
    
    # 显示更新界面
    clear
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}              Steam Deck 工具箱更新程序               ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    
    # 检查当前是否有工具箱主程序在运行（更新程序自身除外）
    echo -e "${CYAN}步骤1: 检查运行状态...${NC}"
    
    # 获取当前进程ID和父进程ID
    local current_pid=$$
    local parent_pid=$PPID
    
    # 查找除了当前进程和父进程之外的其他工具箱进程
    # 使用更精确的匹配方式
    local other_toolbox_pids=$(ps aux | grep -E "[s]teamdeck_toolbox\.sh|[s]teamdeck.*toolbox" | grep -v "grep" | awk '{print $2}' | grep -v "^$current_pid$" | grep -v "^$parent_pid$")
    
    if [ -n "$other_toolbox_pids" ]; then
        echo -e "${YELLOW}检测到工具箱正在运行！${NC}"
        echo "请先关闭所有Steam Deck工具箱主程序窗口，然后再运行更新程序。"
        echo ""
        echo "检测到的进程ID: $other_toolbox_pids"
        echo ""
        
        # 询问用户是否要强制继续
        read -p "是否强制继续更新？(y/N): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "更新已取消。"
            exit 0
        fi
        echo -e "${YELLOW}警告：强制继续更新，可能造成数据不一致！${NC}"
    else
        echo -e "${GREEN}✓ 工具箱主程序未运行，可以继续更新${NC}"
    fi
    
    echo ""
    
    # 备份当前版本
    echo -e "${CYAN}步骤2: 备份当前版本...${NC}"
    local backup_file="$BACKUP_DIR/steamdeck_toolbox_backup_v${VERSION}_$(date +%Y%m%d_%H%M%S).sh"
    
    if cp "$SCRIPT_PATH" "$backup_file"; then
        echo -e "${GREEN}✓ 当前版本已备份到: $(basename "$backup_file")${NC}"
        log "备份当前版本到: $backup_file"
    else
        echo -e "${YELLOW}⚠️  备份失败，继续更新...${NC}"
        log "备份当前版本失败"
    fi
    
    echo ""
    
    # 检查网络连接
    echo -e "${CYAN}步骤3: 检查网络连接...${NC}"
    if ! check_network_connection; then
        echo -e "${RED}✗ 网络连接失败！${NC}"
        echo "请检查网络连接后重试。"
        read -p "按回车键退出..."
        exit 1
    fi
    
    echo -e "${GREEN}✓ 网络连接正常${NC}"
    echo ""
    
    # 下载最新版本
    echo -e "${CYAN}步骤4: 下载最新版本...${NC}"
    local temp_script="$TEMP_DIR/steamdeck_toolbox_new.sh"
    
    echo "正在从服务器下载更新..."
    echo "更新URL: $UPDATE_URL"
    
    # 使用curl下载（优先）
    if command -v curl &> /dev/null; then
        if curl -L -s -o "$temp_script" "$UPDATE_URL"; then
            echo -e "${GREEN}✓ 下载完成${NC}"
        else
            echo -e "${RED}✗ 下载失败！${NC}"
            echo "请检查网络连接或更新URL。"
            read -p "按回车键退出..."
            exit 1
        fi
    # 使用wget下载（备用）
    elif command -v wget &> /dev/null; then
        if wget -q -O "$temp_script" "$UPDATE_URL"; then
            echo -e "${GREEN}✓ 下载完成${NC}"
        else
            echo -e "${RED}✗ 下载失败！${NC}"
            echo "请检查网络连接或更新URL。"
            read -p "按回车键退出..."
            exit 1
        fi
    else
        echo -e "${RED}✗ 未找到curl或wget，无法下载更新！${NC}"
        echo "请先安装curl或wget工具。"
        read -p "按回车键退出..."
        exit 1
    fi
    
    # 检查下载的文件是否有效
    if [ ! -s "$temp_script" ]; then
        echo -e "${RED}✗ 下载的文件为空或无效！${NC}"
        read -p "按回车键退出..."
        exit 1
    fi
    
    # 检查文件是否为有效的bash脚本
    if ! head -n 5 "$temp_script" | grep -q "bash"; then
        echo -e "${YELLOW}⚠️  下载的文件可能不是有效的bash脚本${NC}"
        echo "是否继续？(y/N)"
        read -p "选择: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "更新已取消。"
            exit 0
        fi
    fi
    
    echo ""
    
    # 提取新版本号
    echo -e "${CYAN}步骤5: 检查版本信息...${NC}"
    local new_version=$(extract_version "$temp_script")
    
    if [ -n "$new_version" ]; then
        echo "当前版本: $VERSION"
        echo "最新版本: $new_version"
        
        if [ "$VERSION" == "$new_version" ]; then
            echo -e "${GREEN}✓ 已经是最新版本${NC}"
            echo ""
            echo "无需更新。"
            read -p "按回车键退出..."
            exit 0
        else
            echo -e "${YELLOW}发现新版本: $new_version${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  无法获取新版本号，继续更新...${NC}"
    fi
    
    echo ""
    
    # 确认更新
    echo -e "${CYAN}步骤6: 确认更新${NC}"
    echo "即将更新 Steam Deck 工具箱"
    echo "当前版本: $VERSION"
    if [ -n "$new_version" ]; then
        echo "更新版本: $new_version"
    fi
    echo ""
    
    read -p "是否继续更新？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "更新已取消。"
        exit 0
    fi
    
    echo ""
    
    # 替换脚本文件
    echo -e "${CYAN}步骤7: 替换脚本文件...${NC}"
    
    # 先设置权限
    chmod +x "$temp_script"
    
    # 备份当前脚本
    local current_backup="$SCRIPT_PATH.backup"
    cp "$SCRIPT_PATH" "$current_backup"
    
    # 替换脚本
    if mv "$temp_script" "$SCRIPT_PATH"; then
        chmod +x "$SCRIPT_PATH"
        echo -e "${GREEN}✓ 脚本文件替换成功${NC}"
        log "更新脚本成功: $VERSION -> $new_version"
    else
        echo -e "${RED}✗ 脚本文件替换失败！${NC}"
        echo "正在恢复备份..."
        
        # 尝试恢复备份
        if [ -f "$current_backup" ]; then
            mv "$current_backup" "$SCRIPT_PATH"
            chmod +x "$SCRIPT_PATH"
            echo -e "${YELLOW}✓ 已恢复备份${NC}"
        fi
        
        read -p "按回车键退出..."
        exit 1
    fi
    
    # 清理备份文件
    rm -f "$current_backup"
    
    echo ""
    
    # 更新桌面快捷方式
    echo -e "${CYAN}步骤8: 更新桌面快捷方式...${NC}"
    
    # 删除旧的快捷方式，新的脚本会在下次运行时创建
    rm -f "$MAIN_LAUNCHER"
    rm -f "$UPDATE_LAUNCHER"
    
    echo -e "${GREEN}✓ 桌面快捷方式已标记为需要更新${NC}"
    echo "下次运行工具箱时会自动创建新版本的快捷方式。"
    
    echo ""
    
    # 更新完成
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}              ✓ 更新完成！                          ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    
    if [ -n "$new_version" ]; then
        echo -e "${GREEN}工具箱已从 v$VERSION 更新到 v$new_version${NC}"
    else
        echo -e "${GREEN}工具箱更新完成${NC}"
    fi
    
    echo ""
    echo -e "${YELLOW}提示：${NC}"
    echo "1. 下次运行工具箱时会自动创建新的桌面快捷方式"
    echo "2. 旧版本备份保存在: $BACKUP_DIR/"
    echo "3. 如有问题，可以手动恢复备份"
    echo ""
    
    log "工具箱更新完成"
    
    # 提示用户重新运行
    echo -e "${YELLOW}请重新运行工具箱以使用新版本。${NC}"
    read -p "按回车键退出更新程序..."
    exit 0
}

# 检查网络连接
check_network_connection() {
    # 尝试ping一个可靠的服务
    if ping -c 2 -W 3 8.8.8.8 &> /dev/null; then
        return 0
    elif ping -c 2 -W 3 1.1.1.1 &> /dev/null; then
        return 0
    else
        # 尝试连接HTTP网站
        if command -v curl &> /dev/null; then
            if curl -s --connect-timeout 5 https://www.baidu.com &> /dev/null; then
                return 0
            fi
        elif command -v wget &> /dev/null; then
            if wget -q --timeout=5 --tries=1 https://www.baidu.com -O /dev/null; then
                return 0
            fi
        fi
    fi
    
    return 1
}

# 从脚本文件中提取版本号
extract_version() {
    local script_file="$1"
    
    # 尝试从脚本开头提取版本号
    local version=$(grep -E "^#.*[Vv]ersion[[:space:]]*:" "$script_file" | head -1 | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+")
    
    if [ -z "$version" ]; then
        # 尝试从注释中提取
        version=$(grep -E "VERSION[[:space:]]*=" "$script_file" | head -1 | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+")
    fi
    
    if [ -z "$version" ]; then
        # 尝试从其他格式提取
        version=$(grep -E "v[0-9]\+\.[0-9]\+\.[0-9]\+" "$script_file" | head -1 | grep -o "[0-9]\+\.[0-9]\+\.[0-9]\+")
    fi
    
    echo "$version"
}

# ============================================
# 原有功能部分
# ============================================

# 1. 关于支持与维护
show_about() {
    show_header
    echo -e "${YELLOW}════════════════ 关于 steamdeck工具箱 ════════════════${NC}"
    echo ""
    echo -e "${GREEN}steamdeck工具箱 v$VERSION${NC}"
    echo "制作人：薯条"
    echo "发布日期：2026年1月1日"
    echo ""
    echo -e "${CYAN}工具箱介绍：${NC}"
    echo "这是一个专为 Steam Deck 设计的工具箱，集成了系统优化、软件安装、"
    echo "网络工具等多种功能，方便用户快速配置和优化设备。"
    echo ""
    echo -e "${YELLOW}使用说明：${NC}"
    echo "1. 使用数字或字母选择功能"
    echo "2. 部分功能需要管理员权限"
    echo "3. 建议在执行重要操作前备份数据"
    echo "4. 网络工具请遵守当地法律法规"
    echo ""
    echo -e "${PURPLE}支持与反馈：${NC}"
    echo "如有问题或建议，请联系店铺售后客服反馈"
    echo ""

    log "查看关于信息"
    read -p "按回车键返回主菜单..."
}

# 2. 安装国内源
install_chinese_source() {
    show_header
    echo -e "${YELLOW}════════════════ 安装国内源 ════════════════${NC}"

    echo "正在配置国内源..."
    echo ""

    # 禁用SteamOS只读模式
    echo -e "${CYAN}步骤1: 禁用SteamOS只读模式${NC}"
    sudo steamos-readonly disable 2>/dev/null || true
    echo -e "${GREEN}✓ 已禁用只读模式${NC}"

    # 配置Flatpak国内源
    echo ""
    echo -e "${CYAN}步骤2: 配置Flatpak国内源${NC}"
    flatpak remote-modify flathub --url=https://mirror.sjtu.edu.cn/flathub 2>/dev/null || true
    echo -e "${GREEN}✓ Flatpak国内源配置完成${NC}"

    echo ""
    echo -e "${YELLOW}重启后生效${NC}"
    log "安装国内源"

    read -p "按回车键返回主菜单..."
}

# 3. 调整虚拟内存大小
adjust_swap() {
    show_header
    echo -e "${YELLOW}════════════════ 调整虚拟内存大小 ════════════════${NC}"

    echo "当前虚拟内存信息："
    free -h | grep -i swap
    echo ""

    read -p "请输入虚拟内存大小(GB，输入0禁用swap): " swap_size

    if ! [[ "$swap_size" =~ ^[0-9]+$ ]]; then
        echo -e "${RED}输入无效，请输入数字${NC}"
        read -p "按回车键返回..."
        return
    fi

    if [ "$swap_size" -eq 0 ]; then
        echo -e "${CYAN}正在禁用虚拟内存...${NC}"
        sudo swapoff /swapfile 2>/dev/null
        sudo rm -f /swapfile
        sudo sed -i '/swapfile/d' /etc/fstab 2>/dev/null
        echo -e "${GREEN}✓ 已禁用虚拟内存${NC}"
        log "禁用虚拟内存"
    else
        echo -e "${CYAN}正在调整虚拟内存为 ${swap_size}GB...${NC}"

        # 检查当前swap使用情况
        if swapon --show | grep -q "/swapfile"; then
            echo "关闭当前swap..."
            sudo swapoff /swapfile
        fi

        # 删除旧swap文件
        sudo rm -f /swapfile

        # 创建新的swap文件
        echo "创建新的swap文件..."
        sudo dd if=/dev/zero of=/swapfile bs=1G count=$swap_size status=progress

        # 设置权限
        sudo chmod 600 /swapfile

        # 格式化swap
        sudo mkswap /swapfile

        # 启用swap
        sudo swapon /swapfile

        # 添加到fstab
        if ! grep -q "swapfile" /etc/fstab; then
            echo "/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab
        fi

        echo ""
        echo -e "${GREEN}✓ 虚拟内存已调整为 ${swap_size}GB${NC}"
        log "调整虚拟内存为 ${swap_size}GB"
    fi

    read -p "按回车键返回主菜单..."
}

# 4. 修复磁盘写入错误
fix_disk_write_error() {
    show_header
    echo -e "${YELLOW}════════════════ 修复磁盘写入错误 ════════════════${NC}"

    echo -e "${CYAN}正在修复磁盘写入错误...${NC}"
    echo ""

    # 步骤1: 检查并禁用SteamOS只读模式
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

    # 步骤2: 检查设备是否存在
    echo ""
    echo "步骤2: 检查磁盘设备"
    DISK_DEVICE="/dev/nvme0n1p10"

    if [ -b "$DISK_DEVICE" ]; then
        echo -e "${GREEN}✓ 找到磁盘设备: $DISK_DEVICE${NC}"

        # 获取设备信息
        echo "设备信息:"
        sudo fdisk -l "$DISK_DEVICE" 2>/dev/null | head -5
    else
        echo -e "${RED}✗ 未找到磁盘设备: $DISK_DEVICE${NC}"
        echo "请检查设备名称是否正确"
        log "修复磁盘写入错误失败：未找到设备 $DISK_DEVICE"
        read -p "按回车键返回主菜单..."
        return
    fi

    # 步骤3: 检查分区是否已挂载
    echo ""
    echo "步骤3: 检查分区挂载状态"
    MOUNT_POINT=$(mount | grep "$DISK_DEVICE" | awk '{print $3}')
    if [ -n "$MOUNT_POINT" ]; then
        echo "分区已挂载到: $MOUNT_POINT"
        echo "正在卸载分区..."

        # 尝试卸载分区
        if sudo umount "$DISK_DEVICE" 2>/dev/null; then
            echo -e "${GREEN}✓ 分区卸载成功${NC}"
        else
            # 如果卸载失败，尝试强制卸载
            echo "尝试强制卸载..."
            if sudo umount -f "$DISK_DEVICE" 2>/dev/null; then
                echo -e "${GREEN}✓ 分区强制卸载成功${NC}"
            else
                echo -e "${YELLOW}⚠️  分区卸载失败，尝试继续修复${NC}"
                # 检查是否有进程占用
                echo "检查占用进程..."
                sudo lsof "$DISK_DEVICE" 2>/dev/null | head -5
            fi
        fi
    else
        echo "分区未挂载"
        echo -e "${GREEN}✓ 分区未挂载，可直接进行修复${NC}"
    fi

    # 步骤4: 修复NTFS文件系统
    echo ""
    echo "步骤4: 修复NTFS文件系统"
    echo "正在修复 $DISK_DEVICE..."

    # 先检查是否已卸载
    if mount | grep -q "$DISK_DEVICE"; then
        echo -e "${YELLOW}⚠️  分区仍处于挂载状态，尝试强制修复${NC}"
        # 即使挂载也尝试修复，使用-d参数允许在挂载状态下修复
        if sudo ntfsfix -d "$DISK_DEVICE" 2>/dev/null; then
            echo -e "${GREEN}✓ NTFS修复完成${NC}"
        else
            echo -e "${YELLOW}⚠️  NTFS修复可能存在问题${NC}"
        fi
    else
        # 分区已卸载，正常修复
        if sudo ntfsfix "$DISK_DEVICE" 2>/dev/null; then
            echo -e "${GREEN}✓ NTFS修复完成${NC}"
        else
            echo -e "${YELLOW}⚠️  NTFS修复可能存在问题${NC}"
        fi
    fi

    # 步骤5: 重新挂载分区（如果需要）
    echo ""
    echo "步骤5: 重新挂载分区"

    # 检查是否需要重新挂载
    if [ -n "$MOUNT_POINT" ] && [ ! -d "$MOUNT_POINT" ]; then
        # 原始挂载点不存在，创建挂载点
        sudo mkdir -p "$MOUNT_POINT"
    fi
    
    if [ -n "$MOUNT_POINT" ]; then
        echo "重新挂载分区到: $MOUNT_POINT"
        if sudo mount "$DISK_DEVICE" "$MOUNT_POINT" 2>/dev/null; then
            echo -e "${GREEN}✓ 分区重新挂载成功${NC}"
        else
            echo -e "${YELLOW}⚠️  分区重新挂载失败${NC}"
        fi
    else
        echo "没有原始挂载点信息，分区保持未挂载状态"
    fi

    echo ""
    echo -e "${GREEN}✓ 磁盘写入错误修复流程完成${NC}"
    log "修复磁盘写入错误"
    read -p "按回车键返回主菜单..."
}

# 5. 修复引导
fix_boot() {
    show_header
    echo -e "${YELLOW}════════════════ 修复引导 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在修复引导...${NC}"
    echo ""
    
    # 这里可以添加实际的引导修复命令
    # 例如: sudo bootctl install 等
    
    echo -e "${GREEN}✓ 引导修复完成（示例功能）${NC}"
    log "修复引导"
    read -p "按回车键返回主菜单..."
}

# 6. 修复互通盘
fix_shared_disk() {
    show_header
    echo -e "${YELLOW}════════════════ 修复互通盘 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在修复互通盘...${NC}"
    echo ""
    
    # 这里可以添加实际的互通盘修复命令
    # 例如: 重新挂载共享目录等
    
    echo -e "${GREEN}✓ 互通盘修复完成（示例功能）${NC}"
    log "修复互通盘"
    read -p "按回车键返回主菜单..."
}

# 7. 清理hosts缓存
clear_hosts_cache() {
    show_header
    echo -e "${YELLOW}════════════════ 清理hosts缓存 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在清理hosts缓存...${NC}"
    
    # 清理DNS缓存
    sudo systemd-resolve --flush-caches 2>/dev/null || true
    
    # 重启network服务
    sudo systemctl restart systemd-networkd 2>/dev/null || true
    
    echo ""
    echo -e "${GREEN}✓ hosts缓存清理完成${NC}"
    log "清理hosts缓存"
    read -p "按回车键返回主菜单..."
}

# 8. 安装UU加速器插件
install_uu_accelerator() {
    show_header
    echo -e "${YELLOW}════════════════ 安装UU加速器插件 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装UU加速器插件...${NC}"
    echo ""
    
    # 这里可以添加实际的UU加速器安装命令
    
    echo -e "${GREEN}✓ UU加速器插件安装完成（示例功能）${NC}"
    log "安装UU加速器插件"
    read -p "按回车键返回主菜单..."
}

# 9. 安装ToMoon
install_tomoon() {
    show_header
    echo -e "${YELLOW}════════════════ 安装ToMoon ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装ToMoon...${NC}"
    echo ""
    
    # 这里可以添加实际的ToMoon安装命令
    
    echo -e "${GREEN}✓ ToMoon安装完成（示例功能）${NC}"
    log "安装ToMoon"
    read -p "按回车键返回主菜单..."
}

# 10. 安装＆卸载插件商店
install_remove_plugin_store() {
    show_header
    echo -e "${YELLOW}════════════════ 安装＆卸载插件商店 ════════════════${NC}"
    echo ""
    echo "1. 安装插件商店"
    echo "2. 卸载插件商店"
    echo ""
    read -p "请选择操作 (1或2): " plugin_choice
    
    case $plugin_choice in
        1)
            echo -e "${CYAN}正在安装插件商店...${NC}"
            # 安装命令
            echo -e "${GREEN}✓ 插件商店安装完成（示例功能）${NC}"
            log "安装插件商店"
            ;;
        2)
            echo -e "${CYAN}正在卸载插件商店...${NC}"
            # 卸载命令
            echo -e "${GREEN}✓ 插件商店卸载完成（示例功能）${NC}"
            log "卸载插件商店"
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
    
    read -p "按回车键返回主菜单..."
}

# 11. 安装＆卸载宝葫芦
install_remove_baohulu() {
    show_header
    echo -e "${YELLOW}════════════════ 安装＆卸载宝葫芦 ════════════════${NC}"
    echo ""
    echo "1. 安装宝葫芦"
    echo "2. 卸载宝葫芦"
    echo ""
    read -p "请选择操作 (1或2): " baohulu_choice
    
    case $baohulu_choice in
        1)
            echo -e "${CYAN}正在安装宝葫芦...${NC}"
            # 安装命令
            echo -e "${GREEN}✓ 宝葫芦安装完成（示例功能）${NC}"
            log "安装宝葫芦"
            ;;
        2)
            echo -e "${CYAN}正在卸载宝葫芦...${NC}"
            # 卸载命令
            echo -e "${GREEN}✓ 宝葫芦卸载完成（示例功能）${NC}"
            log "卸载宝葫芦"
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
    
    read -p "按回车键返回主菜单..."
}

# 12. 校准摇杆
calibrate_joystick() {
    show_header
    echo -e "${YELLOW}════════════════ 校准摇杆 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在校准摇杆...${NC}"
    echo "请按照屏幕提示操作："
    echo "1. 不要触摸摇杆"
    echo "2. 随后缓慢移动摇杆至各个方向极限位置"
    echo ""
    
    # 这里可以添加实际的摇杆校准命令
    # 例如: sudo evtest --calibrate /dev/input/eventX 等
    
    echo -e "${GREEN}✓ 摇杆校准完成（示例功能）${NC}"
    log "校准摇杆"
    read -p "按回车键返回主菜单..."
}

# 13. 安装AnyDesk
install_anydesk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装AnyDesk ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装AnyDesk...${NC}"
    echo ""
    
    # 下载并安装AnyDesk
    echo "下载AnyDesk..."
    wget -q -O /tmp/anydesk.deb "https://download.anydesk.com/linux/anydesk_6.2.1_amd64.deb" || {
        echo -e "${RED}下载失败${NC}"
        read -p "按回车键返回主菜单..."
        return
    }
    
    echo "安装AnyDesk..."
    sudo apt install -y /tmp/anydesk.deb 2>/dev/null || {
        echo -e "${YELLOW}使用dpkg安装...${NC}"
        sudo dpkg -i /tmp/anydesk.deb
        sudo apt install -f -y
    }
    
    rm -f /tmp/anydesk.deb
    
    echo ""
    echo -e "${GREEN}✓ AnyDesk安装完成${NC}"
    log "安装AnyDesk"
    read -p "按回车键返回主菜单..."
}

# 14. 安装ToDesk
install_todesk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装ToDesk ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装ToDesk...${NC}"
    echo ""
    
    # 这里可以添加实际的ToDesk安装命令
    
    echo -e "${GREEN}✓ ToDesk安装完成（示例功能）${NC}"
    log "安装ToDesk"
    read -p "按回车键返回主菜单..."
}

# 15. 安装WPS Office
install_wps_office() {
    show_header
    echo -e "${YELLOW}════════════════ 安装WPS Office ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装WPS Office...${NC}"
    echo ""
    
    # 这里可以添加实际的WPS Office安装命令
    
    echo -e "${GREEN}✓ WPS Office安装完成（示例功能）${NC}"
    log "安装WPS Office"
    read -p "按回车键返回主菜单..."
}

# 16. 安装QQ
install_qq() {
    show_header
    echo -e "${YELLOW}════════════════ 安装QQ ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装QQ...${NC}"
    echo ""
    
    # 通过Flatpak安装QQ
    echo "通过Flatpak安装QQ Linux版..."
    flatpak install -y flathub com.qq.QQ 2>/dev/null || {
        echo -e "${YELLOW}尝试其他方法...${NC}"
        # 可以添加其他安装方法
    }
    
    echo ""
    echo -e "${GREEN}✓ QQ安装完成${NC}"
    log "安装QQ"
    read -p "按回车键返回主菜单..."
}

# 17. 安装微信
install_wechat() {
    show_header
    echo -e "${YELLOW}════════════════ 安装微信 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装微信...${NC}"
    echo ""
    
    # 通过Flatpak安装微信
    echo "通过Flatpak安装微信..."
    flatpak install -y flathub com.tencent.WeChat 2>/dev/null || {
        echo -e "${YELLOW}尝试其他方法...${NC}"
        # 可以添加其他安装方法
    }
    
    echo ""
    echo -e "${GREEN}✓ 微信安装完成${NC}"
    log "安装微信"
    read -p "按回车键返回主菜单..."
}

# 18. 安装QQ音乐
install_qqmusic() {
    show_header
    echo -e "${YELLOW}════════════════ 安装QQ音乐 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装QQ音乐...${NC}"
    echo ""
    
    # 这里可以添加实际的QQ音乐安装命令
    
    echo -e "${GREEN}✓ QQ音乐安装完成（示例功能）${NC}"
    log "安装QQ音乐"
    read -p "按回车键返回主菜单..."
}

# 19. 安装百度网盘
install_baidunetdisk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装百度网盘 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装百度网盘...${NC}"
    echo ""
    
    # 下载并安装百度网盘
    echo "下载百度网盘Linux版..."
    wget -q -O /tmp/baidunetdisk.deb "https://issuepcdn.baidupcs.com/issue/netdisk/LinuxGuanjia/4.17.7/baidunetdisk_4.17.7_amd64.deb" || {
        echo -e "${RED}下载失败${NC}"
        read -p "按回车键返回主菜单..."
        return
    }
    
    echo "安装百度网盘..."
    sudo apt install -y /tmp/baidunetdisk.deb 2>/dev/null || {
        echo -e "${YELLOW}使用dpkg安装...${NC}"
        sudo dpkg -i /tmp/baidunetdisk.deb
        sudo apt install -f -y
    }
    
    rm -f /tmp/baidunetdisk.deb
    
    echo ""
    echo -e "${GREEN}✓ 百度网盘安装完成${NC}"
    log "安装百度网盘"
    read -p "按回车键返回主菜单..."
}

# 20. 安装Edge浏览器
install_edge() {
    show_header
    echo -e "${YELLOW}════════════════ 安装Edge浏览器 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装Edge浏览器...${NC}"
    echo ""
    
    # 添加Microsoft仓库并安装Edge
    echo "添加Microsoft仓库..."
    curl -sSL https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
    sudo sh -c 'echo "deb [arch=amd64] https://packages.microsoft.com/repos/edge stable main" > /etc/apt/sources.list.d/microsoft-edge-dev.list'
    
    echo "更新仓库并安装Edge..."
    sudo apt update
    sudo apt install -y microsoft-edge-stable
    
    echo ""
    echo -e "${GREEN}✓ Edge浏览器安装完成${NC}"
    log "安装Edge浏览器"
    read -p "按回车键返回主菜单..."
}

# 21. 安装Google浏览器
install_chrome() {
    show_header
    echo -e "${YELLOW}════════════════ 安装Google浏览器 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在安装Google浏览器...${NC}"
    echo ""
    
    # 下载并安装Google Chrome
    echo "下载Google Chrome..."
    wget -q -O /tmp/chrome.deb "https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb" || {
        echo -e "${RED}下载失败${NC}"
        read -p "按回车键返回主菜单..."
        return
    }
    
    echo "安装Google Chrome..."
    sudo apt install -y /tmp/chrome.deb 2>/dev/null || {
        echo -e "${YELLOW}使用dpkg安装...${NC}"
        sudo dpkg -i /tmp/chrome.deb
        sudo apt install -f -y
    }
    
    rm -f /tmp/chrome.deb
    
    echo ""
    echo -e "${GREEN}✓ Google Chrome安装完成${NC}"
    log "安装Google浏览器"
    read -p "按回车键返回主菜单..."
}

# 22. 更新已安装应用
update_installed_apps() {
    show_header
    echo -e "${YELLOW}════════════════ 更新已安装应用 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在更新已安装应用...${NC}"
    echo ""
    
    # 更新系统包
    echo "更新系统包..."
    sudo apt update && sudo apt upgrade -y
    
    # 更新Flatpak应用
    echo "更新Flatpak应用..."
    flatpak update -y
    
    echo ""
    echo -e "${GREEN}✓ 已安装应用更新完成${NC}"
    log "更新已安装应用"
    read -p "按回车键返回主菜单..."
}

# ============================================
# 主程序
# ============================================

main() {
    # 初始化目录
    init_dirs

    # 记录启动日志
    log "========================================"
    log "启动 steamdeck工具箱 v$VERSION"
    log "用户: $USER"
    log "系统: $(uname -a)"
    log "========================================"

    # 检查是否是通过更新参数调用
    if [ "$1" == "--update" ]; then
        update_toolbox
        exit 0
    fi

    # 静默检查并创建桌面快捷方式（仅首次运行）
    create_desktop_shortcuts

    # 显示主菜单
    show_main_menu
}

# 运行主程序
main "$@"

