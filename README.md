

# SteamDeck 工具箱

一个专为 SteamDeck 打造的一站式系统管理与增强工具，集成 **系统优化、软件安装、网络加速、双系统支持、游戏增强** 等 29 项实用功能，全面覆盖日常使用与进阶调校需求。无论您是初次使用还是资深玩家，都能快速找到所需工具，让 SteamDeck 更好用、更好玩。

## 主要功能

### 🔧 系统优化
- 国内源配置
- 虚拟内存调整
- 磁盘写入错误修复
- hosts 缓存清理
- 管理员密码设置

### 📦 软件管理
一键安装常用应用：
- QQ、微信、WPS
- Edge/Chrome 浏览器
- 百度网盘、QQ音乐
- 应用更新与卸载

### 🌐 网络工具
- UU/迅游加速器插件
- ToMoon 网络优化
- AnyDesk 远程协助
- ToDesk 远程协助

### 🔄 双系统支持
- 引导修复
- Windows-SteamOS 互通盘配置
- 双系统维护

### 🎮 游戏增强
- 摇杆校准
- 插件商店/宝葫芦管理
- 小黄鸭插件/软件
- Steam 缓存清理

### 📁 便捷工具
- 虚拟内存调整
- 工具箱自更新
- 已安装应用管理
- 缓存清理

## 一键安装

在 Konsole 中执行以下命令即可安装：

```bash
curl -L https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_toolbox.sh -o steamdeck_toolbox.sh && chmod +x steamdeck_toolbox.sh && konsole --hold -e ./steamdeck_toolbox.sh
```

## 项目结构

```
steamdeck_toolbox/
├── steamdeck_toolbox.sh    # 主程序脚本
├── LICENSE                 # 开源协议
└── README.md               # 说明文档
```

## 技术特性

- **彩色终端界面**：红、绿、黄、蓝、青、紫六种颜色输出
- **智能检测**：自动识别系统类型
- **目录管理**：自动创建安装目录、桌面快捷方式、备份目录
- **自更新功能**：支持工具箱在线更新
- **网络检测**：自动检测网络连接状态

## 系统要求

- Steam Deck (运行 SteamOS)
- Konsole 终端模拟器
- 管理员权限（部分功能需要）

## 许可证

本项目采用 [Apache License 2.0](LICENSE) 开源协议。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来完善这个项目。

## 联系方式

- 项目地址：https://gitee.com/Zhucy2100/steamdeck_toolbox
- 问题反馈：https://gitee.com/Zhucy2100/steamdeck_toolbox/issues

---

让您的 SteamDeck 更强大、更易用！🎮