# SteamDeck 工具箱

[English](./README_EN.md)

一个专为 Steam Deck 打造的一站式系统管理与增强工具，集成系统优化、引导管理、软件安装、网络加速、双系统支持、游戏增强等 40 余项实用功能，全面覆盖日常使用与进阶调校需求。

> **版本：v2.1.2** | 更新日期：2026-11-10
> 制作人：Zhucy

## 🚀 一键安装

在 Konsole 中执行以下命令即可安装：

```bash
curl -L decktool.pages.dev/i | sh
```
（如果这个失效就用下面的）
```bash
curl -L https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/install_gui.sh | sh
```

## 🔄 更新方式

- 打开工具箱后启动时自动检查更新（内置自更新）

## 📝 更新日志

完整更新记录请查看 **[CHANGELOG.md](./CHANGELOG.md)**。

## ✨ 特性亮点

- **中英界面**：顶栏一键切换中文 / English，偏好自动保存，重启后保持
- **深色 / 浅色主题**：一键切换深色、浅色或跟随系统，偏好自动保存，重启后保持
- **智能系统检测**：自动识别单 / 双系统，部分功能（修复引导、互通盘）仅对双系统用户显示  
- **图形化引导管理**：支持 Clover 引导的安装、重装，并附带“引导文件配置”工具箱（主题、超时、默认系统等）  
- **双系统专属支持**：Clover 启动顺序修复、Windows–SteamOS 数据互通盘自动挂载  
- **一键软件管理**：涵盖办公、通讯、浏览器、云盘、音乐等常用应用（Flatpak / 脚本安装）  
- **深度性能优化**：虚拟内存调整（CryoByte33 方案 / 传统 Swap / ZRAM）、GE-Proton 兼容层管理、Steam 着色器与兼容数据缓存管理、Hosts 缓存清理  
- **游戏增强组件**：摇杆与扳机校准、LSFG‑VK / Framegen / Freedeck 插件、小黄鸭软件（Lossless Scaling）  
- **第三方游戏平台**：支持安装育碧（Ubisoft Connect）、Epic、战网（Battle.net）等游戏平台  
- **持续更新**：启动时自动检测更新，支持一键升级，无需手动下载  

## 📋 功能列表

### 系统优化与修复
- 切换软件源（4 个国内 Flatpak 镜像可选，也可恢复官方源）  
- 虚拟内存调整（CryoByte33 推荐 / Swap 文件 / ZRAM / 清理所有配置）  
- 修复磁盘写入错误（NTFS 分区脏标志修复）  
- 清理 hosts 缓存   
- 校准设备（摇杆 + 扳机）   
- Steam 缓存管理器（图形界面，支持删除着色器缓存与 Proton 兼容数据）   
- GE-Proton 管理（安装 / 卸载 GE 兼容层）  

### 引导管理（单 / 双系统通用）
- 安装 / 重装 Clover 图形化引导管理器  
- （安装后自动生成“引导文件配置”桌面工具，支持主题、超时、默认系统等高级设置）  

### 双系统支持（仅双系统用户可见）
- 修复引导（自动将 Clover 设为 UEFI 第一启动项） 
- 修复互通盘（自动挂载 Windows 与 SteamOS 共享分区，写入 fstab） 

### 网络与远程工具
- UU 加速器插件  
- 迅游加速器插件  
- 奇游联机宝加速插件  
- Watt Toolkit (Steam++)（含加速证书信任、卸载时可选清除系统改动）  
- AnyDesk 远程协助  
- ToDesk 远程协助  
- AskLink 远程协助  

### 常用软件安装
- 安装 Flatpak 应用：图形界面一次勾选安装多个应用，已安装的自动隐藏，共 37 个常用应用
  - 通讯：微信、QQ、钉钉、飞书、腾讯会议、Telegram、Discord
  - 浏览器：Microsoft Edge、Google Chrome、Firefox
  - 影音：QQ 音乐、网易云音乐、VLC、Spotify
  - 网盘与下载：百度网盘、迅雷
  - 办公与笔记：WPS Office、LibreOffice、Thunderbird、Obsidian、Joplin
  - 创作工具：OBS Studio、GIMP、Krita、Inkscape、Audacity、Blender
  - 远程控制：RustDesk、Remmina
  - 游戏工具：Lutris、Heroic、Prism Launcher、RetroArch、PCSX2、Dolphin
  - 系统工具：Flatseal、Fcitx 5（含中文输入法插件）

### 游戏增强与 Decky 插件  
- 插件商店（Decky Loader）安装 / 卸载 
- ToMoon 插件（安装 / 更新 / 卸载） 
- Freedeck 插件（安装 / 更新 / 卸载）  
- LSFG‑VK 插件（安装 / 更新 / 卸载）  
- Framegen 插件（安装 / 更新 / 卸载）  
- 小黄鸭软件（Lossless Scaling，帧生成工具） 

### 第三方游戏平台（安装 / 卸载）
- 育碧平台（Ubisoft Connect）  
- Epic 平台  
- 战网平台（Battle.net）  

### 应用管理与维护
- 更新已安装应用（Flatpak 全局更新）
- 卸载已安装应用：AnyDesk、ToDesk 各有独立入口，其余全部 Flatpak 应用（含 WPS Office / QQ / 微信 / QQ音乐 / 百度网盘 / Edge / Chrome / Fcitx 5）统一在「卸载其他已安装应用」的图形界面里勾选卸载

### 工具箱自身
- 界面语言切换（中文 / English，自动记忆）  
- 深色 / 浅色主题切换（深色 / 浅色 / 跟随系统，自动记忆）  
- 启动时自动检查更新，支持一键更新（无需手动下载）
