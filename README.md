

# SteamDeck 工具箱

一个专为 SteamDeck 打造的一站式系统管理与增强工具，集成系统优化、软件安装、网络加速、双系统支持、游戏增强等 28 项实用功能，全面覆盖日常使用与进阶调校需求。

## 特性亮点

- **智能系统检测**：自动识别单/双系统，只显示相关功能
- **双系统专属支持**：修复引导、配置互通盘等功能仅对双系统用户开放
- **常用软件全覆盖**：从办公到娱乐，一键安装所需应用
- **性能优化**：虚拟内存调整、摇杆校准等提升游戏体验
- **持续更新**：定期添加新功能和优化

## 功能列表

### 系统优化
- 国内源配置
- 虚拟内存调整
- 磁盘写入错误修复
- hosts 缓存清理
- 管理员密码设置

### 软件管理
- 一键安装常用应用：QQ、微信、WPS、Edge/Chrome 浏览器、百度网盘、QQ音乐等
- 应用更新与卸载
- 已安装应用管理

### 网络工具
- UU/迅游加速器插件
- ToMoon 网络优化
- AnyDesk 远程协助
- ToDesk 远程协助

### 双系统支持（仅双系统用户可见）
- 引导修复
- Windows-SteamOS 互通盘配置
- 双系统维护

### 游戏增强
- 摇杆校准
- 插件商店/宝葫芦管理
- 小黄鸭软件
- Steam 缓存清理

### 便捷工具
- 工具箱自更新
- 缓存清理

## 一键安装

在 Konsole 中执行以下命令即可安装：

```bash
curl -L https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_toolbox.sh -o /tmp/steamdeck_toolbox.sh && chmod +x /tmp/steamdeck_toolbox.sh && /tmp/steamdeck_toolbox.sh
```

## 项目结构

```
steamdeck_toolbox/
├── steamdeck_toolbox.sh    # 主程序脚本
├── LICENSE                 # 许可证文件
└── README.md              # 说明文档
```

## 命令行参数

工具箱支持以下命令行参数：

| 参数 | 说明 |
|------|------|
| `-h` 或 `--help` | 显示帮助信息 |
| `-v` 或 `--version` | 显示版本信息 |
| `-u` 或 `--update` | 更新工具箱 |
| `--check` | 检查网络连接 |

## 系统要求

- Steam Deck 或其他 Linux 系统（基于 Arch Linux）
- 管理员权限（sudo）
- 稳定的网络连接

## 常见问题

**Q: 工具箱支持哪些系统类型？**
A: 工具箱会自动检测系统类型，单系统用户和双系统用户将看到不同的功能选项。

**Q: 安装后如何启动？**
A: 安装完成后，可在应用程序菜单中找到"SteamDeck 工具箱"快捷方式，或在终端中运行 `steamdeck_toolbox` 命令。

**Q: 如何更新工具箱？**
A: 工具箱内置自动更新功能，或在终端中运行 `steamdeck_toolbox --update`。

## 贡献指南

欢迎提交 Issue 和 Pull Request 来帮助改进本项目。

## 许可证

本项目采用 MIT 许可证开源。