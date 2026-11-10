# Steam Deck Toolbox

[中文](./README.md)

An all-in-one system management and enhancement toolkit for Steam Deck. It covers system optimization, boot management, software installs, network acceleration, dual-boot helpers, game enhancements, and 40+ practical tools for daily use and advanced tweaking.

> **Version: v2.1.2** | Updated: 2026-11-10
> Made by: Zhucy

## 🚀 One-click install

Run this in Konsole:

```bash
curl -L decktools.pages.dev/i | sh
```

(If that fails, use the Gitee installer below.)

```bash
curl -L https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/install_gui.sh | sh
```

## 🔄 Updates

- Open the toolbox; it checks for updates on startup (built-in self-update)

## 📝 Changelog

See **[CHANGELOG_EN.md](./CHANGELOG_EN.md)** for the full release history.

Current version: **v2.1.2** (2026-11-10)

## ✨ Highlights

- **Chinese / English UI**: switch from the top bar; preference is saved across restarts
- **Dark / light theme**: dark, light, or follow system; preference saved
- **Smart dual-boot detection**: single- vs dual-boot aware; Fix Boot / shared disk tools only show for dual-boot users
- **Graphical boot management**: install/reinstall Clover, plus a boot-config helper (theme, timeout, default OS, …)
- **Dual-boot helpers**: Clover boot-order repair, Windows–SteamOS shared disk auto-mount
- **One-click software**: office, chat, browsers, cloud drive, music, and more (Flatpak / scripts)
- **Performance tweaks**: virtual memory (CryoByte33 / Swap / ZRAM), GE-Proton management, Steam shader & compatdata cache tools, hosts cache cleanup
- **Game extras**: stick/trigger calibration, LSFG-VK / Framegen / Freedeck plugins, Lossless Scaling helper
- **Third-party launchers**: Ubisoft Connect, Epic, Battle.net install/uninstall
- **Self-updating**: checks on launch and can upgrade in one click

## 📋 Feature list

### System optimization & repair
- Switch software source (4 China Flatpak mirrors, or restore Official)
- Virtual memory (CryoByte33 / Swap file / ZRAM / clear all configs)
- Fix disk write errors (NTFS dirty flag)
- Clear hosts cache
- Calibrate device (sticks + triggers)
- Steam cache manager (GUI for shader cache & Proton compatdata)
- GE-Proton manager (install / uninstall)

### Boot management (single- and dual-boot)
- Install / reinstall Clover graphical boot manager
- (After install, a desktop “boot file config” tool is created for theme, timeout, default OS, …)

### Dual-boot support (dual-boot users only)
- Fix Boot (set Clover as the first UEFI boot entry)
- Fix shared disk (auto-mount the Windows–SteamOS shared partition and write fstab)

### Network & remote tools
- UU / Xunyou / Qiyou accelerator plugins
- Watt Toolkit (Steam++) (certificate trust; optional system-change cleanup on uninstall)
- AnyDesk / ToDesk / AskLink remote assistance

### Common software
- Install Flatpak Apps: tick several apps in one GUI; already-installed ones are hidden (37 apps)
  - Chat: WeChat, QQ, DingTalk, Feishu, Wemeet, Telegram, Discord
  - Browsers: Microsoft Edge, Google Chrome, Firefox
  - Media: QQ Music, NetEase Cloud Music, VLC, Spotify
  - Cloud & download: Baidu Netdisk, Thunder
  - Office & notes: WPS Office, LibreOffice, Thunderbird, Obsidian, Joplin
  - Creator tools: OBS Studio, GIMP, Krita, Inkscape, Audacity, Blender
  - Remote access: RustDesk, Remmina
  - Gaming: Lutris, Heroic, Prism Launcher, RetroArch, PCSX2, Dolphin
  - System tools: Flatseal, Fcitx 5 (incl. the Chinese input-method add-on)

### Game extras & Decky plugins
- Decky Loader plugin store install / uninstall
- ToMoon / Freedeck / LSFG-VK / Framegen plugins (install / update / uninstall)
- Lossless Scaling helper

### Third-party game platforms (install / uninstall)
- Ubisoft Connect, Epic, Battle.net

### App management
- Update installed Flatpak apps
- Uninstall installed apps: AnyDesk and ToDesk have dedicated entries; every other Flatpak app (incl. WPS / QQ / WeChat / QQ Music / Baidu Netdisk / Edge / Chrome / Fcitx 5) is ticked and removed from the unified "Uninstall Other Installed Apps" GUI

### Toolbox itself
- UI language switch (Chinese / English, remembered)
- Dark / light / follow-system theme (remembered)
- Auto update check on launch with one-click upgrade
