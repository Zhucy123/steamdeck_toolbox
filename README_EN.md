# Steam Deck Toolbox

[中文](./README.md)

An all-in-one system management and enhancement toolkit for Steam Deck. It covers system optimization, boot management, software installs, network acceleration, dual-boot helpers, game enhancements, and 40+ practical tools for daily use and advanced tweaking.

> **Version: v1.9.7** | Updated: 2026-11-01
> Made by: Zhucy

## 🚀 One-click install

Run this in Konsole:

```bash
curl -L decktool.pages.dev/i | sh
```

(If that fails, use the Gitee installer below.)

```bash
curl -L https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/install_gui.sh | sh
```

> Note: the install commands above are the same ones used by the Chinese README / Gitee distribution. This repository’s primary mirror for China is Gitee; GitHub may lag or differ for some releases.

## 🔄 Updates

- Open the toolbox; it checks for updates on startup (built-in self-update)

## 📝 Changelog

2026-11-01 (v1.9.7)
[New features]
- Added UI language switching (Chinese / English): switch anytime from the top bar; preference is saved to the `language` field in `~/.config/steamdeck_toolbox/config.json` and restored on next launch
- In English mode, UI strings, category/feature names, the changelog, dialog buttons (including Yes / No / OK), and user-visible embedded terminal script output are all English; Chinese mode stays Chinese
- Help page follows the language: Chinese keeps the Bilibili nudge entry; English shows a clickable X link [@AlanWake2100](https://x.com/AlanWake2100)
[UI improvements]
- Credits updated to Made by / 制作人 **Zhucy** in both languages
- Dangerous-confirm and other dialogs no longer rely on system-locale Yes/No/OK labels; they follow the toolbox language instead
- Note: the system `sudo` password prompt still follows the OS language; that is expected and not toolbox UI text

2026-10-27 (v1.9.6)
[Bug fixes]
- Fixed “Switch software source” falsely warning that the flathub public key could not be downloaded
  - Cause: every switch unconditionally re-downloaded the key from `dl.flathub.org`, which is often unreachable, so a yellow warning appeared every time. The key only needs to be imported once and is already present on normal devices (`/var/lib/flatpak/repo/flathub.trustedkeys.gpg`); the feature itself worked — the warning was misleading
  - Now check for a usable local key first (and verify with `gpg` that it really contains the Flathub key). If present, skip the download and print no warning
  - Only download when missing, trying Official → USTC → CERNET in order
  - Warn only when all sources fail, and clearly state the consequence (`Could not find public key`) plus two manual fix commands

2026-10-26 (v1.9.5)
[Bug fixes]
- Fixed “Update all apps” hanging for a long time after “No updates.”
  - Root cause: `flatpak update` refreshes appstream metadata from `dl.flathub.org` (~10MB) after the update check; that host is often unreachable and retries for minutes
  - Appstream is display metadata only; the toolbox now skips it, uses `remote-ls` for the update check, then runs `update` as needed
  - When everything is current it clearly says so instead of hanging; failed online checks fall back to the local cache; downloads have a 20-minute timeout
[Improvements]
- “Install China source” became “Switch software source (China / Official)” with a menu: 4 China mirrors + restore Official, with validation and auto-rollback on failure

2026-10-26 (v1.9.4)
[Bug fixes]
- Fixed “GE-Proton Manager” falsely reporting extract failure after upstream renamed artifacts with an architecture suffix (`GE-Proton11-11-x86_64`); install dir / Steam display name still use the tag without the suffix
- Truncated mirror downloads are now caught with size + sha512 checks before extract; clearer error messages for incomplete download / checksum / bad archive layout

2026-10-26 (v1.9.3)
[Improvements]
- Watt Toolkit (Steam++) install now includes a “Trust certificate” step (root cert into the system trust store; `/etc/hosts` made writable for accelerator host edits)
- Separate “Trust certificate” menu item under Network tools; uninstall can optionally undo those system changes

2026-10-26 (v1.9.2) / 2026-10-25 (v1.9.1–v1.9.0)
[Improvements]
- ToDesk install/detect/uninstall flow rewritten: pacman package or `/opt/todesk` manual install, reinstall / exit / uninstall options, cleanup of desktop/autostart leftovers without deleting user data by default
- No longer runs third-party install shell scripts; installs via community `todesk-bin` package after integrity checks

Older entries (UI polish for dialogs/CSD, system health check, etc.) are available in the in-app Changelog dialog.

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
- WPS Office, QQ, WeChat, QQ Music, Baidu Netdisk, Microsoft Edge, Google Chrome, Fcitx 5, and more

### Game extras & Decky plugins
- Decky Loader plugin store install / uninstall
- ToMoon / Freedeck / LSFG-VK / Framegen plugins (install / update / uninstall)
- Lossless Scaling helper

### Third-party game platforms (install / uninstall)
- Ubisoft Connect, Epic, Battle.net

### App management
- Update installed Flatpak apps
- Uninstall installed apps (WPS / QQ / WeChat / QQ Music / Baidu Netdisk / Edge / Chrome / AnyDesk / ToDesk / Fcitx 5 and other Flatpaks)

### Toolbox itself
- UI language switch (Chinese / English, remembered)
- Dark / light / follow-system theme (remembered)
- Auto update check on launch with one-click upgrade
