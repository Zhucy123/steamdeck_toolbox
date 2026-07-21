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
