#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version('Gtk', '3.0')
try:
    gi.require_version('Vte', '2.91')
    from gi.repository import Vte
    VTE_AVAILABLE = True
except (ValueError, ImportError):
    VTE_AVAILABLE = False

from gi.repository import Gtk, GLib, GdkPixbuf
import subprocess
import os
import sys
import re
import tempfile
import shutil
import threading
import urllib.request
import atexit

# ============================================================================
# 版本定义
# ============================================================================
VERSION = "1.6.3"
REPO_RAW_URL = "https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_gui.py"
REPO_URL = "https://gitee.com/Zhucy2100/steamdeck_toolbox"
VERSION_CHECK_TIMEOUT = 10

# ============================================================================
# 内嵌完整的 Bash 脚本
# ============================================================================
BASH_SCRIPT = r'''#!/bin/bash
TEMP_DIR="/tmp/steamdeck_toolbox"
cleanup_temp() {
    rm -rf "$TEMP_DIR" 2>/dev/null
}
trap 'cleanup_temp; exit 0' EXIT
trap 'echo -e "\n${YELLOW}用户取消操作，关闭窗口。${NC}"; cleanup_temp; exit 0' INT TERM

PYTHON_CMD="python3"
command -v python3 &>/dev/null || PYTHON_CMD="python"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
PURPLE='\033[0;35m'
NC='\033[0m'

mk_temp_dir() {
    mkdir -p "$TEMP_DIR"
}

safe_lsblk() {
    local pycmd="python3"
    command -v python3 &>/dev/null || pycmd="python"
    lsblk -J -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID,PARTTYPE,SIZE | $pycmd << 'PYEOF'
import sys, json
data = json.load(sys.stdin)
for dev in data.get('blockdevices', []):
    def process(d, parent_name=''):
        name = parent_name + d['name']
        if d.get('type') == 'part':
            print('{}|{}|{}|{}|{}|{}|{}'.format(
                name,
                d.get('label', ''),
                d.get('fstype', ''),
                d.get('mountpoint', ''),
                d.get('uuid', ''),
                d.get('parttype', ''),
                d.get('size', '')
            ))
        if 'children' in d:
            for child in d['children']:
                process(child, name + '/')
    process(dev)
PYEOF
}

install_flatpak_app() {
    local app_title="$1"; shift
    local desktop_name="$1"; shift
    local desktop_categories="$1"; shift
    local app_ids=("$@")
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装 ${app_title} ════════════════${NC}"

    local already_installed=""
    for app_id in "${app_ids[@]}"; do
        if flatpak info "$app_id" &>/dev/null; then
            already_installed="$app_id"
            break
        fi
    done
    if [ -n "$already_installed" ]; then
        echo -e "${GREEN}✓ ${app_title} 已安装 (${already_installed})，无需重复安装。${NC}"
        return 0
    fi

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo 2>/dev/null

    local available_id=""
    for app_id in "${app_ids[@]}"; do
        echo "正在查询 ${app_id} ..."
        if timeout 10 flatpak remote-info flathub "$app_id" &>/dev/null; then
            available_id="$app_id"
            break
        else
            echo -e "${YELLOW}${app_id} 不存在或查询超时，尝试下一个...${NC}"
        fi
    done

    if [ -z "$available_id" ]; then
        echo -e "${RED}✗ 未找到可安装的 ${app_title} 包。${NC}"
        return 1
    fi

    echo "正在安装 ${available_id} ..."
    if flatpak install flathub "$available_id" -y 2>/dev/null; then
        echo -e "${GREEN}✓ ${app_title} 安装成功${NC}"
        cat > "$HOME/Desktop/${desktop_name}.desktop" << EOF
[Desktop Entry]
Type=Application
Name=${desktop_name}
Exec=flatpak run ${available_id}
Icon=${available_id}
Terminal=false
Categories=${desktop_categories};
EOF
        chmod +x "$HOME/Desktop/${desktop_name}.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ 安装失败，请检查网络或手动安装。${NC}"
    fi
}

uninstall_flatpak_app() {
    local app_title="$1"; shift
    local desktop_name="$1"; shift
    local app_ids=("$@")
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 ${app_title} ════════════════${NC}"
    local installed=""
    for pkg in "${app_ids[@]}"; do
        if flatpak info "$pkg" &>/dev/null; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
        echo
        if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
            echo "继续卸载..."
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ ${app_title} 卸载完成${NC}"

                local desktop_dir="$HOME/Desktop"
                if [ -d "$desktop_dir" ]; then
                    local deleted_any=false
                    for f in "$desktop_dir"/*.desktop; do
                        local base=$(basename "$f")
                        if [ "$base" = "${desktop_name}.desktop" ] || \
                           [ "$base" = "${installed}.desktop" ] || \
                           [[ "$base" == *"${installed//./_}"* ]]; then
                            rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ 桌面快捷方式已删除: $base${NC}" && deleted_any=true
                        fi
                    done
                    if ! $deleted_any; then
                        echo -e "${YELLOW}未找到与 ${desktop_name} 或 ${installed} 匹配的桌面快捷方式。${NC}"
                    fi
                fi

                local data_dir="$HOME/.var/app/$installed"
                if [ -d "$data_dir" ]; then
                    echo ""
                    echo -e "${CYAN}是否删除该应用的所有设置和用户数据？${NC}"
                    read -n1 -p "按回车键或 A 键确认删除，其他键保留: " del_data
                    echo
                    if [[ -z "$del_data" || "$del_data" =~ [Aa] ]]; then
                        rm -rf "$data_dir" && echo -e "${GREEN}✓ 用户数据已删除${NC}"
                    else
                        echo -e "${YELLOW}已保留用户数据。${NC}"
                    fi
                else
                    echo -e "${GREEN}未发现用户数据目录，无需清理。${NC}"
                fi

                echo ""
                echo -e "${GREEN}${app_title} 卸载流程结束。${NC}"
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 ${app_title}。${NC}"
    fi
}

install_chinese_source() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装国内源 ════════════════${NC}"
    echo "正在配置国内源..."
    echo ""
    echo -e "${CYAN}步骤1: 禁用SteamOS只读模式${NC}"
    if sudo steamos-readonly disable 2>/dev/null; then
        echo -e "${GREEN}✓ 已禁用只读模式${NC}"
    else
        local exit_code=$?
        echo -e "${RED}✗ 禁用只读模式失败 (退出码: ${exit_code})${NC}"
        echo -e "${YELLOW}可能原因：密码错误、用户取消操作或无需此操作。${NC}"
        echo -e "${YELLOW}已跳过国内源配置。${NC}"
        return 1
    fi
    echo ""
    echo -e "${CYAN}步骤2: 配置Flatpak国内源${NC}"
    if flatpak remote-modify flathub --url=https://mirror.sjtu.edu.cn/flathub 2>/dev/null; then
        echo -e "${GREEN}✓ Flatpak国内源配置完成${NC}"
    else
        echo -e "${RED}✗ Flatpak国内源配置失败${NC}"
        echo -e "${YELLOW}可能原因：密码错误、用户取消操作或 flatpak 未正常运行。${NC}"
        return 1
    fi
    echo ""
    echo -e "${YELLOW}重启后生效${NC}"
}

adjust_swap() {
    mk_temp_dir
    while true; do
        clear
        echo -e "${YELLOW}════════════════ 调整虚拟内存大小 ════════════════${NC}"
        echo ""
        echo -e "${CYAN}当前系统状态${NC}"
        echo "--------------------------------------------"
        if command -v free &> /dev/null; then
            mem_line=$(LANG=C free -h | grep '^Mem:')
            swap_line=$(LANG=C free -h | grep '^Swap:')
            if [ -n "$mem_line" ]; then
                mem_total=$(echo "$mem_line" | awk '{print $2}')
                mem_used=$(echo "$mem_line" | awk '{print $3}')
                echo -e "物理内存: ${GREEN}${mem_total}${NC} | 已用: ${YELLOW}${mem_used}${NC}"
            fi
            if [ -n "$swap_line" ]; then
                swap_total=$(echo "$swap_line" | awk '{print $2}')
                swap_used=$(echo "$swap_line" | awk '{print $3}')
                echo -e "交换空间: ${GREEN}${swap_total}${NC} | 已用: ${YELLOW}${swap_used}${NC}"
            fi
        fi
        echo ""
        echo -e "${CYAN}请选择要执行的操作${NC}"
        echo "============================================"
        echo -e "${GREEN}[1] 一键应用CryoByte33推荐方案${NC}"
        echo -e "${GREEN}[2] 调整传统Swap文件大小${NC}"
        echo -e "${GREEN}[3] 配置ZRAM (内存压缩交换)${NC}"
        echo -e "${GREEN}[4] 清理所有虚拟内存配置并重新开始${NC}"
        echo "============================================"
        echo ""
        read -p "请输入选项 [1-4]: " main_choice < /dev/tty
        case $main_choice in
            1) apply_cryo_recommendation
               echo ""
               read -p "按回车键返回主菜单..." < /dev/tty
               continue ;;
            2) adjust_swapfile
               echo ""
               read -p "按回车键返回主菜单..." < /dev/tty
               continue ;;
            3) configure_zram
               echo ""
               read -p "按回车键返回主菜单..." < /dev/tty
               continue ;;
            4) cleanup_swap
               echo ""
               read -p "按回车键返回主菜单..." < /dev/tty
               continue ;;
            *) echo -e "${RED}无效选择，请重新输入。${NC}"
               sleep 1
               ;;
        esac
    done
}

apply_cryo_recommendation() {
    mk_temp_dir
    echo ""
    echo -e "${YELLOW}═══════════════ 应用CryoByte33推荐方案 ═══════════════${NC}"
    echo ""
    read -n1 -p "按回车键或 A 键确认，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续执行..."
    else
        echo "取消操作。"
        return
    fi
    local swap_size_gb=16
    local block_count=$((swap_size_gb * 1024))
    echo "• 停用现有交换文件..."
    sudo swapoff /home/swapfile 2>/dev/null
    sudo swapoff -a 2>/dev/null
    sudo rm -f /home/swapfile
    echo "• 创建新文件..."
    sudo touch /home/swapfile
    sudo chattr +C /home/swapfile 2>/dev/null || true
    sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$block_count conv=fsync status=progress 2>/dev/null
    sudo chmod 600 /home/swapfile
    sudo mkswap /home/swapfile
    sudo swapon /home/swapfile
    sudo sed -i '\\|/home/swapfile|d' /etc/fstab 2>/dev/null
    echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null
    echo -e "${GREEN}✓ 16GB交换文件创建完成${NC}"
    sudo tee /etc/sysctl.d/99-cryo-optimizations.conf > /dev/null <<'EOF'
vm.swappiness=1
vm.vfs_cache_pressure=50
vm.page-cluster=0
vm.dirty_background_ratio=3
vm.dirty_ratio=50
EOF
    sudo sysctl --system --load=/etc/sysctl.d/99-cryo-optimizations.conf >/dev/null 2>&1
    echo -e "${GREEN}✓ 内核参数优化完成${NC}"
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    echo -e "${GREEN}✓ ZRAM已停用${NC}"
    echo -e "${GREEN}✅ CryoByte33推荐方案已成功应用！${NC}"
}

adjust_swapfile() {
    mk_temp_dir
    while true; do
        clear
        echo ""
        echo -e "${YELLOW}调整传统Swap文件大小${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        if [ -f "/home/swapfile" ]; then
            current_size=$(sudo du -h /home/swapfile 2>/dev/null | cut -f1)
            echo -e "现有文件大小: ${GREEN}$current_size${NC}"
        else
            echo -e "现有文件: ${YELLOW}未找到${NC}"
        fi
        echo ""
        df -h / | tail -1
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "选择新的大小:"
        echo " 1.  1GB (轻度使用)"
        echo " 2.  4GB (基础游戏)"
        echo " 3.  8GB (推荐，平衡型)"
        echo " 4. 16GB (大型游戏/多任务)"
        echo " 5. 32GB (虚拟机/专业用途)"
        echo " 6. 自定义大小"

        local swap_size_gb=""
        read -p "请选择 [1-6]: " size_choice < /dev/tty
        case $size_choice in
            1) swap_size_gb=1 ;;
            2) swap_size_gb=4 ;;
            3) swap_size_gb=8 ;;
            4) swap_size_gb=16 ;;
            5) swap_size_gb=32 ;;
            6) read -p "请输入大小 (单位GB，数字): " custom_size < /dev/tty
                if [[ "$custom_size" =~ ^[0-9]+$ ]]; then
                    swap_size_gb=$custom_size
                else
                    echo -e "${RED}无效数字，请重新选择。${NC}"
                    sleep 1
                    continue
                fi
                ;;
            *) echo -e "${RED}无效选项，请重新选择。${NC}"
               sleep 1
               continue
               ;;
        esac

        break
    done

    echo "正在创建 ${swap_size_gb}GB 交换文件..."
    sudo swapoff /home/swapfile 2>/dev/null
    sudo rm -f /home/swapfile
    sudo touch /home/swapfile
if mount | grep " /home " | grep -q btrfs; then
    sudo chattr +C /home/swapfile 2>/dev/null || echo -e "${YELLOW}⚠  chattr +C 失败，继续${NC}"
fi
    block_count=$((swap_size_gb * 1024))
    sudo dd if=/dev/zero of=/home/swapfile bs=1M count=$block_count status=progress conv=fsync 2>/dev/null
    sudo chmod 600 /home/swapfile
    sudo mkswap /home/swapfile
    sudo swapon /home/swapfile
    if ! grep -q "/home/swapfile" /etc/fstab 2>/dev/null; then
        echo "/home/swapfile none swap defaults 0 0" | sudo tee -a /etc/fstab > /dev/null
    fi
    echo -e "${GREEN}✅ Swap文件创建成功${NC}"
}

configure_zram() {
    mk_temp_dir
    while true; do
        clear
        echo ""
        echo -e "${YELLOW}配置ZRAM (内存压缩交换)${NC}"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "选择ZRAM大小 (基于16GB物理内存):"
        echo " 1. 2GB (保守)"
        echo " 2. 4GB (平衡推荐)"
        echo " 3. 8GB (积极)"

        local zram_size_gb=""
        read -p "请选择 [1-3]: " zram_choice < /dev/tty
        case $zram_choice in
            1) zram_size_gb=2 ;;
            2) zram_size_gb=4 ;;
            3) zram_size_gb=8 ;;
            *) echo -e "${RED}无效选项，请重新选择。${NC}"
               sleep 1
               continue
               ;;
        esac

        break
    done

    echo "正在加载 ZRAM 内核模块..."
    sudo modprobe zram

    echo "正在清理旧的 ZRAM 配置..."
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl daemon-reload 2>/dev/null

    if swapon --show | grep -q /dev/zram0; then
        sudo swapoff /dev/zram0 2>/dev/null
    fi
    sudo zramctl /dev/zram0 --reset 2>/dev/null

    echo "正在创建 ${zram_size_gb}GB ZRAM 设备..."
    sudo zramctl /dev/zram0 --size ${zram_size_gb}G --algorithm lz4 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "尝试动态创建 ZRAM 设备..."
        local zram_dev=$(sudo zramctl --find --size ${zram_size_gb}G --algorithm lz4)
        if [ -n "$zram_dev" ]; then
            echo "ZRAM 设备创建成功: $zram_dev"
            sudo mkswap $zram_dev
            sudo swapon $zram_dev -p 100
            if swapon --show | grep -q "$zram_dev"; then
                local actual_size=$(swapon --show | grep "$zram_dev" | awk '{print $3}')
                echo -e "${GREEN}✅ ZRAM 已成功启用！设备: $zram_dev, 大小: ${actual_size}${NC}"
            else
                echo -e "${RED}❌ ZRAM 启用失败。${NC}"
            fi
            sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null
            echo "完成。"
            return 0
        else
            echo -e "${RED}❌ 无法创建 ZRAM 设备。${NC}"
            return 1
        fi
    else
        sudo mkswap /dev/zram0
        sudo swapon /dev/zram0 -p 100
        if swapon --show | grep -q /dev/zram0; then
            local actual_size=$(swapon --show | grep /dev/zram0 | awk '{print $3}')
            echo -e "${GREEN}✅ ZRAM 已成功启用！大小: ${actual_size}${NC}"
        else
            echo -e "${RED}❌ ZRAM 启用失败。${NC}"
        fi
        sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null
        echo "完成。"
        return 0
    fi
}

cleanup_swap() {
    mk_temp_dir
    echo ""
    echo -e "${YELLOW}清理所有虚拟内存配置${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    read -n1 -p "按回车键或 A 键确认，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续执行..."
    else
        echo "操作已取消。"
        return
    fi

    echo "正在关闭所有交换设备..."
    sudo swapoff -a 2>/dev/null

    if [ -b /dev/zram0 ]; then
        echo "正在重置 ZRAM 设备..."
        sudo zramctl /dev/zram0 --reset 2>/dev/null || echo -e "${YELLOW}⚠️  ZRAM 重置失败，可能未加载 zram 模块。${NC}"
    fi

    echo "正在删除交换文件..."
    sudo rm -f /home/swapfile 2>/dev/null

    echo "正在清理 fstab 配置..."
    sudo sed -i '/\/home\/swapfile/d' /etc/fstab 2>/dev/null

    echo "正在清理 systemd zram 服务..."
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null
    sudo systemctl daemon-reload

    echo -e "${GREEN}✅ 所有虚拟内存配置已清理完成。${NC}"
}

fix_single_ntfs() {
    local device="$1"
    local mountpoint="$2"

    echo ""
    echo -e "${CYAN}正在修复分区: $device${NC}"

    if [ -n "$mountpoint" ]; then
        echo "  正在卸载 $mountpoint ..."
        sudo umount "$device" 2>/dev/null || sudo umount -f "$device" 2>/dev/null
    fi

    echo "  执行 ntfsfix ..."
    if sudo ntfsfix "$device" 2>/dev/null; then
        echo -e "${GREEN}  ✓ 修复成功${NC}"
    else
        echo -e "${RED}  ✗ 修复失败，请检查 dmesg 输出。${NC}"
    fi

    if [ -n "$mountpoint" ] && [ -d "$mountpoint" ]; then
        echo "  尝试重新挂载到 $mountpoint ..."
        if sudo mount "$device" "$mountpoint" 2>/dev/null; then
            echo -e "${GREEN}  ✓ 重新挂载成功${NC}"
        else
            echo -e "${YELLOW}  ⚠️  自动挂载失败，请手动挂载。${NC}"
        fi
    fi
}

fix_disk_write_error() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 修复磁盘写入错误 ════════════════${NC}"
    echo -e "${CYAN}正在扫描 NTFS 分区并检查是否存在错误...${NC}"

    echo ""
    echo -e "${CYAN}请输入您的 sudo 密码以继续操作（输入时不会显示）${NC}"
    if ! sudo -v 2>/dev/null; then
        echo -e "${RED}密码验证失败或已取消，操作终止。${NC}"
        return 1
    fi
    echo -e "${GREEN}密码已验证，继续执行。${NC}"

    if ! command -v ntfsfix &> /dev/null; then
        echo -e "${RED}错误: 未安装 ntfsfix 工具。${NC}"
        echo "请安装 ntfs-3g 包："
        echo "  sudo pacman -S ntfs-3g   (Arch/SteamOS)"
        echo "  sudo apt install ntfs-3g (Debian/Ubuntu)"
        return 1
    fi

    if command -v steamos-readonly &> /dev/null; then
        echo ""
        echo "步骤1: 检查并禁用 SteamOS 只读模式"
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            sudo steamos-readonly disable 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✓ 已禁用只读模式${NC}"
            else
                echo -e "${YELLOW}⚠️  禁用只读模式失败，尝试继续...${NC}"
            fi
        else
            echo -e "${GREEN}✓ 系统已处于读写模式${NC}"
        fi
    else
        echo ""
        echo "步骤1: 跳过 SteamOS 只读模式（当前系统非 SteamOS）"
    fi

    echo ""
    echo "步骤2: 扫描 NTFS 分区..."
    local ntfs_devices=()
    local ntfs_labels=()
    local ntfs_mountpoints=()
    local ntfs_uuids=()
    local ntfs_count=0

    # 方法1: 使用 blkid 直接获取所有 NTFS 分区（推荐，稳定且无需 JSON）
    while IFS= read -r line; do
        # 提取设备路径 (第一个冒号前)
        dev=$(echo "$line" | cut -d: -f1)
        # 提取文件系统类型 (TYPE="xxx")
        fstype=$(echo "$line" | grep -oP 'TYPE="\K[^"]+' | head -1)
        # 提取卷标 (LABEL="xxx")
        label=$(echo "$line" | grep -oP 'LABEL="\K[^"]+' | head -1)
        # 提取 UUID
        uuid=$(echo "$line" | grep -oP 'UUID="\K[^"]+' | head -1)

        # 只处理 NTFS 或 fuseblk
        if [[ "$fstype" == "ntfs" || "$fstype" == "fuseblk" ]]; then
            ntfs_devices+=("$dev")
            ntfs_labels+=("${label:-无标签}")
            ntfs_uuids+=("${uuid:-}")
            # 获取当前挂载点（如果已挂载）
            mountpoint=$(findmnt -n -o TARGET "$dev" 2>/dev/null || echo "")
            ntfs_mountpoints+=("$mountpoint")
            ((ntfs_count++))
        fi
    done < <(sudo blkid 2>/dev/null)

    # 如果 blkid 没有找到，尝试使用 lsblk（但这次用非 JSON 模式，纯文本）
    if [ $ntfs_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  blkid 未找到 NTFS 分区，尝试使用 lsblk 文本模式...${NC}"
        # 使用 lsblk -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID,SIZE 输出，不依赖 JSON
        while read -r name type label fstype mountpoint uuid size; do
            # 跳过表头
            [[ "$name" == "NAME" ]] && continue
            if [[ "$fstype" == "ntfs" || "$fstype" == "fuseblk" ]]; then
                dev="/dev/$name"
                ntfs_devices+=("$dev")
                ntfs_labels+=("${label:-无标签}")
                ntfs_uuids+=("${uuid:-}")
                ntfs_mountpoints+=("$mountpoint")
                ((ntfs_count++))
            fi
        done < <(lsblk -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID,SIZE --noheadings 2>/dev/null)
    fi

    if [ $ntfs_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  未找到任何 NTFS 分区。${NC}"
        return 0
    fi

    if [ $ntfs_count -eq 0 ]; then
        while IFS='|' read -r device fstype label; do
            if [[ "$fstype" == "ntfs" || "$fstype" == "fuseblk" ]]; then
                ntfs_devices+=("$device")
                ntfs_labels+=("$label")
                ntfs_mountpoints+=("")
                ((ntfs_count++))
            fi
done < <(sudo blkid | grep -E 'TYPE="(ntfs|fuseblk)"' | $PYTHON_CMD << 'PYEOF'
import sys, re
for line in sys.stdin:
    dev = line.split(':')[0]
    fstype_m = re.search(r'TYPE="(.*?)"', line)
    label_m = re.search(r'LABEL="(.*?)"', line)
    fstype = fstype_m.group(1) if fstype_m else ''
    label = label_m.group(1) if label_m else ''
    print('{}|{}|{}'.format(dev, fstype, label))
PYEOF
        )
    fi

    if [ $ntfs_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  未找到任何 NTFS 分区。${NC}"
        return 0
    fi

    echo -e "${CYAN}找到 $ntfs_count 个 NTFS 分区，正在检查错误状态...${NC}"

    local dirty_indices=()
    for ((i=0; i<ntfs_count; i++)); do
        echo -n "  检查 ${ntfs_devices[$i]} ... "
        if sudo ntfsfix -n "${ntfs_devices[$i]}" 2>&1 | grep -qi "Volume is dirty"; then
            echo -e "${RED}有错误（脏）${NC}"
            dirty_indices+=("$i")
        else
            echo -e "${GREEN}正常${NC}"
        fi
    done

    if [ ${#dirty_indices[@]} -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✅ 所有 NTFS 分区状态正常，无磁盘写入错误。${NC}"
        return 0
    fi

    echo ""
    echo -e "${YELLOW}发现 ${#dirty_indices[@]} 个分区存在写入错误（脏标志）：${NC}"
    for idx in "${dirty_indices[@]}"; do
        echo "  $(($idx+1)). ${ntfs_devices[$idx]}  标签:${ntfs_labels[$idx]:-无}  挂载点:${ntfs_mountpoints[$idx]:-未挂载}"
    done

    echo ""
    echo "请选择修复方式："
    echo "  1) 修复所有有错误的分区"
    echo "  2) 选择特定分区修复"
    echo "  3) 取消修复"

    local fix_choice
    while true; do
        read -p "请输入选项 [1-3]: " fix_choice < /dev/tty
        case $fix_choice in
            1|2|3) break ;;
            *) echo -e "${RED}无效选项，请重新选择。${NC}" ;;
        esac
    done

    case $fix_choice in
        1)
            for idx in "${dirty_indices[@]}"; do
                fix_single_ntfs "${ntfs_devices[$idx]}" "${ntfs_mountpoints[$idx]}"
            done
            ;;
        2)
            echo "请输入要修复的分区编号（多个编号用空格分隔，如 1 3）："
            while true; do
                read -p "编号: " -a indices < /dev/tty
                local valid=false
                for idx in "${indices[@]}"; do
                    if [[ "$idx" =~ ^[0-9]+$ ]] && [ "$idx" -ge 1 ] && [ "$idx" -le $ntfs_count ]; then
                        for d in "${dirty_indices[@]}"; do
                            if [ "$d" -eq "$((idx-1))" ]; then
                                valid=true
                                break 2
                            fi
                        done
                    fi
                done
                if [ "$valid" = true ]; then
                    break
                else
                    echo -e "${RED}无效编号或分区未脏，请重新输入。${NC}"
                fi
            done
            for idx in "${indices[@]}"; do
                if [[ "$idx" =~ ^[0-9]+$ ]] && [ "$idx" -ge 1 ] && [ "$idx" -le $ntfs_count ]; then
                    fix_single_ntfs "${ntfs_devices[$((idx-1))]}" "${ntfs_mountpoints[$((idx-1))]}"
                fi
            done
            ;;
        3|*)
            echo "操作取消。"
            return 0
            ;;
    esac

    echo ""
    echo -e "${GREEN}✅ 修复流程完成。${NC}"
}

clear_hosts_cache() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 清理hosts缓存 ════════════════${NC}"
    echo -e "${CYAN}正在清理hosts缓存...${NC}"
    sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d_%H%M%S)
    sudo sh -c 'echo "" > /etc/hosts'
    echo -e "${GREEN}✓ hosts缓存已清理完成${NC}"
}

calibrate_joystick_stick() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 校准摇杆 ════════════════${NC}"
    echo -e "${CYAN}正在校准摇杆...${NC}"
    if thumbstick_cal; then
        echo -e "${GREEN}✓ 摇杆校准完成${NC}"
    else
        echo -e "${RED}✗ 摇杆校准失败${NC}"
        echo "请确保系统中已安装摇杆校准工具 (thumbstick_cal)"
    fi
}

calibrate_joystick_trigger() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 校准扳机 ════════════════${NC}"
    echo -e "${CYAN}正在校准扳机...${NC}"
    if trigger_cal; then
        echo -e "${GREEN}✓ 扳机校准完成${NC}"
    else
        echo -e "${RED}✗ 扳机校准失败${NC}"
        echo "请确保系统中已安装扳机校准工具 (trigger_cal)"
    fi
}

steamdeck_cache_manager() {
    if ! command -v zenity &>/dev/null; then
        zenity --error --text="未找到 zenity，请安装。"
        return 1
    fi

    local steamapps_dir="/home/deck/.local/share/Steam/steamapps"
    if [ ! -d "$steamapps_dir" ]; then
        zenity --error --text="未找到 Steam 目录。"
        return 1
    fi

    while true; do
        local choice=$(zenity --list --radiolist \
            --title="Steam 缓存管理器" \
            --text="请选择要清理的缓存类型" \
            --column="选择" --column="类型" \
            FALSE "着色器缓存" \
            FALSE "兼容数据 (Proton前缀)" \
            --width=400 --height=200)

        if [ -z "$choice" ]; then
            break
        fi

        if [ "$choice" = "着色器缓存" ]; then
            cache_type="shadercache"
            title="着色器缓存"
        else
            cache_type="compatdata"
            title="兼容数据"
        fi

        local cache_dir="$steamapps_dir/$cache_type"
        if [ ! -d "$cache_dir" ]; then
            zenity --info --text="未找到 $title 目录。"
            continue
        fi

        local apps=()
        for dir in "$cache_dir"/*; do
            if [ -d "$dir" ]; then
                local app_id=$(basename "$dir")
                if [[ "$app_id" =~ ^[0-9]+$ ]]; then
                    local size=$(du -sm "$dir" 2>/dev/null | cut -f1)
                    if [ -n "$size" ] && [ "$size" -gt 0 ]; then
                        local manifest="$steamapps_dir/appmanifest_${app_id}.acf"
                        if [ -f "$manifest" ]; then
                            game_name=$(grep '"name"' "$manifest" | cut -d'"' -f4)
                        else
                            game_name="Unknown"
                        fi
                        apps+=("$app_id|$game_name|$size|$dir")
                    fi
                fi
            fi
        done

        if [ ${#apps[@]} -eq 0 ]; then
            zenity --info --text="没有找到可清理的 $title。"
            continue
        fi

        local list_data=()
        for entry in "${apps[@]}"; do
            IFS='|' read -r app_id game_name size dir <<< "$entry"
            list_data+=("FALSE" "$game_name (ID: $app_id)" "${size}MB")
        done

        local selections=$(zenity --list --checklist \
            --title="选择要删除的 $title" \
            --text="请勾选要删除的缓存项" \
            --column="选择" --column="游戏名" --column="大小" \
            "${list_data[@]}" \
            --width=600 --height=400 \
            --multiple)

        if [ -z "$selections" ]; then
            continue
        fi

        IFS='|' read -r -a selected_names <<< "$selections"
        local selected_dirs=()
        for selected in "${selected_names[@]}"; do
            for entry in "${apps[@]}"; do
                IFS='|' read -r app_id game_name size dir <<< "$entry"
                local display_name="$game_name (ID: $app_id)"
                if [ "$display_name" = "$selected" ]; then
                    selected_dirs+=("$dir")
                    break
                fi
            done
        done

        if [ ${#selected_dirs[@]} -eq 0 ]; then
            zenity --info --text="未选择任何有效项目。"
            continue
        fi

        zenity --question \
            --text="确定要删除选中的 $title 吗？\n共 ${#selected_dirs[@]} 项。" \
            --ok-label="删除" --cancel-label="取消"
        if [ $? -ne 0 ]; then
            continue
        fi

        local deleted=0 failed=0
        for d in "${selected_dirs[@]}"; do
            if rm -rf "$d"; then
                ((deleted++))
            else
                ((failed++))
            fi
        done

        zenity --info --text="删除完成！\n成功: $deleted 项\n失败: $failed 项"
    done
}

fix_boot() {
    mk_temp_dir
    clear
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

read -n1 -p "按回车键或 A 键确认，其他键取消: " confirm_boot
echo

if [[ -z "$confirm_boot" || "$confirm_boot" =~ [Aa] ]]; then
    echo "继续执行..."
else
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
}

fix_shared_disk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 自动挂载 Windows 分区 ════════════════${NC}"
    echo ""
    echo "步骤1: 禁用 SteamOS 只读模式"
    sudo steamos-readonly disable 2>/dev/null
    echo -e "${GREEN}✓ 已处理${NC}"
    echo ""
    echo "步骤2: 修改 UDisks2 权限文件"
    UDISKS2_FILE="/usr/share/polkit-1/actions/org.freedesktop.UDisks2.policy"
    if [ -f "$UDISKS2_FILE" ]; then
        sudo cp "$UDISKS2_FILE" "$UDISKS2_FILE.backup.$(date +%Y%m%d)" 2>/dev/null
        sudo sed -i '181s/<allow_active>[^<]*<\\/allow_active>/<allow_active>yes<\\/allow_active>/' "$UDISKS2_FILE" 2>/dev/null
        echo -e "${GREEN}✓ 已修改${NC}"
    else
        echo -e "${YELLOW}⚠️  未找到 UDisks2 文件，跳过${NC}"
    fi
    echo ""

    echo "步骤3: 扫描 Windows (NTFS) 分区（忽略恢复分区）..."
    local sys_mounts=("/" "/home" "/var" "/efi" "/esp" "/boot" "/boot/efi")
    local recovery_guid="de94bba4-06d1-4d40-a16a-bfd50179d6ac"

    local part_devices=()
    local part_labels=()
    local part_mountpoints=()
    local part_uuids=()
    local part_sizes=()
    local part_count=0
    local all_mounted=true

    while read -r name type label fstype mountpoint uuid parttype size; do
        [[ "$name" == "NAME" ]] && continue
        [[ "$type" != "part" ]] && continue
        [[ ! "$fstype" =~ ^(ntfs|fuseblk|ntfs3)$ ]] && continue

        local skip=0
        local sysmp
        for sysmp in "${sys_mounts[@]}"; do
            if [[ "$mountpoint" == "$sysmp" ]]; then
                skip=1
                break
            fi
        done
        [ $skip -eq 1 ] && continue

        if [ -n "$parttype" ] && [[ "${parttype,,}" == "$recovery_guid" ]]; then
            if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ] && mountpoint -q "$mountpoint"; then
                echo "  恢复分区 /dev/$name 已挂载，正在卸载..."
                sudo umount "$mountpoint" 2>/dev/null
            fi
            if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ] && [ -d "$mountpoint" ]; then
                if [ -z "$(ls -A "$mountpoint" 2>/dev/null)" ]; then
                    sudo rmdir "$mountpoint" 2>/dev/null && echo "  已删除空挂载点 $mountpoint"
                fi
            fi
            continue
        fi

        part_devices+=("/dev/$name")
        part_labels+=("$label")
        part_mountpoints+=("$mountpoint")
        part_uuids+=("$uuid")
        part_sizes+=("$size")
        ((part_count++))

        if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ] && mountpoint -q "$mountpoint" 2>/dev/null; then
            :
        else
            all_mounted=false
        fi
    done < <(lsblk -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID,PARTTYPE,SIZE --noheadings 2>/dev/null)

    if [ $part_count -eq 0 ]; then
        while read -r source fstype mountpoint; do
            if [[ "$source" =~ ^/dev/ ]]; then
                dev="$source"
                label=$(lsblk -n -o LABEL "$dev" 2>/dev/null)
                uuid=$(lsblk -n -o UUID "$dev" 2>/dev/null)
                size=$(lsblk -n -o SIZE "$dev" 2>/dev/null)
                part_devices+=("$dev")
                part_labels+=("${label:-无标签}")
                part_mountpoints+=("$mountpoint")
                part_uuids+=("$uuid")
                part_sizes+=("${size:-}")
                ((part_count++))
            fi
        done < <(findmnt -t ntfs,fuseblk,ntfs3 -o SOURCE,FSTYPE,TARGET -n 2>/dev/null)
    fi

    if [ $part_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  未检测到任何符合条件的 Windows (NTFS) 分区。${NC}"
        return
    fi

    echo -e "${CYAN}检测到以下 Windows 分区：${NC}"
    for ((i=0; i<part_count; i++)); do
        echo "  $((i+1)). ${part_devices[$i]} 标签:${part_labels[$i]:-无} 大小:${part_sizes[$i]} 挂载点:${part_mountpoints[$i]:-未挂载}"
    done
    echo ""

    echo "步骤4: 清理残留的非 Windows 分区挂载条目和空目录..."
    local cleaned=0
    local mp dev parttype fstype
    while read -r mp; do
        if [ -n "$mp" ] && mountpoint -q "$mp"; then
            dev=$(findmnt -n -o SOURCE "$mp" 2>/dev/null)
            if [ -n "$dev" ]; then
                parttype=$(lsblk -n -o PARTTYPE "$dev" 2>/dev/null)
                fstype=$(df -T "$mp" | tail -1 | awk '{print $2}')
                if [[ "${parttype,,}" == "$recovery_guid" ]] || [[ "$fstype" != "ntfs" && "$fstype" != "fuseblk" ]]; then
                    echo "  正在卸载 $mp ..."
                    sudo umount "$mp" 2>/dev/null && ((cleaned++))
                fi
            fi
        fi
    done < <(mount | grep ' /run/media/deck/' | awk '{print $3}')

    for d in /run/media/deck/*; do
        if [ -d "$d" ] && ! mountpoint -q "$d" && [ -z "$(ls -A "$d" 2>/dev/null)" ]; then
            echo "  删除空目录 $d"
            sudo rmdir "$d" 2>/dev/null && ((cleaned++))
        fi
    done

    if [ $cleaned -gt 0 ]; then
        echo -e "${GREEN}✓ 清理完成${NC}"
    else
        echo "  无需清理。"
    fi
    echo ""

    if $all_mounted; then
        echo -e "${GREEN}✅ 所有 Windows 分区均已挂载，无需操作。${NC}"
        return
    fi

    echo "步骤5: 开始挂载并写入 fstab..."
    local mount_point clean_label devname suffix
    for ((i=0; i<part_count; i++)); do
        device="${part_devices[$i]}"
        label="${part_labels[$i]}"
        mountpoint="${part_mountpoints[$i]}"
        uuid="${part_uuids[$i]}"

        echo -e "\n${CYAN}处理分区 $device${NC}"

        if [ -n "$mountpoint" ] && [ "$mountpoint" != "None" ]; then
            mount_point="$mountpoint"
            echo "  当前已挂载到 $mount_point"
        else
            if [ -n "$label" ] && [ "$label" != "None" ]; then
                clean_label=$(echo "$label" | sed 's/ /_/g')
                mount_point="/run/media/deck/$clean_label"
            else
                devname=$(basename "$device")
                mount_point="/run/media/deck/$devname"
            fi
            if [ -d "$mount_point" ] && [ -n "$(ls -A "$mount_point" 2>/dev/null)" ]; then
                suffix=1
                while [ -d "${mount_point}_$suffix" ]; do ((suffix++)); done
                mount_point="${mount_point}_$suffix"
            fi
            sudo mkdir -p "$mount_point"
            sudo chown deck:deck "$mount_point"
            echo "  创建挂载点: $mount_point"
        fi

        if grep -q "UUID=$uuid" /etc/fstab 2>/dev/null; then
            echo "  fstab 中已存在该 UUID，跳过添加。"
        else
            echo "UUID=$uuid $mount_point ntfs-3g rw,exec,uid=1000,gid=1000,windows_names,nofail 0 0" | sudo tee -a /etc/fstab > /dev/null
            echo "  已添加 fstab 条目。"
        fi

        if mountpoint -q "$mount_point"; then
            echo "  分区已挂载到 $mount_point"
        else
            if sudo mount -U "$uuid" "$mount_point" 2>/dev/null; then
                echo -e "${GREEN}  ✓ 挂载成功到 $mount_point${NC}"
            else
                echo -e "${RED}  ✗ 挂载失败，请检查 dmesg 输出。${NC}"
            fi
        fi
    done
    echo ""
    echo -e "${GREEN}════════════════ 全部完成 ════════════════${NC}"
}

install_uu_accelerator() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装UU加速器插件 ════════════════${NC}"
    echo -e "${CYAN}正在安装UU加速器插件...${NC}"
    curl -s uudeck.com | sudo sh
    echo -e "${GREEN}UU加速器插件安装完成。${NC}"
}

install_xunyou_accelerator() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装迅游加速器插件 ════════════════${NC}"
    echo -e "${CYAN}正在安装迅游加速器插件...${NC}"
    curl -s sd.xunyou.com | sudo sh
    echo -e "${GREEN}迅游加速器插件安装完成。${NC}"
}

install_qiyou_accelerator() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装奇游联机宝加速插件 ════════════════${NC}"
    echo -e "${CYAN}正在安装奇游联机宝加速插件...${NC}"
    curl -s sd.qiyou.cn | sudo sh
    echo -e "${GREEN}奇游联机宝加速插件安装完成。${NC}"
}

install_asklink() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ AskLink 远程 ════════════════${NC}"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}AskLink 已安装。${NC}"
        echo -e "${YELLOW}按 回车键/A键 卸载，按其他键保持安装并退出。${NC}"
        read -p "请选择: " -n 1 -r
        echo ""
        if [[ $REPLY == "" ]]; then
            echo -e "${CYAN}正在卸载 AskLink...${NC}"
            sudo rm -rf /opt/AskLink
            rm -f "$HOME/Desktop/AskLink.desktop"
            sudo rm -f /usr/share/applications/AskLink.desktop
            rm -f "$HOME/.local/share/applications/AskLink.desktop"
            if [ -d "$HOME/Documents/AskLink" ]; then
                rm -rf "$HOME/Documents/AskLink"
                echo -e "${CYAN}已删除配置文件目录 $HOME/Documents/AskLink${NC}"
            fi
            echo -e "${GREEN}✅ AskLink 已卸载。${NC}"
        else
            echo -e "${GREEN}保持 AskLink 安装。${NC}"
        fi
        return 0
    fi

    echo -e "${CYAN}检查 SteamOS 只读状态...${NC}"
    if command -v steamos-readonly &>/dev/null; then
        if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
            echo -e "${CYAN}正在禁用只读模式...${NC}"
            sudo steamos-readonly disable
            if [ $? -ne 0 ]; then
                echo -e "${RED}禁用只读模式失败，请手动执行 sudo steamos-readonly disable${NC}"
                return 1
            fi
        else
            echo -e "${GREEN}只读模式已禁用${NC}"
        fi
    fi

    if ! command -v dpkg &>/dev/null; then
        echo -e "${CYAN}未检测到 dpkg，正在安装...${NC}"
        if command -v pacman &>/dev/null; then
            sudo pacman -S --noconfirm dpkg
            if [ $? -ne 0 ]; then
                echo -e "${RED}安装 dpkg 失败，请手动执行 sudo pacman -S dpkg${NC}"
                return 1
            fi
            echo -e "${GREEN}dpkg 安装完成${NC}"
        else
            echo -e "${RED}未找到包管理器，无法安装 dpkg。请手动安装 dpkg。${NC}"
            return 1
        fi
    else
        echo -e "${GREEN}dpkg 已存在${NC}"
    fi

    local ASKLINK_URL="https://dl.asklink.com/linux/4.0.33.0/AskLink-4.0.33.0-x86_64.deb"
    local FILENAME="AskLink-4.0.33.0-x86_64.deb"

    echo -e "${CYAN}下载地址: ${ASKLINK_URL}${NC}"
    echo -e "${CYAN}正在下载 ${FILENAME} ...${NC}"

    cd "$TEMP_DIR" || return
    if command -v wget &>/dev/null; then
        wget --show-progress "$ASKLINK_URL" -O "$FILENAME"
    else
        curl -L --progress-bar "$ASKLINK_URL" -o "$FILENAME"
    fi
    if [ $? -ne 0 ] || [ ! -f "$FILENAME" ]; then
        echo -e "${RED}下载失败。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在安装...${NC}"
    sudo dpkg --force-depends -i "$FILENAME" 2>/dev/null

    rm -f "$FILENAME"

    if [ -d "/opt/AskLink" ] || command -v asklink &>/dev/null; then
        echo -e "${GREEN}✅ AskLink 安装成功！${NC}"
        local DESKTOP_FILE="$HOME/Desktop/AskLink.desktop"
        cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=AskLink
Comment=远程协助工具
Exec=/opt/AskLink/AskLink
Icon=AskLink
Terminal=false
Categories=Network;RemoteAccess;
EOF
        chmod +x "$DESKTOP_FILE"
        echo -e "${GREEN}✓ 桌面快捷方式已创建。${NC}"
    else
        echo -e "${RED}安装失败，请手动检查。${NC}"
        return 1
    fi

    echo -e "${GREEN}AskLink 安装流程结束。${NC}"
}

watt_toolkit_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}═══════安装/更新 Watt Toolkit (Steam++) ═══════${NC}"
    echo ""

    local INSTALL_DIR="/home/deck/Watt Toolkit"
    local DESKTOP_DIR="/home/deck/Desktop"
    local DOWNLOAD_URL="https://gitee.com/rmbgame/SteamTools/releases/download/3.1.0/Steam%20%20_v3.1.0_linux_x64.tgz"
    local VERSION="3.1.0"

    for cmd in curl sudo unzip tar; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    local installed_version=""
    if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/.version" ]; then
        installed_version=$(cat "$INSTALL_DIR/.version")
        echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
    else
        echo -e "${YELLOW}未检测到已安装的 Watt Toolkit。${NC}"
    fi

    if [ -n "$installed_version" ] && [ "$installed_version" = "$VERSION" ]; then
        echo -e "${GREEN}✅ 已是最新版本 ${installed_version}，无需操作。${NC}"
        return 0
    fi

    echo -e "${GREEN}将安装版本: ${VERSION}${NC}"
    echo "正在下载 ${DOWNLOAD_URL} ..."

    local temp_dir="/tmp/watt_toolkit_install"
    rm -rf "$temp_dir"
    mkdir -p "$temp_dir"
    cd "$temp_dir" || return 1

    local filename="Steam_v${VERSION}_linux_x64.tgz"
    curl -L --progress-bar -o "$filename" "$DOWNLOAD_URL"
    if [ $? -ne 0 ] || [ ! -f "$filename" ]; then
        echo -e "${RED}下载失败，请检查网络后重试。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在解压...${NC}"
    local temp_extract="$temp_dir/extracted"
    mkdir -p "$temp_extract"
    if ! tar -xzf "$filename" -C "$temp_extract"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$temp_dir"
        return 1
    fi

    local content_count=$(ls -1 "$temp_extract" | wc -l)
    local first_item=$(ls -1 "$temp_extract" | head -1)

    if [ -d "$INSTALL_DIR" ]; then
        echo "检测到旧安装目录，正在删除..."
        rm -rf "$INSTALL_DIR"
    fi
    mkdir -p "$INSTALL_DIR"

    if [ $content_count -eq 1 ] && [ -d "$temp_extract/$first_item" ]; then
        echo -e "${CYAN}检测到顶层目录，移动内容到 $INSTALL_DIR ...${NC}"
        shopt -s dotglob
        mv "$temp_extract/$first_item"/* "$INSTALL_DIR/"
        shopt -u dotglob
        find "$temp_extract/$first_item" -maxdepth 1 -name ".*" ! -name "." ! -name ".." -exec mv {} "$INSTALL_DIR/" \;
        rm -rf "$temp_extract/$first_item"
    else
        echo -e "${CYAN}移动所有内容到 $INSTALL_DIR ...${NC}"
        shopt -s dotglob
        mv "$temp_extract"/* "$INSTALL_DIR/"
        shopt -u dotglob
        find "$temp_extract" -maxdepth 1 -name ".*" ! -name "." ! -name ".." -exec mv {} "$INSTALL_DIR/" \;
    fi

    rm -rf "$temp_dir"


    echo "$VERSION" > "$INSTALL_DIR/.version"

    local desktop_file="$DESKTOP_DIR/Watt_Toolkit.desktop"
    local dotnet_root="$INSTALL_DIR/dotnet"
    local dll_path="$INSTALL_DIR/assemblies/Steam++.dll"
    local icon_path="$INSTALL_DIR/Icons/Watt-Toolkit.png"

    if [ ! -f "$dll_path" ] || [ ! -f "$dotnet_root/dotnet" ]; then
        echo -e "${RED}错误: 关键文件缺失，安装可能不完整。${NC}"
        echo "请检查 $INSTALL_DIR 目录内容。"
        return 1
    fi

    cat > "$desktop_file" << EOF
[Desktop Entry]
Categories=Network;Game;
Comment[zh_CN]=Steam 工具箱
Comment=Steam 工具箱
Exec=env 'DOTNET_ROOT=${dotnet_root}' '${dotnet_root}/dotnet' '${dll_path}'
GenericName[zh_CN]=
GenericName=
Icon=${icon_path}
MimeType=
Name[zh_CN]=Watt Toolkit (Steam++)
Name=Watt Toolkit (Steam++)
Path=
StartupNotify=true
Terminal=false
TerminalOptions=
Type=Application
X-KDE-SubstituteUID=false
X-KDE-Username=
EOF
    chmod +x "$desktop_file"
    echo -e "${GREEN}✓ 桌面快捷方式已创建: ${desktop_file}${NC}"

    echo ""
    echo -e "${GREEN}✅ Watt Toolkit ${VERSION} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${INSTALL_DIR}${NC}"
    echo ""
    echo -e "${YELLOW}使用提示：${NC}"
    echo "如果加速报错，请按照下面步骤操作："
    echo "  网络加速 → 加速设置 → 安装证书"
    echo ""
    echo "请在桌面启动 Watt Toolkit。"
}

watt_toolkit_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}══════════════ 卸载 Watt Toolkit ══════════════${NC}"
    local INSTALL_DIR="/home/deck/Watt Toolkit"
    local DESKTOP_DIR="/home/deck/Desktop"

    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}未检测到已安装的 Watt Toolkit。${NC}"
        return 0
    fi

    echo -e "${CYAN}正在卸载 Watt Toolkit...${NC}"
    echo "将删除以下目录: ${INSTALL_DIR}"
    echo "将删除桌面快捷方式: ${DESKTOP_DIR}/Watt_Toolkit.desktop"
    echo ""

    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    if rm -rf "$INSTALL_DIR"; then
        echo -e "${GREEN}✓ 已删除安装目录${NC}"
    else
        echo -e "${RED}✗ 删除安装目录失败${NC}"
    fi

    if rm -f "${DESKTOP_DIR}/Watt_Toolkit.desktop"; then
        echo -e "${GREEN}✓ 已删除桌面快捷方式${NC}"
    else
        echo -e "${RED}✗ 删除桌面快捷方式失败${NC}"
    fi

    echo ""
    echo -e "${GREEN}✅ Watt Toolkit 已卸载完成。${NC}"
}

install_plugin_store() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装插件商店 ════════════════${NC}"
    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"

    local releases_json=$(curl -s "https://api.github.com/repos/SteamDeckHomebrew/decky-loader/releases")
    if [ -z "$releases_json" ]; then
        echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
        return 1
    fi

    local versions_info=$(echo "$releases_json" | $PYTHON_CMD -c "
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
except:
    print('STABLE:')
    print('PRERELEASE:')
")
    if [ -z "$versions_info" ]; then
        echo -e "${RED}错误: 无法解析版本信息。${NC}"
        return 1
    fi

    local stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
    local prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

    local latest_stable=""
    if [ -n "$stable_list" ]; then
        latest_stable=$(echo "$stable_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
        [ -n "$latest_stable" ] && latest_stable="v${latest_stable}"
    fi

    local latest_prerelease=""
    if [ -n "$prerelease_list" ]; then
        latest_prerelease=$(echo "$prerelease_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
        [ -n "$latest_prerelease" ] && latest_prerelease="v${latest_prerelease}"
    fi

    local PLUGIN_LOADER="/home/deck/homebrew/services/PluginLoader"
    local installed_version=""
    if [[ -f "$PLUGIN_LOADER" && -x "$PLUGIN_LOADER" ]]; then
        installed_version=$(sudo journalctl -u plugin_loader --no-pager 2>/dev/null | grep -i "Starting Decky version" | tail -1 | grep -oP 'version v?\K[0-9.]+(-pre[0-9]+)?')
        if [[ -z "$installed_version" ]]; then
            installed_version=$("$PLUGIN_LOADER" --version 2>/dev/null | grep -oP '\d+\.\d+\.\d+(-pre\d+)?')
        fi
        if [[ -n "$installed_version" ]]; then
            installed_version="v${installed_version}"
            echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
        else
            echo -e "${YELLOW}已安装但无法获取版本。${NC}"
        fi
    else
        echo "未检测到现有安装。"
    fi

    local options=()
    local labels=()
    if [ -n "$latest_stable" ]; then
        options+=("$latest_stable")
        labels+=("正式版 $latest_stable")
    fi
    if [ -n "$latest_prerelease" ]; then
        options+=("$latest_prerelease")
        labels+=("预发布版 $latest_prerelease")
    fi

    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}错误: 未找到任何版本。${NC}"
        return 1
    fi

    local target_version=""

    if [ -z "$installed_version" ]; then
        while true; do
            clear
            echo -e "${YELLOW}════════════════ 安装插件商店 ════════════════${NC}"
            echo ""
            echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
            echo -e "${YELLOW}未检测到现有安装。${NC}"
            echo ""
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
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
    else
        local is_prerelease=false
        if [ -n "$prerelease_list" ]; then
            local inst_ver_clean=$(echo "$installed_version" | sed 's/^v//')
            for tag in $(echo "$prerelease_list" | tr ',' '\n'); do
                local tag_clean=$(echo "$tag" | sed 's/^v//')
                if [ "$tag_clean" = "$inst_ver_clean" ]; then
                    is_prerelease=true
                    break
                fi
            done
        fi

        if [ "$is_prerelease" = true ]; then
            if [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}当前已安装预发布版 ${installed_version}。${NC}"
                echo -e "${YELLOW}是否切换为正式版 ${latest_stable}？${NC}"
                read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新预发布版 ${installed_version}，且没有正式版可切换。${NC}"
                return 0
            fi
        else
            if [ -n "$latest_prerelease" ]; then
                local stable_num=$(echo "$installed_version" | sed 's/^v//')
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
                if [ "$higher" = "$prerelease_num" ]; then
                    echo -e "${YELLOW}当前已安装正式版 ${installed_version}。${NC}"
                    echo -e "${YELLOW}发现更高或相等的预发布版 ${latest_prerelease}，是否切换？${NC}"
                    read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice
                    echo
                    if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                        target_version="$latest_prerelease"
                        echo -e "${GREEN}将切换至预发布版: ${target_version}${NC}"
                    else
                        echo "保持当前版本。"
                        return 0
                    fi
                else
                    echo -e "${GREEN}已是最新正式版 ${installed_version}，且没有更高的预发布版。${NC}"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新正式版 ${installed_version}，且没有预发布版。${NC}"
                return 0
            fi
        fi
    fi

    if [ -z "$target_version" ]; then
        echo -e "${RED}错误: 未确定目标版本。${NC}"
        return 1
    fi

    HOME_DIR="/home/deck"
    HOMEBREW_DIR="${HOME_DIR}/homebrew"
    SERVICE_DIR="${HOMEBREW_DIR}/services"
    PLUGIN_DIR="${HOMEBREW_DIR}/plugins"
    PLUGIN_LOADER="${SERVICE_DIR}/PluginLoader"
    SERVICE_FILE="${SERVICE_DIR}/plugin_loader.service"
    SERVICE_DEST="/etc/systemd/system/plugin_loader.service"
    CURRENT_USER=$(whoami)

    MIRRORS=(
        "http://gh.ddlc.top/"
        "http://ghproxy.net/"
        "http://mirror.ghproxy.com/"
        "https://github.com/"
    )
    DOWNLOAD_PATH="https://github.com/SteamDeckHomebrew/decky-loader/releases/download/${target_version}/PluginLoader"
    TMP_FILE="${PLUGIN_LOADER}.tmp"

    mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR"
    sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "$HOMEBREW_DIR" 2>/dev/null || true

    local DOWNLOAD_SUCCESS=false
    while true; do
        clear
        echo -e "${YELLOW}════════════════ 安装插件商店 ════════════════${NC}"
        echo ""
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
        echo ""
        echo "请选择下载镜像源（输入编号，0取消）："
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRRORS[$i]}"
        done

        read -p "请输入选择: " choice < /dev/tty

        if [[ -z "$choice" ]]; then
            echo -e "${RED}输入无效，请重新选择。${NC}"
            sleep 1
            continue
        fi
        if [[ "$choice" == "0" ]]; then
            echo "操作已取消。"
            return 0
        fi
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            mirror="${MIRRORS[$((choice-1))]}"
            FULL_URL="${mirror}${DOWNLOAD_PATH}"
            echo -e "尝试从 ${mirror} 下载..."
            curl -L --progress-bar -o "$TMP_FILE" "$FULL_URL"
            curl_exit=$?
            if [[ $curl_exit -eq 0 ]] && [[ -f "$TMP_FILE" ]]; then
                FILE_SIZE=$(stat -c%s "$TMP_FILE" 2>/dev/null || stat -f%z "$TMP_FILE" 2>/dev/null)
                if [[ -n "$FILE_SIZE" ]] && [[ "$FILE_SIZE" -gt 1000000 ]]; then
                    echo -e "\n${GREEN}下载成功 (大小: $((FILE_SIZE/1024/1024)) MB)${NC}"
                    DOWNLOAD_SUCCESS=true
                    break
                else
                    echo -e "\n${RED}下载文件无效 (${FILE_SIZE} 字节)。${NC}"
                    rm -f "$TMP_FILE"
                    sleep 1
                fi
            else
                echo -e "\n${RED}下载失败 (退出码: $curl_exit)。${NC}"
                rm -f "$TMP_FILE"
                sleep 1
            fi
        else
            echo -e "${RED}无效编号，请重新选择。${NC}"
            sleep 1
        fi
    done

    if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
        echo -e "${RED}下载失败，安装中止。${NC}"
        return 1
    fi

    for cmd in curl "$PYTHON_CMD" systemctl sudo journalctl stat; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    if [[ ! -d "$HOMEBREW_DIR" ]]; then
        sudo mkdir -p "$HOMEBREW_DIR"
    fi
    sudo chown -R ${CURRENT_USER}:${CURRENT_USER} "$HOMEBREW_DIR" 2>/dev/null || true
    mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR" 2>/dev/null || {
        sudo mkdir -p "$SERVICE_DIR" "$PLUGIN_DIR"
        sudo chown ${CURRENT_USER}:${CURRENT_USER} "$SERVICE_DIR" "$PLUGIN_DIR"
    }

    if [[ -f "$PLUGIN_LOADER" ]]; then
        sudo rm -f "$PLUGIN_LOADER"
    fi
    mv "$TMP_FILE" "$PLUGIN_LOADER"
    chmod +x "$PLUGIN_LOADER"

    touch "${HOME_DIR}/.steam/steam/.cef-enable-remote-debugging"
    if [[ -d "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/" ]]; then
        touch "${HOME_DIR}/.var/app/com.valvesoftware.Steam/data/Steam/.cef-enable-remote-debugging"
    fi

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
    echo -e "${GREEN}✅ Decky Loader ${target_version} 安装/更新完成！${NC}"
    echo "请切换回游戏模式，按 '...' 键打开侧边栏检查。"
}

uninstall_plugin_store() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载插件商店 ════════════════${NC}"
    if [ ! -d "/home/deck/homebrew" ]; then
        echo -e "${YELLOW}未检测到已安装的插件商店。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到已安装插件商店。${NC}"
    echo "警告：这将删除整个 /home/deck/homebrew 目录，包括所有插件。"
    echo ""
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    echo "正在执行卸载..."
    if sudo rm -rf /home/deck/homebrew; then
        echo -e "${GREEN}✓ 插件商店卸载完成${NC}"
        echo "如需重新安装，请使用 '安装插件商店' 功能。"
    else
        echo -e "${RED}✗ 插件商店卸载失败${NC}"
    fi
}

install_tomoon_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 ToMoon 插件 ════════════════${NC}"
    echo ""

    local PLUGIN_DIR="/home/deck/homebrew/plugins/tomoon"
    local VERSION_FILE="$PLUGIN_DIR/package.json"
    local TEMP_DIR="/tmp/tomoon_install"
    local MIRRORS=(
        "http://gh.ddlc.top/"
        "http://ghproxy.net/"
        "http://mirror.ghproxy.com/"
        "https://github.com/"
    )

    for cmd in curl sudo unzip; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    echo -e "${CYAN}正在从 GitHub 获取最新版本...${NC}"
    local release_info=$(curl -s "https://api.github.com/repos/YukiCoco/ToMoon/releases/latest")
    if [ -z "$release_info" ]; then
        echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
        return 1
    fi

    local latest_version=$(echo "$release_info" | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//; s/".*//')
    if [ -z "$latest_version" ]; then
        echo -e "${RED}错误: 无法解析版本号，API 返回内容可能异常。${NC}"
        echo -e "${YELLOW}返回内容（前200字符）: ${release_info:0:200}${NC}"
        return 1
    fi

    local download_url=$(echo "$release_info" | grep -o '"browser_download_url": *"[^"]*tomoon-[^"]*\.zip"' | head -1 | sed 's/.*"browser_download_url": *"//; s/".*//')
    if [ -z "$download_url" ]; then
        echo -e "${RED}错误: 无法获取 ZIP 下载链接。${NC}"
        echo -e "${YELLOW}请检查该 release 是否包含 tomoon-*.zip 资产。${NC}"
        return 1
    fi

    local local_version=""
    if [ -f "$VERSION_FILE" ]; then
        local_version=$(grep -o '"version": *"[^"]*"' "$VERSION_FILE" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$local_version" ]; then
            local_version="v${local_version}"
        else
            echo -e "${YELLOW}已安装但无法读取版本号。${NC}"
        fi
    fi

    if [ -n "$local_version" ] && [ "$local_version" = "$latest_version" ]; then
        echo -e "${GREEN}已经是最新版本 ${local_version}，无需更新。${NC}"
        return 0
    fi

    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return

    local zip_filename="tomoon-${latest_version}.zip"
    local DOWNLOAD_SUCCESS=false

    while true; do
        clear
        echo -e "${YELLOW}════════════════ 安装/更新 ToMoon 插件 ════════════════${NC}"
        echo ""
        echo -e "${GREEN}最新版本: ${latest_version}${NC}"
        if [ -n "$local_version" ]; then
            echo -e "${CYAN}当前已安装版本: ${local_version}${NC}"
        else
            echo -e "${YELLOW}未检测到已安装的 ToMoon 插件。${NC}"
        fi
        echo -e "${GREEN}将安装版本: ${latest_version}${NC}"
        echo ""
        echo "请选择下载镜像源（输入编号，0取消）："
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRRORS[$i]}"
        done

        read -p "请输入选择: " choice < /dev/tty

        if [[ -z "$choice" ]]; then
            echo -e "${RED}输入无效，请重新选择。${NC}"
            sleep 1
            continue
        fi
        if [[ "$choice" == "0" ]]; then
            echo "操作已取消。"
            return 0
        fi
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            mirror="${MIRRORS[$((choice-1))]}"
            FULL_URL="${mirror}${download_url}"
            echo -e "尝试从 ${mirror} 下载..."

            curl -L --progress-bar -f -o "$zip_filename" "$FULL_URL"
            local curl_exit=$?

            if [ $curl_exit -eq 0 ] && [ -f "$zip_filename" ]; then
                if unzip -t "$zip_filename" &> /dev/null; then
                    echo -e "${GREEN}下载成功，文件完整。${NC}"
                    DOWNLOAD_SUCCESS=true
                    break
                else
                    echo -e "${RED}下载文件不完整（zip 校验失败），请重新选择镜像源。${NC}"
                    rm -f "$zip_filename"
                    sleep 1
                fi
            else
                echo -e "${RED}下载失败（curl 退出码: $curl_exit），请重新选择镜像源。${NC}"
                rm -f "$zip_filename"
                sleep 1
            fi
        else
            echo -e "${RED}无效编号，请重新选择。${NC}"
            sleep 1
        fi
    done

    if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
        echo -e "${RED}下载失败，安装中止。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在解压并安装到 ${PLUGIN_DIR}...${NC}"

    local EXTRACT_DIR="$TEMP_DIR/extract"
    mkdir -p "$EXTRACT_DIR"

    if ! sudo unzip -q "$zip_filename" -d "$EXTRACT_DIR"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$TEMP_DIR"
        return 1
    fi

    local extracted_dir=""
    extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 2 -type f -name "package.json" -exec dirname {} \; | head -1)
    if [ -z "$extracted_dir" ]; then
        extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 2 -type f -name "tomoon" -exec dirname {} \; | head -1)
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 1 -type d ! -path "$EXTRACT_DIR" | head -1)
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir="$EXTRACT_DIR"
    fi

    sudo rm -rf "$PLUGIN_DIR"
    sudo mkdir -p /home/deck/homebrew/plugins
    sudo mv "$extracted_dir" "$PLUGIN_DIR"
    sudo chown -R deck:deck "$PLUGIN_DIR"

    rm -rf "$TEMP_DIR"

    echo -e "${GREEN}✅ ToMoon 插件 ${latest_version} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${PLUGIN_DIR}${NC}"
}

install_tomoon_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 ToMoon 插件 ════════════════${NC}"
    if [ ! -d "/home/deck/homebrew/plugins/tomoon" ]; then
        echo -e "${YELLOW}未检测到已安装的 ToMoon 插件。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到已安装 ToMoon 插件。${NC}"
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    sudo rm -rf /home/deck/homebrew/plugins/tomoon
    echo -e "${GREEN}✅ 卸载完成${NC}"
}

install_freedeck_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 Freedeck 插件 ════════════════${NC}"
    echo ""

    local GITHUB_REPO="panyiwei-home/Freedeck"
    local PLUGIN_DIR="/home/deck/homebrew/plugins/Freedeck"
    local VERSION_FILE="$PLUGIN_DIR/package.json"
    local TEMP_DIR="/tmp/freedeck_install"
    local MIRRORS=(
        "http://gh.ddlc.top/"
        "http://ghproxy.net/"
        "http://mirror.ghproxy.com/"
        "https://github.com/"
    )

    for cmd in curl sudo unzip; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    echo -e "${CYAN}正在从 GitHub 获取最新正式版信息...${NC}"
    local release_json=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases/latest")
    if [ -z "$release_json" ]; then
        echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
        return 1
    fi

    local target_version=$(echo "$release_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tag = data.get('tag_name', '')
    print(tag)
except:
    print('')
")
    if [ -z "$target_version" ]; then
        echo -e "${RED}错误: 无法解析最新版本号。${NC}"
        return 1
    fi

    local download_url=$(echo "$release_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for asset in data.get('assets', []):
        if asset.get('name', '').endswith('.zip'):
            print(asset.get('browser_download_url', ''))
            break
except:
    pass
")
    if [ -z "$download_url" ]; then
        echo -e "${RED}错误: 无法获取 ${target_version} 的下载链接。${NC}"
        return 1
    fi

    local local_version=""
    if [ -f "$VERSION_FILE" ]; then
        local_version=$(grep -o '"version": *"[^"]*"' "$VERSION_FILE" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$local_version" ]; then
            local_ver_clean="${local_version#v}"
            target_ver_clean="${target_version#v}"
            if [ "$local_ver_clean" = "$target_ver_clean" ]; then
                echo -e "${GREEN}✅ 已是最新版本 ${target_version}，无需操作。${NC}"
                return 0
            fi
        fi
    fi

    echo -e "${CYAN}将安装版本: ${target_version}${NC}"

    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return

    local zip_filename="Freedeck.zip"
    local DOWNLOAD_SUCCESS=false

    while true; do
        clear
        echo -e "${YELLOW}════════════════ 安装/更新 Freedeck 插件 ════════════════${NC}"
        echo ""
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
        echo ""
        echo "请选择下载镜像源（输入编号，0取消）："
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRRORS[$i]}"
        done

        read -p "请输入选择: " choice < /dev/tty

        if [[ -z "$choice" ]]; then
            echo -e "${RED}输入无效，请重新选择。${NC}"
            sleep 1
            continue
        fi
        if [[ "$choice" == "0" ]]; then
            echo "操作已取消。"
            return 0
        fi
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            mirror="${MIRRORS[$((choice-1))]}"
            FULL_URL="${mirror}${download_url}"
            echo -e "尝试从 ${mirror} 下载..."

            curl -L --progress-bar -f -o "$zip_filename" "$FULL_URL"
            local curl_exit=$?

            if [ $curl_exit -eq 0 ] && [ -f "$zip_filename" ]; then
                if unzip -t "$zip_filename" &> /dev/null; then
                    echo -e "${GREEN}下载成功，文件完整。${NC}"
                    DOWNLOAD_SUCCESS=true
                    break
                else
                    echo -e "${RED}下载文件不完整（zip 校验失败），请重新选择镜像源。${NC}"
                    rm -f "$zip_filename"
                    sleep 1
                fi
            else
                echo -e "${RED}下载失败（curl 退出码: $curl_exit），请重新选择镜像源。${NC}"
                rm -f "$zip_filename"
                sleep 1
            fi
        else
            echo -e "${RED}无效编号，请重新选择。${NC}"
            sleep 1
        fi
    done

    if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
        echo -e "${RED}下载失败，安装中止。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在解压并安装到 ${PLUGIN_DIR}...${NC}"

    local EXTRACT_DIR="$TEMP_DIR/extract"
    mkdir -p "$EXTRACT_DIR"

    if ! unzip -q "$zip_filename" -d "$EXTRACT_DIR"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$TEMP_DIR"
        return 1
    fi

    local extracted_dir=""
    extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 2 -type f -name "package.json" -exec dirname {} \; | head -1)
    if [ -z "$extracted_dir" ]; then
        extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 1 -type d ! -path "$EXTRACT_DIR" | head -1)
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir="$EXTRACT_DIR"
    fi

    sudo rm -rf "$PLUGIN_DIR"
    sudo mkdir -p /home/deck/homebrew/plugins
    sudo mv "$extracted_dir" "$PLUGIN_DIR"
    sudo chown -R deck:deck "$PLUGIN_DIR"

    rm -rf "$TEMP_DIR"

    echo -e "${GREEN}✅ Freedeck 插件 ${target_version} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${PLUGIN_DIR}${NC}"
}

install_freedeck_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Freedeck 插件 ════════════════${NC}"
    if [ ! -d "/home/deck/homebrew/plugins/Freedeck" ]; then
        echo -e "${YELLOW}未检测到已安装的 Freedeck 插件。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到已安装 Freedeck 插件。${NC}"
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    sudo rm -rf /home/deck/homebrew/plugins/Freedeck
    echo -e "${GREEN}✅ 卸载完成${NC}"
}

get_ge_proton_versions() {
    curl -s "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases?per_page=100" | \
        python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    tags = []
    for rel in data:
        tag = rel.get('tag_name', '')
        if tag.startswith('GE-Proton'):
            tags.append(tag)
    print('\n'.join(tags))
except:
    pass
"
}

get_installed_ge_proton() {
    local install_dir="$HOME/.local/share/Steam/compatibilitytools.d"
    [ -d "$install_dir" ] || return
    for dir in "$install_dir"/GE-Proton*; do
        [ -d "$dir" ] && basename "$dir"
    done
}

ge_proton_manager() {
    while true; do
        local choice=$(zenity --list --radiolist \
            --title="GE-Proton 兼容层管理" \
            --text="请选择要执行的操作" \
            --column="选择" --column="操作" \
            FALSE "安装 GE-Proton" \
            FALSE "卸载 GE-Proton" \
            --width=400 --height=200 2>/dev/null)
        [ $? -eq 1 ] && return 0
        case "$choice" in
            "安装 GE-Proton") ge_proton_install ;;
            "卸载 GE-Proton") ge_proton_uninstall ;;
            *) return 0 ;;
        esac
    done
}

ge_proton_install() {
    (
        echo "10"; echo "# 正在获取版本列表，请稍候..."
        sleep 0.5
        echo "50"; echo "# 正在连接 GitHub API..."
        sleep 0.5
        echo "100"
    ) | zenity --progress --pulsate --title="加载中" --text="正在获取版本列表..." --width=400 2>/dev/null &
    ZENITY_PID=$!

    local all_versions=$(get_ge_proton_versions)

    kill $ZENITY_PID 2>/dev/null
    wait $ZENITY_PID 2>/dev/null

    [ -z "$all_versions" ] && {
        zenity --error --text="无法获取版本列表，请检查网络。" --width=400 2>/dev/null
        return 1
    }
    mapfile -t version_array <<< "$all_versions"

    local installed_list=$(get_installed_ge_proton)
    local installed_array=()
    [ -n "$installed_list" ] && mapfile -t installed_array <<< "$installed_list"

    local available_versions=()
    for ver in "${version_array[@]}"; do
        local already=false
        for inst in "${installed_array[@]}"; do
            [ "$ver" = "$inst" ] && { already=true; break; }
        done
        [ "$already" = false ] && available_versions+=("$ver")
    done

    [ ${#available_versions[@]} -eq 0 ] && {
        zenity --info --text="所有 GE-Proton 版本已安装！" --width=400 2>/dev/null
        return 0
    }

    local list_args=(
        --list --checklist
        --title="安装 GE-Proton 兼容层"
        --text="请选择要安装的版本（可多选）\n共 ${#available_versions[@]} 个版本可用，已排除已安装版本"
        --column="选择" --column="版本"
        --width=600 --height=500
        --ok-label="安装"
        --cancel-label="返回"
    )
    for ver in "${available_versions[@]}"; do
        list_args+=("FALSE" "$ver")
    done

    local selection
    selection=$(zenity "${list_args[@]}" 2>/dev/null)
    local ret=$?

    if [ $ret -eq 1 ] || [ $ret -eq -1 ]; then
        return 0
    elif [ $ret -eq 0 ]; then
        [ -z "$selection" ] && {
            zenity --warning --text="请至少选择一个版本。" --width=300 2>/dev/null
            return 0
        }
        IFS='|' read -r -a selected <<< "$selection"
        ge_proton_do_install "${selected[@]}"
    fi
}

ge_proton_do_install() {
    local versions=("$@")
    local total=${#versions[@]}
    local install_dir="$HOME/.local/share/Steam/compatibilitytools.d"
    mkdir -p "$install_dir"

    local success_count=0
    local failed_count=0
    local failed_list=""

    local mirror_choice=$(zenity --list --radiolist \
        --title="选择下载镜像源" \
        --text="所有版本将使用同一镜像源" \
        --column="选择" --column="镜像源" \
        FALSE "gh.ddlc.top (国内镜像)" \
        FALSE "ghproxy.net (国内镜像)" \
        FALSE "mirror.ghproxy.com (国内镜像)" \
        FALSE "GitHub (官方源)" \
        --width=500 --height=250 2>/dev/null)
    [ -z "$mirror_choice" ] && return 0

    local mirror=""
    case "$mirror_choice" in
        "gh.ddlc.top (国内镜像)") mirror="http://gh.ddlc.top/" ;;
        "ghproxy.net (国内镜像)") mirror="http://ghproxy.net/" ;;
        "mirror.ghproxy.com (国内镜像)") mirror="http://mirror.ghproxy.com/" ;;
        "GitHub (官方源)") mirror="https://github.com/" ;;
    esac

    local pipe="/tmp/zenity_pipe_$$"
    mkfifo "$pipe"
    zenity --progress --pulsate --title="安装 GE-Proton" --text="准备开始..." --width=500 < "$pipe" &
    local zenity_pid=$!
    exec 3> "$pipe"

    for i in "${!versions[@]}"; do
        if ! kill -0 $zenity_pid 2>/dev/null; then
            echo "用户取消安装" >&2
            break
        fi

        local version="${versions[$i]}"
        local idx=$((i+1))
        echo "# 正在处理第 $idx/$total 个: $version (准备下载...)" >&3

        local download_url=$(curl -s "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/tags/${version}" | \
            python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for asset in data.get('assets', []):
        name = asset.get('name', '')
        if name.endswith('.tar.gz') and 'aarch64' not in name:
            print(asset.get('browser_download_url', ''))
            break
except:
    pass
")
        if [ -z "$download_url" ]; then
            echo "# 错误：无法获取 $version 的下载链接，跳过" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (无法获取下载链接)"
            continue
        fi

        local full_url="${mirror}${download_url}"
        local temp_dir="/tmp/ge_proton_$$"
        mkdir -p "$temp_dir"
        cd "$temp_dir" || continue
        local filename="${version}.tar.gz"

        echo "# 正在处理第 $idx/$total 个: $version (下载中...)" >&3
        curl -L -f -S --connect-timeout 30 --max-time 600 -o "$filename" "$full_url" 2> /tmp/curl_err_$$.log
        local curl_ret=$?
        if [ $curl_ret -ne 0 ]; then
            echo "# 下载失败，错误信息：" >&3
            tail -n 5 /tmp/curl_err_$$.log >&3
            rm -f /tmp/curl_err_$$.log
            rm -f "$filename"
            cd /tmp && rm -rf "$temp_dir"
            ((failed_count++))
            failed_list="${failed_list}\n  $version (下载失败)"
            continue
        fi
        rm -f /tmp/curl_err_$$.log

        echo "# 正在处理第 $idx/$total 个: $version (解压中...)" >&3
        tar -xzf "$filename" -C "$install_dir"
        local tar_ret=$?

        rm -f "$filename"
        cd /tmp && rm -rf "$temp_dir"

        if [ $tar_ret -eq 0 ] && [ -d "$install_dir/$version" ]; then
            echo "# 第 $idx/$total 个: $version 安装成功" >&3
            ((success_count++))
        else
            echo "# 第 $idx/$total 个: $version 安装失败" >&3
            ((failed_count++))
            failed_list="${failed_list}\n  $version (解压失败)"
        fi
    done

    if kill -0 $zenity_pid 2>/dev/null; then
        local result_msg="\n========== 安装完成 ==========\n成功: $success_count 个"
        if [ $failed_count -gt 0 ]; then
            result_msg+="\n失败: $failed_count 个\n失败的版本:${failed_list}"
        fi
        if [ $success_count -gt 0 ]; then
            result_msg+="\n\n建议重启 Steam 以刷新兼容层列表。"
        fi
        echo "# $result_msg" >&3
        exec 3>&-
        wait $zenity_pid 2>/dev/null
    fi

    rm -f "$pipe"
}

ge_proton_uninstall() {
    local installed_list=$(get_installed_ge_proton)
    [ -z "$installed_list" ] && {
        zenity --info --text="未检测到已安装的 GE-Proton。" --ok-label="返回" --width=400 2>/dev/null
        return 0
    }
    mapfile -t installed_array <<< "$installed_list"

    local list_args=(
        --list --checklist
        --title="卸载 GE-Proton 兼容层"
        --text="请选择要卸载的版本（可多选）"
        --column="选择" --column="版本"
        --width=500 --height=350
        --ok-label="卸载"
        --cancel-label="返回"
    )
    for ver in "${installed_array[@]}"; do
        list_args+=("FALSE" "$ver")
    done

    local selection=$(zenity "${list_args[@]}" 2>/dev/null)
    [ -z "$selection" ] && return 0
    IFS='|' read -r -a selected <<< "$selection"

    local install_dir="$HOME/.local/share/Steam/compatibilitytools.d"
    local total=${#selected[@]}
    local success=0 fail=0
    local failed_list=""

    local pipe="/tmp/zenity_pipe_$$"
    mkfifo "$pipe"
    zenity --progress --pulsate --title="卸载 GE-Proton" --text="准备开始..." --width=500 < "$pipe" &
    local zenity_pid=$!
    exec 3> "$pipe"

    for i in "${!selected[@]}"; do
        if ! kill -0 $zenity_pid 2>/dev/null; then
            echo "用户取消卸载" >&2
            break
        fi

        local version="${selected[$i]}"
        local idx=$((i+1))

        echo "# 正在处理第 $idx/$total 个: $version ..." >&3

        if [ -d "$install_dir/$version" ]; then
            rm -rf "$install_dir/$version"
            if [ ! -d "$install_dir/$version" ]; then
                ((success++))
                echo "# 第 $idx/$total 个: $version 已卸载" >&3
            else
                ((fail++))
                failed_list="${failed_list}\n  $version (删除失败)"
                echo "# 第 $idx/$total 个: $version 卸载失败" >&3
            fi
        else
            ((success++))
            echo "# 第 $idx/$total 个: $version (目录不存在，跳过)" >&3
        fi
        sleep 0.3
    done

    if kill -0 $zenity_pid 2>/dev/null; then
        local result_msg="\n========== 卸载完成 ==========\n成功: $success 个"
        if [ $fail -gt 0 ]; then
            result_msg+="\n失败: $fail 个\n失败的版本:${failed_list}"
        fi
        result_msg+="\n\n建议重启 Steam 以使更改生效。"
        echo "# $result_msg" >&3
        exec 3>&-
        wait $zenity_pid 2>/dev/null
    fi

    rm -f "$pipe"
}

install_decky_lsfg_vk_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 LSFG-VK 插件 ════════════════${NC}"
    echo ""

    local GITHUB_REPO="xXJSONDeruloXx/decky-lsfg-vk"
    local PLUGIN_DIR="/home/deck/homebrew/plugins/Decky-LSFG-VK"
    local VERSION_FILE="$PLUGIN_DIR/package.json"
    local TEMP_DIR="/tmp/lsfg_vk_install"
    local MIRRORS=(
        "http://gh.ddlc.top/"
        "http://ghproxy.net/"
        "http://mirror.ghproxy.com/"
        "https://github.com/"
    )

    for cmd in curl sudo unzip python3; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
    local releases_json=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases")
    if [ -z "$releases_json" ]; then
        echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
        return 1
    fi

    local versions_info=$(echo "$releases_json" | $PYTHON_CMD -c "
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
except:
    print('STABLE:')
    print('PRERELEASE:')
")
    if [ -z "$versions_info" ]; then
        echo -e "${RED}错误: 无法解析版本信息。${NC}"
        return 1
    fi

    local stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
    local prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

    local latest_stable=""
    if [ -n "$stable_list" ]; then
        latest_stable=$(echo "$stable_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
        [ -n "$latest_stable" ] && latest_stable="v${latest_stable}"
    fi

    local latest_prerelease=""
    if [ -n "$prerelease_list" ]; then
        latest_prerelease=$(echo "$prerelease_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
        [ -n "$latest_prerelease" ] && latest_prerelease="v${latest_prerelease}"
    fi

    local local_version=""
    if [ -f "$VERSION_FILE" ]; then
        local_version=$(grep -o '"version": *"[^"]*"' "$VERSION_FILE" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$local_version" ]; then
            local_version="v${local_version}"
            echo -e "${CYAN}当前已安装版本: ${local_version}${NC}"
        else
            echo -e "${YELLOW}已安装但无法读取版本号。${NC}"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 LSFG-VK 插件。${NC}"
    fi

    local options=()
    local labels=()
    if [ -n "$latest_stable" ]; then
        options+=("$latest_stable")
        labels+=("正式版 $latest_stable")
    fi
    if [ -n "$latest_prerelease" ]; then
        options+=("$latest_prerelease")
        labels+=("预发布版 $latest_prerelease")
    fi

    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}错误: 未找到任何版本。${NC}"
        return 1
    fi

    local target_version=""

    if [ -z "$local_version" ]; then
        while true; do
            clear
            echo -e "${YELLOW}════════════════ 安装/更新 LSFG-VK 插件 ════════════════${NC}"
            echo ""
            echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
            echo -e "${YELLOW}未检测到已安装的 LSFG-VK 插件。${NC}"
            echo ""
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
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
    else
        local is_prerelease=false
        if [ -n "$prerelease_list" ]; then
            local inst_ver_clean=$(echo "$local_version" | sed 's/^v//')
            for tag in $(echo "$prerelease_list" | tr ',' '\n'); do
                local tag_clean=$(echo "$tag" | sed 's/^v//')
                if [ "$tag_clean" = "$inst_ver_clean" ]; then
                    is_prerelease=true
                    break
                fi
            done
        fi

        if [ "$is_prerelease" = true ]; then
            if [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}当前已安装预发布版 ${local_version}。${NC}"
                echo -e "${YELLOW}是否切换为正式版 ${latest_stable}？${NC}"
                read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新预发布版 ${local_version}，且没有正式版可切换。${NC}"
                return 0
            fi
        else
            if [ -n "$latest_prerelease" ]; then
                local stable_num=$(echo "$local_version" | sed 's/^v//')
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
                if [ "$higher" = "$prerelease_num" ]; then
                    echo -e "${YELLOW}当前已安装正式版 ${local_version}。${NC}"
                    echo -e "${YELLOW}发现更高或相等的预发布版 ${latest_prerelease}，是否切换？${NC}"
                    read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice
                    echo
                    if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                        target_version="$latest_prerelease"
                        echo -e "${GREEN}将切换至预发布版: ${target_version}${NC}"
                    else
                        echo "保持当前版本。"
                        return 0
                    fi
                else
                    echo -e "${GREEN}已是最新正式版 ${local_version}，且没有更高的预发布版。${NC}"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新正式版 ${local_version}，且没有预发布版。${NC}"
                return 0
            fi
        fi
    fi

    if [ -z "$target_version" ]; then
        echo -e "${RED}错误: 未确定目标版本。${NC}"
        return 1
    fi

    local download_url=$(echo "$releases_json" | $PYTHON_CMD -c "
import sys, json
try:
    data = json.load(sys.stdin)
    target_tag = '$target_version'
    for rel in data:
        if rel.get('tag_name') == target_tag:
            for asset in rel.get('assets', []):
                name = asset.get('name', '')
                if name.endswith('.zip'):
                    print(asset.get('browser_download_url', ''))
                    break
            break
except:
    pass
")
    if [ -z "$download_url" ]; then
        echo -e "${RED}错误: 无法获取 ${target_version} 的下载链接。${NC}"
        return 1
    fi

    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return

    local zip_filename="Decky.LSFG-VK.zip"
    local DOWNLOAD_SUCCESS=false

    while true; do
        clear
        echo -e "${YELLOW}════════════════ 安装/更新 LSFG-VK 插件 ════════════════${NC}"
        echo ""
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
        echo ""
        echo "请选择下载镜像源（输入编号，0取消）："
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRRORS[$i]}"
        done

        read -p "请输入选择: " choice < /dev/tty

        if [[ -z "$choice" ]]; then
            echo -e "${RED}输入无效，请重新选择。${NC}"
            sleep 1
            continue
        fi
        if [[ "$choice" == "0" ]]; then
            echo "操作已取消。"
            return 0
        fi
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            mirror="${MIRRORS[$((choice-1))]}"
            FULL_URL="${mirror}${download_url}"
            echo -e "尝试从 ${mirror} 下载..."

            curl -L --progress-bar -f -o "$zip_filename" "$FULL_URL"
            local curl_exit=$?

            if [ $curl_exit -eq 0 ] && [ -f "$zip_filename" ]; then
                if unzip -t "$zip_filename" &> /dev/null; then
                    echo -e "${GREEN}下载成功，文件完整。${NC}"
                    DOWNLOAD_SUCCESS=true
                    break
                else
                    echo -e "${RED}下载文件不完整（zip 校验失败），请重新选择镜像源。${NC}"
                    rm -f "$zip_filename"
                    sleep 1
                fi
            else
                echo -e "${RED}下载失败（curl 退出码: $curl_exit），请重新选择镜像源。${NC}"
                rm -f "$zip_filename"
                sleep 1
            fi
        else
            echo -e "${RED}无效编号，请重新选择。${NC}"
            sleep 1
        fi
    done

    if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
        echo -e "${RED}下载失败，安装中止。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在解压并安装到 ${PLUGIN_DIR}...${NC}"

    local EXTRACT_DIR="$TEMP_DIR/extract"
    mkdir -p "$EXTRACT_DIR"

    if ! sudo unzip -q "$zip_filename" -d "$EXTRACT_DIR"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$TEMP_DIR"
        return 1
    fi

    local extracted_dir=""
    extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 2 -type f -name "package.json" -exec dirname {} \; | head -1)
    if [ -z "$extracted_dir" ]; then
        extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 1 -type d ! -path "$EXTRACT_DIR" | head -1)
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir="$EXTRACT_DIR"
    fi

    sudo rm -rf "$PLUGIN_DIR"
    sudo mkdir -p /home/deck/homebrew/plugins
    sudo mv "$extracted_dir" "$PLUGIN_DIR"
    sudo chown -R deck:deck "$PLUGIN_DIR"

    rm -rf "$TEMP_DIR"

    echo -e "${GREEN}✅ LSFG-VK 插件 ${target_version} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${PLUGIN_DIR}${NC}"
}

install_decky_lsfg_vk_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 LSFG-VK 插件 ════════════════${NC}"
    if [ ! -d "/home/deck/homebrew/plugins/Decky-LSFG-VK" ]; then
        echo -e "${YELLOW}未检测到已安装的 LSFG-VK 插件。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到已安装 LSFG-VK 插件。${NC}"
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    sudo rm -rf /home/deck/homebrew/plugins/Decky-LSFG-VK
    echo -e "${GREEN}已卸载${NC}"
}

install_decky_framegen_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 Framegen 插件 ════════════════${NC}"
    echo ""

    local GITHUB_REPO="xXJSONDeruloXx/Decky-Framegen"
    local PLUGIN_DIR="/home/deck/homebrew/plugins/Decky-Framegen"
    local VERSION_FILE="$PLUGIN_DIR/package.json"
    local TEMP_DIR="/tmp/framegen_install"
    local MIRRORS=(
        "http://gh.ddlc.top/"
        "http://ghproxy.net/"
        "http://mirror.ghproxy.com/"
        "https://github.com/"
    )

    for cmd in curl sudo unzip python3; do
        if ! command -v $cmd &> /dev/null; then
            echo -e "${RED}错误: 未找到 $cmd 命令，请先安装。${NC}"
            return 1
        fi
    done

    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
    local releases_json=$(curl -s "https://api.github.com/repos/${GITHUB_REPO}/releases")
    if [ -z "$releases_json" ]; then
        echo -e "${RED}错误: 无法连接到 GitHub API，请检查网络。${NC}"
        return 1
    fi

    local versions_info=$(echo "$releases_json" | $PYTHON_CMD -c "
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
except:
    print('STABLE:')
    print('PRERELEASE:')
")
    if [ -z "$versions_info" ]; then
        echo -e "${RED}错误: 无法解析版本信息。${NC}"
        return 1
    fi

    local stable_list=$(echo "$versions_info" | grep "^STABLE:" | sed 's/^STABLE://')
    local prerelease_list=$(echo "$versions_info" | grep "^PRERELEASE:" | sed 's/^PRERELEASE://')

    local latest_stable=""
    if [ -n "$stable_list" ]; then
        latest_stable=$(echo "$stable_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
        [ -n "$latest_stable" ] && latest_stable="v${latest_stable}"
    fi

    local latest_prerelease=""
    if [ -n "$prerelease_list" ]; then
        latest_prerelease=$(echo "$prerelease_list" | tr ',' '\n' | sed 's/^v//' | sort -V | tail -1)
        [ -n "$latest_prerelease" ] && latest_prerelease="v${latest_prerelease}"
    fi

    local local_version=""
    if [ -f "$VERSION_FILE" ]; then
        local_version=$(grep -o '"version": *"[^"]*"' "$VERSION_FILE" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$local_version" ]; then
            local_version="v${local_version}"
            echo -e "${CYAN}当前已安装版本: ${local_version}${NC}"
        else
            echo -e "${YELLOW}已安装但无法读取版本号。${NC}"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 Framegen 插件。${NC}"
    fi

    local options=()
    local labels=()
    if [ -n "$latest_stable" ]; then
        options+=("$latest_stable")
        labels+=("正式版 $latest_stable")
    fi
    if [ -n "$latest_prerelease" ]; then
        options+=("$latest_prerelease")
        labels+=("预发布版 $latest_prerelease")
    fi

    if [ ${#options[@]} -eq 0 ]; then
        echo -e "${RED}错误: 未找到任何版本。${NC}"
        return 1
    fi

    local target_version=""

    if [ -z "$local_version" ]; then
        while true; do
            clear
            echo -e "${YELLOW}════════════════ 安装/更新 Framegen 插件 ════════════════${NC}"
            echo ""
            echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
            echo -e "${YELLOW}未检测到已安装的 Framegen 插件。${NC}"
            echo ""
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
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
    else
        local is_prerelease=false
        if [ -n "$prerelease_list" ]; then
            local inst_ver_clean=$(echo "$local_version" | sed 's/^v//')
            for tag in $(echo "$prerelease_list" | tr ',' '\n'); do
                local tag_clean=$(echo "$tag" | sed 's/^v//')
                if [ "$tag_clean" = "$inst_ver_clean" ]; then
                    is_prerelease=true
                    break
                fi
            done
        fi

        if [ "$is_prerelease" = true ]; then
            if [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}当前已安装预发布版 ${local_version}。${NC}"
                echo -e "${YELLOW}是否切换为正式版 ${latest_stable}？${NC}"
                read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice
                echo
                if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                    target_version="$latest_stable"
                    echo -e "${GREEN}将切换至正式版: ${target_version}${NC}"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新预发布版 ${local_version}，且没有正式版可切换。${NC}"
                return 0
            fi
        else
            if [ -n "$latest_prerelease" ]; then
                local stable_num=$(echo "$local_version" | sed 's/^v//')
                local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
                local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
                if [ "$higher" = "$prerelease_num" ]; then
                    echo -e "${YELLOW}当前已安装正式版 ${local_version}。${NC}"
                    echo -e "${YELLOW}发现更高或相等的预发布版 ${latest_prerelease}，是否切换？${NC}"
                    read -n1 -p "按回车键或 A 键切换，其他键保持: " switch_choice
                    echo
                    if [[ -z "$switch_choice" || "$switch_choice" == "a" || "$switch_choice" == "A" ]]; then
                        target_version="$latest_prerelease"
                        echo -e "${GREEN}将切换至预发布版: ${target_version}${NC}"
                    else
                        echo "保持当前版本。"
                        return 0
                    fi
                else
                    echo -e "${GREEN}已是最新正式版 ${local_version}，且没有更高的预发布版。${NC}"
                    return 0
                fi
            else
                echo -e "${GREEN}已是最新正式版 ${local_version}，且没有预发布版。${NC}"
                return 0
            fi
        fi
    fi

    if [ -z "$target_version" ]; then
        echo -e "${RED}错误: 未确定目标版本。${NC}"
        return 1
    fi

    local download_url=$(echo "$releases_json" | $PYTHON_CMD -c "
import sys, json
try:
    data = json.load(sys.stdin)
    target_tag = '$target_version'
    for rel in data:
        if rel.get('tag_name') == target_tag:
            for asset in rel.get('assets', []):
                name = asset.get('name', '')
                if name.endswith('.zip'):
                    print(asset.get('browser_download_url', ''))
                    break
            break
except:
    pass
")
    if [ -z "$download_url" ]; then
        echo -e "${RED}错误: 无法获取 ${target_version} 的下载链接。${NC}"
        return 1
    fi

    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return

    local zip_filename="Decky-Framegen.zip"
    local DOWNLOAD_SUCCESS=false

    while true; do
        clear
        echo -e "${YELLOW}════════════════ 安装/更新 Framegen 插件 ════════════════${NC}"
        echo ""
        echo -e "${GREEN}将安装版本: ${target_version}${NC}"
        echo ""
        echo "请选择下载镜像源（输入编号，0取消）："
        for i in "${!MIRRORS[@]}"; do
            echo "  $((i+1)). ${MIRRORS[$i]}"
        done

        read -p "请输入选择: " choice < /dev/tty

        if [[ -z "$choice" ]]; then
            echo -e "${RED}输入无效，请重新选择。${NC}"
            sleep 1
            continue
        fi
        if [[ "$choice" == "0" ]]; then
            echo "操作已取消。"
            return 0
        fi
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
            mirror="${MIRRORS[$((choice-1))]}"
            FULL_URL="${mirror}${download_url}"
            echo -e "尝试从 ${mirror} 下载..."

            curl -L --progress-bar -f -o "$zip_filename" "$FULL_URL"
            local curl_exit=$?

            if [ $curl_exit -eq 0 ] && [ -f "$zip_filename" ]; then
                if unzip -t "$zip_filename" &> /dev/null; then
                    echo -e "${GREEN}下载成功，文件完整。${NC}"
                    DOWNLOAD_SUCCESS=true
                    break
                else
                    echo -e "${RED}下载文件不完整（zip 校验失败），请重新选择镜像源。${NC}"
                    rm -f "$zip_filename"
                    sleep 1
                fi
            else
                echo -e "${RED}下载失败（curl 退出码: $curl_exit），请重新选择镜像源。${NC}"
                rm -f "$zip_filename"
                sleep 1
            fi
        else
            echo -e "${RED}无效编号，请重新选择。${NC}"
            sleep 1
        fi
    done

    if [[ "$DOWNLOAD_SUCCESS" != "true" ]]; then
        echo -e "${RED}下载失败，安装中止。${NC}"
        return 1
    fi

    echo -e "${CYAN}正在解压并安装到 ${PLUGIN_DIR}...${NC}"

    local EXTRACT_DIR="$TEMP_DIR/extract"
    mkdir -p "$EXTRACT_DIR"

    if ! sudo unzip -q "$zip_filename" -d "$EXTRACT_DIR"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$TEMP_DIR"
        return 1
    fi

    local extracted_dir=""
    extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 2 -type f -name "package.json" -exec dirname {} \; | head -1)
    if [ -z "$extracted_dir" ]; then
        extracted_dir=$(find "$EXTRACT_DIR" -maxdepth 1 -type d ! -path "$EXTRACT_DIR" | head -1)
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir="$EXTRACT_DIR"
    fi

    sudo rm -rf "$PLUGIN_DIR"
    sudo mkdir -p /home/deck/homebrew/plugins
    sudo mv "$extracted_dir" "$PLUGIN_DIR"
    sudo chown -R deck:deck "$PLUGIN_DIR"

    rm -rf "$TEMP_DIR"

    echo -e "${GREEN}✅ Framegen 插件 ${target_version} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${PLUGIN_DIR}${NC}"
}

install_decky_framegen_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Framegen 插件 ════════════════${NC}"
    if [ ! -d "/home/deck/homebrew/plugins/Decky-Framegen" ]; then
        echo -e "${YELLOW}未检测到已安装的 Framegen 插件。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到已安装 Framegen 插件。${NC}"
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    sudo rm -rf /home/deck/homebrew/plugins/Decky-Framegen
    echo -e "${GREEN}已卸载${NC}"
}

clover_install_or_reinstall() {
    clear
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
    echo "1) GitHub 官方"
    echo "2) ghproxy.net 镜像"
    read -p "请输入数字 [1-2]: " choice < /dev/tty

    case "$choice" in
        1) BASE_URL="https://github.com" ;;
        2) BASE_URL="https://ghproxy.net/https://github.com" ;;
        *) echo "操作已取消。"; return 0 ;;
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
    if ! git clone --progress --depth=1 "$REPO_URL" "$TARGET_DIR" 2>&1 | tee /tmp/clone_log.txt; then
        echo -e "${RED}克隆失败，请检查网络或更换镜像源。${NC}"
        rm -rf "$TARGET_DIR"
        read -p "按回车键返回主菜单..." < /dev/tty
        return 1
    fi

    echo -e "${GREEN}克隆完成。${NC}"
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
    echo "⚠️ 警告：设备不在官方支持列表，强制继续安装（风险自负）！"
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

CLOVER_FILE="Clover-${CLOVER_VERSION}-X64.iso.7z"
CLOVER_BASE=$(basename -s .7z "${CLOVER_FILE}")

MIRRORS=(
    "http://gh.ddlc.top/https://github.com"
    "http://ghproxy.net/https://github.com"
    "https://github.com"
)

DOWNLOAD_SUCCESS=0
while true; do
    echo ""
    echo "请选择下载镜像源（输入编号，0取消）："
    for i in "${!MIRRORS[@]}"; do
        echo "  $((i+1)). ${MIRRORS[$i]}"
    done
    read -p "请输入选择: " choice < /dev/tty

    if [[ -z "$choice" ]]; then
        echo "输入无效，请重新选择。"
        continue
    fi
    if [[ "$choice" == "0" ]]; then
        echo "操作已取消。"
        exit 0
    fi
    if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le ${#MIRRORS[@]} ]; then
        mirror="${MIRRORS[$((choice-1))]}"
        CLOVER_URL="${mirror}/CloverHackyColor/CloverBootloader/releases/download/${CLOVER_VERSION}/${CLOVER_FILE}"
        echo "尝试从 ${mirror} 下载..."
        if curl -# -L --fail --connect-timeout 10 --max-time 120 -o "${CLOVER_FILE}" "${CLOVER_URL}"; then
            echo "✅ 下载成功！"
            DOWNLOAD_SUCCESS=1
            break
        else
            echo "⚠️ 下载失败，请重新选择镜像源。"
            rm -f "${CLOVER_FILE}"
        fi
    else
        echo "无效编号，请重新选择。"
    fi
done

if [ ${DOWNLOAD_SUCCESS} -eq 0 ]; then
    echo "❌ 下载 Clover 失败！所有镜像源均不可用，请检查网络后重试。"
    exit 1
fi

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

    cat > ~/1Clover-tools/Clover-Toolbox.sh << 'TOOLBOX_EOF'
#!/bin/bash

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
		echo -e "$current_password\n" | sudo -S sed -i '/<string>os_batocera<\/string>/!b;n;n;c\\t\t\t\t\t<string>\\efi\\batocera\\grubx64\.efi<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "已为 Batocera v39 及更新版本更新 Clover 配置！" --width 450 --height 75

	elif [ "$Batocera_Choice" == "v38" ]
	then
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
		echo -e "$current_password\n" | sudo -S cp $EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig $EFI_PATH/Microsoft/Boot/bootmgfw.efi

		Windows=$(efibootmgr | grep -i Windows | colrm 9 | colrm 1 4)
		echo -e "$current_password\n" | sudo -S efibootmgr -n $Windows &> /dev/null

		echo -e "$current_password\n" | sudo -S systemctl disable --now clover-bootmanager
		zenity --warning --title "Clover 工具箱" --text "Clover systemd 服务已禁用。Windows 现已激活！" --width 500 --height 75

	elif [ "$Service_Choice" == "启用" ]
	then
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
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\microsoft\\bootmgfw\.efi<\/string>' $EFI_PATH/clover/config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist

		zenity --warning --title "Clover 工具箱" --text "Windows 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "SteamOS" ]
	then
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\efi\\steamos\\steamcl\.efi<\/string>' $EFI_PATH/clover/config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "SteamOS 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "Bazzite" ]
	then
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultLoader<\/key>/!b;n;c\\t\t<string>\\EFI\\FEDORA\\shimx64\.efi<\/string>' $EFI_PATH/clover/config.plist
		echo -e "$current_password\n" | sudo -S sed -i '/<key>DefaultVolume<\/key>/!b;n;c\\t\t<string>esp<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "Bazzite 现在是 Clover 中的默认启动项！" --width 400 --height 75

	elif [ "$Boot_Choice" == "上次系统" ]
	then
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
		echo -e "$current_password\n" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1280x800<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1280x800。" --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckHD" ]
	then
		echo -e "$current_password\n" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1200<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1920x1200。" --width 400 --height 75

	elif [ "$Resolution_Choice" == "DeckSight" ]
	then
		echo -e "$current_password\n" | sudo -S sed -i '/<key>ScreenResolution<\/key>/!b;n;c\\t\t<string>1920x1080<\/string>' $EFI_PATH/clover/config.plist
		zenity --warning --title "Clover 工具箱" --text "屏幕分辨率已设置为 1920x1080。" --width 400 --height 75

	fi

elif [ "$Choice" == "自定义" ]
then
	echo -e "$current_password\n" | sudo -S cp ~/1Clover-tools/efi/custom_clover_5157.efi $EFI_PATH/clover/cloverx64.efi
	zenity --warning --title "Clover 工具箱" --text "自定义 Clover EFI 已安装！" --width 400 --height 75

elif [ "$Choice" == "卸载" ]
then
	echo -e "$current_password\n" | sudo -S mv $EFI_PATH/Microsoft/Boot/bootmgfw.efi.orig $EFI_PATH/Microsoft/Boot/bootmgfw.efi
	if [ $? -eq 0 ]
	then
		echo -e "$current_password\n" | sudo -S rm $EFI_PATH/Microsoft/bootmgfw.efi
	else
		echo -e "$current_password\n" | sudo -S mv $EFI_PATH/Microsoft/bootmgfw.efi $EFI_PATH/Microsoft/Boot/bootmgfw.efi
	fi
	echo -e "$current_password\n" | sudo -S mv $BOOTX64.orig $BOOTX64

	echo -e "$current_password\n" | sudo -S rm -rf $EFI_PATH/clover

	for entry in $(efibootmgr | grep "Clover - GUI" | colrm 9 | colrm 1 4)
	do
		echo -e "$current_password\n" | sudo -S efibootmgr -b $entry -B &> /dev/null
	done

	echo -e "$current_password\n" | sudo -S rm $EFI_PATH/steamos/steamos.png &> /dev/null

	echo -e "$current_password\n" | sudo -S steamos-readonly disable

	echo -e "$current_password\n" | sudo -S systemctl stop clover-bootmanager.service
	echo -e "$current_password\n" | sudo -S rm /etc/systemd/system/clover-bootmanager*
	echo -e "$current_password\n" | sudo -S systemctl daemon-reload

	echo -e "$current_password\n" | sudo -S rm -f /etc/atomic-update.conf.d/clover-whitelist.conf

	echo -e "$current_password\n" | sudo -S steamos-readonly enable

	rm ~/.local/share/kservices5/ServiceMenus/open_as_root.desktop

	rm -rf ~/SteamDeck-Clover-dualboot
	rm -rf ~/1Clover-tools/

	rm -f ~/Desktop/引导文件配置.desktop

	zenity --warning --title "Clover 工具箱" --text "Clover 已卸载，Windows EFI 条目已激活！" --width 600 --height 75
	exit
fi
done
TOOLBOX_EOF

    chmod +x ~/1Clover-tools/Clover-Toolbox.sh
    echo -e "${GREEN}✓ 已更新 Clover-Toolbox.sh 为汉化版。${NC}"

    echo -e "${YELLOW}建议重启设备以使引导生效。${NC}"
    echo ""
}

install_anydesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 AnyDesk ════════════════${NC}"

    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    local ANYDESK_BIN="$ANYDESK_INSTALL_DIR/anydesk"
    local DESKTOP_FILE="$HOME/Desktop/AnyDesk.desktop"

    echo "正在检查最新版本..."
    local REMOTE_VERSION=$(curl -s https://anydesk.com.cn/zhs/downloads/linux | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1 | sed 's/^v//')
    if [ -z "$REMOTE_VERSION" ]; then
        echo -e "${YELLOW}无法自动获取版本，尝试使用默认版本 8.0.4${NC}"
        REMOTE_VERSION="8.0.4"
    fi
    echo "最新版本: $REMOTE_VERSION"

    local LOCAL_VERSION=""
    if [ -f "$ANYDESK_BIN" ] && [ -x "$ANYDESK_BIN" ]; then
        LOCAL_VERSION=$("$ANYDESK_BIN" --version 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [ -n "$LOCAL_VERSION" ]; then
            echo -e "${CYAN}当前已安装版本: ${LOCAL_VERSION}${NC}"
        else
            echo -e "${YELLOW}已安装但无法读取版本号，将重新安装。${NC}"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 AnyDesk。${NC}"
    fi

    local TARGET_VERSION=""
    if [ -n "$LOCAL_VERSION" ]; then
        if [ "$LOCAL_VERSION" = "$REMOTE_VERSION" ]; then
            echo -e "${GREEN}✅ 已是最新版本 ${LOCAL_VERSION}，无需操作。${NC}"
            return 0
        else
            echo -e "${YELLOW}发现新版本 ${REMOTE_VERSION}（当前: ${LOCAL_VERSION}）${NC}"
            read -n1 -p "按回车键或 A 键更新，其他键取消: " confirm
            echo
            if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
                TARGET_VERSION="$REMOTE_VERSION"
            else
                echo "取消更新。"
                return 0
            fi
        fi
    else
        TARGET_VERSION="$REMOTE_VERSION"
    fi

    if [ -z "$TARGET_VERSION" ]; then
        echo "未指定目标版本，操作取消。"
        return 0
    fi

    echo "正在安装 AnyDesk ${TARGET_VERSION}..."
    cd /tmp || return

    local URL="https://download.anydesk.com/linux/anydesk-${TARGET_VERSION}-amd64.tar.gz"
    echo "下载中..."

    if [ -d "$ANYDESK_INSTALL_DIR" ]; then
        rm -rf "$ANYDESK_INSTALL_DIR"
    fi
    mkdir -p "$ANYDESK_INSTALL_DIR"

    wget -q --show-progress "$URL" -O anydesk.tar.gz || {
        echo -e "${RED}下载失败，请检查网络后重试。${NC}"
        return 1
    }

    tar -xzf anydesk.tar.gz -C "$ANYDESK_INSTALL_DIR" --strip-components=1
    chmod +x "$ANYDESK_BIN"
    mkdir -p "$HOME/.local/bin"
    ln -sf "$ANYDESK_BIN" "$HOME/.local/bin/anydesk"

    cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Name=AnyDesk
Exec=$ANYDESK_BIN
Icon=$ANYDESK_INSTALL_DIR/icons/hicolor/256x256/apps/anydesk.png
Type=Application
Categories=Network;RemoteAccess;
EOF
    chmod +x "$DESKTOP_FILE"
    rm -f anydesk.tar.gz

    echo ""
    echo -e "${GREEN}✅ AnyDesk ${TARGET_VERSION} 安装完成！桌面快捷方式已创建。${NC}"
}

install_todesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装ToDesk ════════════════${NC}"
    echo -e "${CYAN}正在安装ToDesk...${NC}"
    sudo steamos-readonly disable
    curl -L todesk.lanbai.top | sh
    echo -e "${GREEN}✓ ToDesk安装脚本已执行${NC}"
    echo -e "${YELLOW}请在桌面上运行'todesk安装'或'todesk重新安装'的文件来完成安装${NC}"
}

install_wps_office() { install_flatpak_app "WPS Office" "WPS Office" "Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"; }
install_qq() { install_flatpak_app "QQ" "QQ" "Network;Chat" "com.qq.QQ" "com.tencent.qq"; }
install_wechat() { install_flatpak_app "微信" "微信" "Network;Chat" "com.tencent.WeChat" "com.qq.weixin"; }
install_qqmusic() { install_flatpak_app "QQ音乐" "QQ音乐" "Audio" "com.qq.QQmusic" "com.tencent.QQmusic"; }
install_baidunetdisk() { install_flatpak_app "百度网盘" "百度网盘" "Network;FileTransfer" "com.baidu.NetDisk" "com.baidu.pan"; }
install_edge() { install_flatpak_app "Edge浏览器" "Microsoft Edge" "Network;WebBrowser" "com.microsoft.Edge"; }
install_chrome() { install_flatpak_app "Google浏览器" "Google Chrome" "Network;WebBrowser" "com.google.Chrome"; }
install_fcitx5() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装 Fcitx 5 ════════════════${NC}"
    echo ""

    if flatpak info org.fcitx.Fcitx5 &>/dev/null; then
        echo -e "${GREEN}✓ Fcitx 5 主程序已安装。${NC}"
    else
        install_flatpak_app "Fcitx 5" "Fcitx 5" "Utility;Settings" "org.fcitx.Fcitx5"
    fi

    echo ""
    if flatpak info org.fcitx.Fcitx5.Addon.ChineseAddons &>/dev/null; then
        echo -e "${GREEN}✓ 中文输入法插件已安装。${NC}"
    else
        echo "正在安装中文输入法插件..."
        flatpak install flathub org.fcitx.Fcitx5.Addon.ChineseAddons -y 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 中文插件安装完成${NC}"
        else
            echo -e "${YELLOW}⚠️  中文插件安装失败，可稍后手动在软件中心安装。${NC}"
        fi
    fi
}

update_installed_apps() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 更新全部应用 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在更新所有应用...${NC}"
    flatpak update -y
    echo -e "${GREEN}✓ 所有应用更新完成${NC}"
}

uninstall_wps_office() { uninstall_flatpak_app "WPS Office" "WPS Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"; }
uninstall_qq() { uninstall_flatpak_app "QQ" "QQ" "com.qq.QQ" "com.tencent.qq"; }
uninstall_wechat() { uninstall_flatpak_app "微信" "微信" "com.tencent.WeChat" "com.qq.weixin"; }
uninstall_qqmusic() { uninstall_flatpak_app "QQ音乐" "QQ音乐" "com.qq.QQmusic" "com.tencent.QQmusic"; }
uninstall_baidunetdisk() { uninstall_flatpak_app "百度网盘" "百度网盘" "com.baidu.NetDisk" "com.baidu.pan"; }
uninstall_edge() { uninstall_flatpak_app "Edge浏览器" "Microsoft Edge" "com.microsoft.Edge"; }
uninstall_chrome() { uninstall_flatpak_app "Google浏览器" "Google Chrome" "com.google.Chrome" "org.chromium.Chromium"; }
uninstall_anydesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 AnyDesk ════════════════${NC}"

    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    local DESKTOP_FILE="$HOME/Desktop/AnyDesk.desktop"
    local BIN_LINK="$HOME/.local/bin/anydesk"
    local flatpak_id="com.anydesk.Anydesk"

    local local_found=false
    local flatpak_found=false
    [ -d "$ANYDESK_INSTALL_DIR" ] && local_found=true
    flatpak info "$flatpak_id" &>/dev/null && flatpak_found=true

    if ! $local_found && ! $flatpak_found; then
        echo -e "${YELLOW}未检测到已安装的 AnyDesk。${NC}"
        return 0
    fi

    echo -e "${CYAN}检测到 AnyDesk 安装：${NC}"
    $local_found && echo "  • 本地安装 ($ANYDESK_INSTALL_DIR)"
    $flatpak_found && echo "  • Flatpak 安装 ($flatpak_id)"

    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "继续卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    if $local_found; then
        rm -rf "$ANYDESK_INSTALL_DIR" && echo -e "${GREEN}✓ 已删除本地安装目录${NC}"
        rm -f "$DESKTOP_FILE" && echo -e "${GREEN}✓ 已删除本地桌面快捷方式${NC}"
        rm -f "$BIN_LINK" && echo -e "${GREEN}✓ 已删除命令链接${NC}"
    fi

    if $flatpak_found; then
        echo "正在卸载 Flatpak 版本的 AnyDesk..."
        if flatpak uninstall "$flatpak_id" -y &>/dev/null; then
            echo -e "${GREEN}✓ Flatpak 版本已卸载${NC}"
            local desktop_dir="$HOME/Desktop"
            if [ -d "$desktop_dir" ]; then
                for f in "$desktop_dir"/*.desktop; do
                    local base=$(basename "$f")
                    if [ "$base" = "AnyDesk.desktop" ] || \
                       [ "$base" = "${flatpak_id}.desktop" ] || \
                       [[ "$base" == *"${flatpak_id//./_}"* ]]; then
                        rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ 已删除桌面快捷方式 $base${NC}"
                    fi
                done
            fi

            local data_dir="$HOME/.var/app/$flatpak_id"
            if [ -d "$data_dir" ]; then
                echo ""
                echo -e "${CYAN}是否删除 AnyDesk 的所有设置和用户数据？${NC}"
                read -n1 -p "按回车键或 A 键确认删除，其他键保留: " del_data
                echo
                if [[ -z "$del_data" || "$del_data" =~ [Aa] ]]; then
                    rm -rf "$data_dir" && echo -e "${GREEN}✓ 用户数据已删除${NC}"
                else
                    echo -e "${YELLOW}已保留用户数据。${NC}"
                fi
            else
                echo -e "${YELLOW}未找到用户数据目录，跳过。${NC}"
            fi

        else
            echo -e "${RED}✗ Flatpak 版本卸载失败${NC}"
        fi
    fi

    echo ""
    echo -e "${GREEN}✅ AnyDesk 卸载完成。${NC}"
}

uninstall_fcitx5() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Fcitx 5 ════════════════${NC}"

    local MAIN_APP="org.fcitx.Fcitx5"
    local ADDON_APP="org.fcitx.Fcitx5.Addon.ChineseAddons"
    local DESKTOP_NAME="Fcitx 5"

    if ! flatpak info "$MAIN_APP" &>/dev/null; then
        echo -e "${YELLOW}未检测到已安装的 Fcitx 5 主程序。${NC}"
        if flatpak info "$ADDON_APP" &>/dev/null; then
            echo -e "${CYAN}检测到中文插件已安装但主程序缺失，是否只卸载插件？${NC}"
            read -n1 -p "按回车键或 A 键确认卸载插件，其他键取消: " confirm
            echo
            if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
                flatpak uninstall "$ADDON_APP" -y 2>/dev/null && echo -e "${GREEN}✓ 中文插件已卸载${NC}"
            else
                echo "取消操作。"
            fi
        fi
        return 0
    fi

    echo -e "${CYAN}检测到 Fcitx 5 主程序已安装。${NC}"
    read -n1 -p "按回车键或 A 键确认卸载，其他键取消: " confirm
    echo
    if [[ -z "$confirm" || "$confirm" =~ [Aa] ]]; then
        echo "开始卸载..."
    else
        echo "取消卸载。"
        return 0
    fi

    if flatpak info "$ADDON_APP" &>/dev/null; then
        echo "正在卸载中文插件..."
        flatpak uninstall "$ADDON_APP" -y 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✓ 中文插件已卸载${NC}"
        else
            echo -e "${YELLOW}⚠️  中文插件卸载失败（可能已被移除）${NC}"
        fi
    else
        echo -e "${YELLOW}中文插件未安装，跳过。${NC}"
    fi

    echo "正在卸载 Fcitx 5 主程序..."
    flatpak uninstall "$MAIN_APP" -y 2>/dev/null
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Fcitx 5 主程序已卸载${NC}"
    else
        echo -e "${RED}✗ 主程序卸载失败，请检查 flatpak 状态。${NC}"
        return 1
    fi

    local desktop_dir="$HOME/Desktop"
    if [ -d "$desktop_dir" ]; then
        for f in "$desktop_dir/Fcitx 5.desktop" "$desktop_dir/org.fcitx.Fcitx5.desktop"; do
            if [ -f "$f" ]; then
                rm -f "$f" 2>/dev/null && echo -e "${GREEN}✓ 已删除桌面快捷方式 $(basename "$f")${NC}"
            fi
        done
        find "$desktop_dir" -maxdepth 1 -name "*Fcitx*" -name "*.desktop" -exec rm -f {} \; 2>/dev/null
    fi

    echo ""
    echo -e "${GREEN}✅ Fcitx 5 及其相关组件已卸载完成。${NC}"
}

uninstall_other_flatpak_apps() {
    if ! command -v zenity &>/dev/null; then
        echo "未找到 zenity，请在桌面环境运行。"
        return 1
    fi

    local exclude_ids=(
        "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"
        "com.qq.QQ" "com.tencent.qq"
        "com.tencent.WeChat" "com.qq.weixin"
        "com.qq.QQmusic" "com.tencent.QQmusic"
        "com.baidu.NetDisk" "com.baidu.pan"
        "com.microsoft.Edge"
        "com.google.Chrome" "org.chromium.Chromium"
        "org.fcitx.Fcitx5" "org.fcitx.Fcitx5.Addon.ChineseAddons"
    )

    _remove_shortcut() {
        local app_id="$1"
        local desktop_dir="$HOME/Desktop"
        [ -d "$desktop_dir" ] || return
        for f in "$desktop_dir"/*.desktop; do
            local base=$(basename "$f")
            if [ "$base" = "${app_id}.desktop" ] || [[ "$base" == *"${app_id//./_}"* ]]; then
                rm -f "$f" 2>/dev/null && echo "已删除桌面快捷方式 $base"
            fi
        done
    }

    while true; do
        local installed_apps=()
        while IFS=$'\t' read -r app_id app_name; do
            local skip=0
            for exclude in "${exclude_ids[@]}"; do
                if [[ "$app_id" == "$exclude" ]]; then
                    skip=1
                    break
                fi
            done
            if [ $skip -eq 0 ]; then
                installed_apps+=("$app_id|$app_name")
            fi
        done < <(flatpak list --app --columns=application,name 2>/dev/null)

        if [ ${#installed_apps[@]} -eq 0 ]; then
            zenity --info --text="没有其他已安装的 Flatpak 应用可卸载。" --width=400
            break
        fi

        local list_data=()
        for entry in "${installed_apps[@]}"; do
            IFS='|' read -r app_id app_name <<< "$entry"
            list_data+=("FALSE" "$app_name ($app_id)")
        done

        local selections
        selections=$(zenity --list --checklist \
            --title="卸载其他 Flatpak 应用" \
            --text="请选择要卸载的应用（可多选）：" \
            --column="选择" --column="应用" \
            "${list_data[@]}" \
            --width=700 --height=400 \
            --multiple 2>/dev/null)

        if [ $? -ne 0 ] || [ -z "$selections" ]; then
            break
        fi

        IFS='|' read -r -a selected_names <<< "$selections"
        local selected_ids=()
        for selected in "${selected_names[@]}"; do
            for entry in "${installed_apps[@]}"; do
                IFS='|' read -r app_id app_name <<< "$entry"
                if [ "$app_name ($app_id)" = "$selected" ]; then
                    selected_ids+=("$app_id")
                    break
                fi
            done
        done

        [ ${#selected_ids[@]} -eq 0 ] && continue

        zenity --question \
            --text="确定要卸载选中的应用吗？\n共 ${#selected_ids[@]} 项。" \
            --ok-label="卸载" --cancel-label="取消" 2>/dev/null || continue

        local total=${#selected_ids[@]}
        local success=0
        local fail=0
        local failed_list=""
        local data_dirs=()

        local pipe="/tmp/zenity_pipe_$$"
        mkfifo "$pipe"
        zenity --progress --pulsate --no-cancel --auto-close \
            --title="卸载应用" --text="准备开始..." --width=500 < "$pipe" &
        local zenity_pid=$!
        exec 3> "$pipe"

        for i in "${!selected_ids[@]}"; do
            local app_id="${selected_ids[$i]}"
            local idx=$((i+1))

            echo "# 正在处理第 $idx/$total 个: $app_id (卸载中...)" >&3

            if flatpak uninstall "$app_id" -y &>/dev/null; then
                ((success++))
                _remove_shortcut "$app_id"
                local data_dir="$HOME/.var/app/$app_id"
                if [ -d "$data_dir" ]; then
                    data_dirs+=("$data_dir")
                fi
                echo "# 第 $idx/$total 个: $app_id 卸载成功" >&3
            else
                ((fail++))
                failed_list+=" $app_id"
                echo "# 第 $idx/$total 个: $app_id 卸载失败" >&3
            fi
            sleep 0.2
        done

        exec 3>&-
        wait $zenity_pid 2>/dev/null
        rm -f "$pipe"

        sleep 1.0

        local result_msg="卸载结果：\n成功: $success 个"
        if [ $fail -gt 0 ]; then
            result_msg+="\n失败: $fail 个\n失败的 ID:${failed_list}"
        fi

        if [ ${#data_dirs[@]} -gt 0 ]; then
            local question_msg="$result_msg\n\n以下应用的用户数据目录仍然存在："
            for d in "${data_dirs[@]}"; do
                question_msg+="\n  $d"
            done
            question_msg+="\n\n是否删除这些数据目录？"

            if zenity --question --text="$question_msg" --width=600 \
                --ok-label="删除数据" --cancel-label="保留" 2>/dev/null; then
                for d in "${data_dirs[@]}"; do
                    rm -rf "$d" && echo "已删除 $d"
                done
            else
                :
            fi
            continue
        else
            zenity --info --text="$result_msg" --width=400 2>/dev/null
            continue
        fi
    done
}

install_yellow_duck_software() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装小黄鸭软件 ════════════════${NC}"
    echo ""
    local LOSS_DIR="/home/deck/.local/share/Steam/steamapps/common/Lossless Scaling"
    if [[ -d "$LOSS_DIR" ]]; then
        echo -e "${CYAN}检测到已安装小黄鸭软件。${NC}"
        echo "   安装目录: $LOSS_DIR"
        echo ""
        read -p "是否要卸载已安装的小黄鸭软件？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo "开始卸载小黄鸭软件..."
            if sudo rm -rf "$LOSS_DIR"; then
                echo -e "${GREEN}✅ 小黄鸭软件已成功卸载。${NC}"
                echo "如需重新安装，请再次运行此功能。"
            else
                echo -e "${RED}❌ 卸载失败，请检查权限。${NC}"
            fi
            return
        else
            echo "取消操作。"
            return
        fi
    fi
    echo -e "${CYAN}未检测到小黄鸭软件，开始从 Gitee 克隆并安装...${NC}"
    local CLONE_DIR="$HOME/lossless-scaling-repo"
    rm -rf "$CLONE_DIR"
    git clone --depth=1 https://gitee.com/Zhucy2100/lossless-scaling.git "$CLONE_DIR"
    if [ $? -ne 0 ]; then
        echo -e "${RED}克隆失败，请检查网络。${NC}"
        return
    fi
    cd "$CLONE_DIR" || return
    echo "合并分卷文件并解压..."
    cat "Lossless Scaling.zip".* > Lossless-Scaling-Combined.zip
    unzip -o Lossless-Scaling-Combined.zip -d "/home/deck/.local/share/Steam/steamapps/common/"
    if [ $? -ne 0 ]; then
        echo -e "${RED}解压失败。${NC}"
        cd
        rm -rf "$CLONE_DIR"
        return
    fi
    sudo chown -R deck:deck "/home/deck/.local/share/Steam/steamapps/common/Lossless Scaling"
    rm -rf "$CLONE_DIR"
    echo -e "${GREEN}✅ 小黄鸭软件安装完成！${NC}"
}

if [ -n "$1" ] && declare -f "$1" > /dev/null; then
    "$@"
else
    echo "此脚本为内嵌库，请通过参数调用具体功能。"
fi
'''

# ============================================================================
# Python GUI 部分
# ============================================================================
def create_temp_script(extra_content=''):
    fd, path = tempfile.mkstemp(suffix='.sh')
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(BASH_SCRIPT)
        if extra_content:
            f.write('\n' + extra_content + '\n')
    os.chmod(path, 0o755)
    atexit.register(lambda: os.path.exists(path) and os.unlink(path))
    return path

class TaskWindow(Gtk.Window):
    def __init__(self, parent, func_key, display_name):
        super().__init__(title=f"执行任务: {display_name}")
        self.set_default_size(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.terminal = None
        self.completed = False
        self.temp_script = None
        self._force_closing = False
        self.use_external_terminal = not VTE_AVAILABLE
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)
        if self.use_external_terminal:
            label = Gtk.Label(label="任务已在外部终端中运行，请查看弹出的终端窗口。")
            label.set_margin_top(20)
            label.set_margin_bottom(20)
            vbox.pack_start(label, True, True, 0)
            self.action_btn = Gtk.Button(label="关闭")
            self.action_btn.connect("clicked", lambda btn: self.destroy())
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_margin_bottom(5)
            button_box.pack_start(Gtk.Label(), True, True, 0)
            button_box.pack_start(self.action_btn, False, False, 0)
            vbox.pack_start(button_box, False, False, 0)
            self.show_all()
            self.run_external(func_key)
        else:
            self.terminal = Vte.Terminal()
            self.terminal.set_vexpand(True)
            self.terminal.set_hexpand(True)
            self.terminal.set_scrollback_lines(10000)
            vbox.pack_start(self.terminal, True, True, 0)
            button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
            button_box.set_margin_top(5)
            button_box.set_margin_bottom(5)
            button_box.set_margin_start(10)
            button_box.set_margin_end(10)
            button_box.pack_start(Gtk.Label(), True, True, 0)
            self.action_btn = Gtk.Button(label="取消")
            self.action_btn.connect("clicked", self.on_action_button_clicked)
            button_box.pack_start(self.action_btn, False, False, 0)
            vbox.pack_start(button_box, False, False, 0)
            self.temp_script = create_temp_script()
            self.connect("destroy", self.on_window_destroy)
            self.start_command(func_key)
            self.show_all()

    def run_external(self, func_key):
        tmp_path = create_temp_script()
        cmd = [
            "konsole",
            "-e",
            "bash",
            "-c",
            f"bash {tmp_path} {func_key}; read -p '按回车键关闭...' -n1"
        ]
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

    def start_command(self, func_key):
        self.terminal.spawn_sync(
            Vte.PtyFlags.DEFAULT,
            os.path.expanduser("~"),
            ["/bin/bash"],
            None,
            GLib.SpawnFlags.DEFAULT,
            None,
            None,
            None
        )
        cmd = f"bash {self.temp_script} {func_key}; exit 2>/dev/null\n"
        self.terminal.feed_child(cmd.encode('utf-8'))
        self.terminal.connect("child-exited", self.on_child_exited)

    def on_child_exited(self, terminal, status):
        GLib.idle_add(self.set_completed)

    def set_completed(self):
        self.completed = True
        self.action_btn.set_sensitive(True)
        self.action_btn.set_label("完成")

    def on_action_button_clicked(self, button):
        if self.completed:
            self.destroy()
            return
        self.terminal.feed_child(b'\x03')
        self.action_btn.set_sensitive(False)
        self.action_btn.set_label("正在取消...")
        GLib.timeout_add(2000, self.force_kill)

    def force_kill(self):
        if not self.completed:
            self._force_closing = True
            self.terminal.feed_child(b'\x1a')
            self.destroy()
        return False

    def on_window_destroy(self, widget):
        if self._force_closing:
            return
        if self.terminal and not self.completed:
            self.terminal.feed_child(b'\x03')
            GLib.timeout_add(500, self._force_close)

    def _force_close(self):
        self._force_closing = True
        self.destroy()
        return False

# ============================================================================
# 主窗口
# ============================================================================

class MainWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="Steam Deck 工具箱")
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(950, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.system_type = self.detect_system_type()
        self.task_window = None

        self.icon_map = {
            "支持和维护": "pushpin.png",
            "更新日志": "clipboard_twemoji.png",
            "系统优化": "hammer_wrench.png",
            "软件安装": "package.png",
            "网络工具": "globe.png",
            "插件相关": "game_controller.png",
            "引导管理": "refresh.png",
            "更新和卸载软件": "inbox.png",
            "其他": "trash.png"
        }

        self.category_icons = {}

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.set_vexpand(True)
        main_vbox.pack_start(hbox, True, True, 0)

        self.list_store = Gtk.ListStore(GdkPixbuf.Pixbuf, str)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        icon_dir = os.path.join(script_dir, "emoji_icons")

        categories = [
            "支持和维护",
            "更新日志",
            "系统优化",
            "软件安装",
            "网络工具",
            "插件相关",
            "引导管理",
            "更新和卸载软件",
            "其他"
        ]

        for cat in categories:
            pixbuf = None
            icon_file = self.icon_map.get(cat)
            if icon_file:
                icon_path = os.path.join(icon_dir, icon_file)
                if os.path.exists(icon_path):
                    try:
                        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_size(icon_path, 24, 24)
                    except Exception as e:
                        print(f"加载图标失败 {icon_path}: {e}")
            self.list_store.append([pixbuf, cat])
            self.category_icons[cat] = pixbuf

        self.cat_view = Gtk.TreeView(model=self.list_store)

        col = Gtk.TreeViewColumn()
        col.set_title("")
        col.set_spacing(6)

        renderer_icon = Gtk.CellRendererPixbuf()
        col.pack_start(renderer_icon, False)
        col.add_attribute(renderer_icon, "pixbuf", 0)

        renderer_text = Gtk.CellRendererText()
        col.pack_start(renderer_text, True)
        col.add_attribute(renderer_text, "text", 1)

        self.cat_view.append_column(col)
        self.cat_view.set_activate_on_single_click(True)
        self.cat_view.connect("row-activated", self.on_category_activated)

        scrolled_left = Gtk.ScrolledWindow()
        scrolled_left.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_left.set_vexpand(True)
        scrolled_left.set_valign(Gtk.Align.FILL)
        scrolled_left.add(self.cat_view)
        scrolled_left.set_size_request(250, -1)
        hbox.pack_start(scrolled_left, False, True, 0)

        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_vexpand(True)
        self.stack.set_valign(Gtk.Align.FILL)
        hbox.pack_start(self.stack, True, True, 0)

        about_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        about_box.set_margin_top(20)
        about_box.set_margin_bottom(20)
        about_box.set_margin_start(20)
        about_box.set_margin_end(20)
        about_title = Gtk.Label()
        about_title.set_markup("<big><b>关于本工具</b></big>")
        about_box.pack_start(about_title, False, False, 0)
        about_textview = Gtk.TextView()
        about_textview.set_editable(False)
        about_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        about_text = f"""
steamdeck工具箱 v{VERSION}
制作人：薯条 & DeepSeek
发布日期：2026年1月1日

工具箱介绍：
这是一个专为 Steam Deck 设计的工具箱，集成了系统优化、软件安装、
网络工具等多种功能，方便用户快速配置和优化设备。
感谢DeepSeek提供的大量技术支持

使用说明：
1. 点击左侧分类，右侧显示功能列表
2. 点击功能将弹出独立任务窗口
3. gitee网址 https://gitee.com/Zhucy2100/steamdeck_toolbox
"""
        about_textview.get_buffer().set_text(about_text)
        scrolled_about = Gtk.ScrolledWindow()
        scrolled_about.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_about.set_vexpand(True)
        scrolled_about.add(about_textview)
        about_box.pack_start(scrolled_about, True, True, 0)
        self.stack.add_named(about_box, "about")

        changelog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        changelog_box.set_margin_top(20)
        changelog_box.set_margin_bottom(20)
        changelog_box.set_margin_start(20)
        changelog_box.set_margin_end(20)

        self.changelog_textview = Gtk.TextView()
        self.changelog_textview.set_editable(False)
        self.changelog_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.changelog_textview.set_cursor_visible(False)

        css_provider = Gtk.CssProvider()
        css_provider.load_from_data(b'textview { font: 10pt Monospace; }')
        style_context = self.changelog_textview.get_style_context()
        style_context.add_provider(css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        scrolled_changelog = Gtk.ScrolledWindow()
        scrolled_changelog.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_changelog.set_vexpand(True)
        scrolled_changelog.add(self.changelog_textview)
        changelog_box.pack_start(scrolled_changelog, True, True, 0)

        self.stack.add_named(changelog_box, "changelog")

        func_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        func_page.set_margin_top(20)
        func_page.set_margin_bottom(20)
        func_page.set_margin_start(20)
        func_page.set_margin_end(20)
        func_page.set_vexpand(True)
        func_page.set_valign(Gtk.Align.FILL)

        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_box.set_halign(Gtk.Align.START)
        self.title_icon = Gtk.Image()
        self.title_icon.set_visible(False)
        title_box.pack_start(self.title_icon, False, False, 0)

        self.category_title = Gtk.Label()
        self.category_title.set_markup("<big><b>系统优化</b></big>")
        self.category_title.set_visible(False)
        title_box.pack_start(self.category_title, False, False, 0)

        func_page.pack_start(title_box, False, False, 0)

        self.func_store = Gtk.TreeStore(str)
        self.func_view = Gtk.TreeView(model=self.func_store)

        func_col = Gtk.TreeViewColumn()
        renderer_func = Gtk.CellRendererText()
        func_col.pack_start(renderer_func, True)
        func_col.add_attribute(renderer_func, "text", 0)
        self.func_view.append_column(func_col)
        self.func_view.set_headers_visible(False)
        self.func_view.set_activate_on_single_click(True)
        self.func_view.connect("row-activated", self.on_func_row_activated)
        self.func_view.set_expander_column(func_col)

        scrolled_func = Gtk.ScrolledWindow()
        scrolled_func.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_func.set_vexpand(True)
        scrolled_func.set_valign(Gtk.Align.FILL)
        scrolled_func.add(self.func_view)
        func_page.pack_start(scrolled_func, True, True, 0)
        self.stack.add_named(func_page, "func")

        selection = self.cat_view.get_selection()
        first_path = Gtk.TreePath.new_first()
        selection.select_path(first_path)
        self.on_category_activated(self.cat_view, first_path, None)

        bottom_bar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        bottom_bar.set_margin_top(5)
        bottom_bar.set_margin_bottom(5)
        bottom_bar.set_margin_start(10)
        bottom_bar.set_margin_end(10)
        help_btn = Gtk.Button(label="帮助")
        help_btn.connect("clicked", self.on_help_clicked)
        bottom_bar.pack_start(help_btn, False, False, 0)
        bottom_bar.pack_start(Gtk.Label(), True, True, 0)
        quit_btn = Gtk.Button(label="退出")
        quit_btn.connect("clicked", self.on_quit_clicked)
        bottom_bar.pack_start(quit_btn, False, False, 0)
        main_vbox.pack_start(bottom_bar, False, False, 0)

        self.func_map = {
            "安装国内源": "install_chinese_source",
            "调整虚拟内存": "adjust_swap",
            "修复磁盘写入错误": "fix_disk_write_error",
            "清理hosts缓存": "clear_hosts_cache",
            "校准摇杆": "calibrate_joystick_stick",
            "校准扳机": "calibrate_joystick_trigger",
            "Steam缓存管理": "steamdeck_cache_manager",
            "修复引导": "fix_boot",
            "修复互通盘": "fix_shared_disk",
            "AnyDesk": "install_anydesk",
            "ToDesk": "install_todesk",
            "AskLink远程": "install_asklink",
            "WPS Office": "install_wps_office",
            "QQ": "install_qq",
            "微信": "install_wechat",
            "QQ音乐": "install_qqmusic",
            "百度网盘": "install_baidunetdisk",
            "Edge浏览器": "install_edge",
            "Google浏览器": "install_chrome",
            "UU加速器插件": "install_uu_accelerator",
            "迅游加速器插件": "install_xunyou_accelerator",
            "奇游联机宝加速插件": "install_qiyou_accelerator",
            "安装": "watt_toolkit_install",
            "卸载": "watt_toolkit_uninstall",
            "安装插件商店": "install_plugin_store",
            "卸载插件商店": "uninstall_plugin_store",
            "安装/更新 ToMoon": "install_tomoon_install",
            "卸载 ToMoon": "install_tomoon_uninstall",
            "安装/更新 LSFG-VK": "install_decky_lsfg_vk_install",
            "卸载 LSFG-VK": "install_decky_lsfg_vk_uninstall",
            "安装/更新 Framegen": "install_decky_framegen_install",
            "卸载 Framegen": "install_decky_framegen_uninstall",
            "安装/重装 Clover": "clover_install_or_reinstall",
            "更新已安装应用": "update_installed_apps",
            "卸载 WPS Office": "uninstall_wps_office",
            "卸载 QQ": "uninstall_qq",
            "卸载微信": "uninstall_wechat",
            "卸载 QQ音乐": "uninstall_qqmusic",
            "卸载百度网盘": "uninstall_baidunetdisk",
            "卸载 Edge浏览器": "uninstall_edge",
            "卸载 Google浏览器": "uninstall_chrome",
            "卸载 AnyDesk": "uninstall_anydesk",
            "Fcitx 5": "install_fcitx5",
            "卸载Fcitx 5": "uninstall_fcitx5",
            "卸载其他已安装应用": "uninstall_other_flatpak_apps",
            "小黄鸭软件": "install_yellow_duck_software",
            "安装/更新 Freedeck": "install_freedeck_install",
            "卸载 Freedeck": "install_freedeck_uninstall",
            "GE-Proton 管理": "ge_proton_manager"
        }

        self.category_tree = {
            "支持和维护": [],
            "系统优化": [
                "安装国内源",
                "调整虚拟内存",
                "修复磁盘写入错误",
                "清理hosts缓存",
                ("校准设备", ["校准摇杆", "校准扳机"]),
                "Steam缓存管理",
                "GE-Proton 管理"
            ],
            "软件安装": [
                "AnyDesk",
                "ToDesk",
                "AskLink远程",
                "WPS Office",
                "QQ",
                "微信",
                "QQ音乐",
                "百度网盘",
                "Edge浏览器",
                "Google浏览器",
                "Fcitx 5"
            ],
            "网络工具": [
                "UU加速器插件",
                "迅游加速器插件",
                "奇游联机宝加速插件",
                ("Watt Toolkit (Steam++)", ["安装", "卸载"])
            ],
            "插件相关": [
                ("安装/卸载插件商店", ["安装插件商店", "卸载插件商店"]),
                ("ToMoon 插件", ["安装/更新 ToMoon", "卸载 ToMoon"]),
                ("Freedeck 插件", ["安装/更新 Freedeck", "卸载 Freedeck"]),
                ("LSFG-VK插件", ["安装/更新 LSFG-VK", "卸载 LSFG-VK"]),
                ("Framegen插件", ["安装/更新 Framegen", "卸载 Framegen"])
            ],
            "引导管理": [
                "安装/重装 Clover"
            ],
            "更新和卸载软件": [
                "更新已安装应用",
                ("卸载已安装应用", ["卸载 WPS Office", "卸载 QQ", "卸载微信", "卸载 QQ音乐", "卸载百度网盘", "卸载 Edge浏览器", "卸载 Google浏览器", "卸载 AnyDesk","卸载Fcitx 5", "卸载其他已安装应用"])
            ],
            "其他": [
                "小黄鸭软件"
            ]
        }

    def detect_system_type(self):
        try:
            result = subprocess.run(["efibootmgr"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                if re.search(r'(?i)windows', result.stdout) or re.search(r'(?i)clover', result.stdout):
                    return "双系统"
        except:
            pass
        return "单系统"

    def on_category_activated(self, treeview, path, column):
        model = treeview.get_model()
        iter_ = model.get_iter(path)
        category = model.get_value(iter_, 1)  # 文本在第二列
        if category == "支持和维护":
            self.stack.set_visible_child_name("about")
            self.title_icon.set_visible(False)
            self.category_title.set_visible(False)
            return

        if category == "更新日志":
            self.stack.set_visible_child_name("changelog")
            icon_pixbuf = self.category_icons.get(category)
            if icon_pixbuf:
                self.title_icon.set_from_pixbuf(icon_pixbuf)
                self.title_icon.set_visible(True)
            else:
                self.title_icon.set_visible(False)
            self.category_title.set_markup(f"<big><b>{category}</b></big>")
            self.category_title.set_visible(True)
            self.display_changelog()
            return

        self.stack.set_visible_child_name("func")

        icon_pixbuf = self.category_icons.get(category)
        if icon_pixbuf:
            self.title_icon.set_from_pixbuf(icon_pixbuf)
            self.title_icon.set_visible(True)
        else:
            self.title_icon.set_visible(False)

        if category == "系统优化":
            title_text = f"<big><b>{category} [{self.system_type}]</b></big>"
        else:
            title_text = f"<big><b>{category}</b></big>"
        self.category_title.set_markup(title_text)
        self.category_title.set_visible(True)

        self.func_store.clear()
        items = self.category_tree.get(category, [])
        if category == "系统优化" and self.system_type == "双系统":
            items = items + ["修复引导", "修复互通盘"]

        for item in items:
            if isinstance(item, tuple):
                parent_name, children = item
                parent_iter = self.func_store.append(None, [parent_name])
                for child in children:
                    self.func_store.append(parent_iter, [child])
            else:
                self.func_store.append(None, [item])
        self.func_view.show_all()

    def display_changelog(self):
        changelog_content = """2026-08-01（v1.6.3包含 v1.6.2 的调整） 完善了卸载已安装应用功能的删除快捷方式的步骤，并增加了询问是否删除应用数据的步骤
2026-07-31（v1.6.1） 增加了GE-Proton 管理的功能，可以安装/卸载GE兼容层
2026-07-30（v1.6.0包含 v1.5.7-v1.5.9 的调整） 新增了安装Freedeck插件的功能，并修复了一些bug和优化完善了一些功能
2026-07-29（v1.5.6包含 v1.5.2-v1.5.5 的调整） 增加了安装Fcitx 5的功能并继续修复了一些bug,并调整了部分功能的逻辑
2026-07-27（v1.5.1包含 v1.5.0 的调整） 修复了一些bug,并优化完善了一些功能
2026-07-26（v1.4.9） 增加了安装Asklink远程的功能
2026-07-25（v1.4.8包含 v1.3.9-v1.4.7 的调整）将文字形式停止更新，替换为图文形式，操作更加便捷，并对功能进行了修改和优化完善
删除了设置管理员密码的功能，增加了安装奇游联机宝加速插件的功能
2026-07-18（v1.3.8包含 v1.3.7 的调整） 替换steamcommunity 302功能为安装Watt Toolkit (Steam++)，增加实用性
调整了安装插件商店以及安装LSFG-VK插件和Framegen插件功能的部分逻辑，将校准摇杆更改为校准设备，增加了校准扳机
2026-07-09（v1.3.6） 修改了修复互通盘功能的实现逻辑，更具有通用性
2026-07-08（v1.3.5包含 v1.3.4 的调整） 删除了"远程无法连接点我"功能，调整从 GitHub 安装的功能的镜像顺序
2026-06-30（v1.3.2） 修复了安装AnyDesk功能的bug
2026-06-28（v1.3.1） 修复了调整虚拟内存大小功能的bug
2026-06-27（v1.3.0） 增加"远程无法连接点我"功能
调整安装 AnyDesk 功能的安装逻辑，改为从官网安装
2026-06-03（v1.2.7） 增加安装/重装 Clover 引导功能，并进行多项完善
2026-06-02（v1.2.6） 调整从 GitHub 安装的功能的安装逻辑，支持预发布版本和正式版选择
2026-05-31（v1.2.4，包含 v1.1.9、v1.2.0、v1.2.1 的调整） 增加安装 LSFG‑VK 插件和 Framegen 插件功能（从 GitHub 安装，并使用镜像下载）
调整插件商店功能的安装步骤，改用国内镜像加快下载速度，并增加镜像下载失败后的自动重试
调整 Steam Deck 缓存管理器功能的部分参数
2026-05-30（v1.1.8） 调整自动更新的逻辑
2026-05-28（v1.1.8，包含 v1.1.7） 更改插件商店功能，改为从 GitHub 安装
更新工具箱打开后自动更新的步骤
2026-03-17（v1.1.2） 由于宝葫芦停止维护，删除"安装＆卸载宝葫芦"功能
2026-03-05（v1.1.1） 更改安装 ToMoon 功能的实现逻辑，改为从 Gitee 克隆下载安装
2026-03-02（v1.1.0） 更改安装插件商店功能的实现逻辑，改为从 Gitee 克隆下载安装
2026-01-21（v1.0.9） 新增安装 Steam 社区 302 功能
2026-01-16（v1.0.8） 完善调整虚拟内存大小功能的文本展示
2026-01-11（v1.0.7） 完善调整虚拟内存大小功能
最初发布在github，没做详细的统计，发布日期为2026-01-01"""
        self.changelog_textview.get_buffer().set_text(changelog_content)

    def on_func_row_activated(self, treeview, path, column):
        model = treeview.get_model()
        iter_ = model.get_iter(path)
        func_name = model.get_value(iter_, 0)
        if not func_name:
            return

        if model.iter_has_child(iter_):
            if treeview.row_expanded(path):
                treeview.collapse_row(path)
            else:
                treeview.expand_row(path, False)
            return

        if func_name == "UU加速器插件":
            func_key = self.func_map.get(func_name)
            if func_key:
                self.run_external_terminal(func_key)
            return

        if func_name == "Steam缓存管理":
            self.run_cache_manager_gui()
            return

        if func_name == "GE-Proton 管理":
            self.run_ge_proton_manager_gui()
            return

        if func_name == "卸载其他已安装应用":
            self.run_uninstall_other_apps_gui()
            return

        func_key = self.func_map.get(func_name)
        if not func_key:
            return
        if self.task_window:
            self.task_window.destroy()
        self.task_window = TaskWindow(self, func_key, func_name)

    def on_help_clicked(self, button):
        help_dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Steam Deck 工具箱"
        )
        help_dialog.format_secondary_text(
            "本工具集成了系统优化、软件安装、网络工具等功能。\n"
            "点击左侧分类，右侧显示功能列表。\n"
            "小破站关注up主 AlanWake2100  可以来催更哦~"
        )
        help_dialog.run()
        help_dialog.destroy()

    def _run_standalone_script(self, func_key):
        tmp_path = create_temp_script()
        subprocess.Popen(
            [tmp_path, func_key],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

    def run_cache_manager_gui(self):
        self._run_standalone_script("steamdeck_cache_manager")

    def run_ge_proton_manager_gui(self):
        self._run_standalone_script("ge_proton_manager")

    def run_uninstall_other_apps_gui(self):
        self._run_standalone_script("uninstall_other_flatpak_apps")

    def on_quit_clicked(self, button):
        self.destroy()

    def run_external_terminal(self, func_key):
        tmp_path = create_temp_script()
        cmd = [
            "konsole",
            "-e",
            "bash",
            "-c",
            f"bash {tmp_path} {func_key}; read -p '按回车键关闭...' -n1"
        ]
        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

# ============================================================================
# 启动后处理
# ============================================================================

def ensure_desktop_shortcut():
    script_path = os.path.abspath(sys.argv[0])
    desktop_dir = os.path.expanduser("~/Desktop")
    desktop_file = os.path.join(desktop_dir, "Deck工具箱.desktop")
    if os.path.exists(desktop_file):
        return
    content = f"""[Desktop Entry]
Type=Application
Name=Deck工具箱
Exec=python3 "{script_path}"
Icon=input-gamepad-symbolic
Terminal=false
StartupNotify=true
Categories=Utility;
"""
    try:
        with open(desktop_file, 'w') as f:
            f.write(content)
        os.chmod(desktop_file, 0o755)
    except Exception as e:
        print(f"创建桌面快捷方式失败: {e}")

def ensure_vte_installed():
    if VTE_AVAILABLE:
        return
    dialog = Gtk.MessageDialog(
        None,
        Gtk.DialogFlags.MODAL,
        Gtk.MessageType.QUESTION,
        Gtk.ButtonsType.NONE,
        "未检测到 VTE 终端组件。\n是否立即安装？(需要 sudo 密码，安装后请手动重启程序)"
    )
    dialog.format_secondary_text(
        "点击“是”将自动解除只读模式并安装 vte3。"
    )
    dialog.add_button("是", Gtk.ResponseType.YES)
    dialog.add_button("否", Gtk.ResponseType.NO)
    dialog.set_icon_name("input-gamepad-symbolic")
    response = dialog.run()
    dialog.destroy()
    if response == Gtk.ResponseType.YES:
        subprocess.Popen(
            ["konsole", "-e", "bash", "-c",
             "sudo steamos-readonly disable 2>/dev/null; "
             "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF && "
             "sudo pacman -S --noconfirm vte3; "
             "echo '安装完成，请手动重启本程序。'; read -n1"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True
        )

def sync_emoji_icons():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_icon_dir = os.path.join(script_dir, "emoji_icons")
    required_icons = set([
        "pushpin.png", "clipboard_twemoji.png", "hammer_wrench.png",
        "package.png", "globe.png", "game_controller.png",
        "refresh.png", "inbox.png", "trash.png"
    ])
    base_raw_url = "https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/emoji_icons"
    os.makedirs(local_icon_dir, exist_ok=True)
    for icon_name in required_icons:
        local_path = os.path.join(local_icon_dir, icon_name)
        if os.path.isfile(local_path):
            continue
        try:
            url = f"{base_raw_url}/{icon_name}"
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as resp:
                with open(local_path, 'wb') as f:
                    f.write(resp.read())
        except Exception as e:
            print(f"下载图标 {icon_name} 失败: {e}")

def get_remote_version():
    try:
        req = urllib.request.Request(
            REPO_RAW_URL,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=VERSION_CHECK_TIMEOUT) as response:
            content = response.read().decode('utf-8')
            match = re.search(r'^VERSION\s*=\s*["\']([0-9.]+)["\']', content, re.MULTILINE)
            if match:
                return match.group(1)
            match = re.search(r'VERSION\s*=\s*["\']([0-9.]+)["\']', content)
            if match:
                return match.group(1)
            return None
    except Exception as e:
        print(f"检查更新失败: {e}")
        return None

def _perform_update_in_dialog(dialog, remote_version):
    def do_download():
        try:
            req = urllib.request.Request(
                REPO_RAW_URL,
                headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
            )
            with urllib.request.urlopen(req, timeout=30) as response:
                new_content = response.read().decode('utf-8')

            current_path = os.path.abspath(sys.argv[0])
            backup_path = current_path + ".bak"
            try:
                shutil.copy2(current_path, backup_path)
            except:
                pass

            with open(current_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            os.chmod(current_path, 0o755)

            GLib.idle_add(_update_dialog_success, dialog, remote_version)

        except Exception as e:
            GLib.idle_add(_update_dialog_error, dialog, str(e))

    threading.Thread(target=do_download, daemon=True).start()


def _update_dialog_success(dialog, remote_version):
    dialog.set_markup("<big><b>✅ 更新完成</b></big>")
    dialog.format_secondary_text(
        f"新版本 v{remote_version} 已下载。\n程序即将自动重启..."
    )
    def restart():
        dialog.destroy()
        import sys, subprocess
        subprocess.Popen([sys.executable, sys.argv[0]])
        Gtk.main_quit()
    GLib.timeout_add(500, restart)


def _update_dialog_error(dialog, error_msg):
    dialog.set_markup("<big><b>❌ 更新失败</b></big>")
    dialog.format_secondary_text(
        f"更新过程中发生错误：{error_msg}\n请手动从以下地址下载最新版本：\n{REPO_RAW_URL}"
    )
    for btn in dialog.get_action_area().get_children():
        btn.destroy()
    dialog.add_button("确定", Gtk.ResponseType.CLOSE)
    dialog.connect("response", lambda d, r: (dialog.destroy(), show_main_window()))
    dialog.show_all()

class UpdateCheckWindow(Gtk.Window):
    def __init__(self):
        super().__init__(title="检查更新")
        self.set_icon_name("input-gamepad-symbolic")
        self.set_default_size(400, 150)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_deletable(False)

        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        vbox.set_margin_top(20)
        vbox.set_margin_bottom(20)
        vbox.set_margin_start(20)
        vbox.set_margin_end(20)
        self.add(vbox)

        self.label = Gtk.Label(label="正在检查更新...")
        self.label.set_justify(Gtk.Justification.CENTER)
        vbox.pack_start(self.label, True, True, 0)

        self.button = None
        self.vbox = vbox
        self.show_all()
        GLib.timeout_add(200, self.perform_check)

    def perform_check(self):
        def check_thread():
            sync_emoji_icons()
            remote_version = get_remote_version()
            GLib.idle_add(self.on_check_done, remote_version)
        threading.Thread(target=check_thread, daemon=True).start()
        return False

    def on_check_done(self, remote_version):
        if remote_version is None:
            self.label.set_text("检查更新失败，请检查网络连接。")
            if self.button is None:
                self.button = Gtk.Button(label="进入主界面")
                self.button.connect("clicked", self.on_button_clicked)
                self.vbox.pack_start(self.button, False, False, 0)
            self.button.show()
            return

        if remote_version == VERSION:
            self.label.set_text(f"当前已是最新版本 (v{VERSION})")
            if self.button is not None:
                self.button.hide()
            GLib.timeout_add(300, self.auto_enter_main)
            return

        self.label.set_text(f"发现新版本 v{remote_version}\n当前版本: v{VERSION}")
        if self.button is not None:
            self.button.hide()
        self.show_update_prompt(remote_version)

    def auto_enter_main(self):
        self.destroy()
        show_main_window()
        return False

    def show_update_prompt(self, remote_version):
        self.destroy()

        dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.QUESTION,
            Gtk.ButtonsType.NONE,
            "发现新版本"
        )
        dialog.set_default_size(400, 150)
        dialog.set_markup(f"<big><b>发现新版本 v{remote_version}</b></big>")
        dialog.format_secondary_text(
            f"当前版本: v{VERSION}\n最新版本: v{remote_version}\n\n是否立即更新？"
        )
        dialog.add_button("是", Gtk.ResponseType.YES)
        dialog.add_button("否", Gtk.ResponseType.NO)
        dialog.set_icon_name("input-gamepad-symbolic")

        response = dialog.run()
        if response == Gtk.ResponseType.YES:
            dialog.set_markup("<big><b>正在更新...</b></big>")
            dialog.format_secondary_text("正在下载新版本，请稍候。")
            for btn in dialog.get_action_area().get_children():
                btn.destroy()
            dialog.show_all()
            _perform_update_in_dialog(dialog, remote_version)
        else:
            dialog.destroy()
            show_main_window()

    def on_button_clicked(self, button):
        self.destroy()
        show_main_window()

def show_main_window():
    window = MainWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    GLib.idle_add(ensure_desktop_shortcut)
    GLib.idle_add(ensure_vte_installed)

def main():
    update_win = UpdateCheckWindow()
    Gtk.main()

if __name__ == "__main__":
    main()
