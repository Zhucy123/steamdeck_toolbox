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

from gi.repository import Gtk, GLib, GdkPixbuf, Pango
import subprocess
import os
import sys
import re
import tempfile
import shutil
import threading
import urllib.request
import json          # [新增] 用于解析 API 响应

# ============================================================================
# 版本定义
# ============================================================================
VERSION = "1.4.6"
REPO_RAW_URL = "https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_gui.py"
REPO_URL = "https://gitee.com/Zhucy2100/steamdeck_toolbox"   # [新增] 仓库根地址
VERSION_CHECK_TIMEOUT = 10

# ============================================================================
# 内嵌完整的 Bash 脚本（完全保留用户原版，无改动）
# ============================================================================
BASH_SCRIPT = r'''#!/bin/bash
trap 'echo -e "\n${YELLOW}用户取消操作，关闭窗口。${NC}"; exit 0' INT TERM

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

VERSION="1.3.8"
REPO_URL="https://gitee.com/Zhucy2100/steamdeck_toolbox"

SYSTEM_TYPE=""

# ---------- 通用辅助 ----------
mk_temp_dir() {
    mkdir -p "$TEMP_DIR"
}

# ========== 系统优化 ==========
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
    echo -e "${GREEN}[4] 清理所有Swap配置并重新开始${NC}"
    echo "============================================"
    echo ""
    read -p "请输入选项 [1-4]: " main_choice < /dev/tty
    case $main_choice in
        1) apply_cryo_recommendation ;;
        2) adjust_swapfile ;;
        3) configure_zram ;;
        4) cleanup_swap ;;
        *) echo -e "${RED}无效选择${NC}" ;;
    esac
}

apply_cryo_recommendation() {
    mk_temp_dir
    echo ""
    echo -e "${YELLOW}═══════════════ 应用CryoByte33推荐方案 ═══════════════${NC}"
    echo ""
    read -p "是否继续？(输入 y 确认，其他键取消): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then echo "取消"; return; fi
    local swap_size_gb=16
    local block_count=$((swap_size_gb * 1024))
    echo "• 停用现有交换文件..."
    sudo swapoff /home/swapfile 2>/dev/null
    sudo swapoff -a 2>/dev/null
    sudo rm -f /home/swapfile
    echo "• 创建新文件..."
    sudo touch /home/swapfile
    sudo chattr +C /home/swapfile 2>/dev/null || echo -e "${YELLOW}  提示: chattr +C 可能失败，继续执行...${NC}"
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
    sudo sysctl --system --load=/etc/sysctl.d/99-cryo-optimizations.conf
    echo -e "${GREEN}✓ 内核参数优化完成${NC}"
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    echo -e "${GREEN}✓ ZRAM已停用${NC}"
    echo -e "${GREEN}✅ CryoByte33推荐方案已成功应用！${NC}"
}

adjust_swapfile() {
    mk_temp_dir
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
    read -p "请选择 [1-6]: " size_choice < /dev/tty
    case $size_choice in
        1) swap_size_gb=1;; 2) swap_size_gb=4;; 3) swap_size_gb=8;;
        4) swap_size_gb=16;; 5) swap_size_gb=32;;
        6) read -p "请输入大小 (单位GB，数字): " custom_size < /dev/tty
           if [[ "$custom_size" =~ ^[0-9]+$ ]]; then swap_size_gb=$custom_size; else echo "无效"; return; fi;;
        *) echo "无效"; return;;
    esac
    read -p "是否继续? (y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then return; fi
    sudo swapoff /home/swapfile 2>/dev/null
    sudo rm -f /home/swapfile
    sudo touch /home/swapfile
    sudo chattr +C /home/swapfile 2>/dev/null || echo -e "${YELLOW}⚠  chattr +C 失败，继续${NC}"
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
    echo ""
    echo -e "${YELLOW}配置ZRAM (内存压缩交换)${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "选择ZRAM大小 (基于16GB物理内存):"
    echo " 1. 2GB (保守)"
    echo " 2. 4GB (平衡推荐)"
    echo " 3. 8GB (积极)"
    read -p "请选择 [1-3]: " zram_choice < /dev/tty
    case $zram_choice in
        1) zram_size_gb=2;; 2) zram_size_gb=4;; 3) zram_size_gb=8;;
        *) echo "无效"; return;;
    esac
    sudo pacman -S --noconfirm systemd-zram-generator 2>/dev/null
    sudo tee /etc/systemd/zram-generator.conf > /dev/null <<EOF
[zram0]
zram-size = min(ram, ${zram_size_gb}G)
compression-algorithm = lz4
swap-priority = 100
EOF
    sudo systemctl daemon-reload
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl start systemd-zram-setup@zram0
    sudo systemctl enable systemd-zram-setup@zram0
    sleep 2
    if swapon --show | grep -q zram; then echo -e "${GREEN}✓ ZRAM已启用${NC}"; else echo -e "${YELLOW}⚠  ZRAM可能未启动${NC}"; fi
}

cleanup_swap() {
    mk_temp_dir
    echo ""
    echo -e "${YELLOW}清理所有Swap配置${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    read -p "确定要清理吗？(y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then return; fi
    sudo swapoff -a
    sudo rm -f /home/swapfile
    sudo sed -i '\\|/home/swapfile|d' /etc/fstab
    sudo systemctl stop systemd-zram-setup@zram0 2>/dev/null
    sudo systemctl disable systemd-zram-setup@zram0 2>/dev/null
    sudo rm -f /etc/systemd/zram-generator.conf 2>/dev/null
    sudo systemctl daemon-reload
    echo -e "${GREEN}✅ 已清理所有Swap配置${NC}"
}

fix_disk_write_error() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 修复磁盘写入错误 ════════════════${NC}"
    echo -e "${CYAN}正在修复磁盘写入错误...${NC}"
    echo ""
    echo "步骤1: 检查并禁用SteamOS只读模式"
    if steamos-readonly status 2>/dev/null | grep -q "enabled"; then
        sudo steamos-readonly disable 2>/dev/null
        if [ $? -eq 0 ]; then echo -e "${GREEN}✓ 已禁用只读模式${NC}"; else echo -e "${YELLOW}⚠️  禁用只读模式时出现警告${NC}"; fi
    else
        echo -e "${GREEN}✓ 系统已处于读写模式${NC}"
    fi
    echo ""
    echo "步骤2: 检查磁盘设备"
    DISK_DEVICE="/dev/nvme0n1p10"
    if [ -b "$DISK_DEVICE" ]; then
        echo -e "${GREEN}✓ 找到磁盘设备: $DISK_DEVICE${NC}"
    else
        echo -e "${RED}✗ 未找到磁盘设备: $DISK_DEVICE${NC}"
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
            fi
        fi
    else
        echo -e "${GREEN}✓ 分区未挂载，可直接进行修复${NC}"
    fi
    echo ""
    echo "步骤4: 修复NTFS文件系统"
    if mount | grep -q "$DISK_DEVICE"; then
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
        if sudo mount "$DISK_DEVICE" "$MOUNT_POINT" 2>/dev/null; then
            echo -e "${GREEN}✓ 分区重新挂载完成${NC}"
        else
            if sudo mount "$DISK_DEVICE" 2>/dev/null; then
                NEW_MOUNT_POINT=$(mount | grep "$DISK_DEVICE" | awk '{print $3}')
                echo -e "${GREEN}✓ 分区自动挂载完成: $NEW_MOUNT_POINT${NC}"
            else
                echo -e "${YELLOW}⚠️  分区重新挂载失败${NC}"
            fi
        fi
    else
        if sudo mount "$DISK_DEVICE" 2>/dev/null; then
            echo -e "${GREEN}✓ 分区挂载完成${NC}"
        else
            echo -e "${YELLOW}分区未挂载，可在需要时手动挂载${NC}"
        fi
    fi
    echo ""
    echo -e "${GREEN}✓ 磁盘写入错误修复流程已完成${NC}"
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

set_admin_password() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 设置管理员密码 ════════════════${NC}"
    echo -e "${CYAN}正在检查是否已设置管理员密码...${NC}"
    if sudo -n true 2>/dev/null; then
        echo -e "${GREEN}✓ 管理员密码已经设置${NC}"
    else
        echo -e "${YELLOW}检测到未设置管理员密码或密码已过期${NC}"
        echo ""
        echo "现在开始设置管理员密码..."
        sudo passwd
        if [ $? -eq 0 ]; then echo -e "${GREEN}✓ 管理员密码设置完成${NC}"; else echo -e "${RED}✗ 设置失败${NC}"; fi
    fi
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

# ========== Steam 缓存管理器（Zenity 图形界面，循环选择） ==========
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
        # 选择缓存类型
        local choice=$(zenity --list --radiolist \
            --title="Steam 缓存管理器" \
            --text="请选择要清理的缓存类型" \
            --column="选择" --column="类型" \
            FALSE "着色器缓存" \
            FALSE "兼容数据 (Proton前缀)" \
            --width=400 --height=200)

        if [ -z "$choice" ]; then
            break  # 用户取消，退出循环
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

        # 收集所有非空缓存目录
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

        # 构建 checklist 数据
        local list_data=()
        for entry in "${apps[@]}"; do
            IFS='|' read -r app_id game_name size dir <<< "$entry"
            list_data+=("FALSE" "$game_name (ID: $app_id)" "${size}MB")
        done

        # 显示多选列表
        local selections=$(zenity --list --checklist \
            --title="选择要删除的 $title" \
            --text="请勾选要删除的缓存项" \
            --column="选择" --column="游戏名" --column="大小" \
            "${list_data[@]}" \
            --width=600 --height=400 \
            --multiple)

        if [ -z "$selections" ]; then
            continue  # 用户取消选择，回到类型选择
        fi

        # 解析选中的游戏名
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

        # 确认删除
        zenity --question \
            --text="确定要删除选中的 $title 吗？\n共 ${#selected_dirs[@]} 项。" \
            --ok-label="删除" --cancel-label="取消"
        if [ $? -ne 0 ]; then
            continue
        fi

        # 执行删除
        local deleted=0 failed=0
        for d in "${selected_dirs[@]}"; do
            if rm -rf "$d"; then
                ((deleted++))
            else
                ((failed++))
            fi
        done

        zenity --info --text="删除完成！\n成功: $deleted 项\n失败: $failed 项"
        # 完成后自动回到类型选择
    done
}

# ========== 引导相关 ==========
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
}

fix_shared_disk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 自动挂载所有非系统分区 ════════════════${NC}"
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
    echo "步骤3: 扫描非系统分区..."
    local sys_mounts=("/" "/home" "/var" "/efi" "/esp" "/boot" "/boot/efi")
    local partitions=()
    while IFS= read -r line; do
        eval "$line"
        [[ "$TYPE" != "part" ]] && continue
        [[ -z "$FSTYPE" || "$FSTYPE" == "swap" ]] && continue
        [[ "$MOUNTPOINT" == /var/mnt/* ]] && continue
        for sysmp in "${sys_mounts[@]}"; do
            if [[ "$MOUNTPOINT" == "$sysmp" ]]; then continue 2; fi
        done
        partitions+=("DEVICE=/dev/$NAME LABEL=$LABEL FSTYPE=$FSTYPE MOUNTPOINT=$MOUNTPOINT UUID=$UUID SIZE=$SIZE")
    done < <(lsblk -o NAME,TYPE,LABEL,FSTYPE,MOUNTPOINT,UUID,SIZE -n -P)
    if [ ${#partitions[@]} -eq 0 ]; then
        echo -e "${YELLOW}⚠️  未检测到任何可挂载的非系统分区。${NC}"
        return
    fi
    echo -e "${CYAN}检测到以下分区：${NC}"
    for i in "${!partitions[@]}"; do
        eval "${partitions[$i]}"
        echo "  $((i+1)). $DEVICE 标签:${LABEL:-无} 类型:$FSTYPE 大小:$SIZE 挂载点:${MOUNTPOINT:-未挂载}"
    done
    echo ""
    echo "步骤4: 开始挂载并写入 fstab..."
    for partinfo in "${partitions[@]}"; do
        eval "$partinfo"
        echo -e "\n${CYAN}处理分区 $DEVICE${NC}"
        if [ -n "$MOUNTPOINT" ]; then
            mount_point="$MOUNTPOINT"
            echo "  当前已挂载到 $mount_point"
        else
            if [ -n "$LABEL" ]; then
                clean_label=$(echo "$LABEL" | sed 's/ /_/g')
                mount_point="/run/media/deck/$clean_label"
            else
                devname=$(basename "$DEVICE")
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
        if grep -q "UUID=$UUID" /etc/fstab 2>/dev/null; then
            echo "  fstab 中已存在该 UUID，跳过添加。"
        else
            if [[ "$FSTYPE" == "ntfs" ]]; then
                fstype_opt="ntfs-3g"
                mount_opts="rw,exec,uid=1000,gid=1000,windows_names,nofail"
            else
                fstype_opt="$FSTYPE"
                mount_opts="defaults,nofail"
            fi
            echo "UUID=$UUID $mount_point $fstype_opt $mount_opts 0 0" | sudo tee -a /etc/fstab > /dev/null
            echo "  已添加 fstab 条目。"
        fi
        if mountpoint -q "$mount_point"; then
            echo "  分区已挂载到 $mount_point"
        else
            if sudo mount -U "$UUID" "$mount_point" 2>/dev/null; then
                echo -e "${GREEN}  ✓ 挂载成功到 $mount_point${NC}"
            else
                echo -e "${RED}  ✗ 挂载失败，请检查 dmesg 输出。${NC}"
            fi
        fi
    done
    echo ""
    echo -e "${GREEN}════════════════ 全部完成 ════════════════${NC}"
}

# ========== 网络工具 ==========
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

# ---------- Steam++ 安装 ----------
install_watt_toolkit_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 Watt Toolkit (Steam++) ════════════════${NC}"
    echo ""

    local GITHUB_REPO="BeyondDimension/SteamTools"
    local INSTALL_DIR="/home/deck/Watt Toolkit"
    local DESKTOP_DIR="/home/deck/Desktop"
    local TEMP_DIR="/tmp/watt_toolkit_install"
    local MIRRORS=(
        "https://gh.ddlc.top/"
        "https://ghproxy.net/"
        "https://mirror.ghproxy.com/"
        "https://github.com/"
        "https://gitclone.com/"
        "https://gh.api.99988866.xyz/"
        "https://download.fastgit.org/"
        "https://hub.gitmirror.com/"
        "https://git.xfj0.xyz/"
    )
    local DOWNLOAD_TIMEOUT=120
    local MAX_RETRY_PER_MIRROR=1

    for cmd in curl sudo unzip tar python3; do
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

    local versions_info=$(echo "$releases_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for rel in data:
        tag = rel.get('tag_name', '')
        prerelease = rel.get('prerelease', False)
        if tag:
            print(f'{tag}|{str(prerelease).lower()}')
except:
    pass
")
    if [ -z "$versions_info" ]; then
        echo -e "${RED}错误: 无法解析版本信息。${NC}"
        return 1
    fi

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

    local installed_version=""
    if [ -d "$INSTALL_DIR" ] && [ -f "$INSTALL_DIR/.version" ]; then
        installed_version=$(cat "$INSTALL_DIR/.version")
        echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
    else
        echo "未检测到已安装版本。"
    fi

    local target_version=""
    if [ -n "$installed_version" ]; then
        if [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
            local stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
            local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
            if [ "$higher" = "$prerelease_num" ]; then
                echo -e "${GREEN}已安装最新正式版 ${installed_version}${NC}"
                echo -e "${YELLOW}发现更高版本的预发布版: ${latest_prerelease}${NC}"
                read -p "输入 y 升级到预发布版，按其他键保持当前版本: " upgrade < /dev/tty
                if [[ $upgrade =~ ^[Yy]$ ]]; then
                    target_version="$latest_prerelease"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                echo -e "${GREEN}已经是最新版本 (正式版 ${installed_version})${NC}"
                return 0
            fi
        elif [ -n "$latest_prerelease" ] && [ "$installed_version" = "$latest_prerelease" ] && [ -n "$latest_stable" ]; then
            local stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
            local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
            if [ "$higher" = "$prerelease_num" ]; then
                echo -e "${GREEN}已安装最新预发布版 ${installed_version}${NC}"
                echo -e "${YELLOW}当前正式版为: ${latest_stable}${NC}"
                read -p "输入 y 切换到正式版，按其他键保持当前版本: " switch < /dev/tty
                if [[ $switch =~ ^[Yy]$ ]]; then
                    target_version="$latest_stable"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                echo -e "${YELLOW}当前预发布版 ${installed_version} 低于正式版 ${latest_stable}，将升级到正式版。${NC}"
                target_version="$latest_stable"
            fi
        elif [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ] && [ -z "$latest_prerelease" ]; then
            echo -e "${GREEN}已经是最新版本 (正式版 ${installed_version})，无需更新。${NC}"
            return 0
        elif [ -n "$latest_prerelease" ] && [ "$installed_version" = "$latest_prerelease" ] && [ -z "$latest_stable" ]; then
            echo -e "${GREEN}已经是最新版本 (预发布版 ${installed_version})，无需更新。${NC}"
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
                return 1
            fi
        fi
    else
        if [ -n "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
            local stable_num=$(echo "$latest_stable" | sed 's/^v//')
            local prerelease_num=$(echo "$latest_prerelease" | sed 's/^v//')
            local higher=$(printf '%s\n' "$stable_num" "$prerelease_num" | sort -V | tail -1)
            if [ "$higher" = "$prerelease_num" ]; then
                echo "请选择要安装的版本："
                echo "1. 正式版 ${latest_stable}"
                echo "2. 预发布版 ${latest_prerelease}"
                read -p "请输入选择 [1-2] (默认正式版): " choice < /dev/tty
                case $choice in
                    2) target_version="$latest_prerelease" ;;
                    *) target_version="$latest_stable" ;;
                esac
            else
                target_version="$latest_stable"
            fi
        elif [ -n "$latest_stable" ]; then
            target_version="$latest_stable"
            echo "将安装正式版 ${target_version}"
        elif [ -n "$latest_prerelease" ]; then
            target_version="$latest_prerelease"
            echo -e "${YELLOW}注意: 当前只有预发布版本 ${target_version}${NC}"
        else
            echo -e "${RED}错误: 无法获取任何版本。${NC}"
            return 1
        fi
    fi

    if [ -z "$target_version" ]; then
        echo "未选择版本，操作取消。"
        return 0
    fi

    echo -e "${GREEN}将安装版本: ${target_version}${NC}"

    local download_url=""
    local asset_info=$(echo "$releases_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    target_tag = '$target_version'
    found = False
    for rel in data:
        if rel.get('tag_name') == target_tag:
            for asset in rel.get('assets', []):
                name = asset.get('name', '')
                if name.endswith('_linux_x64.tgz') and '_linux_x64.tgz' in name:
                    print(asset.get('browser_download_url', ''))
                    found = True
                    break
            break
    if not found:
        for rel in data:
            for asset in rel.get('assets', []):
                name = asset.get('name', '')
                if 'linux_x64.tgz' in name and 'source' not in name.lower():
                    print(asset.get('browser_download_url', ''))
                    found = True
                    break
            if found:
                break
except Exception as e:
    pass
")
    if [ -z "$asset_info" ]; then
        echo -e "${RED}错误: 无法获取 ${target_version} 的下载链接。${NC}"
        echo "请检查 GitHub 上该版本是否包含 linux_x64.tgz 文件。"
        return 1
    fi
    download_url="$asset_info"

    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"

    local filename="Steam++_${target_version}_linux_x64.tgz"
    local DOWNLOAD_SUCCESS=false

    for mirror in "${MIRRORS[@]}"; do
        local full_url="${mirror}${download_url}"
        echo -e "尝试从 ${mirror} 下载..."

        local retry_count=0
        while [[ $retry_count -le $MAX_RETRY_PER_MIRROR ]]; do
            if [[ $retry_count -gt 0 ]]; then
                echo -e "${YELLOW}重试下载 (第 ${retry_count} 次重试)...${NC}"
            fi

            curl -L --progress-bar --max-time "$DOWNLOAD_TIMEOUT" -o "$filename" "$full_url"
            local curl_exit=$?

            if [[ $curl_exit -eq 0 ]] && [[ -f "$filename" ]]; then
                local file_size=$(stat -c%s "$filename" 2>/dev/null || stat -f%z "$filename" 2>/dev/null)
                if [[ -n "$file_size" ]] && [[ "$file_size" -gt 1000000 ]]; then
                    echo -e "\n${GREEN}下载成功 (大小: $((file_size/1024/1024)) MB)${NC}"
                    DOWNLOAD_SUCCESS=true
                    break 2
                else
                    echo -e "\n${RED}下载文件无效 (${file_size} 字节)，尝试下一个镜像...${NC}"
                    rm -f "$filename"
                    break
                fi
            else
                echo -e "\n${RED}下载失败 (退出码: $curl_exit)${NC}"
                rm -f "$filename"
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
        return 1
    fi

    echo -e "${CYAN}正在解压到临时目录...${NC}"
    local temp_extract="$TEMP_DIR/extracted"
    mkdir -p "$temp_extract"
    if ! tar -xzf "$filename" -C "$temp_extract"; then
        echo -e "${RED}解压失败。${NC}"
        rm -rf "$TEMP_DIR"
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

    rm -rf "$TEMP_DIR"

    echo "$target_version" > "$INSTALL_DIR/.version"

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
    echo -e "${GREEN}✅ Watt Toolkit ${target_version} 安装完成！${NC}"
    echo -e "${GREEN}安装目录: ${INSTALL_DIR}${NC}"
    echo ""
    echo -e "${YELLOW}使用提示：${NC}"
    echo "如果加速报错，请按照下面步骤操作："
    echo "  网络加速 → 加速设置 → 安装证书"
    echo ""
    echo "请在桌面启动 Watt Toolkit。"
}

install_watt_toolkit_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Watt Toolkit ════════════════${NC}"
    local INSTALL_DIR="/home/deck/Watt Toolkit"
    local DESKTOP_DIR="/home/deck/Desktop"

    echo -e "${CYAN}正在卸载 Watt Toolkit...${NC}"
    echo ""

    if [ ! -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}未检测到已安装的 Watt Toolkit。${NC}"
        return 0
    fi

    echo "将删除以下目录: ${INSTALL_DIR}"
    echo "将删除桌面快捷方式: ${DESKTOP_DIR}/Watt_Toolkit.desktop"
    echo ""

    read -p "确定要卸载吗？(y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "卸载已取消。"
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

# ========== 插件相关 ==========
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

    local versions_info=$(echo "$releases_json" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    for rel in data:
        tag = rel.get('tag_name', '')
        prerelease = rel.get('prerelease', False)
        if tag:
            print(f'{tag}|{str(prerelease).lower()}')
except:
    pass
")
    if [ -z "$versions_info" ]; then
        echo -e "${RED}错误: 无法解析版本信息。${NC}"
        return 1
    fi

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

    local target_version=""
    if [ -n "$installed_version" ]; then
        if [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ]; then
            echo -e "${GREEN}已经是最新稳定版 ${installed_version}，无需更新。${NC}"
            if [ -n "$latest_prerelease" ]; then
                echo -e "${YELLOW}发现预发布版: ${latest_prerelease}${NC}"
                read -p "是否升级到预发布版？(y/N): " upgrade < /dev/tty
                if [[ $upgrade =~ ^[Yy]$ ]]; then
                    target_version="$latest_prerelease"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                return 0
            fi
        elif [ -n "$latest_prerelease" ] && [ "$installed_version" = "$latest_prerelease" ]; then
            echo -e "${GREEN}已安装最新预发布版 ${installed_version}${NC}"
            if [ -n "$latest_stable" ]; then
                echo -e "${YELLOW}发现正式版: ${latest_stable}${NC}"
                read -p "是否切换到正式版？(y/N): " switch < /dev/tty
                if [[ $switch =~ ^[Yy]$ ]]; then
                    target_version="$latest_stable"
                else
                    echo "保持当前版本。"
                    return 0
                fi
            else
                return 0
            fi
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
                return 1
            fi
        fi
    else
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
            echo -e "${RED}错误: 无法获取任何版本。${NC}"
            return 1
        fi
    fi

    if [ -z "$target_version" ]; then
        echo "未选择版本，操作取消。"
        return 0
    fi

    echo -e "${GREEN}将安装版本: ${target_version}${NC}"
    read -p "是否继续？(y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作已取消。"
        return 0
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

    DOWNLOAD_SUCCESS=false
    TMP_FILE="${PLUGIN_LOADER}.tmp"
    DOWNLOAD_PATH="https://github.com/SteamDeckHomebrew/decky-loader/releases/download/${target_version}/PluginLoader"

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
        return 1
    fi

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
    echo -e "${CYAN}正在卸载插件商店...${NC}"
    echo "警告：这将删除整个 /home/deck/homebrew 目录，包括所有插件。"
    echo ""
    read -p "确定要卸载插件商店吗？(y/N): " -n 1 -r < /dev/tty
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "卸载已取消。"
        return
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
    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
    local latest_version=$(curl -s "https://api.github.com/repos/YukiCoco/ToMoon/releases/latest" | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//; s/".*//')
    if [ -z "$latest_version" ]; then
        echo -e "${RED}错误: 无法获取版本信息。${NC}"
        return
    fi
    echo -e "${GREEN}最新版本: ${latest_version}${NC}"
    local TARGET_DIR="/home/deck/homebrew/plugins/tomoon"
    local installed_version=""
    if [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/package.json" ]; then
        installed_version=$(grep -o '"version": *"[^"]*"' "$TARGET_DIR/package.json" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$installed_version" ]; then
            installed_version="v${installed_version}"
            echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
            if [ "$installed_version" = "$latest_version" ]; then
                echo -e "${GREEN}已经是最新版本。${NC}"
                return
            else
                echo -e "${YELLOW}发现新版本，将覆盖安装。${NC}"
            fi
        else
            echo -e "${YELLOW}已安装但无法获取版本，将覆盖安装。${NC}"
        fi
    else
        echo "未检测到已安装版本。"
    fi
    read -p "是否继续安装/更新？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then echo "取消。"; return; fi
    local TEMP_DIR="/tmp/tomoon_install"
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return
    local zip_filename="tomoon-${latest_version}.zip"
    local download_path="https://github.com/YukiCoco/ToMoon/releases/download/${latest_version}/${zip_filename}"
    for mirror in "https://gh.ddlc.top/" "https://ghproxy.net/" "https://mirror.ghproxy.com/" "https://github.com/"; do
        full_url="${mirror}${download_path}"
        echo -e "尝试从 ${mirror} 下载..."
        curl -L --progress-bar --max-time 60 -o "$zip_filename" "$full_url"
        if [ -f "$zip_filename" ] && [ "$(stat -c%s "$zip_filename" 2>/dev/null || stat -f%z "$zip_filename" 2>/dev/null)" -gt 10000 ]; then
            echo -e "${GREEN}下载成功${NC}"
            break
        fi
        rm -f "$zip_filename"
    done
    if [ ! -f "$zip_filename" ]; then echo -e "${RED}下载失败${NC}"; return; fi
    unzip -q "$zip_filename"
    local extracted_dir
    extracted_dir="$(find "$TEMP_DIR" -maxdepth 2 -type f -name "tomoon" -exec dirname {} \; | head -1)"
    if [ -z "$extracted_dir" ]; then
        extracted_dir="$(find "$TEMP_DIR" -maxdepth 1 -type d -name "tomoon*" | head -1)"
    fi
    if [ -z "$extracted_dir" ]; then
        extracted_dir="$TEMP_DIR"
    fi
    sudo mkdir -p /home/deck/homebrew/plugins
    sudo rm -rf "$TARGET_DIR"
    sudo mv "$extracted_dir" "$TARGET_DIR"
    sudo chown -R deck:deck "$TARGET_DIR"
    echo -e "${GREEN}✅ ToMoon 插件 ${latest_version} 安装完成！${NC}"
}

install_tomoon_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 ToMoon 插件 ════════════════${NC}"
    sudo rm -rf /home/deck/homebrew/plugins/tomoon
    echo -e "${GREEN}卸载完成${NC}"
}

install_decky_lsfg_vk_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 LSFG-VK 插件 ════════════════${NC}"
    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
    local VERSION=$(curl -s "https://api.github.com/repos/xXJSONDeruloXx/decky-lsfg-vk/releases/latest" | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//; s/".*//')
    if [ -z "$VERSION" ]; then echo -e "${RED}版本获取失败${NC}"; return; fi
    echo -e "${GREEN}最新版本: ${VERSION}${NC}"
    local TARGET_DIR="/home/deck/homebrew/plugins/Decky-LSFG-VK"
    local installed_version=""
    if [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/package.json" ]; then
        installed_version=$(grep -o '"version": *"[^"]*"' "$TARGET_DIR/package.json" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$installed_version" ]; then
            installed_version="v${installed_version}"
            echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
            if [ "$installed_version" = "$VERSION" ]; then
                echo -e "${GREEN}已经是最新版本。${NC}"
                return
            fi
        fi
    else
        echo "未检测到已安装版本。"
    fi
    read -p "是否继续安装/更新？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then echo "取消。"; return; fi
    local TEMP_DIR="/tmp/lsfg_vk"
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return
    local URL="https://github.com/xXJSONDeruloXx/decky-lsfg-vk/releases/download/${VERSION}/Decky.LSFG-VK.zip"
    curl -L --progress-bar "$URL" -o plugin.zip
    unzip -q plugin.zip
    sudo mkdir -p /home/deck/homebrew/plugins
    sudo rm -rf "$TARGET_DIR"
    local extracted_dir="$(find . -maxdepth 1 -type d -name "*LSFG*" | head -1)"
    if [ -z "$extracted_dir" ]; then extracted_dir="."; fi
    sudo mv "$extracted_dir" "$TARGET_DIR"
    sudo chown -R deck:deck "$TARGET_DIR"
    echo -e "${GREEN}✅ LSFG-VK 插件 ${VERSION} 安装完成！${NC}"
}

install_decky_lsfg_vk_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 LSFG-VK 插件 ════════════════${NC}"
    sudo rm -rf /home/deck/homebrew/plugins/Decky-LSFG-VK
    echo -e "${GREEN}已卸载${NC}"
}

install_decky_framegen_install() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装/更新 Framegen 插件 ════════════════${NC}"
    echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
    local VERSION=$(curl -s "https://api.github.com/repos/xXJSONDeruloXx/Decky-Framegen/releases/latest" | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//; s/".*//')
    if [ -z "$VERSION" ]; then echo -e "${RED}版本获取失败${NC}"; return; fi
    echo -e "${GREEN}最新版本: ${VERSION}${NC}"
    local TARGET_DIR="/home/deck/homebrew/plugins/Decky-Framegen"
    local installed_version=""
    if [ -d "$TARGET_DIR" ] && [ -f "$TARGET_DIR/package.json" ]; then
        installed_version=$(grep -o '"version": *"[^"]*"' "$TARGET_DIR/package.json" | head -1 | sed 's/.*"version": *"//; s/".*//')
        if [ -n "$installed_version" ]; then
            installed_version="v${installed_version}"
            echo -e "${CYAN}当前已安装版本: ${installed_version}${NC}"
            if [ "$installed_version" = "$VERSION" ]; then
                echo -e "${GREEN}已经是最新版本。${NC}"
                return
            fi
        fi
    else
        echo "未检测到已安装版本。"
    fi
    read -p "是否继续安装/更新？(y/N): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then echo "取消。"; return; fi
    local TEMP_DIR="/tmp/framegen"
    rm -rf "$TEMP_DIR"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR" || return
    local URL="https://github.com/xXJSONDeruloXx/Decky-Framegen/releases/download/${VERSION}/Decky-Framegen.zip"
    curl -L --progress-bar "$URL" -o plugin.zip
    unzip -q plugin.zip
    sudo mkdir -p /home/deck/homebrew/plugins
    sudo rm -rf "$TARGET_DIR"
    local extracted_dir="$(find . -maxdepth 1 -type d -name "*Framegen*" | head -1)"
    if [ -z "$extracted_dir" ]; then extracted_dir="."; fi
    sudo mv "$extracted_dir" "$TARGET_DIR"
    sudo chown -R deck:deck "$TARGET_DIR"
    echo -e "${GREEN}✅ Framegen 插件 ${VERSION} 安装完成！${NC}"
}

install_decky_framegen_uninstall() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Framegen 插件 ════════════════${NC}"
    sudo rm -rf /home/deck/homebrew/plugins/Decky-Framegen
    echo -e "${GREEN}已卸载${NC}"
}

# ========== 引导管理 ==========
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
    if [ -d "$TARGET_DIR" ]; then
        echo -e "${YELLOW}目录 $TARGET_DIR 已存在，删除后重新克隆。${NC}"
        rm -rf "$TARGET_DIR"
    fi

    if ! script -q -c "git clone --progress --depth=1 '$REPO_URL' '$TARGET_DIR'" /dev/null; then
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
    # exit   # 已跳过退出
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
    "https://gh.ddlc.top/https://github.com"
    "https://ghproxy.net/https://github.com"
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

    echo -e "${YELLOW}建议重启设备以使引导生效。${NC}"
    echo ""
}

# ========== 软件安装 ==========
install_anydesk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装 AnyDesk ════════════════${NC}"
    echo "正在安装 AnyDesk（便携版）..."
    local ANYDESK_INSTALL_DIR="$HOME/.local/share/anydesk"
    mkdir -p "$ANYDESK_INSTALL_DIR"
    cd /tmp || return
    echo "获取最新版本..."
    local VERSION=$(curl -s https://anydesk.com.cn/zhs/downloads/linux | grep -oP 'v?\\d+\\.\\d+\\.\\d+' | head -1 | sed 's/^v//')
    if [ -z "$VERSION" ]; then echo "版本获取失败"; return; fi
    echo "版本: $VERSION"
    local URL="https://download.anydesk.com/linux/anydesk-${VERSION}-amd64.tar.gz"
    echo "下载中..."
    wget -q --show-progress "$URL" -O anydesk.tar.gz
    tar -xzf anydesk.tar.gz -C "$ANYDESK_INSTALL_DIR" --strip-components=1
    chmod +x "$ANYDESK_INSTALL_DIR/anydesk"
    mkdir -p "$HOME/.local/bin"
    ln -sf "$ANYDESK_INSTALL_DIR/anydesk" "$HOME/.local/bin/anydesk"
    cat > "$HOME/Desktop/AnyDesk.desktop" << EOF
[Desktop Entry]
Name=AnyDesk
Exec=$ANYDESK_INSTALL_DIR/anydesk
Icon=$ANYDESK_INSTALL_DIR/icons/hicolor/256x256/apps/anydesk.png
Type=Application
Categories=Network;RemoteAccess;
EOF
    chmod +x "$HOME/Desktop/AnyDesk.desktop"
    rm -f anydesk.tar.gz
    echo -e "${GREEN}✓ AnyDesk 安装完成！桌面快捷方式已创建。${NC}"
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

install_wps_office() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装WPS Office ════════════════${NC}"
    echo "正在通过 Flatpak 安装 WPS Office..."

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    local app_id=""
    local success=0

    if flatpak install flathub com.wps.Office -y 2>/dev/null; then
        app_id="com.wps.Office"
        success=1
    elif flatpak install flathub cn.wps.wps-office -y 2>/dev/null; then
        app_id="cn.wps.wps-office"
        success=1
    elif flatpak install flathub com.kingsoft.wps -y 2>/dev/null; then
        app_id="com.kingsoft.wps"
        success=1
    fi

    if [ $success -eq 1 ]; then
        echo -e "${GREEN}✓ WPS Office 安装成功${NC}"
        cat > "$HOME/Desktop/WPS Office.desktop" << EOF
[Desktop Entry]
Type=Application
Name=WPS Office
Exec=flatpak run ${app_id}
Icon=${app_id}
Terminal=false
Categories=Office;
EOF
        chmod +x "$HOME/Desktop/WPS Office.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ WPS Office 安装失败，请检查网络或手动安装。${NC}"
    fi
}

install_qq() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装QQ ════════════════${NC}"
    echo "正在通过 Flatpak 安装 QQ..."

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    local app_id=""
    local success=0

    if flatpak install flathub com.qq.QQ -y 2>/dev/null; then
        app_id="com.qq.QQ"
        success=1
    elif flatpak install flathub com.tencent.qq -y 2>/dev/null; then
        app_id="com.tencent.qq"
        success=1
    fi

    if [ $success -eq 1 ]; then
        echo -e "${GREEN}✓ QQ 安装成功${NC}"
        cat > "$HOME/Desktop/QQ.desktop" << EOF
[Desktop Entry]
Type=Application
Name=QQ
Exec=flatpak run ${app_id}
Icon=${app_id}
Terminal=false
Categories=Network;Chat;
EOF
        chmod +x "$HOME/Desktop/QQ.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ QQ 安装失败，请检查网络或手动安装。${NC}"
    fi
}

install_wechat() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装微信 ════════════════${NC}"
    echo "正在通过 Flatpak 安装微信..."

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    local app_id=""
    local success=0
    local error_msg=""

    # 尝试安装 com.tencent.WeChat
    echo "尝试安装 com.tencent.WeChat..."
    if flatpak install flathub com.tencent.WeChat -y 2>/tmp/wechat_error.log; then
        app_id="com.tencent.WeChat"
        success=1
    else
        error_msg=$(cat /tmp/wechat_error.log 2>/dev/null)
        if echo "$error_msg" | grep -q "Transferred a partial file"; then
            echo -e "${YELLOW}下载中断，尝试使用 com.qq.weixin...${NC}"
        elif echo "$error_msg" | grep -q "No remote refs found"; then
            echo -e "${YELLOW}com.tencent.WeChat 不存在，尝试使用 com.qq.weixin...${NC}"
        else
            echo -e "${YELLOW}com.tencent.WeChat 安装失败，尝试使用 com.qq.weixin...${NC}"
        fi
        rm -f /tmp/wechat_error.log
    fi

    if [ $success -eq 0 ]; then
        echo "尝试安装 com.qq.weixin..."
        if flatpak install flathub com.qq.weixin -y 2>/tmp/wechat_error2.log; then
            app_id="com.qq.weixin"
            success=1
        else
            error_msg=$(cat /tmp/wechat_error2.log 2>/dev/null)
            if echo "$error_msg" | grep -q "No remote refs found"; then
                echo -e "${YELLOW}com.qq.weixin 在 flathub 中不存在${NC}"
            else
                echo -e "${YELLOW}com.qq.weixin 安装失败${NC}"
            fi
            rm -f /tmp/wechat_error2.log
        fi
    fi

    if [ $success -eq 1 ]; then
        echo -e "${GREEN}✓ 微信 安装成功${NC}"
        cat > "$HOME/Desktop/微信.desktop" << EOF
[Desktop Entry]
Type=Application
Name=微信
Exec=flatpak run ${app_id}
Icon=${app_id}
Terminal=false
Categories=Network;Chat;
EOF
        chmod +x "$HOME/Desktop/微信.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ 微信 安装失败，请检查网络或手动安装。${NC}"
        echo -e "${YELLOW}提示：Flathub 上的微信可能已改名或下架。${NC}"
        echo -e "${YELLOW}建议尝试：从 https://flatpak.org 搜索 wechat 获取最新 ID。${NC}"
    fi
}

install_qqmusic() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装QQ音乐 ════════════════${NC}"
    echo "正在通过 Flatpak 安装 QQ音乐..."

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    local app_id=""
    local success=0

    if flatpak install flathub com.qq.QQmusic -y 2>/dev/null; then
        app_id="com.qq.QQmusic"
        success=1
    elif flatpak install flathub com.tencent.QQmusic -y 2>/dev/null; then
        app_id="com.tencent.QQmusic"
        success=1
    fi

    if [ $success -eq 1 ]; then
        echo -e "${GREEN}✓ QQ音乐 安装成功${NC}"
        cat > "$HOME/Desktop/QQ音乐.desktop" << EOF
[Desktop Entry]
Type=Application
Name=QQ音乐
Exec=flatpak run ${app_id}
Icon=${app_id}
Terminal=false
Categories=Audio;
EOF
        chmod +x "$HOME/Desktop/QQ音乐.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ QQ音乐 安装失败，请检查网络或手动安装。${NC}"
    fi
}

install_baidunetdisk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装百度网盘 ════════════════${NC}"
    echo "正在通过 Flatpak 安装百度网盘..."

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    local app_id=""
    local success=0

    if flatpak install flathub com.baidu.NetDisk -y 2>/dev/null; then
        app_id="com.baidu.NetDisk"
        success=1
    elif flatpak install flathub com.baidu.pan -y 2>/dev/null; then
        app_id="com.baidu.pan"
        success=1
    fi

    if [ $success -eq 1 ]; then
        echo -e "${GREEN}✓ 百度网盘 安装成功${NC}"
        cat > "$HOME/Desktop/百度网盘.desktop" << EOF
[Desktop Entry]
Type=Application
Name=百度网盘
Exec=flatpak run ${app_id}
Icon=${app_id}
Terminal=false
Categories=Network;FileTransfer;
EOF
        chmod +x "$HOME/Desktop/百度网盘.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ 百度网盘 安装失败，请检查网络或手动安装。${NC}"
    fi
}

install_edge() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装Edge浏览器 ════════════════${NC}"
    echo "正在通过 Flatpak 安装 Edge..."

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    if flatpak install flathub com.microsoft.Edge -y 2>/dev/null; then
        echo -e "${GREEN}✓ Edge 安装成功${NC}"
        cat > "$HOME/Desktop/Microsoft Edge.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Microsoft Edge
Exec=flatpak run com.microsoft.Edge
Icon=com.microsoft.Edge
Terminal=false
Categories=Network;WebBrowser;
EOF
        chmod +x "$HOME/Desktop/Microsoft Edge.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ Edge 安装失败，请检查网络或手动安装。${NC}"
    fi
}

install_chrome() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 安装Google浏览器 ════════════════${NC}"
    echo "正在通过 Flatpak 安装 Chrome..."

    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo

    if flatpak install flathub com.google.Chrome -y 2>/dev/null; then
        echo -e "${GREEN}✓ Chrome 安装成功${NC}"
        cat > "$HOME/Desktop/Google Chrome.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Google Chrome
Exec=flatpak run com.google.Chrome
Icon=com.google.Chrome
Terminal=false
Categories=Network;WebBrowser;
EOF
        chmod +x "$HOME/Desktop/Google Chrome.desktop"
        echo -e "${GREEN}✓ 桌面快捷方式已创建${NC}"
    else
        echo -e "${RED}✗ Chrome 安装失败，请检查网络或手动安装。${NC}"
    fi
}

# ========== 更新软件 ==========
update_installed_apps() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 更新全部应用 ════════════════${NC}"
    echo ""
    echo -e "${CYAN}正在更新所有应用...${NC}"
    flatpak update -y
    echo -e "${GREEN}✓ 所有应用更新完成${NC}"
}

# ---------- 卸载子函数 ----------
uninstall_wps_office() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 WPS Office ════════════════${NC}"
    local installed=""
    for pkg in "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps"; do
        if flatpak list | grep -q "$pkg"; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -p "确定要卸载 WPS Office？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ WPS Office 卸载完成${NC}"
                local desktop_file="$HOME/Desktop/WPS Office.desktop"
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
                fi
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 WPS Office。${NC}"
    fi
}

uninstall_qq() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 QQ ════════════════${NC}"
    local installed=""
    for pkg in "com.qq.QQ" "com.tencent.qq"; do
        if flatpak list | grep -q "$pkg"; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -p "确定要卸载 QQ？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ QQ 卸载完成${NC}"
                local desktop_file="$HOME/Desktop/QQ.desktop"
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
                fi
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 QQ。${NC}"
    fi
}

uninstall_wechat() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载微信 ════════════════${NC}"
    local installed=""
    for pkg in "com.tencent.WeChat" "com.qq.weixin"; do
        if flatpak list | grep -q "$pkg"; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -p "确定要卸载微信？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ 微信 卸载完成${NC}"
                local desktop_file="$HOME/Desktop/微信.desktop"
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
                fi
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的微信。${NC}"
    fi
}

uninstall_qqmusic() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 QQ音乐 ════════════════${NC}"
    local installed=""
    for pkg in "com.qq.QQmusic" "com.tencent.QQmusic"; do
        if flatpak list | grep -q "$pkg"; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -p "确定要卸载 QQ音乐？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ QQ音乐 卸载完成${NC}"
                local desktop_file="$HOME/Desktop/QQ音乐.desktop"
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
                fi
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 QQ音乐。${NC}"
    fi
}

uninstall_baidunetdisk() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载百度网盘 ════════════════${NC}"
    local installed=""
    for pkg in "com.baidu.NetDisk" "com.baidu.pan"; do
        if flatpak list | grep -q "$pkg"; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -p "确定要卸载百度网盘？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ 百度网盘 卸载完成${NC}"
                local desktop_file="$HOME/Desktop/百度网盘.desktop"
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
                fi
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的百度网盘。${NC}"
    fi
}

uninstall_edge() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Edge浏览器 ════════════════${NC}"
    local installed=""
    for pkg in "com.microsoft.Edge"; do
        if flatpak list | grep -q "$pkg"; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -p "确定要卸载 Edge浏览器？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ Edge浏览器 卸载完成${NC}"
                local desktop_file="$HOME/Desktop/Microsoft Edge.desktop"
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
                fi
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 Edge浏览器。${NC}"
    fi
}

uninstall_chrome() {
    mk_temp_dir
    clear
    echo -e "${YELLOW}════════════════ 卸载 Google浏览器 ════════════════${NC}"
    local installed=""
    for pkg in "com.google.Chrome" "org.chromium.Chromium"; do
        if flatpak list | grep -q "$pkg"; then
            installed="$pkg"
            break
        fi
    done
    if [ -n "$installed" ]; then
        read -p "确定要卸载 Google浏览器？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            if flatpak uninstall "$installed" -y; then
                echo -e "${GREEN}✓ Google浏览器 卸载完成${NC}"
                local desktop_file="$HOME/Desktop/Google Chrome.desktop"
                if [ -f "$desktop_file" ]; then
                    rm -f "$desktop_file"
                    echo -e "${GREEN}✓ 桌面快捷方式已删除${NC}"
                fi
            else
                echo -e "${RED}✗ 卸载失败${NC}"
            fi
        else
            echo "取消卸载。"
        fi
    else
        echo -e "${YELLOW}未检测到已安装的 Google浏览器。${NC}"
    fi
}

# ========== 其他 ==========
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

# ---------- 主函数 ----------
main() {
    echo "此脚本为内嵌库，请通过参数调用具体功能。"
}

if [ -n "$1" ] && declare -f "$1" > /dev/null; then
    "$@"
else
    main "$@"
fi
'''

# ============================================================================
# Python GUI 部分
# ============================================================================

class TaskWindow(Gtk.Window):
    def __init__(self, parent, func_key, display_name):
        super().__init__(title=f"执行任务: {display_name}")
        self.set_default_size(700, 500)
        self.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        self.set_transient_for(parent)
        self.set_modal(True)
        self.terminal = None
        self.process = None
        self.completed = False
        self.temp_script = None
        vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(vbox)
        if VTE_AVAILABLE:
            self.terminal = Vte.Terminal()
            self.terminal.set_vexpand(True)
            self.terminal.set_hexpand(True)
            self.terminal.set_scrollback_lines(10000)
            vbox.pack_start(self.terminal, True, True, 0)
        else:
            scrolled = Gtk.ScrolledWindow()
            scrolled.set_vexpand(True)
            self.textview = Gtk.TextView()
            self.textview.set_editable(False)
            self.textview.set_wrap_mode(Gtk.WrapMode.WORD)
            scrolled.add(self.textview)
            vbox.pack_start(scrolled, True, True, 0)
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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False, encoding='utf-8') as f:
            f.write(BASH_SCRIPT)
            self.temp_script = f.name
        os.chmod(self.temp_script, 0o755)
        self.connect("destroy", self.on_window_destroy)
        self.start_command(func_key)
        self.show_all()

    def start_command(self, func_key):
        if VTE_AVAILABLE:
            env = os.environ.copy()
            env['TERM'] = 'xterm-256color'
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
        else:
            self.process = subprocess.Popen(
                ["bash", self.temp_script, func_key],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )
            import threading
            def read_output():
                for line in self.process.stdout:
                    GLib.idle_add(self.append_text, line)
                GLib.idle_add(self.set_completed)
            thread = threading.Thread(target=read_output)
            thread.daemon = True
            thread.start()

    def on_child_exited(self, terminal, status):
        GLib.idle_add(self.set_completed)

    def append_text(self, text):
        buffer = self.textview.get_buffer()
        end_iter = buffer.get_end_iter()
        buffer.insert(end_iter, text)

    def set_completed(self):
        self.completed = True
        self.action_btn.set_sensitive(True)
        self.action_btn.set_label("完成")

    def on_action_button_clicked(self, button):
        if self.completed:
            self.destroy()
        else:
            if VTE_AVAILABLE and self.terminal:
                self.terminal.feed_child(b'\x03')
            elif self.process:
                self.process.terminate()
            self.action_btn.set_sensitive(False)
            self.action_btn.set_label("正在取消...")
            GLib.timeout_add(1000, self.force_close)

    def force_close(self):
        self.destroy()
        return False

    def on_window_destroy(self, widget):
        if self.temp_script and os.path.exists(self.temp_script):
            try:
                os.unlink(self.temp_script)
            except:
                pass
        if self.process and self.process.poll() is None:
            self.process.terminate()

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

        # 分类名称 → 图标文件名 映射
        self.icon_map = {
            "支持和维护": "pushpin.png",
            "更新日志": "clipboard_twemoji.png",
            "系统优化": "hammer_wrench.png",
            "软件安装": "package.png",
            "网络工具": "globe.png",
            "插件相关": "game_controller.png",
            "引导管理": "refresh.png",
            "更新软件": "inbox.png",
            "其他": "trash.png"
        }

        # 存储分类图标 Pixbuf 以便右侧标题使用
        self.category_icons = {}

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        hbox.set_vexpand(True)   # 使 hbox 垂直填满
        main_vbox.pack_start(hbox, True, True, 0)

        # ---------- 左侧分类列表 ----------
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
            "更新软件",
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
            self.category_icons[cat] = pixbuf  # 保存供右侧标题使用

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

        # ---------- 右侧 Stack ----------
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
        self.stack.set_vexpand(True)
        self.stack.set_valign(Gtk.Align.FILL)
        hbox.pack_start(self.stack, True, True, 0)

        # 关于页面
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

        # ---------- 更新日志页面 ----------
        changelog_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        changelog_box.set_margin_top(20)
        changelog_box.set_margin_bottom(20)
        changelog_box.set_margin_start(20)
        changelog_box.set_margin_end(20)

        self.changelog_textview = Gtk.TextView()
        self.changelog_textview.set_editable(False)
        self.changelog_textview.set_wrap_mode(Gtk.WrapMode.WORD)
        self.changelog_textview.set_cursor_visible(False)

        # 等宽字体
        font_desc = Pango.FontDescription("Monospace 10")
        self.changelog_textview.modify_font(font_desc)

        scrolled_changelog = Gtk.ScrolledWindow()
        scrolled_changelog.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_changelog.set_vexpand(True)
        scrolled_changelog.add(self.changelog_textview)
        changelog_box.pack_start(scrolled_changelog, True, True, 0)

        self.stack.add_named(changelog_box, "changelog")

        # ---------- 功能列表页面 ----------
        func_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        func_page.set_margin_top(20)
        func_page.set_margin_bottom(20)
        func_page.set_margin_start(20)
        func_page.set_margin_end(20)
        func_page.set_vexpand(True)
        func_page.set_valign(Gtk.Align.FILL)

        # ---- 右侧分类标题（带图标） ----
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

        # ---- 功能列表（只有文本，无图标） ----
        self.func_store = Gtk.TreeStore(str)   # 只存文本
        self.func_view = Gtk.TreeView(model=self.func_store)

        # 不显示列标题（去掉“功能”二字）
        func_col = Gtk.TreeViewColumn()
        renderer_func = Gtk.CellRendererText()
        func_col.pack_start(renderer_func, True)
        func_col.add_attribute(renderer_func, "text", 0)
        self.func_view.append_column(func_col)
        self.func_view.set_headers_visible(False)   # 隐藏所有列头
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

        # 默认选中第一个分类
        selection = self.cat_view.get_selection()
        first_path = Gtk.TreePath.new_first()
        selection.select_path(first_path)
        self.on_category_activated(self.cat_view, first_path, None)

        # 底部按钮
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

        # ---------- 功能映射 ----------
        self.func_map = {
            "安装国内源": "install_chinese_source",
            "调整虚拟内存": "adjust_swap",
            "修复磁盘写入错误": "fix_disk_write_error",
            "清理hosts缓存": "clear_hosts_cache",
            "设置管理员密码": "set_admin_password",
            "校准摇杆": "calibrate_joystick_stick",
            "校准扳机": "calibrate_joystick_trigger",
            "Steam缓存管理": "steamdeck_cache_manager",
            "修复引导": "fix_boot",
            "修复互通盘": "fix_shared_disk",
            "AnyDesk": "install_anydesk",
            "ToDesk": "install_todesk",
            "WPS Office": "install_wps_office",
            "QQ": "install_qq",
            "微信": "install_wechat",
            "QQ音乐": "install_qqmusic",
            "百度网盘": "install_baidunetdisk",
            "Edge浏览器": "install_edge",
            "Google浏览器": "install_chrome",
            "UU加速器插件": "install_uu_accelerator",
            "迅游加速器插件": "install_xunyou_accelerator",
            "安装/更新": "install_watt_toolkit_install",
            "卸载": "install_watt_toolkit_uninstall",
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
            "小黄鸭软件": "install_yellow_duck_software"
        }

        # ---------- 分类树 ----------
        self.category_tree = {
            "支持和维护": [],
            "系统优化": [
                "安装国内源",
                "调整虚拟内存",
                "修复磁盘写入错误",
                "清理hosts缓存",
                "设置管理员密码",
                ("校准设备", ["校准摇杆", "校准扳机"]),
                "Steam缓存管理"
            ],
            "软件安装": [
                "AnyDesk",
                "ToDesk",
                "WPS Office",
                "QQ",
                "微信",
                "QQ音乐",
                "百度网盘",
                "Edge浏览器",
                "Google浏览器"
            ],
            "网络工具": [
                "UU加速器插件",
                "迅游加速器插件",
                ("Watt Toolkit (Steam++)", ["安装/更新", "卸载"])
            ],
            "插件相关": [
                ("安装/卸载插件商店", ["安装插件商店", "卸载插件商店"]),
                ("ToMoon 插件", ["安装/更新 ToMoon", "卸载 ToMoon"]),
                ("LSFG-VK插件", ["安装/更新 LSFG-VK", "卸载 LSFG-VK"]),
                ("Framegen插件", ["安装/更新 Framegen", "卸载 Framegen"])
            ],
            "引导管理": [
                "安装/重装 Clover"
            ],
            "更新软件": [
                "更新已安装应用",
                ("卸载已安装应用", ["卸载 WPS Office", "卸载 QQ", "卸载微信", "卸载 QQ音乐", "卸载百度网盘", "卸载 Edge浏览器", "卸载 Google浏览器"])
            ],
            "其他": [
                "小黄鸭软件"
            ]
        }

    def detect_system_type(self):
        has_clover = os.path.isdir("/boot/efi/EFI/CLOVER") or os.path.isdir("/boot/efi/EFI/Clover")
        has_windows = os.path.isdir("/boot/efi/EFI/Microsoft")
        if has_clover or has_windows:
            return "双系统"
        try:
            result = subprocess.run(["efibootmgr"], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                boot_entries = re.findall(r'Boot[0-9A-Fa-f]{4}', result.stdout)
                if len(boot_entries) > 2:
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

        # 更新日志分支
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

        # 更新标题图标和文字
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

        # 填充功能列表（只存文本）
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
        """显示手动输入的更新日志内容"""
        changelog_content = """2026-07-25（v1.4.6包含 v1.3.9-v1.4.5 的调整）将文字形式停止更新，替换为图文形式，操作更加便捷，并对功能进行了修改和优化完善
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

        # 如果是父节点，展开/折叠并返回
        if model.iter_has_child(iter_):
            if treeview.row_expanded(path):
                treeview.collapse_row(path)
            else:
                treeview.expand_row(path, False)
            return

        # 处理“UU加速器插件”：在独立 konsole 中运行
        if func_name == "UU加速器插件":
            func_key = self.func_map.get(func_name)
            if func_key:
                self.run_external_terminal(func_key)
            return

        # 处理“Steam缓存管理”：使用 zenity 图形界面
        if func_name == "Steam缓存管理":
            self.run_cache_manager_gui()
            return

        # 通用功能：在内嵌终端中运行
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

    def run_cache_manager_gui(self):
        """直接运行 zenity 图形化缓存管理器，不显示终端窗口"""
        func_name = "steamdeck_cache_manager"
        script_content = BASH_SCRIPT + f"\n\n{func_name}\n"
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False, encoding='utf-8') as f:
            f.write(script_content)
            tmp_path = f.name
        os.chmod(tmp_path, 0o755)
        subprocess.Popen(
            [tmp_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

    def on_quit_clicked(self, button):
        self.destroy()

    def run_external_terminal(self, func_key):
        """在独立的 konsole 终端中运行指定的 Bash 函数"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.sh', delete=False, encoding='utf-8') as f:
            f.write(BASH_SCRIPT + f"\n\n{func_key}\n")
            tmp_path = f.name
        os.chmod(tmp_path, 0o755)

        cmd = [
            "konsole",
            "-e",
            "bash",
            "-c",
            f"bash {tmp_path}; read -p '按回车键关闭...' -n1"
        ]

        subprocess.Popen(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            stdin=subprocess.DEVNULL,
            start_new_session=True
        )

# ============================================================================
# 启动后处理：桌面快捷方式创建、VTE检测与安装
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
Exec=python3 {script_path}
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

def on_vte_install_finished(pid, status, user_data):
    dialog = Gtk.MessageDialog(
        None,
        Gtk.DialogFlags.MODAL,
        Gtk.MessageType.INFO,
        Gtk.ButtonsType.OK,
        "VTE 安装已完成。\n\n请手动关闭并重新打开本程序以生效。"
    )
    dialog.run()
    dialog.destroy()

def ensure_vte_installed():
    if VTE_AVAILABLE:
        return

    dialog = Gtk.MessageDialog(
        None,
        Gtk.DialogFlags.MODAL,
        Gtk.MessageType.INFO,
        Gtk.ButtonsType.NONE,
        "VTE 终端组件未安装"
    )
    dialog.format_secondary_text(
        "本工具需要 VTE 组件以实现内嵌终端交互。\n"
        "点击“是”将自动解除只读模式并安装（需要 sudo 密码）。\n"
        "安装完成后请手动重启本程序。"
    )
    dialog.add_button("是", Gtk.ResponseType.YES)
    dialog.add_button("否", Gtk.ResponseType.NO)
    try:
        dialog.set_alternative_button_order_from_array([Gtk.ResponseType.YES, Gtk.ResponseType.NO])
    except AttributeError:
        try:
            dialog.set_alternative_button_order(Gtk.ResponseType.YES, Gtk.ResponseType.NO)
        except AttributeError:
            pass

    response = dialog.run()
    dialog.destroy()

    if response != Gtk.ResponseType.YES:
        return

    try:
        result = subprocess.run(["steamos-readonly", "status"], capture_output=True, text=True)
        if "enabled" in result.stdout.lower():
            subprocess.run(["sudo", "steamos-readonly", "disable"], check=True)
    except FileNotFoundError:
        pass
    except subprocess.CalledProcessError as e:
        try:
            result = subprocess.run(["steamos-readonly", "status"], capture_output=True, text=True)
            if "enabled" in result.stdout.lower():
                error_dialog = Gtk.MessageDialog(
                    None,
                    Gtk.DialogFlags.MODAL,
                    Gtk.MessageType.ERROR,
                    Gtk.ButtonsType.OK,
                    f"解除只读模式失败：{e}\n"
                    "请手动执行以下命令后重试：\n"
                    "sudo steamos-readonly disable"
                )
                error_dialog.run()
                error_dialog.destroy()
                return
        except:
            pass

    terminal = shutil.which("konsole") or shutil.which("xterm")
    if not terminal:
        error_dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.ERROR,
            Gtk.ButtonsType.OK,
            "未找到终端模拟器，请手动执行：\n"
            "sudo steamos-readonly disable\n"
            "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF\n"
            "sudo pacman -S vte3"
        )
        error_dialog.run()
        error_dialog.destroy()
        return

    if terminal.endswith("konsole"):
        cmd = [terminal, "-e", "bash", "-c",
               "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF && sudo pacman -S --noconfirm vte3"]
    else:
        cmd = [terminal, "-hold", "-e", "bash", "-c",
               "sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF && sudo pacman -S --noconfirm vte3"]

    proc = subprocess.Popen(cmd)
    GLib.child_watch_add(proc.pid, on_vte_install_finished)

# ============================================================================
# 图标同步函数（新增）
# ============================================================================
def sync_emoji_icons():
    """检查本地图标是否与远程仓库一致，不一致则同步"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    local_icon_dir = os.path.join(script_dir, "emoji_icons")
    # 获取远程文件列表
    remote_count = 0
    try:
        api_url = "https://gitee.com/api/v5/repos/Zhucy2100/steamdeck_toolbox/contents/emoji_icons"
        req = urllib.request.Request(api_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            # data 是列表，每个元素代表一个文件/目录
            remote_count = len([item for item in data if item['type'] == 'file'])
    except Exception as e:
        print(f"获取远程图标列表失败: {e}")
        # 如果网络失败，跳过同步
        return False
    # 本地数量
    local_count = 0
    if os.path.isdir(local_icon_dir):
        local_count = len([f for f in os.listdir(local_icon_dir) if os.path.isfile(os.path.join(local_icon_dir, f))])
    if local_count == remote_count and remote_count > 0:
        print("图标数量一致，无需同步。")
        return True
    print(f"图标数量不一致: 本地 {local_count}, 远程 {remote_count}，开始同步...")
    # 进行同步：使用 git clone
    temp_dir = "/tmp/steamdeck_icons_sync"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    try:
        # 检查 git 命令
        subprocess.run(["git", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        print("git 未安装，无法同步图标。")
        return False
    try:
        repo_url = "https://gitee.com/Zhucy2100/steamdeck_toolbox.git"
        subprocess.run(["git", "clone", "--depth=1", repo_url, temp_dir], check=True, timeout=60)
        remote_icon_dir = os.path.join(temp_dir, "emoji_icons")
        if os.path.isdir(remote_icon_dir):
            # 确保本地目录存在
            os.makedirs(local_icon_dir, exist_ok=True)
            # 复制所有文件
            for item in os.listdir(remote_icon_dir):
                src = os.path.join(remote_icon_dir, item)
                dst = os.path.join(local_icon_dir, item)
                if os.path.isfile(src):
                    shutil.copy2(src, dst)
            print("图标同步完成。")
            return True
        else:
            print("克隆的仓库中未找到 emoji_icons 目录。")
            return False
    except Exception as e:
        print(f"图标同步失败: {e}")
        return False
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)

# ============================================================================
# 更新相关函数
# ============================================================================

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

def perform_update(remote_version, parent_window=None):
    try:
        progress_dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.NONE,
            text="正在下载更新..."
        )
        progress_dialog.set_default_size(300, 100)
        progress_dialog.show_all()
        while Gtk.events_pending():
            Gtk.main_iteration()

        req = urllib.request.Request(
            REPO_RAW_URL,
            headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'}
        )
        with urllib.request.urlopen(req, timeout=30) as response:
            new_content = response.read().decode('utf-8')

        progress_dialog.destroy()

        current_path = os.path.abspath(sys.argv[0])
        backup_path = current_path + ".bak"
        try:
            shutil.copy2(current_path, backup_path)
        except:
            pass

        with open(current_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        os.chmod(current_path, 0o755)

        restart_dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="✅ 更新完成！"
        )
        restart_dialog.format_secondary_text(
            f"新版本 v{remote_version} 已下载。\n点击下方按钮关闭并重新打开Deck工具箱。"
        )
        restart_dialog.connect("response", lambda dialog, resp: Gtk.main_quit() or sys.exit(0))
        restart_dialog.run()

    except Exception as e:
        error_dialog = Gtk.MessageDialog(
            parent=parent_window,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=f"更新失败：{e}"
        )
        error_dialog.format_secondary_text(
            "请手动从以下地址下载最新版本：\n"
            f"{REPO_RAW_URL}"
        )
        error_dialog.run()
        error_dialog.destroy()
        if parent_window:
            parent_window.destroy()
        show_main_window()

def show_main_window():
    window = MainWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    GLib.idle_add(ensure_desktop_shortcut)
    GLib.idle_add(ensure_vte_installed)

# ============================================================================
# 更新检查窗口
# ============================================================================

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
            # 先同步图标
            sync_emoji_icons()
            # 再检查版本
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
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.NONE,
            text=f"发现新版本 v{remote_version}"
        )
        dialog.format_secondary_text(
            f"当前版本: v{VERSION}\n"
            f"最新版本: v{remote_version}\n\n"
            "是否立即更新？\n（更新将下载新版本，完成后请手动重启程序）"
        )

        dialog.add_button("是", Gtk.ResponseType.YES)
        dialog.add_button("否", Gtk.ResponseType.NO)

        try:
            dialog.set_alternative_button_order_from_array([Gtk.ResponseType.YES, Gtk.ResponseType.NO])
        except AttributeError:
            try:
                dialog.set_alternative_button_order(Gtk.ResponseType.YES, Gtk.ResponseType.NO)
            except AttributeError:
                pass

        response = dialog.run()
        dialog.destroy()

        if response == Gtk.ResponseType.YES:
            perform_update(remote_version, self)
        else:
            self.destroy()
            show_main_window()

    def on_button_clicked(self, button):
        self.destroy()
        show_main_window()

# ============================================================================
# 启动
# ============================================================================

def main():
    update_win = UpdateCheckWindow()
    Gtk.main()

if __name__ == "__main__":
    main()
