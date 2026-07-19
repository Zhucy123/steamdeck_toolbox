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

from gi.repository import Gtk, GLib
import subprocess
import os
import sys
import re
import tempfile

# ============================================================================
# 内嵌完整的 Bash 脚本（所有函数末尾的“按回车返回主菜单”已移除）
# ============================================================================
BASH_SCRIPT = r'''#!/bin/bash
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

VERSION="1.3.8"
REPO_URL="https://gitee.com/Zhucy2100/steamdeck_toolbox"

SYSTEM_TYPE=""

# ---------- 所有功能函数 ----------
show_about() {
    clear
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
}

install_chinese_source() {
    clear
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
}

adjust_swap() {
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

fix_boot() {
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

clear_hosts_cache() {
    clear
    echo -e "${YELLOW}════════════════ 清理hosts缓存 ════════════════${NC}"
    echo -e "${CYAN}正在清理hosts缓存...${NC}"
    sudo cp /etc/hosts /etc/hosts.backup.$(date +%Y%m%d_%H%M%S)
    sudo sh -c 'echo "" > /etc/hosts'
    echo -e "${GREEN}✓ hosts缓存已清理完成${NC}"
}

install_uu_accelerator() {
    clear
    echo -e "${YELLOW}════════════════ 安装UU加速器插件 ════════════════${NC}"
    echo -e "${CYAN}正在安装UU加速器插件...${NC}"
    curl -s uudeck.com | sudo sh
}

install_xunyou_accelerator() {
    clear
    echo -e "${YELLOW}════════════════ 安装迅游加速器插件 ════════════════${NC}"
    echo -e "${CYAN}正在安装迅游加速器插件...${NC}"
    curl -s sd.xunyou.com | sudo sh
}

install_tomoon() {
    clear
    echo -e "${YELLOW}════════════════ 安装/卸载 ToMoon 插件 ════════════════${NC}"
    echo ""
    echo "请选择要执行的操作："
    echo "1. 安装/更新 ToMoon 插件"
    echo "2. 卸载 ToMoon 插件"
    read -p "请输入选择 [1-2]: " action_choice < /dev/tty
    case $action_choice in
        1)
            echo -e "${CYAN}正在从 GitHub 获取版本信息...${NC}"
            local latest_version=$(curl -s "https://api.github.com/repos/YukiCoco/ToMoon/releases/latest" | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//; s/".*//')
            if [ -z "$latest_version" ]; then echo -e "${RED}错误: 无法获取版本${NC}"; return; fi
            echo -e "${GREEN}最新版本: ${latest_version}${NC}"
            local TARGET_DIR="/home/deck/homebrew/plugins/tomoon"
            if [ -d "$TARGET_DIR" ]; then
                echo "检测到旧版本，将覆盖安装。"
            fi
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
            echo -e "${GREEN}✅ ToMoon 插件安装完成！${NC}"
            ;;
        2)
            echo "卸载 ToMoon..."
            sudo rm -rf /home/deck/homebrew/plugins/tomoon
            echo -e "${GREEN}卸载完成${NC}"
            ;;
        *) echo "取消";;
    esac
}

install_remove_plugin_store() {
    clear
    echo -e "${YELLOW}════════════════ 安装＆卸载插件商店 ════════════════${NC}"
    echo "请选择操作："
    echo "1. 安装插件商店"
    echo "2. 卸载插件商店"
    read -p "请输入选择 [1-2]: " plugin_choice < /dev/tty
    case $plugin_choice in
        1)
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
                if [ -n "$latest_stable" ] && [ "$installed_version" = "$latest_stable" ] && [ -n "$latest_prerelease" ]; then
                    echo -e "${GREEN}已安装最新正式版 ${installed_version}${NC}"
                    echo -e "${YELLOW}发现更高版本的预发布版: ${latest_prerelease}${NC}"
                    read -p "是否升级到预发布版？(y/N): " upgrade < /dev/tty
                    if [[ $upgrade =~ ^[Yy]$ ]]; then
                        target_version="$latest_prerelease"
                    else
                        echo "保持当前版本。"
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
                        return 0
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
            echo "服务状态："
            systemctl status plugin_loader --no-pager
            echo ""
            echo -e "${GREEN}✓ Decky Loader ${target_version} 安装/更新完成${NC}"
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
                return
            fi
            echo "正在执行卸载..."
            if sudo rm -rf /home/deck/homebrew; then
                echo -e "${GREEN}✓ 插件商店卸载完成${NC}"
            else
                echo -e "${RED}✗ 插件商店卸载失败${NC}"
            fi
            ;;
        *)
            echo -e "${RED}无效选择${NC}"
            ;;
    esac
}

calibrate_joystick() {
    clear
    echo -e "${YELLOW}════════════════ 校准设备 ════════════════${NC}"
    echo ""
    echo "请选择要校准的设备："
    echo "1. 校准摇杆"
    echo "2. 校准扳机"
    read -p "请输入选择 [1-2]: " choice < /dev/tty
    case $choice in
        1) echo -e "${CYAN}正在校准摇杆...${NC}"; thumbstick_cal && echo -e "${GREEN}✓ 摇杆校准完成${NC}" || echo -e "${RED}✗ 摇杆校准失败${NC}";;
        2) echo -e "${CYAN}正在校准扳机...${NC}"; trigger_cal && echo -e "${GREEN}✓ 扳机校准完成${NC}" || echo -e "${RED}✗ 扳机校准失败${NC}";;
        *) echo -e "${RED}无效选择${NC}";;
    esac
}

set_admin_password() {
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

install_anydesk() {
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
    clear
    echo -e "${YELLOW}════════════════ 安装ToDesk ════════════════${NC}"
    echo -e "${CYAN}正在安装ToDesk...${NC}"
    sudo steamos-readonly disable
    curl -L todesk.lanbai.top | sh
    echo -e "${GREEN}✓ ToDesk安装脚本已执行${NC}"
    echo -e "${YELLOW}请在桌面上运行'todesk安装'或'todesk重新安装'的文件来完成安装${NC}"
}

install_wps_office() {
    clear
    echo -e "${YELLOW}════════════════ 安装WPS Office ════════════════${NC}"
    echo "正在通过 Flatpak 安装 WPS Office..."
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub com.wps.Office -y || flatpak install flathub cn.wps.wps-office -y || flatpak install flathub com.kingsoft.wps -y
    echo -e "${GREEN}WPS Office 安装完成${NC}"
}

install_qq() {
    clear
    echo -e "${YELLOW}════════════════ 安装QQ ════════════════${NC}"
    echo "正在通过 Flatpak 安装 QQ..."
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub com.qq.QQ -y || flatpak install flathub com.tencent.qq -y
    echo -e "${GREEN}QQ 安装完成${NC}"
}

install_wechat() {
    clear
    echo -e "${YELLOW}════════════════ 安装微信 ════════════════${NC}"
    echo "正在通过 Flatpak 安装微信..."
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub com.tencent.WeChat -y || flatpak install flathub com.qq.weixin -y
    echo -e "${GREEN}微信 安装完成${NC}"
}

install_qqmusic() {
    clear
    echo -e "${YELLOW}════════════════ 安装QQ音乐 ════════════════${NC}"
    echo "正在通过 Flatpak 安装 QQ音乐..."
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub com.qq.QQmusic -y || flatpak install flathub com.tencent.QQmusic -y
    echo -e "${GREEN}QQ音乐 安装完成${NC}"
}

install_baidunetdisk() {
    clear
    echo -e "${YELLOW}════════════════ 安装百度网盘 ════════════════${NC}"
    echo "正在通过 Flatpak 安装百度网盘..."
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub com.baidu.NetDisk -y || flatpak install flathub com.baidu.pan -y
    echo -e "${GREEN}百度网盘 安装完成${NC}"
}

install_edge() {
    clear
    echo -e "${YELLOW}════════════════ 安装Edge浏览器 ════════════════${NC}"
    echo "正在通过 Flatpak 安装 Edge..."
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub com.microsoft.Edge -y
    echo -e "${GREEN}Edge 安装完成${NC}"
}

install_chrome() {
    clear
    echo -e "${YELLOW}════════════════ 安装Google浏览器 ════════════════${NC}"
    echo "正在通过 Flatpak 安装 Chrome..."
    flatpak remote-add --if-not-exists flathub https://flathub.org/repo/flathub.flatpakrepo
    flatpak install flathub com.google.Chrome -y
    echo -e "${GREEN}Chrome 安装完成${NC}"
}

steamdeck_cache_manager() {
    clear
    echo -e "${YELLOW}════════════════ Steam Deck 缓存管理器 ════════════════${NC}"
    echo ""
    echo "正在启动 Steam Deck 缓存管理器..."
    echo "该功能需要图形界面支持，请确保您在桌面模式下运行。"
    echo ""
    if [ -z "$DISPLAY" ]; then
        echo -e "${RED}错误：未检测到图形界面环境。${NC}"
        return
    fi
    if ! command -v zenity &> /dev/null; then
        echo -e "${YELLOW}未找到zenity工具，正在尝试安装...${NC}"
        sudo pacman -Sy --noconfirm zenity 2>/dev/null || sudo apt install -y zenity 2>/dev/null
        if ! command -v zenity &> /dev/null; then
            echo -e "${RED}✗ Zenity安装失败！${NC}"
            return
        fi
    fi
    echo -e "${GREEN}✓ 环境检查完成，启动缓存管理器...${NC}"
    echo "缓存管理器已启动（演示），实际功能请使用原脚本。"
}

update_installed_apps() {
    clear
    echo -e "${YELLOW}════════════════ 更新全部应用 ════════════════${NC}"
    echo ""
    read -p "是否更新所有已安装的 Flatpak 应用？(y/N): " confirm < /dev/tty
    if [[ $confirm =~ ^[Yy]$ ]]; then
        echo -e "${CYAN}正在更新所有应用...${NC}"
        flatpak update -y
        echo -e "${GREEN}✓ 所有应用更新完成${NC}"
    else
        echo "取消更新。"
    fi
}

uninstall_apps() {
    clear
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
    read -p "请输入选择 [1-7]: " app_choice < /dev/tty
    case $app_choice in
        1) uninstall_flatpak "WPS Office" "com.wps.Office" "cn.wps.wps-office" "com.kingsoft.wps";;
        2) uninstall_flatpak "QQ" "com.qq.QQ" "com.tencent.qq";;
        3) uninstall_flatpak "微信" "com.tencent.WeChat" "com.qq.weixin";;
        4) uninstall_flatpak "QQ音乐" "com.qq.QQmusic" "com.tencent.QQmusic";;
        5) uninstall_flatpak "百度网盘" "com.baidu.NetDisk" "com.baidu.pan";;
        6) uninstall_flatpak "Edge浏览器" "com.microsoft.Edge";;
        7) uninstall_flatpak "Google浏览器" "com.google.Chrome";;
        *) echo "返回";;
    esac
}

uninstall_flatpak() {
    local app_name="$1"
    shift
    local packages=("$@")
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
        read -p "是否卸载 $app_name？(y/N): " -n 1 -r < /dev/tty
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            flatpak uninstall "$installed_package" -y && echo -e "${GREEN}✓ $app_name 卸载完成${NC}" || echo -e "${RED}✗ 卸载失败${NC}"
        else
            echo "取消卸载"
        fi
    else
        echo -e "${YELLOW}⚠️  未检测到已安装的$app_name${NC}"
    fi
}

install_yellow_duck_software() {
    clear
    echo -e "${YELLOW}════════════════ 安装小黄鸭软件 ════════════════${NC}"
    echo "正在从 Gitee 克隆并安装..."
    local CLONE_DIR="$HOME/lossless-scaling-repo"
    rm -rf "$CLONE_DIR"
    git clone --depth=1 https://gitee.com/Zhucy2100/lossless-scaling.git "$CLONE_DIR"
    if [ $? -ne 0 ]; then echo "克隆失败"; return; fi
    cd "$CLONE_DIR" || return
    cat "Lossless Scaling.zip".* > Lossless-Scaling-Combined.zip
    unzip -o Lossless-Scaling-Combined.zip -d "/home/deck/.local/share/Steam/steamapps/common/"
    sudo chown -R deck:deck "/home/deck/.local/share/Steam/steamapps/common/Lossless Scaling"
    rm -rf "$CLONE_DIR"
    echo -e "${GREEN}小黄鸭软件安装完成！${NC}"
}

install_watt_toolkit() {
    clear
    echo -e "${YELLOW}════════════════ 安装 Watt Toolkit (Steam++) ════════════════${NC}"
    echo "请选择：1.安装/更新  2.卸载"
    read -p "输入选择: " choice < /dev/tty
    case $choice in
        1)
            local INSTALL_DIR="/home/deck/Watt Toolkit"
            mkdir -p "$INSTALL_DIR"
            local TEMP_DIR="/tmp/watt_toolkit"
            rm -rf "$TEMP_DIR"
            mkdir -p "$TEMP_DIR"
            cd "$TEMP_DIR" || return
            local VERSION=$(curl -s https://api.github.com/repos/BeyondDimension/SteamTools/releases | grep -o '"tag_name": *"v[^"]*"' | head -1 | sed 's/.*"v//;s/".*//')
            if [ -z "$VERSION" ]; then echo "版本获取失败"; return; fi
            local URL="https://github.com/BeyondDimension/SteamTools/releases/download/v${VERSION}/Steam++_v${VERSION}_linux_x64.tgz"
            echo "下载 $URL"
            curl -L --progress-bar "$URL" -o steam++.tgz
            tar -xzf steam++.tgz -C "$INSTALL_DIR" --strip-components=1
            echo "$VERSION" > "$INSTALL_DIR/.version"
            local dotnet_root="$INSTALL_DIR/dotnet"
            local dll_path="$INSTALL_DIR/assemblies/Steam++.dll"
            cat > "$HOME/Desktop/Watt_Toolkit.desktop" << EOF
[Desktop Entry]
Name=Watt Toolkit (Steam++)
Exec=env 'DOTNET_ROOT=${dotnet_root}' '${dotnet_root}/dotnet' '${dll_path}'
Icon=$INSTALL_DIR/Icons/Watt-Toolkit.png
Type=Application
Categories=Network;Game;
EOF
            chmod +x "$HOME/Desktop/Watt_Toolkit.desktop"
            echo -e "${GREEN}Watt Toolkit 安装完成${NC}"
            ;;
        2)
            rm -rf "/home/deck/Watt Toolkit"
            rm -f "$HOME/Desktop/Watt_Toolkit.desktop"
            echo -e "${GREEN}已卸载${NC}"
            ;;
        *) echo "取消";;
    esac
}

install_decky_lsfg_vk() {
    clear
    echo -e "${YELLOW}════════════════ 安装/卸载 LSFG-VK 插件 ════════════════${NC}"
    echo "请选择：1.安装/更新  2.卸载"
    read -p "输入选择: " choice < /dev/tty
    case $choice in
        1)
            local TEMP_DIR="/tmp/lsfg_vk"
            rm -rf "$TEMP_DIR"
            mkdir -p "$TEMP_DIR"
            cd "$TEMP_DIR" || return
            local VERSION=$(curl -s https://api.github.com/repos/xXJSONDeruloXx/decky-lsfg-vk/releases | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//;s/".*//')
            if [ -z "$VERSION" ]; then echo "版本获取失败"; return; fi
            local URL="https://github.com/xXJSONDeruloXx/decky-lsfg-vk/releases/download/${VERSION}/Decky.LSFG-VK.zip"
            curl -L --progress-bar "$URL" -o plugin.zip
            unzip -q plugin.zip
            sudo mkdir -p /home/deck/homebrew/plugins
            sudo rm -rf /home/deck/homebrew/plugins/Decky-LSFG-VK
            local extracted_dir="$(find . -maxdepth 1 -type d -name "*LSFG*" | head -1)"
            if [ -z "$extracted_dir" ]; then
                extracted_dir="."
            fi
            sudo mv "$extracted_dir" /home/deck/homebrew/plugins/Decky-LSFG-VK
            sudo chown -R deck:deck /home/deck/homebrew/plugins/Decky-LSFG-VK
            echo -e "${GREEN}LSFG-VK 插件安装完成${NC}"
            ;;
        2)
            sudo rm -rf /home/deck/homebrew/plugins/Decky-LSFG-VK
            echo -e "${GREEN}已卸载${NC}"
            ;;
        *) echo "取消";;
    esac
}

install_decky_framegen() {
    clear
    echo -e "${YELLOW}════════════════ 安装/卸载 Framegen 插件 ════════════════${NC}"
    echo "请选择：1.安装/更新  2.卸载"
    read -p "输入选择: " choice < /dev/tty
    case $choice in
        1)
            local TEMP_DIR="/tmp/framegen"
            rm -rf "$TEMP_DIR"
            mkdir -p "$TEMP_DIR"
            cd "$TEMP_DIR" || return
            local VERSION=$(curl -s https://api.github.com/repos/xXJSONDeruloXx/Decky-Framegen/releases | grep -o '"tag_name": *"[^"]*"' | head -1 | sed 's/.*"tag_name": *"//;s/".*//')
            if [ -z "$VERSION" ]; then echo "版本获取失败"; return; fi
            local URL="https://github.com/xXJSONDeruloXx/Decky-Framegen/releases/download/${VERSION}/Decky-Framegen.zip"
            curl -L --progress-bar "$URL" -o plugin.zip
            unzip -q plugin.zip
            sudo mkdir -p /home/deck/homebrew/plugins
            sudo rm -rf /home/deck/homebrew/plugins/Decky-Framegen
            local extracted_dir="$(find . -maxdepth 1 -type d -name "*Framegen*" | head -1)"
            if [ -z "$extracted_dir" ]; then
                extracted_dir="."
            fi
            sudo mv "$extracted_dir" /home/deck/homebrew/plugins/Decky-Framegen
            sudo chown -R deck:deck /home/deck/homebrew/plugins/Decky-Framegen
            echo -e "${GREEN}Framegen 插件安装完成${NC}"
            ;;
        2)
            sudo rm -rf /home/deck/homebrew/plugins/Decky-Framegen
            echo -e "${GREEN}已卸载${NC}"
            ;;
        *) echo "取消";;
    esac
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
        if [[ $REPLY =~ ^[Yy]$ ]]; then rm -rf "$TARGET_DIR"; else return; fi
    fi
    echo -e "${CYAN}正在克隆仓库...${NC}"
    git clone "$REPO_URL" "$TARGET_DIR" || { echo -e "${RED}克隆失败${NC}"; return; }
    cd "$TARGET_DIR" || return
    echo "运行官方安装脚本..."
    bash install-Clover.sh
    echo -e "${GREEN}Clover 安装/重装完成${NC}"
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
    """独立任务窗口，包含 VTE 终端和按钮"""
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
                [],
                GLib.SpawnFlags.DEFAULT,
                None,
                None,
                None
            )
            # 执行命令，完成后自动退出 shell（无需用户按回车）
            cmd = f"bash {self.temp_script} {func_key}; exit\n"
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
        self.set_default_size(950, 600)
        self.set_position(Gtk.WindowPosition.CENTER)

        self.system_type = self.detect_system_type()
        self.task_window = None

        main_vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.add(main_vbox)

        hbox = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        main_vbox.pack_start(hbox, True, True, 0)

        # 左侧分类
        self.list_store = Gtk.ListStore(str)
        categories = [
            "📌 支持和维护",
            "🛠 系统优化",
            "📦 软件安装",
            "🌐 网络工具",
            "🎮 插件相关",
            "🔄 引导管理",
            "📥 更新软件",
            "🗑 其他"
        ]
        for cat in categories:
            self.list_store.append([cat])

        self.cat_view = Gtk.TreeView(model=self.list_store)
        renderer = Gtk.CellRendererText()
        column = Gtk.TreeViewColumn("", renderer, text=0)
        self.cat_view.append_column(column)
        self.cat_view.set_activate_on_single_click(True)
        self.cat_view.connect("row-activated", self.on_category_activated)

        scrolled_left = Gtk.ScrolledWindow()
        scrolled_left.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_left.add(self.cat_view)
        scrolled_left.set_size_request(250, -1)
        hbox.pack_start(scrolled_left, False, False, 0)

        # 右侧 Stack
        self.stack = Gtk.Stack()
        self.stack.set_transition_type(Gtk.StackTransitionType.CROSSFADE)
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
        about_textview.get_buffer().set_text("""
steamdeck工具箱 v1.3.8
制作人：薯条 & DeepSeek
发布日期：2026年1月1日

工具箱介绍：
这是一个专为 Steam Deck 设计的工具箱，集成了系统优化、软件安装、
网络工具等多种功能，方便用户快速配置和优化设备。
感谢DeepSeek提供的大量技术支持

使用说明：
1. 点击左侧分类，右侧显示功能列表
2. 点击功能将弹出独立任务窗口
3. 所有交互在终端内进行
""")
        scrolled_about = Gtk.ScrolledWindow()
        scrolled_about.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_about.set_vexpand(True)
        scrolled_about.add(about_textview)
        about_box.pack_start(scrolled_about, True, True, 0)
        self.stack.add_named(about_box, "about")

        # 功能列表页面
        func_page = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=15)
        func_page.set_margin_top(20)
        func_page.set_margin_bottom(20)
        func_page.set_margin_start(20)
        func_page.set_margin_end(20)

        self.category_title = Gtk.Label()
        self.category_title.set_markup("<big><b>系统优化</b></big>")
        self.category_title.set_visible(False)
        func_page.pack_start(self.category_title, False, False, 0)

        self.func_store = Gtk.ListStore(str)
        self.func_view = Gtk.TreeView(model=self.func_store)
        renderer_func = Gtk.CellRendererText()
        column_func = Gtk.TreeViewColumn("功能", renderer_func, text=0)
        self.func_view.append_column(column_func)
        self.func_view.set_activate_on_single_click(True)
        self.func_view.connect("row-activated", self.on_func_row_activated)

        scrolled_func = Gtk.ScrolledWindow()
        scrolled_func.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled_func.set_vexpand(True)
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
            "设置管理员密码": "set_admin_password",
            "校准设备": "calibrate_joystick",
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
            "Watt Toolkit (Steam++)": "install_watt_toolkit",
            "安装/卸载插件商店": "install_remove_plugin_store",
            "ToMoon 插件": "install_tomoon",
            "LSFG-VK插件": "install_decky_lsfg_vk",
            "Framegen插件": "install_decky_framegen",
            "安装/重装 Clover 引导": "clover_install_or_reinstall",
            "小黄鸭软件": "install_yellow_duck_software",
            "更新已安装应用": "update_installed_apps",
            "卸载已安装应用": "uninstall_apps"
        }

        self.base_category_functions = {
            "📌 支持和维护": [],
            "🛠 系统优化": [
                "安装国内源", "调整虚拟内存", "修复磁盘写入错误",
                "清理hosts缓存", "设置管理员密码", "校准设备",
                "Steam缓存管理"
            ],
            "📦 软件安装": [
                "AnyDesk", "ToDesk", "WPS Office", "QQ",
                "微信", "QQ音乐", "百度网盘",
                "Edge浏览器", "Google浏览器"
            ],
            "🌐 网络工具": [
                "UU加速器插件", "迅游加速器插件",
                "Watt Toolkit (Steam++)"
            ],
            "🎮 插件相关": [
                "安装/卸载插件商店", "ToMoon 插件",
                "LSFG-VK插件", "Framegen插件"
            ],
            "🔄 引导管理": [
                "安装/重装 Clover 引导"
            ],
            "📥 更新软件": [
                "更新已安装应用", "卸载已安装应用"
            ],
            "🗑 其他": [
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
        category = model.get_value(iter_, 0)

        if category == "📌 支持和维护":
            self.stack.set_visible_child_name("about")
            self.category_title.set_visible(False)
            return

        self.stack.set_visible_child_name("func")
        if category == "🛠 系统优化":
            title_text = f"<big><b>{category} [{self.system_type}]</b></big>"
        else:
            title_text = f"<big><b>{category}</b></big>"
        self.category_title.set_markup(title_text)
        self.category_title.set_visible(True)

        self.func_store.clear()

        funcs = self.base_category_functions.get(category, [])
        if category == "🛠 系统优化" and self.system_type == "双系统":
            funcs = funcs + ["修复引导", "修复互通盘"]

        for func_name in funcs:
            self.func_store.append([func_name])

        self.func_view.show_all()

    def on_func_row_activated(self, treeview, path, column):
        model = treeview.get_model()
        iter_ = model.get_iter(path)
        func_name = model.get_value(iter_, 0)

        if not func_name:
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
            "点击功能将打开独立任务窗口执行。"
        )
        help_dialog.run()
        help_dialog.destroy()

    def on_quit_clicked(self, button):
        self.destroy()

# ============================================================================
# 启动
# ============================================================================

def main():
    if not VTE_AVAILABLE:
        warn_dialog = Gtk.MessageDialog(
            None,
            Gtk.DialogFlags.MODAL,
            Gtk.MessageType.WARNING,
            Gtk.ButtonsType.OK,
            "VTE 终端组件未安装，将使用文本输出模式（不支持交互输入）。\n"
            "建议安装 vte3 以享受完整终端交互体验。"
        )
        warn_dialog.run()
        warn_dialog.destroy()

    window = MainWindow()
    window.connect("destroy", Gtk.main_quit)
    window.show_all()
    Gtk.main()

if __name__ == "__main__":
    main()
