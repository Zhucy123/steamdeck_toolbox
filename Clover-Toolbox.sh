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
