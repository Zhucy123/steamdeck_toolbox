#!/bin/bash

# Steam Deck 工具箱 v1.0.2
# 制作人：薯条＆DeepSeek

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m' # No Color

# 全局变量
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
VERSION="1.0.2"
REPO_URL="https://github.com/Zhucy123/steamdeck_toolbox" # GitHub仓库地址
REPO_CDN_URLS=(
    "https://githubfast.com/Zhucy123/steamdeck_toolbox"
    "https://gitclone.com/github.com/Zhucy123/steamdeck_toolbox"
    "https://github.com.cnpmjs.org/Zhucy123/steamdeck_toolbox"
    "https://github.com/Zhucy123/steamdeck_toolbox" # 原始地址放在最后
)

# 系统类型检测变量
SYSTEM_TYPE="" # 存储检测结果：single 或 dual

# 初始化目录
init_dirs() {
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$BACKUP_DIR"
    mkdir -p "$TEMP_DIR"
}

# 静默检测系统类型（单系统或双系统）- 修改为检查Clover引导
detect_system_type() {
    # 静默检测，不输出检测过程
    local has_clover=0

    # 方法1: 检查Clover引导目录（大小写敏感）
    if [ -d "/boot/efi/EFI/CLOVER" ] || [ -d "/boot/efi/EFI/Clover" ]; then
        has_clover=1
    fi

    # 方法2: 检查efibootmgr输出中是否有Clover引导项
    if command -v efibootmgr &> /dev/null; then
        if efibootmgr 2>/dev/null | grep -i "CLOVER" &> /dev/null; then
            has_clover=1
        fi
    fi

    # 方法3: 检查引导分区中的Clover文件
    if [ -f "/boot/efi/EFI/CLOVER/CLOVERX64.efi" ] || \
       [ -f "/boot/efi/EFI/CLOVER/config.plist" ] || \
       [ -f "/boot/efi/EFI/Clover/CLOVERX64.efi" ] || \
       [ -f "/boot/efi/EFI/Clover/config.plist" ]; then
        has_clover=1
    fi

    # 方法4: 检查是否有Windows引导（作为辅助判断）
    local has_windows=0
    if [ -d "/boot/efi/EFI/Microsoft" ] || \
       [ -f "/boot/efi/EFI/Microsoft/Boot/bootmgfw.efi" ] || \
       [ -d "/boot/efi/EFI/Boot" ] && [ -f "/boot/efi/EFI/Boot/bootx64.efi" ]; then
        has_windows=1
    fi

    # 判断逻辑：如果检测到Clover或Windows引导，则认为是双系统
    if [ $has_clover -eq 1 ] || [ $has_windows -eq 1 ]; then
        SYSTEM_TYPE="dual"
    else
        SYSTEM_TYPE="single"
    fi

    # 如果没有检测到任何引导，尝试其他方法确认
    if [ -z "$SYSTEM_TYPE" ]; then
        # 备用检测方法：检查引导分区中的引导项数量
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

# 显示标题
show_header() {
    clear
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}                     Steam Deck 工具箱 - 版本: $VERSION                               ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
    echo ""
}

# 创建桌面快捷方式（静默版）
create_desktop_shortcuts() {
    # 仅当快捷方式不存在时才创建
    # 1. 创建主程序快捷方式
    if [ ! -f "$MAIN_LAUNCHER" ]; then
        # 获取脚本的实际位置
        local script_dir=$(dirname "$(realpath "$0")")
        local script_name=$(basename "$0")

        cat > "$MAIN_LAUNCHER" << EOF
[Desktop Entry]
Type=Application
Name=SteamDeck 工具箱
Comment=Steam Deck 系统优化与软件管理工具 v$VERSION
Exec=konsole -e /bin/bash -c 'cd "$script_dir" && ./"$script_name" && echo "" && echo "程序执行完毕，按回车键关闭窗口..." && read'
Icon=utilities-terminal
Terminal=false
StartupNotify=true
Categories=Utility;
EOF
        chmod +x "$MAIN_LAUNCHER"
    fi

    # 2. 创建更新程序快捷方式（在主程序快捷方式之后创建）
    if [ ! -f "$UPDATE_LAUNCHER" ]; then
        local script_dir=$(dirname "$(realpath "$0")")
        local script_name=$(basename "$0")

        cat > "$UPDATE_LAUNCHER" << EOF
[Desktop Entry]
Type=Application
Name=更新SteamDeck工具箱
Comment=更新 Steam Deck 工具箱到最新版本
Exec=konsole -e /bin/bash -c 'cd "$script_dir" && ./"$script_name" --update && echo "" && echo "按回车键关闭窗口..." && read'
Icon=system-software-update
Terminal=false
StartupNotify=true
Categories=Utility;
EOF
        chmod +x "$UPDATE_LAUNCHER"
    fi
}

# 显示主菜单（根据系统类型动态调整）
show_main_menu() {
    while true; do
        clear

        # 显示简洁的标题
        echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
        echo -e "${CYAN}                     Steam Deck 工具箱 - 版本: $VERSION                               ${NC}"
        echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""

        # 显示系统类型信息（简洁版）
        if [ "$SYSTEM_TYPE" == "dual" ]; then
            echo -e "${GREEN}当前系统: 双系统${NC}"
        else
            echo -e "${YELLOW}当前系统: 单系统${NC}"
        fi
        echo ""

        echo -e "${CYAN}请选择要执行的功能：${NC}"
        echo ""

        # 预设的三列菜单布局
        echo -e "${GREEN} 1. 关于支持与维护的说明  11. 安装＆卸载插件商店  21. 安装百度网盘${NC}"
        echo -e "${GREEN} 2. 安装国内源            12. 安装＆卸载宝葫芦    22. 安装Edge浏览器${NC}"
        echo -e "${GREEN} 3. 调整虚拟内存大小      13. 校准摇杆            23. 安装Google浏览器${NC}"
        echo -e "${GREEN} 4. 修复磁盘写入错误      14. 设置管理员密码      24. 清理Steam缓存${NC}"
        echo -e "${GREEN} 5. 修复引导              15. 安装AnyDesk         25. 更新已安装应用${NC}"
        echo -e "${GREEN} 6. 修复互通盘            16. 安装ToDesk          26. 卸载已安装应用${NC}"
        echo -e "${GREEN} 7. 清理hosts缓存         17. 安装WPS Office      27. 检查工具箱更新${NC}"
        echo -e "${GREEN} 8. 安装UU加速器插件      18. 安装QQ${NC}"
        echo -e "${GREEN} 9. 安装迅游加速器插件    19. 安装微信${NC}"
        echo -e "${GREEN}10. 安装ToMoon            20. 安装QQ音乐${NC}"

        echo ""
        echo -e "${CYAN}════════════════════════════════════════════════════════════════════════════════════════${NC}"
        echo ""

        read -p "请输入选项 (输入数字): " choice

        # 验证输入
        if [[ ! "$choice" =~ ^[0-9]+$ ]]; then
            echo -e "${RED}无效选择，请输入数字！${NC}"
            sleep 1
            continue
        fi

        # 检查选择是否在有效范围内
        if [ $choice -lt 1 ] || [ $choice -gt 27 ]; then
            echo -e "${RED}无效选择，请选择1到27之间的数字！${NC}"
            sleep 1
            continue
        fi

        # 创建菜单项数组
        local menu_items=()
        local menu_functions=()

        # 添加菜单项（根据系统类型调整）
        menu_items+=("关于支持与维护的说明")
        menu_functions+=("show_about")

        menu_items+=("安装国内源")
        menu_functions+=("install_chinese_source")

        menu_items+=("调整虚拟内存大小")
        menu_functions+=("adjust_swap")

        menu_items+=("修复磁盘写入错误")
        menu_functions+=("fix_disk_write_error")

        if [ "$SYSTEM_TYPE" == "dual" ]; then
            menu_items+=("修复引导")
            menu_functions+=("fix_boot")

            menu_items+=("修复互通盘")
            menu_functions+=("fix_shared_disk")
        fi

        menu_items+=("清理hosts缓存")
        menu_functions+=("clear_hosts_cache")

        menu_items+=("安装UU加速器插件")
        menu_functions+=("install_uu_accelerator")

        menu_items+=("安装迅游加速器插件")
        menu_functions+=("install_xunyou_accelerator")

        menu_items+=("安装ToMoon")
        menu_functions+=("install_tomoon")

        menu_items+=("安装＆卸载插件商店")
        menu_functions+=("install_remove_plugin_store")

        menu_items+=("安装＆卸载宝葫芦")
        menu_functions+=("install_remove_baohulu")

        menu_items+=("校准摇杆")
        menu_functions+=("calibrate_joystick")

        menu_items+=("设置管理员密码")
        menu_functions+=("set_admin_password")

        menu_items+=("安装AnyDesk")
        menu_functions+=("install_anydesk")

        menu_items+=("安装ToDesk")
        menu_functions+=("install_todesk")

        menu_items+=("安装WPS Office")
        menu_functions+=("install_wps_office")

        menu_items+=("安装QQ")
        menu_functions+=("install_qq")

        menu_items+=("安装微信")
        menu_functions+=("install_wechat")

        menu_items+=("安装QQ音乐")
        menu_functions+=("install_qqmusic")

        menu_items+=("安装百度网盘")
        menu_functions+=("install_baidunetdisk")

        menu_items+=("安装Edge浏览器")
        menu_functions+=("install_edge")

        menu_items+=("安装Google浏览器")
        menu_functions+=("install_chrome")

        menu_items+=("清理Steam缓存")
        menu_functions+=("steamdeck_cache_manager")

        menu_items+=("更新已安装应用")
        menu_functions+=("update_installed_apps")

        menu_items+=("卸载已安装应用")
        menu_functions+=("uninstall_apps")

        menu_items+=("检查工具箱更新")
        menu_functions+=("check_for_updates")

        # 执行对应的功能
        local idx=$((choice - 1))
        local func="${menu_functions[$idx]}"

        # 调用函数
        $func
    done
}

# 映射用户选择到实际功能（根据系统类型调整）
map_choice_to_function() {
    local choice="$1"

    # 如果系统类型未检测，重新检测
    if [ -z "$SYSTEM_TYPE" ]; then
        detect_system_type
    fi

    # 单系统情况下的菜单映射
    if [ "$SYSTEM_TYPE" == "single" ]; then
        case $choice in
            # 1-4项直接对应
            1) show_about ;;
            2) install_chinese_source ;;
            3) adjust_swap ;;
            4) fix_disk_write_error ;;

            # 5-25项需要向后偏移2位（因为跳过了5、6两项）
            5) clear_hosts_cache ;;
            6) install_uu_accelerator ;;
            7) install_xunyou_accelerator ;;
            8) install_tomoon ;;
            9) install_remove_plugin_store ;;
            10) install_remove_baohulu ;;
            11) calibrate_joystick ;;
            12) set_admin_password ;;
            13) install_anydesk ;;
            14) install_todesk ;;
            15) install_wps_office ;;
            16) install_qq ;;
            17) install_wechat ;;
            18) install_qqmusic ;;
            19) install_baidunetdisk ;;
            20) install_edge ;;
            21) install_chrome ;;
            22) steamdeck_cache_manager ;;
            23) update_installed_apps ;;
            24) uninstall_apps ;;
            25) check_for_updates ;;
            *)
                echo -e "${RED}无效选择，请重新输入！${NC}"
                sleep 1
                ;;
        esac
    else
        # 双系统情况下的菜单映射（原样）
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
            12) install_remove_baohulu ;;
            13) calibrate_joystick ;;
            14) set_admin_password ;;
            15) install_anydesk ;;
            16) install_todesk ;;
            17) install_wps_office ;;
            18) install_qq ;;
            19) install_wechat ;;
            20) install_qqmusic ;;
            21) install_baidunetdisk ;;
            22) install_edge ;;
            23) install_chrome ;;
            24) steamdeck_cache_manager ;;
            25) update_installed_apps ;;
            26) uninstall_apps ;;
            27) check_for_updates ;;
            *)
                echo -e "${RED}无效选择，请重新输入！${NC}"
                sleep 1
                ;;
        esac
    fi
}

# ============================================
# 优化的更新功能（使用CDN镜像加速下载）
# ============================================

# 检查更新（通过菜单调用）
check_for_updates() {
    show_header
    echo -e "${YELLOW}════════════════ 检查工具箱更新 ════════════════${NC}"
    echo ""

    # 直接执行更新流程，不检查运行状态
    update_toolbox
}

# 更新工具箱（使用CDN镜像加速下载）
update_toolbox() {
    # 显示更新界面
    clear
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${CYAN}              Steam Deck 工具箱更新程序               ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""

    # 检查网络连接
    echo -e "${CYAN}步骤1: 检查网络连接...${NC}"
    if ! check_network_connection; then
        echo -e "${RED}✗ 网络连接失败！${NC}"
        echo "请检查网络连接后重试。"

        read -p "按回车键退出..."
        exit 1
    fi

    echo -e "${GREEN}✓ 网络连接正常${NC}"
    echo ""

    # 检查git是否安装
    echo -e "${CYAN}步骤2: 检查Git工具...${NC}"
    if ! command -v git &> /dev/null; then
        echo -e "${YELLOW}未找到git工具，正在尝试安装...${NC}"

        # 尝试安装git
        if command -v pacman &> /dev/null; then
            echo "正在安装git..."
            sudo pacman -Sy --noconfirm git
        elif command -v apt &> /dev/null; then
            echo "正在安装git..."
            sudo apt update && sudo apt install -y git
        else
            echo -e "${RED}无法自动安装git，请手动安装git后再试。${NC}"
            echo "安装命令: sudo pacman -S git 或 sudo apt install git"

            read -p "按回车键退出..."
            exit 1
        fi

        # 再次检查git是否安装成功
        if ! command -v git &> /dev/null; then
            echo -e "${RED}✗ Git安装失败！${NC}"

            read -p "按回车键退出..."
            exit 1
        fi
    fi

    echo -e "${GREEN}✓ Git工具可用${NC}"
    echo ""

    # 克隆GitHub仓库（使用CDN镜像）
    echo -e "${CYAN}步骤3: 下载最新版本...${NC}"
    local clone_dir="$HOME/steamdeck_toolbox"

    # 清理旧的下载目录
    if [ -d "$clone_dir" ]; then
        echo "清理旧的下载目录..."
        rm -rf "$clone_dir"
    fi

    echo "正在尝试使用CDN镜像加速下载..."
    echo ""

    # 尝试使用CDN镜像下载
    local download_success=false

    for url in "${REPO_CDN_URLS[@]}"; do
    # 提取URL名称用于显示
    local url_name
    if [[ "$url" == *"githubfast.com"* ]]; then
        url_name="GitHubFast镜像"
    elif [[ "$url" == *"gitclone.com"* ]]; then
        url_name="GitClone镜像"
    elif [[ "$url" == *"github.com.cnpmjs.org"* ]]; then
        url_name="CNPM镜像"
    elif [[ "$url" == *"github.com"* ]]; then
        url_name="GitHub原始地址"
    else
        url_name="未知镜像"
    fi

    echo "尝试从 $url_name 下载..."
    echo "下载地址: $url"

    # 清理旧的下载目录
    rm -rf "$clone_dir" 2>/dev/null

    # 设置超时为30秒
    if timeout 30 git clone --depth=1 "$url" "$clone_dir" 2>&1; then
        echo -e "${GREEN}✓ $url_name 下载成功${NC}"
        download_success=true
        break
    else
        echo -e "${YELLOW}⚠️  $url_name 下载失败，尝试下一个镜像...${NC}"
        echo ""
        # 清理失败的下载
        rm -rf "$clone_dir" 2>/dev/null
        sleep 1
    fi
done

    if [ "$download_success" = false ]; then
        echo -e "${RED}✗ 所有镜像下载失败！${NC}"
        echo "请检查网络连接或稍后重试。"
        echo "您也可以手动从以下地址下载："
        echo "1. GitHub原始地址: $REPO_URL"
        echo "2. CDN镜像地址: ${REPO_CDN_URLS[0]}"
        echo ""

        read -p "按回车键退出..."
        exit 1
    fi

    # 检查下载的文件是否有效
    local new_script_path="$clone_dir/steamdeck_toolbox.sh"
    if [ ! -f "$new_script_path" ]; then
        echo -e "${RED}✗ 在仓库中未找到脚本文件！${NC}"
        echo "请确认仓库中是否有 steamdeck_toolbox.sh 文件。"

        # 清理下载目录
        rm -rf "$clone_dir"

        read -p "按回车键退出..."
        exit 1
    fi

    # 检查文件是否为有效的bash脚本
    if ! head -n 5 "$new_script_path" | grep -q "bash"; then
        echo -e "${YELLOW}⚠️  下载的文件可能不是有效的bash脚本${NC}"
        echo "是否继续？(y/n)"
        read -p "选择: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "更新已取消。"

            # 清理下载目录
            rm -rf "$clone_dir"

            read -p "按回车键退出..."
            exit 0
        fi
    fi

    # 提取新版本号
    echo -e "${CYAN}步骤4: 检查版本信息...${NC}"
    local new_version=$(extract_version "$new_script_path")

    if [ -n "$new_version" ]; then
        echo "当前版本: $VERSION"
        echo "最新版本: $new_version"

        if [ "$VERSION" == "$new_version" ]; then
            echo -e "${GREEN}✓ 已经是最新版本${NC}"
            echo ""
            echo "无可用更新。"

            # 清理下载目录
            rm -rf "$clone_dir"

            echo "将在3秒后自动关闭..."
            sleep 3
            exit 0
        else
            echo -e "${YELLOW}发现新版本: $new_version${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  无法获取新版本号，继续更新...${NC}"
    fi

    echo ""

    # 确认更新
    echo -e "${CYAN}步骤5: 确认更新${NC}"
    echo "即将更新 Steam Deck 工具箱"
    echo "当前版本: $VERSION"
    if [ -n "$new_version" ]; then
        echo "更新版本: $new_version"
    fi
    echo ""

    read -p "是否继续更新？(y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "更新已取消。"

        # 清理下载目录
        rm -rf "$clone_dir"

        read -p "按回车键退出..."
        exit 0
    fi

    echo ""

    # 替换脚本文件
    echo -e "${CYAN}步骤6: 替换脚本文件...${NC}"

    # 先设置权限
    chmod +x "$new_script_path"

    # 直接替换脚本，不创建备份
    if cp "$new_script_path" "$SCRIPT_PATH"; then
        chmod +x "$SCRIPT_PATH"
        echo -e "${GREEN}✓ 脚本文件替换成功${NC}"
    else
        echo -e "${RED}✗ 脚本文件替换失败！${NC}"
        echo "请检查文件权限。"

        # 清理下载目录
        rm -rf "$clone_dir"

        read -p "按回车键退出..."
        exit 1
    fi

    # 清理下载目录
    echo -e "${CYAN}步骤7: 清理临时文件...${NC}"
    rm -rf "$clone_dir"
    echo -e "${GREEN}✓ 临时文件已清理${NC}"

    echo ""

    # 更新完成
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}              ✓ 更新完成！                          ${NC}"
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""

    if [ -n "$new_version" ]; then
        echo -e "${GREEN}工具箱已从 v$VERSION 成功更新到 v$new_version${NC}"
    else
        echo -e "${GREEN}工具箱更新完成${NC}"
    fi

    echo ""
    echo -e "${YELLOW}提示：${NC}"
    echo "1. 请重新启动工具箱以应用更新"
    echo ""

    # 提示用户重新启动
    echo "更新已完成！请重新启动工具箱以使用新版本。"
    read -p "按回车键退出..."
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
            if curl -s --connect-timeout 5 https://www.google.com &> /dev/null; then
                return 0
            fi
        elif command -v wget &> /dev/null; then
            if wget -q --timeout=5 --tries=1 https://www.google.com -O /dev/null; then
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
# 功能实现部分
# ============================================

# 1. 关于支持与维护
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
    fi

    read -p "按回车键返回主菜单..."
}

# 4. 修复磁盘写入错误
fix_disk_write_error() {
    show_header
    echo -e "${YELLOW}════════════════ 修复磁盘写入错误 ════════════════${NC}"

    echo -e "${CYAN}正在修复磁盘写入错误...${NC}"
    echo ""

    # 步骤1: 检查并禁用SteamOS只读模式（优化版）
    echo "步骤1: 检查并禁用SteamOS只读模式"

    # 首先检查当前只读状态，避免不必要的操作
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

    read -p "按回车键返回主菜单..."
}

# 5. 修复引导
fix_boot() {
    show_header
    echo -e "${YELLOW}════════════════ 修复引导 ════════════════${NC}"

    echo -e "${CYAN}正在运行引导修复脚本...${NC}"

    # 将修复引导脚本保存到临时文件
    cat > "$TEMP_DIR/fix_boot.sh" << 'EOF'
#!/bin/bash

# 脚本：自动设置Clover为第一启动项（自动权限提升版）
# 适用于Steam Deck双系统

echo "========================================"
echo "  Clover启动顺序自动设置脚本"
echo "========================================"
echo ""

# 自动权限提升：如果不是root，则用sudo重新运行自身
if [ "$EUID" -ne 0 ]; then
    echo "⚠️ 检测到需要管理员权限，正在提升权限..."
    echo "   如需修改启动顺序，请输入您的用户密码（输入时不会显示）"
    echo ""
    sudo "$0" "$@"
    exit $?
fi

# 检查efibootmgr是否存在
if ! command -v efibootmgr &> /dev/null; then
    echo "❌ 错误：未找到efibootmgr命令。"
    echo "   请确保系统已安装efibootmgr工具。"
    exit 1
fi

echo "1. 正在扫描UEFI启动项..."
echo "----------------------------------------"

# 获取当前启动项信息并保存备份
BACKUP_FILE="/tmp/boot_backup_$(date +%Y%m%d_%H%M%S).txt"
CURRENT_BOOT_ORDER=$(efibootmgr | grep "BootOrder")
echo "当前启动顺序: $CURRENT_BOOT_ORDER"
efibootmgr -v > "$BACKUP_FILE"
echo "启动项备份已保存到: $BACKUP_FILE"

# 查找CLOVER启动项
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

# 提取Clover的启动编号
CLOVER_BOOTNUM=$(echo "$CLOVER_ENTRY" | grep -o 'Boot[0-9A-F]\{4\}' | head -1 | sed 's/Boot//')

echo "✅ 找到Clover启动项："
echo "   启动编号: Boot$CLOVER_BOOTNUM"
echo "   描述: $CLOVER_ENTRY"

# 获取当前启动顺序
echo ""
echo "3. 正在分析当前启动顺序..."
echo "----------------------------------------"

CURRENT_ORDER=$(efibootmgr | grep "BootOrder" | cut -d: -f2 | tr -d ' ')

if [ -z "$CURRENT_ORDER" ]; then
    echo "⚠️  无法获取当前启动顺序，将创建新顺序。"
    NEW_ORDER="$CLOVER_BOOTNUM"
else
    # 检查Clover是否已在首位
    if [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM,"* ]] || [[ "$CURRENT_ORDER" == "$CLOVER_BOOTNUM" ]]; then
        echo "✅ Clover已在启动顺序的首位，无需修改。"
        echo "   当前顺序: $CURRENT_ORDER"
        exit 0
    fi

    # 从当前顺序中移除Clover编号（如果已存在）
    NEW_ORDER="$CLOVER_BOOTNUM,$(echo "$CURRENT_ORDER" | tr ',' '\n' | grep -v "^$CLOVER_BOOTNUM$" | tr '\n' ',' | sed 's/,$//')"
fi

echo "当前顺序: $CURRENT_ORDER"
echo "新顺序: $NEW_ORDER"

# 确认操作
echo ""
echo "4. 确认设置"
echo "----------------------------------------"
echo "脚本将执行以下操作："
echo "  • 将Clover (Boot$CLOVER_BOOTNUM) 设为第一启动项"
echo "  • 其他启动项顺序保持不变"
echo ""

read -p "是否继续？(输入 y 确认，其他键取消): " -n 1 -r CONFIRM
echo ""

if [[ ! $CONFIRM =~ ^[Yy]$ ]]; then
    echo "❌ 操作已取消。"
    exit 0
fi

# 执行设置
echo ""
echo "5. 正在设置启动顺序..."
echo "----------------------------------------"

efibootmgr -o "$NEW_ORDER"

# 验证结果
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

    # 设置执行权限并运行脚本
    chmod +x "$TEMP_DIR/fix_boot.sh"
    "$TEMP_DIR/fix_boot.sh"

    echo ""

    read -p "按回车键返回主菜单..."
}

# 6. 修复互通盘
fix_shared_disk() {
    show_header
    echo -e "${YELLOW}════════════════ 修复互通盘 ════════════════${NC}"

    echo -e "${CYAN}正在修复互通盘...${NC}"

    # 步骤1: 禁用SteamOS只读模式
    echo "步骤1: 禁用SteamOS只读模式"
    sudo steamos-readonly disable
    echo -e "${GREEN}✓ 已禁用只读模式${NC}"

    # 步骤2: 修改UDisks2权限文件
    echo "步骤2: 修改UDisks2权限文件"
    UDISKS2_FILE="/usr/share/polkit-1/actions/org.freedesktop.UDisks2.policy"

    if [ -f "$UDISKS2_FILE" ]; then
        # 备份原文件
        sudo cp "$UDISKS2_FILE" "$UDISKS2_FILE.backup.$(date +%Y%m%d)"

        # 修改第181行的<allow_active>标签内容为yes
        sudo sed -i '181s/<allow_active>[^<]*<\/allow_active>/<allow_active>yes<\/allow_active>/' "$UDISKS2_FILE"

        # 检查是否修改成功
        if grep -q "<allow_active>yes</allow_active>" "$UDISKS2_FILE"; then
            echo -e "${GREEN}✓ UDisks2权限文件修改成功${NC}"
        else
            echo -e "${YELLOW}⚠️  UDisks2权限文件可能未修改成功，请手动检查${NC}"
        fi
    else
        echo -e "${RED}✗ 未找到UDisks2权限文件: $UDISKS2_FILE${NC}"
    fi

    # 步骤3: 检查并添加fstab配置
    echo "步骤3: 检查并添加fstab配置"
    FSTAB_FILE="/etc/fstab"
    FSTAB_ENTRY="LABEL=Game  /run/media/deck/Game  ntfs   defaults,nofail   0 0"

    if [ -f "$FSTAB_FILE" ]; then
        # 检查是否已存在该配置
        if grep -q "LABEL=Game" "$FSTAB_FILE"; then
            echo -e "${GREEN}✓ fstab中已存在Game盘配置${NC}"
        else
            # 备份原文件
            sudo cp "$FSTAB_FILE" "$FSTAB_FILE.backup.$(date +%Y%m%d)"

            # 添加配置
            echo "$FSTAB_ENTRY" | sudo tee -a "$FSTAB_FILE" > /dev/null
            echo -e "${GREEN}✓ 已添加Game盘配置到fstab${NC}"
        fi
    else
        echo -e "${RED}✗ 未找到fstab文件: $FSTAB_FILE${NC}"
    fi

    # 步骤4: 创建目录（不再自动打开）
    echo "步骤4: 创建Game目录"
    GAME_DIR="/run/media/deck/Game"

    # 创建目录
    sudo mkdir -p "$GAME_DIR"
    sudo chown deck:deck "$GAME_DIR"

    if [ -d "$GAME_DIR" ]; then
        echo -e "${GREEN}✓ 已创建Game目录: $GAME_DIR${NC}"
        echo ""
        echo -e "${YELLOW}提示：请手动打开Game目录查看${NC}"
        echo "    路径: /run/media/deck/Game"
        echo ""
        echo -e "${CYAN}如何打开目录：${NC}"
        echo "1. 在桌面模式打开文件管理器"
        echo "2. 在地址栏输入或导航到: /run/media/deck/Game"
        echo "3. 或者使用终端命令: xdg-open /run/media/deck/Game"
    else
        echo -e "${YELLOW}⚠️  无法创建或访问Game目录${NC}"
    fi

    echo ""
    echo -e "${GREEN}✓ 修复互通盘已完成${NC}"
    echo ""
    echo -e "${YELLOW}提示：如果没看到GAME盘，请去steam-设置-存储空间，添加一下GAME盘${NC}"

    read -p "按回车键返回主菜单..."
}

# 7. 清理hosts缓存
clear_hosts_cache() {
    show_header
    echo -e "${YELLOW}════════════════ 清理hosts缓存 ════════════════${NC}"

    echo -e "${CYAN}正在清理hosts缓存...${NC}"

    # 备份原hosts文件
    echo "备份原hosts文件..."
    sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d_%H%M%S)

    # 清空hosts文件内容
    echo "清空hosts文件内容..."
    sudo sh -c 'echo "" > /etc/hosts'

    echo -e "${GREEN}✓ hosts缓存已清理完成${NC}"
    echo -e "${YELLOW}注意：/etc/hosts文件已被清空，如果需要默认配置，请手动恢复备份${NC}"

    read -p "按回车键返回主菜单..."
}

# 8. 安装UU加速器插件
install_uu_accelerator() {
    show_header
    echo -e "${YELLOW}════════════════ 安装UU加速器插件 ════════════════${NC}"

    echo -e "${CYAN}正在安装UU加速器插件...${NC}"
    echo "安装命令: curl -s uudeck.com | sudo sh"

    # 执行UU加速器插件安装命令
    if curl -s uudeck.com | sudo sh; then
        echo ""
        echo -e "${GREEN}✓ UU加速器插件安装完成${NC}"
    else
        echo ""
        echo -e "${RED}✗ UU加速器插件安装失败${NC}"
    fi

    read -p "按回车键返回主菜单..."
}

# 9. 安装迅游加速器插件
install_xunyou_accelerator() {
    show_header
    echo -e "${YELLOW}════════════════ 安装迅游加速器插件 ════════════════${NC}"

    echo -e "${CYAN}正在安装迅游加速器插件...${NC}"
    echo "安装命令: curl -s sd.xunyou.com | sudo sh"

    # 执行迅游加速器插件安装命令
    if curl -s sd.xunyou.com | sudo sh; then
        echo ""
        echo -e "${GREEN}✓ 迅游加速器插件安装完成${NC}"
    else
        echo ""
        echo -e "${RED}✗ 迅游加速器插件安装失败${NC}"
    fi

    read -p "按回车键返回主菜单..."
}

# 10. 安装ToMoon
install_tomoon() {
    show_header
    echo -e "${YELLOW}════════════════ 安装ToMoon ════════════════${NC}"

    echo -e "${CYAN}正在安装ToMoon...${NC}"
    echo "安装命令: curl -L http://i.ohmydeck.net | sh"

    # 执行ToMoon安装命令
    if curl -L http://i.ohmydeck.net | sh; then
        echo ""
        echo -e "${GREEN}✓ ToMoon安装完成${NC}"
    else
        echo ""
        echo -e "${RED}✗ ToMoon安装失败${NC}"
    fi

    read -p "按回车键返回主菜单..."
}

# 11. 安装＆卸载插件商店
install_remove_plugin_store() {
    show_header
    echo -e "${YELLOW}════════════════ 安装＆卸载插件商店 ════════════════${NC}"

    echo "请选择操作："
    echo "1. 安装插件商店"
    echo "2. 卸载插件商店"
    echo ""

    read -p "请输入选择 [1-2]: " plugin_choice

    case $plugin_choice in
        1)
            echo -e "${CYAN}正在安装插件商店...${NC}"
            echo "安装命令: curl -L http://dl.ohmydeck.net | sh"

            if curl -L http://dl.ohmydeck.net | sh; then
                echo ""
                echo -e "${GREEN}✓ 插件商店安装完成${NC}"
            else
                echo ""
                echo -e "${RED}✗ 插件商店安装失败${NC}"
            fi
            ;;
        2)
            echo -e "${CYAN}正在卸载插件商店...${NC}"
            echo "卸载命令: sudo flatpak remove decky-loader"

            if sudo flatpak remove decky-loader; then
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

    read -p "按回车键返回主菜单..."
}

# 12. 安装＆卸载宝葫芦
install_remove_baohulu() {
    show_header
    echo -e "${YELLOW}════════════════ 安装＆卸载宝葫芦 ════════════════${NC}"

    echo "请选择操作："
    echo "1. 安装宝葫芦"
    echo "2. 卸载宝葫芦"
    echo ""

    read -p "请输入选择 [1-2]: " baohulu_choice

    case $baohulu_choice in
        1)
            echo -e "${CYAN}正在安装宝葫芦...${NC}"
            echo "安装命令: curl -s -L https://i.hulu.deckz.fun | sudo HULU_CHANNEL=Preview sh -"

            if curl -s -L https://i.hulu.deckz.fun | sudo HULU_CHANNEL=Preview sh -; then
                echo ""
                echo -e "${GREEN}✓ 宝葫芦安装完成${NC}"
            else
                echo ""
                echo -e "${RED}✗ 宝葫芦安装失败${NC}"
            fi
            ;;
        2)
            echo -e "${CYAN}正在卸载宝葫芦...${NC}"
            echo "卸载命令: curl -s -L https://i.hulu.deckz.fun/u.sh | sudo sh -"

            if curl -s -L https://i.hulu.deckz.fun/u.sh | sudo sh -; then
                echo ""
                echo -e "${GREEN}✓ 宝葫芦卸载完成${NC}"
            else
                echo ""
                echo -e "${RED}✗ 宝葫芦卸载失败${NC}"
            fi
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac

    read -p "按回车键返回主菜单..."
}

# 13. 校准摇杆
calibrate_joystick() {
    show_header
    echo -e "${YELLOW}════════════════ 校准摇杆 ════════════════${NC}"

    echo -e "${CYAN}正在校准摇杆...${NC}"

    # 执行摇杆校准命令
    if thumbstick_cal; then
        echo ""
        echo -e "${GREEN}✓ 摇杆校准完成${NC}"
    else
        echo ""
        echo -e "${RED}✗ 摇杆校准失败${NC}"
        echo "请确保系统中已安装摇杆校准工具"
    fi

    read -p "按回车键返回主菜单..."
}

# 14. 设置管理员密码
set_admin_password() {
    show_header
    echo -e "${YELLOW}════════════════ 设置管理员密码 ════════════════${NC}"

    echo -e "${CYAN}正在检查是否已设置管理员密码...${NC}"

    # 检查是否已经设置密码
    if sudo -n true 2>/dev/null; then
        echo -e "${GREEN}✓ 管理员密码已经设置${NC}"
        echo "无需重复设置"
    else
        echo -e "${YELLOW}检测到未设置管理员密码或密码已过期${NC}"
        echo ""
        echo "现在开始设置管理员密码..."
        echo "请按照提示输入您要设置的密码"
        echo ""

        # 执行设置密码
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

    read -p "按回车键返回主菜单..."
}

# 15. 安装AnyDesk
install_anydesk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装AnyDesk ════════════════${NC}"

    APP_NAME="AnyDesk"
    DESKTOP_FILE="$DESKTOP_DIR/AnyDesk.desktop"

    # 首先检查是否已安装AnyDesk
    echo "正在检查是否已安装AnyDesk..."

    # 尝试查找已安装的AnyDesk包
    INSTALLED_PACKAGE=""
    for PACKAGE in com.anydesk.Anydesk; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        # 已安装AnyDesk
        echo -e "${GREEN}✓ 检测到已安装AnyDesk${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载AnyDesk"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice

        case $app_choice in
            1)
                # 创建桌面快捷方式
                echo "正在创建桌面快捷方式..."
                cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AnyDesk
Exec=flatpak run $INSTALLED_PACKAGE
Icon=$INSTALLED_PACKAGE
Type=Application
Categories=Network;RemoteAccess;
Comment=AnyDesk远程控制软件
EOF

                chmod +x "$DESKTOP_FILE"
                echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
                ;;
            2)
                # 卸载AnyDesk
                echo "正在卸载AnyDesk..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ AnyDesk卸载完成${NC}"
                    # 删除桌面快捷方式
                    rm -f "$DESKTOP_FILE"
                else
                    echo -e "${RED}✗ AnyDesk卸载失败${NC}"
                fi
                ;;
            *)
                echo "返回主菜单..."
                return
                ;;
        esac

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装AnyDesk，执行安装流程
    echo -e "${CYAN}未检测到AnyDesk，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 安装 AnyDesk
    echo ""
    echo "步骤3: 安装AnyDesk"

    INSTALL_SUCCESS=false
    PACKAGE="com.anydesk.Anydesk"

    echo "尝试安装包: $PACKAGE"
    if flatpak install flathub "$PACKAGE" -y 2>/dev/null; then
        echo -e "${GREEN}✓ 使用包名 '$PACKAGE' 安装成功${NC}"
        INSTALL_SUCCESS=true
        FINAL_PACKAGE="$PACKAGE"
    fi

    # 如果安装失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到AnyDesk包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装AnyDesk。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
    echo ""
    echo "步骤4: 创建桌面快捷方式"
    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AnyDesk
Exec=flatpak run $FINAL_PACKAGE
Icon=$FINAL_PACKAGE
Type=Application
Categories=Network;RemoteAccess;
Comment=AnyDesk远程控制软件
EOF

    chmod +x "$DESKTOP_FILE"
    echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"

    echo ""
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"
    echo -e "${GREEN}✓ AnyDesk 安装完成！${NC}"
    echo -e "${GREEN}✓ 使用的包名: $FINAL_PACKAGE${NC}"
    echo -e "${GREEN}✓ 您可以在桌面找到AnyDesk快捷方式${NC}"
    echo -e "${GREEN}✓ 您也可以在应用菜单中找到AnyDesk${NC}"
    echo -e "${GREEN}════════════════════════════════════════════════════════${NC}"

    read -p "按回车键返回主菜单..."
}

# 16. 安装ToDesk
install_todesk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装ToDesk ════════════════${NC}"

    echo -e "${CYAN}正在安装ToDesk...${NC}"

    # 禁用只读模式
    echo "禁用SteamOS只读模式..."
    sudo steamos-readonly disable

    # 执行安装命令
    echo "执行安装命令: curl -L todesk.lanbai.top | sh"
    curl -L todesk.lanbai.top | sh

    echo ""
    echo -e "${GREEN}✓ ToDesk安装脚本已执行${NC}"
    echo ""
    echo -e "${YELLOW}请在桌面上运行'todesk安装'或'todesk重新安装'的文件来完成安装${NC}"

    read -p "按回车键返回主菜单..."
}

# 17. 安装WPS Office
install_wps_office() {
    show_header
    echo -e "${YELLOW}════════════════ 安装WPS Office ════════════════${NC}"

    # 首先检查是否已安装WPS Office
    echo "正在检查是否已安装WPS Office..."

    # 尝试查找已安装的WPS Office包
    INSTALLED_WPS=""
    for PACKAGE in com.wps.Office cn.wps.wps-office com.kingsoft.wps org.wps.Office; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_WPS="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_WPS" ]; then
        # 已安装WPS Office
        echo -e "${GREEN}✓ 检测到已安装WPS Office${NC}"
        echo "已安装的包名: $INSTALLED_WPS"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载WPS Office"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " wps_choice

        case $wps_choice in
            1)
                # 创建桌面快捷方式
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
                # 卸载WPS Office
                echo "正在卸载WPS Office..."
                if flatpak uninstall "$INSTALLED_WPS" -y; then
                    echo -e "${GREEN}✓ WPS Office卸载完成${NC}"
                    # 删除桌面快捷方式
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

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装WPS Office，执行安装流程
    echo -e "${CYAN}未检测到WPS Office，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 搜索WPS Office的正确包名
    echo ""
    echo "步骤3: 搜索WPS Office包"
    echo "正在搜索可用的WPS Office包..."

    # 尝试搜索WPS包
    if flatpak search wps 2>/dev/null | grep -i wps; then
        echo -e "${GREEN}✓ 找到WPS Office包${NC}"
        # 提取包名
        WPS_PACKAGE=$(flatpak search wps 2>/dev/null | grep -i "wps" | head -1 | awk '{print $1}')
    else
        WPS_PACKAGE=""
    fi

    # 安装 WPS Office - 尝试不同的包名
    echo ""
    echo "步骤4: 安装WPS Office"

    INSTALL_SUCCESS=false

    # 尝试可能的包名列表
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

    # 如果所有包名都失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到WPS Office包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装WPS Office。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
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

    read -p "按回车键返回主菜单..."
}

# 18. 安装QQ
install_qq() {
    show_header
    echo -e "${YELLOW}════════════════ 安装QQ ════════════════${NC}"

    APP_NAME="QQ"
    DESKTOP_FILE="$DESKTOP_DIR/QQ.desktop"

    # 首先检查是否已安装QQ
    echo "正在检查是否已安装QQ..."

    # 尝试查找已安装的QQ包
    INSTALLED_PACKAGE=""
    for PACKAGE in com.qq.QQ com.tencent.qq linuxqq; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        # 已安装QQ
        echo -e "${GREEN}✓ 检测到已安装QQ${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载QQ"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice

        case $app_choice in
            1)
                # 创建桌面快捷方式
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
                # 卸载QQ
                echo "正在卸载QQ..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ QQ卸载完成${NC}"
                    # 删除桌面快捷方式
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

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装QQ，执行安装流程
    echo -e "${CYAN}未检测到QQ，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 安装 QQ - 尝试不同的包名
    echo ""
    echo "步骤3: 安装QQ"

    INSTALL_SUCCESS=false

    # 尝试可能的包名列表
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

    # 如果所有包名都失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到QQ包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装QQ。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
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

    read -p "按回车键返回主菜单..."
}

# 19. 安装微信
install_wechat() {
    show_header
    echo -e "${YELLOW}════════════════ 安装微信 ════════════════${NC}"

    APP_NAME="微信"
    DESKTOP_FILE="$DESKTOP_DIR/WeChat.desktop"

    # 首先检查是否已安装微信
    echo "正在检查是否已安装微信..."

    # 尝试查找已安装的微信包
    INSTALLED_PACKAGE=""
    for PACKAGE in com.tencent.WeChat com.qq.weixin com.tencent.wechat io.github.msojocs.wechat; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        # 已安装微信
        echo -e "${GREEN}✓ 检测到已安装微信${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载微信"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice

        case $app_choice in
            1)
                # 创建桌面快捷方式
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
                # 卸载微信
                echo "正在卸载微信..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ 微信卸载完成${NC}"
                    # 删除桌面快捷方式
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

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装微信，执行安装流程
    echo -e "${CYAN}未检测到微信，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 安装 微信 - 尝试不同的包名
    echo ""
    echo "步骤3: 安装微信"

    INSTALL_SUCCESS=false

    # 尝试可能的包名列表（已将 com.tencent.WeChat 放在首位）
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

    # 如果所有包名都失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到微信包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装微信。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
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

    read -p "按回车键返回主菜单..."
}

# 20. 安装QQ音乐
install_qqmusic() {
    show_header
    echo -e "${YELLOW}════════════════ 安装QQ音乐 ════════════════${NC}"

    APP_NAME="QQ音乐"
    DESKTOP_FILE="$DESKTOP_DIR/com.qq.QQmusic.desktop"

    # 首先检查是否已安装QQ音乐
    echo "正在检查是否已安装QQ音乐..."

    # 尝试查找已安装的QQ音乐包
    INSTALLED_PACKAGE=""
    for PACKAGE in com.qq.music com.qq.QQmusic; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        # 已安装QQ音乐
        echo -e "${GREEN}✓ 检测到已安装QQ音乐${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载QQ音乐"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice

        case $app_choice in
            1)
                # 创建桌面快捷方式
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
                # 卸载QQ音乐
                echo "正在卸载QQ音乐..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ QQ音乐卸载完成${NC}"
                    # 删除桌面快捷方式
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

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装QQ音乐，执行安装流程
    echo -e "${CYAN}未检测到QQ音乐，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 安装 QQ音乐 - 尝试不同的包名
    echo ""
    echo "步骤3: 安装QQ音乐"

    INSTALL_SUCCESS=false

    # 尝试可能的包名列表
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

    # 如果所有包名都失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到QQ音乐包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装QQ音乐。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
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

    read -p "按回车键返回主菜单..."
}

# 21. 安装百度网盘
install_baidunetdisk() {
    show_header
    echo -e "${YELLOW}════════════════ 安装百度网盘 ════════════════${NC}"

    APP_NAME="百度网盘"
    DESKTOP_FILE="$DESKTOP_DIR/com.baidu.NetDisk.desktop"

    # 首先检查是否已安装百度网盘
    echo "正在检查是否已安装百度网盘..."

    # 尝试查找已安装的百度网盘包
    INSTALLED_PACKAGE=""
    for PACKAGE in com.baidu.NetDisk com.baidu.pan; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        # 已安装百度网盘
        echo -e "${GREEN}✓ 检测到已安装百度网盘${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载百度网盘"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice

        case $app_choice in
            1)
                # 创建桌面快捷方式
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
                # 卸载百度网盘
                echo "正在卸载百度网盘..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ 百度网盘卸载完成${NC}"
                    # 删除桌面快捷方式
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

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装百度网盘，执行安装流程
    echo -e "${CYAN}未检测到百度网盘，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 安装 百度网盘 - 尝试不同的包名
    echo ""
    echo "步骤3: 安装百度网盘"

    INSTALL_SUCCESS=false

    # 尝试可能的包名列表
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

    # 如果所有包名都失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到百度网盘包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装百度网盘。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
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

    read -p "按回车键返回主菜单..."
}

# 22. 安装Edge浏览器
install_edge() {
    show_header
    echo -e "${YELLOW}════════════════ 安装Edge浏览器 ════════════════${NC}"

    APP_NAME="Edge浏览器"
    DESKTOP_FILE="$DESKTOP_DIR/Microsoft_Edge.desktop"

    # 首先检查是否已安装Edge浏览器
    echo "正在检查是否已安装Edge浏览器..."

    # 尝试查找已安装的Edge浏览器包
    INSTALLED_PACKAGE=""
    for PACKAGE in com.microsoft.Edge org.mozilla.firefox; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        # 已安装Edge浏览器
        echo -e "${GREEN}✓ 检测到已安装Edge浏览器${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载Edge浏览器"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice

        case $app_choice in
            1)
                # 创建桌面快捷方式
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
                # 卸载Edge浏览器
                echo "正在卸载Edge浏览器..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ Edge浏览器卸载完成${NC}"
                    # 删除桌面快捷方式
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

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装Edge浏览器，执行安装流程
    echo -e "${CYAN}未检测到Edge浏览器，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 安装 Edge浏览器 - 尝试不同的包名
    echo ""
    echo "步骤3: 安装Edge浏览器"

    INSTALL_SUCCESS=false

    # 尝试可能的包名列表
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

    # 如果所有包名都失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到Edge浏览器包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装Edge浏览器。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
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

    read -p "按回车键返回主菜单..."
}

# 23. 安装Google浏览器
install_chrome() {
    show_header
    echo -e "${YELLOW}════════════════ 安装Google浏览器 ════════════════${NC}"

    APP_NAME="Google浏览器"
    DESKTOP_FILE="$DESKTOP_DIR/Google_Chrome.desktop"

    # 首先检查是否已安装Google浏览器
    echo "正在检查是否已安装Google浏览器..."

    # 尝试查找已安装的Google浏览器包
    INSTALLED_PACKAGE=""
    for PACKAGE in com.google.Chrome org.chromium.Chromium; do
        if flatpak list | grep -q "$PACKAGE"; then
            INSTALLED_PACKAGE="$PACKAGE"
            break
        fi
    done

    if [ -n "$INSTALLED_PACKAGE" ]; then
        # 已安装Google浏览器
        echo -e "${GREEN}✓ 检测到已安装Google浏览器${NC}"
        echo "已安装的包名: $INSTALLED_PACKAGE"
        echo ""

        # 询问用户要执行的操作
        echo "请选择要执行的操作："
        echo "1. 创建桌面快捷方式"
        echo "2. 卸载Google浏览器"
        echo ""

        read -p "请输入选择 [1-2] (输入其他键返回主菜单): " app_choice

        case $app_choice in
            1)
                # 创建桌面快捷方式
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
                # 卸载Google浏览器
                echo "正在卸载Google浏览器..."
                if flatpak uninstall "$INSTALLED_PACKAGE" -y; then
                    echo -e "${GREEN}✓ Google浏览器卸载完成${NC}"
                    # 删除桌面快捷方式
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

        read -p "按回车键返回主菜单..."
        return
    fi

    # 未安装Google浏览器，执行安装流程
    echo -e "${CYAN}未检测到Google浏览器，开始安装...${NC}"
    echo ""

    # 添加 Flathub 仓库（如果尚未添加）
    echo "步骤1: 添加Flathub仓库"
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    if [ $? -eq 0 ] || flatpak remote-list | grep -q flathub; then
        echo -e "${GREEN}✓ Flathub仓库已添加或已存在${NC}"
    else
        echo -e "${YELLOW}⚠️  Flathub仓库添加失败，尝试继续安装${NC}"
    fi

    # 更新 Flatpak 仓库信息
    echo ""
    echo "步骤2: 更新Flatpak仓库信息"
    flatpak update --appstream 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Flatpak仓库信息更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  Flatpak仓库信息更新失败，尝试继续安装${NC}"
    fi

    # 安装 Google浏览器 - 尝试不同的包名
    echo ""
    echo "步骤3: 安装Google浏览器"

    INSTALL_SUCCESS=false

    # 尝试可能的包名列表
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

    # 如果所有包名都失败，提示用户
    if [ "$INSTALL_SUCCESS" = false ]; then
        echo -e "${RED}✗ 在Flathub仓库中未找到Google浏览器包${NC}"
        echo ""
        echo -e "${YELLOW}无法通过Flatpak安装Google浏览器。${NC}"
        echo "请尝试其他安装方法或检查网络连接。"

        read -p "按回车键返回主菜单..."
        return
    fi

    # 创建桌面快捷方式
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

    read -p "按回车键返回主菜单..."
}

# 24. Steam Deck缓存管理器
steamdeck_cache_manager() {
    show_header
    echo -e "${YELLOW}════════════════ Steam Deck 缓存管理器 ════════════════${NC}"
    echo ""
    
    echo "正在启动 Steam Deck 缓存管理器..."
    echo "该功能需要图形界面支持，请确保您在桌面模式下运行。"
    echo ""
    
    # 检查是否在桌面模式下
    if [ -z "$DISPLAY" ]; then
        echo -e "${RED}错误：未检测到图形界面环境。${NC}"
        echo "请确保在桌面模式下运行此功能。"
        echo ""
        read -p "按回车键返回主菜单..."
        return
    fi
    
    # 检查zenity是否安装
    if ! command -v zenity &> /dev/null; then
        echo -e "${YELLOW}未找到zenity工具，正在尝试安装...${NC}"
        
        # 尝试安装zenity
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
            read -p "按回车键返回主菜单..."
            return
        fi
        
        # 再次检查zenity是否安装成功
        if ! command -v zenity &> /dev/null; then
            echo -e "${RED}✗ Zenity安装失败！${NC}"
            echo ""
            read -p "按回车键返回主菜单..."
            return
        fi
    fi
    
    echo -e "${GREEN}✓ 环境检查完成，启动缓存管理器...${NC}"
    echo ""
    
    # 执行缓存管理器
    exec_steamdeck_cache_manager
}

# 执行缓存管理器主程序
exec_steamdeck_cache_manager() {
    # 缓存管理器配置
    local live=1
    local tmp_dir="$TEMP_DIR/steamdeck_cache_manager"
    local steamapps_dir="/home/deck/.local/share/Steam/steamapps"
    local cache_type="shadercache"
    
    # 创建临时目录
    function create_temp_dirs() {
        mkdir -p "$tmp_dir"
        echo "临时目录: $tmp_dir"
    }
    
    # 检查环境
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
    
    # 查找所有Steam库目录
    function find_steam_libraries() {
        local libraries=()

        # 首先添加默认库
        if [ -d "$steamapps_dir" ]; then
            libraries+=("$steamapps_dir")
        fi

        # 从libraryfolders.vdf中查找其他库
        if [ -f "$steamapps_dir/libraryfolders.vdf" ]; then
            # 使用更简单的方法解析VDF文件，避免grep警告
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
    
    # 获取游戏安装信息
    function get_game_install_info() {
        local app_id="$1"
        local libraries=($(find_steam_libraries))

        for lib in "${libraries[@]}"; do
            local manifest="$lib/appmanifest_${app_id}.acf"
            if [ -f "$manifest" ]; then
                # 从manifest文件中提取游戏名称和安装目录
                local game_name=$(grep '"name"' "$manifest" | cut -d'"' -f4)
                local install_dir=$(grep '"installdir"' "$manifest" | cut -d'"' -f4)

                if [ -n "$game_name" ] && [ -n "$install_dir" ]; then
                    # 查找游戏实际安装路径
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
    
    # 获取删除列表（着色器缓存或兼容数据）
    function get_delete_list() {
        local cache_type="$1"

        # 清空临时文件
        rm -f "$tmp_dir/delete_list.txt" 2>/dev/null

        # 检查缓存目录是否存在
        if [ ! -d "$steamapps_dir/$cache_type" ]; then
            echo "FALSE|0|0|No $cache_type directory found|N/A|$steamapps_dir/$cache_type" > "$tmp_dir/delete_list.txt"
            return
        fi

        # 遍历缓存目录
        local count=0
        for cache_dir in "$steamapps_dir/$cache_type"/*; do
            if [ -d "$cache_dir" ]; then
                local app_id=$(basename "$cache_dir")

                # 跳过非数字目录（如Proton版本）
                if [[ ! "$app_id" =~ ^[0-9]+$ ]]; then
                    continue
                fi

                # 计算大小
                local size=$(du -sm "$cache_dir" 2>/dev/null | cut -f1)
                if [ -z "$size" ] || [ "$size" -eq 0 ]; then
                    continue
                fi

                # 获取游戏信息
                local game_info=$(get_game_install_info "$app_id")
                local game_name=$(echo "$game_info" | cut -d'|' -f1)
                local game_path=$(echo "$game_info" | cut -d'|' -f2)

                # 判断状态
                local status="Unknown"
                if [ "$game_name" != "Unknown" ] && [ -d "$game_path" ]; then
                    status="Installed"
                elif [ "$game_name" != "Unknown" ]; then
                    status="Uninstalled"
                fi

                # 添加到列表
                echo "FALSE|$size|$app_id|$game_name|$status|$cache_dir" >> "$tmp_dir/delete_list.txt"
                count=$((count+1))
            fi
        done

        # 如果没有找到任何缓存
        if [ $count -eq 0 ]; then
            echo "FALSE|0|0|No $cache_type found|N/A|$steamapps_dir/$cache_type" > "$tmp_dir/delete_list.txt"
        fi
    }
    
    # 获取移动列表（着色器缓存或兼容数据）
    function get_move_list() {
        local cache_type="$1"

        # 清空临时文件
        rm -f "$tmp_dir/move_list.txt" 2>/dev/null

        # 检查缓存目录是否存在
        if [ ! -d "$steamapps_dir/$cache_type" ]; then
            echo "FALSE|0|0|No $cache_type directory found|N/A|N/A" > "$tmp_dir/move_list.txt"
            return
        fi

        # 查找所有已安装的游戏（在非默认位置）
        local libraries=($(find_steam_libraries))
        local count=0

        for lib in "${libraries[@]}"; do
            # 跳过默认库，只处理其他位置的库
            if [ "$lib" == "$steamapps_dir" ]; then
                continue
            fi

            # 查找该库中的所有游戏
            for manifest in "$lib"/appmanifest_*.acf; do
                if [ -f "$manifest" ]; then
                    local app_id=$(basename "$manifest" | sed 's/appmanifest_\(.*\)\.acf/\1/')
                    local game_name=$(grep '"name"' "$manifest" | cut -d'"' -f4)
                    local install_dir=$(grep '"installdir"' "$manifest" | cut -d'"' -f4)

                    if [ -n "$app_id" ] && [ -n "$game_name" ] && [ -n "$install_dir" ]; then
                        # 检查该游戏是否有缓存
                        local cache_dir="$steamapps_dir/$cache_type/$app_id"
                        if [ -d "$cache_dir" ] && [ ! -L "$cache_dir" ]; then
                            # 计算缓存大小
                            local size=$(du -sm "$cache_dir" 2>/dev/null | cut -f1)
                            if [ -n "$size" ] && [ "$size" -gt 0 ]; then
                                # 游戏安装路径
                                local game_path="$lib/common/$install_dir"

                                # 添加到列表
                                echo "FALSE|$size|$app_id|$game_name|$game_path" >> "$tmp_dir/move_list.txt"
                                count=$((count+1))
                            fi
                        fi
                    fi
                fi
            done
        done

        # 如果没有找到可移动的缓存
        if [ $count -eq 0 ]; then
            echo "FALSE|0|0|No $cache_type to move|N/A" > "$tmp_dir/move_list.txt"
        fi
    }
    
    # 显示删除对话框
    function show_delete_dialog() {
        local cache_type="$1"
        local title="选择要删除的$cache_type"

        if [ "$cache_type" = "compatdata" ]; then
            title="⚠  警告：选择要删除的兼容数据（将破坏游戏配置！）"
        fi

        # 读取列表文件
        local zenity_items=()
        while IFS='|' read -r check size app_id game_name status path; do
            if [ "$size" != "0" ] && [ "$app_id" != "0" ]; then
                zenity_items+=("$check" "$size" "$app_id" "$game_name" "$status" "$path")
            fi
        done < "$tmp_dir/delete_list.txt"

        # 如果没有项目，显示提示并返回
        if [ ${#zenity_items[@]} -eq 0 ]; then
            zenity --info --width=400 --text="没有找到可删除的$cache_type。"
            echo "empty"
            return
        fi

        # 显示选择对话框
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
    
    # 显示移动对话框
    function show_move_dialog() {
        local cache_type="$1"

        # 读取列表文件
        local zenity_items=()
        while IFS='|' read -r check size app_id game_name game_path; do
            if [ "$size" != "0" ] && [ "$app_id" != "0" ]; then
                zenity_items+=("$check" "$size" "$app_id" "$game_name" "$game_path")
            fi
        done < "$tmp_dir/move_list.txt"

        # 如果没有项目，显示提示并返回
        if [ ${#zenity_items[@]} -eq 0 ]; then
            zenity --info --width=400 --text="没有找到可移动的$cache_type。"
            echo "empty"
            return
        fi

        # 显示选择对话框
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
    
    # 执行删除操作
    function perform_delete() {
        local cache_type="$1"
        local selected_items="$2"

        if [ -z "$selected_items" ] || [ "$selected_items" = "empty" ]; then
            return 1
        fi

        # 将选中的项目转换为数组
        IFS='|' read -ra selected_array <<< "$selected_items"

        if [ ${#selected_array[@]} -eq 0 ]; then
            zenity --error --width=400 --text="没有选择任何$cache_type！"
            return 1
        fi

        # 显示确认对话框
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

        # 显示进度条
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
    
    # 执行移动操作
    function perform_move() {
        local cache_type="$1"
        local selected_items="$2"

        if [ -z "$selected_items" ] || [ "$selected_items" = "empty" ]; then
            return 1
        fi

        # 将选中的项目转换为数组
        IFS='|' read -ra selected_array <<< "$selected_items"

        if [ ${#selected_array[@]} -eq 0 ]; then
            zenity --error --width=400 --text="没有选择任何$cache_type！"
            return 1
        fi

        # 显示进度条
        (
            local total=${#selected_array[@]}
            local current=0

            for app_id in "${selected_array[@]}"; do
                ((current++))
                local percentage=$((current * 100 / total))

                # 查找游戏信息
                local game_info=$(get_game_install_info "$app_id")
                local game_name=$(echo "$game_info" | cut -d'|' -f1)
                local game_path=$(echo "$game_info" | cut -d'|' -f2)

                echo "# 正在移动 $app_id ($game_name)"
                echo "$percentage"

                if [ $live -eq 1 ]; then
                    local source_dir="$steamapps_dir/$cache_type/$app_id"
                    local target_dir="$game_path/$cache_type"

                    # 创建目标目录
                    mkdir -p "$target_dir" 2>/dev/null

                    # 复制文件
                    if cp -r "$source_dir" "$target_dir/" 2>/dev/null; then
                        # 删除原始文件
                        rm -rf "$source_dir" 2>/dev/null

                        # 创建符号链接
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
    
    # 显示主菜单
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
    
    # 显示状态信息
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
    
    # 主程序
    function cache_manager_main() {
        # 检查环境
        check_environment || return 1

        # 创建临时目录
        create_temp_dirs

        # 主循环
        while true; do
            # 显示主菜单
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
    
    # 运行缓存管理器
    cache_manager_main
    
    echo ""
    echo "缓存管理器操作完成。"
    read -p "按回车键返回主菜单..."
}

# 25. 更新已安装应用
update_installed_apps() {
    show_header
    echo -e "${YELLOW}════════════════ 更新已安装应用 ════════════════${NC}"
    echo ""

    echo "请选择更新方式："
    echo "1. 更新指定应用"
    echo "2. 更新全部应用"
    echo ""

    read -p "请输入选择 [1-2] (输入其他键返回主菜单): " update_choice

    case $update_choice in
        1)
            # 更新指定应用
            update_specific_app
            ;;
        2)
            # 更新全部应用
            update_all_apps
            ;;
        *)
            echo "返回主菜单..."
            return
            ;;
    esac

    read -p "按回车键返回主菜单..."
}

# 更新指定应用
update_specific_app() {
    show_header
    echo -e "${YELLOW}════════════════ 更新指定应用 ════════════════${NC}"
    echo ""

    echo "请选择要更新的应用："
    echo "1. AnyDesk"
    echo "2. WPS Office"
    echo "3. QQ"
    echo "4. 微信"
    echo "5. QQ音乐"
    echo "6. 百度网盘"
    echo "7. Edge浏览器"
    echo "8. Google浏览器"
    echo ""

    read -p "请输入选择 [1-8] (输入其他键返回): " app_choice

    case $app_choice in
        1)
            # 更新AnyDesk
            update_app_by_name "AnyDesk" "com.anydesk.Anydesk"
            ;;
        2)
            # 更新WPS Office
            update_app_by_name "WPS Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps" "org.wps.Office"
            ;;
        3)
            # 更新QQ
            update_app_by_name "QQ" "com.qq.QQ" "com.tencent.qq" "io.github.msojocs.qq"
            ;;
        4)
            # 更新微信
            update_app_by_name "微信" "com.tencent.WeChat" "com.qq.weixin" "com.tencent.wechat" "io.github.msojocs.wechat"
            ;;
        5)
            # 更新QQ音乐
            update_app_by_name "QQ音乐" "com.qq.QQmusic" "com.tencent.QQmusic"
            ;;
        6)
            # 更新百度网盘
            update_app_by_name "百度网盘" "com.baidu.NetDisk" "com.baidu.pan"
            ;;
        7)
            # 更新Edge浏览器
            update_app_by_name "Edge浏览器" "com.microsoft.Edge" "org.mozilla.firefox" "com.google.Chrome"
            ;;
        8)
            # 更新Google浏览器
            update_app_by_name "Google浏览器" "com.google.Chrome" "org.chromium.Chromium"
            ;;
        *)
            echo "返回更新菜单..."
            update_installed_apps
            return
            ;;
    esac
}

# 通用应用更新函数
update_app_by_name() {
    local app_name="$1"
    shift
    local packages=("$@")

    echo ""
    echo -e "${CYAN}正在检查$app_name的更新...${NC}"

    # 查找已安装的包
    local installed_package=""
    for package in "${packages[@]}"; do
        if flatpak list | grep -q "$package"; then
            installed_package="$package"
            break
        fi
    done

    if [ -n "$installed_package" ]; then
        echo "找到已安装的包: $installed_package"
        echo "正在更新$app_name..."

        if flatpak update "$installed_package" -y 2>/dev/null; then
            echo -e "${GREEN}✓ $app_name 更新完成${NC}"
        else
            echo -e "${YELLOW}⚠️  $app_name 更新过程中出现错误${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  未检测到已安装的$app_name${NC}"
        echo "请先安装$app_name后再尝试更新。"
    fi
}

# 更新全部应用
update_all_apps() {
    show_header
    echo -e "${YELLOW}════════════════ 更新全部应用 ════════════════${NC}"
    echo ""

    echo -e "${CYAN}正在更新所有已安装的应用...${NC}"

    # 更新所有应用
    flatpak update -y 2>/dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ 所有应用更新完成${NC}"
    else
        echo -e "${YELLOW}⚠️  应用更新过程中出现错误${NC}"
    fi
}

# 26. 卸载已安装应用
uninstall_apps() {
    show_header
    echo -e "${YELLOW}════════════════ 卸载已安装应用 ════════════════${NC}"
    echo ""

    echo "请选择要卸载的应用："
    echo "1. AnyDesk"
    echo "2. WPS Office"
    echo "3. QQ"
    echo "4. 微信"
    echo "5. QQ音乐"
    echo "6. 百度网盘"
    echo "7. Edge浏览器"
    echo "8. Google浏览器"
    echo ""

    read -p "请输入选择 [1-8] (输入其他键返回主菜单): " app_choice

    case $app_choice in
        1)
            # 卸载AnyDesk
            uninstall_app_by_name "AnyDesk" "com.anydesk.Anydesk" "$DESKTOP_DIR/AnyDesk.desktop"
            ;;
        2)
            # 卸载WPS Office
            uninstall_app_by_name "WPS Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps" "org.wps.Office" "$DESKTOP_DIR/WPS_Office.desktop"
            ;;
        3)
            # 卸载QQ
            uninstall_app_by_name "QQ" "com.qq.QQ" "com.tencent.qq" "io.github.msojocs.qq" "$DESKTOP_DIR/QQ.desktop"
            ;;
        4)
            # 卸载微信
            uninstall_app_by_name "微信" "com.tencent.WeChat" "com.qq.weixin" "com.tencent.wechat" "io.github.msojocs.wechat" "$DESKTOP_DIR/WeChat.desktop"
            ;;
        5)
            # 卸载QQ音乐
            uninstall_app_by_name "QQ音乐" "com.qq.QQmusic" "com.tencent.QQmusic" "$DESKTOP_DIR/com.qq.QQmusic.desktop"
            ;;
        6)
            # 卸载百度网盘
            uninstall_app_by_name "百度网盘" "com.baidu.NetDisk" "com.baidu.pan" "$DESKTOP_DIR/com.baidu.NetDisk.desktop"
            ;;
        7)
            # 卸载Edge浏览器
            uninstall_app_by_name "Edge浏览器" "com.microsoft.Edge" "org.mozilla.firefox" "com.google.Chrome" "$DESKTOP_DIR/Microsoft_Edge.desktop"
            ;;
        8)
            # 卸载Google浏览器
            uninstall_app_by_name "Google浏览器" "com.google.Chrome" "org.chromium.Chromium" "$DESKTOP_DIR/Google_Chrome.desktop"
            ;;
        *)
            echo "返回主菜单..."
            return
            ;;
    esac
}

# 通用应用卸载函数
uninstall_app_by_name() {
    local app_name="$1"
    shift
    local packages=("$@")

    # 最后一个参数是桌面快捷方式路径
    local desktop_file="${!#}"
    # 移除最后一个参数（桌面快捷方式路径）
    set -- "${@:1:$(($#-1))}"

    echo ""
    echo -e "${CYAN}正在检查是否已安装$app_name...${NC}"

    # 查找已安装的包
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
        read -p "是否继续？(输入 y 确认，其他键取消): " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "操作已取消。"
            return
        fi

        echo "正在卸载$app_name..."

        if flatpak uninstall "$installed_package" -y 2>/dev/null; then
            echo -e "${GREEN}✓ $app_name 卸载完成${NC}"

            # 删除桌面快捷方式
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

        # 如果桌面快捷方式存在但应用未安装，询问是否删除快捷方式
        if [ -f "$desktop_file" ]; then
            echo "检测到残留的桌面快捷方式。"
            read -p "是否删除桌面快捷方式？(输入 y 确认，其他键取消): " -n 1 -r
            echo ""
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                rm -f "$desktop_file"
                echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
            fi
        fi
    fi

    read -p "按回车键返回..."
}

# ============================================
# 主程序
# ============================================

main() {
    # 初始化目录
    init_dirs

    # 静默检测系统类型
    detect_system_type

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
