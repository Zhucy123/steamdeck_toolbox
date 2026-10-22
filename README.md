# SteamDeck Toolbox

An all-in-one system management and enhancement tool built for the Steam Deck. It integrates 40+ practical features — system optimization, boot management, software installation, network acceleration, dual-boot support, gaming enhancements, and more — covering everything from everyday use to advanced tuning.

> **Version: v1.9.5** | Updated: 2026-10-22
> Made by Zhucy123

## 🚀 One-Click Installation

Run the following command in Konsole to install:

```bash
curl -L https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/install_gui.sh | sh
```

## 🔄 Updating

- The toolbox checks for updates automatically at startup (built-in self-update)

## 📝 Changelog

2026-10-22 (v1.9.4)
**Interface**
- Fixed the remaining light strip above dialogs in dark mode: on KDE/KWin the window manager draws the dialog title area with the system (light) colours, which CSS cannot reach. Client-side decorations are now forced so GTK paints it and the app theme applies
- Fixed window corners: all four corners are now rounded (previously only the top two were — the bottom status bar painted an opaque square over them)

2026-10-22 (v1.9.3)
**Interface**
- The X handle in the Help dialog is now a real clickable link (opens https://x.com/AlanWake2100)
- Fixed a white strip above the title bar when running in dark mode on a light desktop theme: the client-side decoration frame and GTK theme variant now follow the app theme

2026-10-22 (v1.9.2)
**Interface**
- Help dialog: the social link now points to X (Twitter) — "Follow AlanWake (@AlanWake2100) on X for updates"
- All dialog buttons are now English regardless of system locale: GTK built-in button sets (OK / Yes-No) were replaced with explicit English labels, and an English locale is forced for the process

2026-10-22 (v1.9.1)
**Bug Fixes**
- Self-update now fetches from GitHub only: the update check and self-update read `VERSION` and the script body from the official GitHub repository
- Replaced the remaining Gitee references:
  - Watt Toolkit (Steam++) download now uses the official GitHub release (`BeyondDimension/SteamTools`) instead of the Gitee mirror
  - ToDesk notice now points to the GitHub project page
  - Changelog wording no longer references Gitee

2026-10-22 (v1.9.0)
**International Release**
- The entire toolbox is now English-only: all UI text, menus, dialogs, status messages, terminal output, comments and documentation translated to English
- Added an English README and translated all installer scripts (`install_gui.sh`, `steamdeck_toolbox.sh`, `install_decky_loader.sh`, `install_steamcommunity_302.sh`)
- Default download source changed to the official GitHub repository: https://github.com/Zhucy123/steamdeck_toolbox

**Feature Removals**
- Removed the "Install Chinese Source" feature (China-only Flatpak mirror configuration)
- Removed all third-party China mirrors (`gh-proxy.com`, `gh.3w.pm`, `cors.isteed.cc`, `ghproxy.net`): all downloads now use the official GitHub source only, and the mirror selection menus were removed
- Removed the "Others" category together with its two features:
  - Yellow Duck Software (Lossless Scaling installer)
  - Third-Party Game Platforms (Ubisoft Connect / Epic / Battle.net install and uninstall)

2026-10-19 (v1.8.2)
**Feature Integration**
- "System Health Check" is now a unified troubleshooting entry point: boot-related issues are repaired inline (no more jumping to the standalone "Repair Boot" screen and losing context), and mount-related issues are fixed inline by writing fstab entries for automatic mounting
- "Repair Boot" now covers the key capabilities it was missing: previously, when the Clover boot entry was missing it only reported an error and exited (so it could not actually recover a "lost boot"); it now probes the ESP dynamically first, then automatically rebuilds the Clover / SteamOS boot entries and sets Clover as the first boot entry
- "Repair Boot" no longer hardcodes `/dev/nvme0n1p1` and partition 1 of `/dev/nvme0n1`: it now locates the ESP dynamically via `findmnt` + the EFI partition type GUID, supporting eMMC / SATA models and different partition numbers
- Removed duplicate implementations shared by the health check, "Repair Boot", and "Repair Shared Drive": boot order adjustment and boot entry rebuilding now share a single code path; inline repairs from the health check no longer clear the screen or reopen the UI
- The health check now backs up fstab automatically before writing mount fixes (a corrupted fstab can keep the system from booting next time)

**Bug Fixes**
- Fixed "Repair Boot" being unable to distinguish "file missing" from "read failure" when checking whether Clover files exist, which could mislead users into reinstalling Clover; it now uses a three-state check and, when permissions are insufficient, clearly notifies the user and still attempts to register the boot entry
- Removed 3 redundant repair functions no longer used by the health check (formerly `hc_fix_clover_entry` / `hc_fix_steamos_entry` / `hc_fix_boot_order`) to avoid two parallel implementations

2026-10-19 (v1.8.1)
**Bug Fixes**
- Fixed misleading conclusions from the system health check: even when only "attention" items were present (environment differences such as the Windows boot entry being taken over by Clover or low ESP free space), it still printed "the above issues require manual handling", making users think the system was faulty; it now decides based on the number of "abnormal" items, and when there are none it clearly shows "✅ Conclusion: no abnormalities found — boot and mounts are normal", explaining that the flagged items do not affect usage
- Fixed health check item 3, "Clover boot file integrity", still reporting "unable to read EFI directory" even after the sudo password had been entered: the original code used a normal-user `[ -d ]` test to determine the EFI directory location, but `/esp` is owned by root with mode 700, so a normal user can never see it, causing a wrong path decision and a failed sudo probe
- EFI directory detection now probes the two candidate paths `/esp/EFI` and `/esp/efi/EFI` with sudo in turn, supporting different models and system layouts; if neither exists, it distinguishes "directory genuinely missing" from "no sudo permission" and prints the actual contents of the ESP root directory for troubleshooting

2026-10-19 (v1.8.0)
**New Features**
- Added "System Health Check" (visible to dual-boot users): designed to troubleshoot missing drives, lost boot entries, and failed mounts after SteamOS updates, covering 6 categories and 18 checks in total
  - **ESP partition**: whether it is detected, mount status, free space (Clover needs about 15 MB)
  - **UEFI boot entries**: whether the Clover / SteamOS / Windows boot entries exist, and whether Clover is the first boot entry
  - **Clover boot files**: whether `cloverx64.efi`, `config.plist`, `BOOTX64.EFI` and their `.orig` backups are complete
  - **Windows partition**: whether it exists, whether it is mounted, and whether the Windows system file structure is complete
  - **/etc/fstab**: whether entries point to partitions that still exist, and whether there are failed mount units
  - **System and boot services**: SteamOS read-only mode, and whether the Clover boot guard service (`clover-bootmanager`) is enabled and running
- The health check is read-only; after finding issues it lists the items that can be fixed automatically and only runs repairs after confirmation
- One-click fixes: rebuild missing Clover / SteamOS boot entries, set Clover as the first boot entry, enable the Clover boot guard service, and comment out invalid fstab entries (with automatic backup before modification)

**Bug Fixes**
- ESP detection in the health check no longer hardcodes `/dev/nvme0n1p1`: it now locates the ESP dynamically via `findmnt` + the EFI partition type GUID, supporting eMMC / SATA models and different partition numbers
- Distinguishes "file genuinely missing" from "cannot read without sudo permission": when permission is insufficient it clearly prompts and skips, instead of falsely reporting every file as missing

2026-10-19 (v1.7.7)
Fixed dual-boot systems being misdetected as single-boot: detection now uses multiple criteria — a Windows EFI boot entry, an NTFS partition labeled Windows, or `Windows\Program Files` / `Windows\Users` directory structures inside an NTFS partition — so any one match identifies a dual-boot setup, while Clover-only single-boot machines are still classified correctly.

2026-10-19 (v1.7.6)
Added a copy button, right-click menu, and keyboard shortcuts (Ctrl+Shift+C / Ctrl+Shift+V / Ctrl+Shift+A) to the embedded terminal; added maximize / restore and free resizing to the task window, which is no longer forced modal; fixed the missing sudo in the printed command for restoring official package sources.

2026-10-19 (v1.7.5)
Unified the GitHub download sources and fixed download source selection menus, Clover clone source selection, and Flatpak source configuration and validation issues.

2026-10-19 (v1.7.4)
A large batch of bug fixes: duplicate fstab swap entries, unconditional read-only mode restore, swapfile / ZRAM persistence, Steam cache scanning, Clover install rollback and dynamic ESP detection, atomic self-update, and dangerous-operation confirmations.

2026-10-19 (v1.7.3)
Fixed unreadable text in dangerous-operation dialogs and incorrect text colors in native popups (drop-down menus, context menus, tooltips) under the light theme.

2026-10-19 (v1.7.2)
Added dark / light theme switching with a follow-system mode and automatic saving; fixed vte3 keyring import, NTFS dirty-flag detection, shared-drive fstab persistence, and theme self-pollution issues.

2026-09-09 (v1.7.1)
Introduced a new Steam Deck-style theme (dark blue-black base with Steam blue highlights, rounded cards, taller touch-friendly list rows), panel titles, rounded search results, and a task window title bar with a dark terminal color scheme.

2026-09-06 (v1.7.0, includes v1.6.9 changes)
Added a HeaderBar, global feature search, a task runtime timer, dangerous-operation confirmations, and a bottom status bar; fixed task cancellation, read-only mode restore, hosts cleanup, self-update validation, and version comparison.

2026-08-07 (v1.6.8)
Adjusted the version comparison logic for features installed from GitHub.

2026-08-05 (v1.6.7)
Fixed several bugs and improved the logic of several features.

2026-08-04 (v1.6.6, includes v1.6.4-v1.6.5 changes)
Added installation of third-party game platforms (currently Ubisoft, Epic, and Battle.net).

2026-08-01 (v1.6.3, includes v1.6.2 changes)
Improved the shortcut removal step when uninstalling installed apps and added a prompt asking whether to delete app data.

2026-07-31 (v1.6.1)
Added GE-Proton management to install / uninstall GE compatibility layers.

2026-07-30 (v1.6.0, includes v1.5.7-v1.5.9 changes)
Added Freedeck plugin installation, along with bug fixes and feature improvements.

2026-07-29 (v1.5.6, includes v1.5.2-v1.5.5 changes)
Added Fcitx 5 installation and continued fixing bugs while adjusting the logic of several features.

2026-07-27 (v1.5.1, includes v1.5.0 changes)
Fixed several bugs and improved several features.

2026-07-26 (v1.4.9)
Added AskLink remote assistance installation.

2026-07-25 (v1.4.8, includes v1.3.9-v1.4.7 changes)
Switched documentation from text-only to illustrated guides, removed the admin password feature, and added the Qiyou acceleration plugin.

2026-07-18 (v1.3.8, includes v1.3.7 changes)
Replaced the steamcommunity 302 feature with Watt Toolkit (Steam++); improved parts of the plugin store, LSFG-VK, and Framegen installation logic; changed joystick calibration to device calibration and added trigger calibration.

2026-07-09 (v1.3.6)
Reworked the shared-drive repair logic to be more generic.

2026-07-08 (v1.3.5, includes v1.3.4 changes)
Removed the "remote connection help" feature and adjusted the download source order for GitHub-installed features.

2026-06-30 (v1.3.2)
Fixed a bug in AnyDesk installation.

2026-06-28 (v1.3.1)
Fixed a bug in the virtual memory size adjustment feature.

2026-06-27 (v1.3.0)
Added the "remote connection help" feature and changed AnyDesk installation to use the official website.

2026-06-03 (v1.2.7)
Added Clover boot manager install / reinstall with multiple improvements.

2026-06-02 (v1.2.6)
Updated the GitHub installation logic to support choosing between pre-release and stable versions.

2026-05-31 (v1.2.4, includes v1.1.9, v1.2.0, v1.2.1 changes)
Added LSFG-VK and Framegen plugin installation, improved the plugin store installation steps, and adjusted several Steam Deck cache manager parameters.

2026-05-30 (v1.1.8)
Adjusted the auto-update logic.

2026-05-28 (v1.1.8, includes v1.1.7 changes)
Changed the plugin store to install from GitHub and updated the auto-update steps at startup.

2026-03-17 (v1.1.2)
Removed the "install / uninstall Baohulu" feature because Baohulu is no longer maintained.

2026-03-05 (v1.1.1)
Switched ToMoon installation to a clone-based install.

2026-03-02 (v1.1.0)
Switched the plugin store implementation to a clone-based install.

2026-01-21 (v1.0.9)
Added Steam Community 302 installation.

2026-01-16 (v1.0.8)
Improved the text output of the virtual memory size adjustment feature.

2026-01-11 (v1.0.7)
Improved the virtual memory size adjustment feature.

First released on GitHub with no detailed changelog; release date: 2026-01-01.

## ✨ Highlights

- **Dark / light themes**: switch between dark, light, or follow-system with one click; preferences are saved automatically and persist across reboots
- **Smart system detection**: automatically identifies single / dual-boot setups; some features (Repair Boot, Shared Drive) are shown only to dual-boot users
- **Graphical boot management**: install and reinstall the Clover boot manager, plus a "Boot Configuration" toolbox (theme, timeout, default system, etc.)
- **Dual-boot exclusive support**: Clover boot order repair and automatic mounting of a shared Windows-SteamOS data drive
- **One-click software management**: covers everyday apps for office, messaging, browsers, cloud storage, music, and more (Flatpak / script installation)
- **Deep performance optimization**: virtual memory tuning (CryoByte33 profile / traditional swap / ZRAM), GE-Proton compatibility layer management, Steam shader and compatibility data cache management, and hosts cache cleanup
- **Gaming enhancement components**: joystick and trigger calibration, plus LSFG-VK / Framegen / Freedeck plugins
- **Continuous updates**: automatically checks for updates at startup with one-click upgrade, no manual download required

## 📋 Feature List

### System Optimization & Repair
- Virtual memory tuning (CryoByte33 recommended / swap file / ZRAM / clear all configurations)
- Fix disk write errors (NTFS partition dirty flag repair)
- Clean hosts cache
- Device calibration (joysticks + triggers)
- Steam cache manager (GUI; delete shader caches and Proton compatibility data)
- GE-Proton management (install / uninstall GE compatibility layers)

### Boot Management (single / dual-boot)
- Install / reinstall the Clover graphical boot manager
- (Automatically creates a "Boot Configuration" desktop tool after installation, supporting theme, timeout, default system, and other advanced settings)

### Dual-Boot Support (visible to dual-boot users only)
- Repair Boot (automatically sets Clover as the first UEFI boot entry)
- Repair Shared Drive (automatically mounts the shared Windows-SteamOS partition and writes it to fstab)

### Network & Remote Tools
- UU accelerator plugin
- Xunyou accelerator plugin
- Qiyou acceleration plugin
- Watt Toolkit (Steam++)
- AnyDesk remote assistance
- ToDesk remote assistance
- AskLink remote assistance

### Common Software Installation
- WPS Office
- QQ
- WeChat
- QQ Music
- Baidu Netdisk
- Microsoft Edge
- Google Chrome
- Fcitx 5 and more

### Gaming Enhancements & Decky Plugins
- Plugin store (Decky Loader) install / uninstall
- ToMoon plugin (install / update / uninstall)
- Freedeck plugin (install / update / uninstall)
- LSFG-VK plugin (install / update / uninstall)
- Framegen plugin (install / update / uninstall)

### App Management & Maintenance
- Update installed apps (global Flatpak update)
- Uninstall installed apps (supports WPS Office / QQ / WeChat / QQ Music / Baidu Netdisk / Edge / Chrome / Google / AnyDesk / Fcitx 5 and other Flatpak apps)

### The Toolbox Itself
- Dark / light theme switching (dark / light / follow system, remembered automatically)
- Automatic update check at startup with one-click update (no manual download required)
