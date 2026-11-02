# Steam Deck Toolbox

[中文](./README.md)

An all-in-one system management and enhancement toolkit for Steam Deck. It covers system optimization, boot management, software installs, network acceleration, dual-boot helpers, game enhancements, and 40+ practical tools for daily use and advanced tweaking.

> **Version: v1.11.4** | Updated: 2026-11-02
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

2026-11-02 (v1.11.4)
[UX improvements]
- Streamlined the "Update all apps" output
  - Removed the three-line "skipped refreshing the appstream catalog" note. In practice `flatpak update` does not refresh appstream by default (only with the explicit `--appstream` flag), so the step never existed and the note was redundant
  - When updates exist, appstream is likewise not involved; the "If it hangs on Updating appstream data" line in the timeout message is gone too, keeping only useful info such as partially downloaded data being kept
  - The completion message is now just "✓ All apps updated"

2026-11-02 (v1.11.3)
[Bug fixes]
- Fixed taskbar icon disappearing after the startup update check (show main window first; unify WM_CLASS / StartupWMClass)

2026-11-02 (v1.11.2)
[UI improvements]
- Sidebar trimmed to 7 items: Support, Changelog, System Optimization, Plugins, Software, Network, Update & Uninstall
  - Compat / emergency / Clover & dual-boot repair fold into System Optimization groups (collapsed by default)
  - Removed standalone Game Compatibility, Emergency, Boot & Dual Boot, and Other
  - Yellow Duck moves under Software Installation
- Launch still defaults to Support & Maintenance

2026-11-02 (v1.11.1)
[UI improvements]
- IA reshuffle: daily optimization → game compatibility → plugins → software → network → emergency → boot/dual-boot → uninstall → other
  - System Optimization no longer holds emergency/compat; new Game Compatibility and Emergency & Recovery
  - Boot becomes Boot & Dual Boot and hosts dual-boot repair tools
  - Third-party game platforms move under Software Installation; Other keeps Yellow Duck etc.
- Groups still start collapsed; launch still opens Support & Maintenance

2026-11-02 (v1.11.0)
[New features]
- Expanded GE-Proton Manager into Compatibility Layer Manager (GE / Proton-CachyOS SLR / DW Proton)
  - CachyOS installs the SLR x86_64 package into compatibilitytools.d
  - DW Proton uses dawn-winery/dwproton-mirror; anime/specific-game note; separate from CheatDeck
  - Reuses GE mirrors, checksums, and stage-then-move installs (tar.xz)
- Plugins: CheatDeck (CheatDeck.zip only), Decky check, Developer mode + ToS disclaimer
- System Optimization: Emergency Reset for Steam config and Gamescope/Game Mode with backup under ~/steamdeck_toolbox_backups/

2026-11-02 (v1.10.0)
[UI improvements]
- Main window now sizes itself to the display instead of a fixed 1100x720
  - Reason: on a Steam Deck (1280x800, usable workarea 1280x746) the content height of 720 plus roughly 40px of title bar totals 760px, exceeding the usable height, so the bottom was pushed off screen
  - On startup it reads the monitor workarea (panel already excluded) and picks one of three tiers by usable height:
    - Small/handheld (usable height < 900): 86% x 92%, cap 1400x820
    - 1K (usable height < 1150): 82% x 88%, cap 1700x1000
    - 2K/4K large screens: 72% x 78%, cap 2000x1300
  - Results: handheld 1100x686, 1K 1574x915, 2K 1843x1092, 4K 2000x1300 -- neither full-screen nor too small to read
- The task window (terminal) follows the same adaptive sizing, one notch smaller than the main window (scale factor 0.8): handheld 880x549, 1K 1259x732, 2K 1474x873
- Uses workarea rather than raw resolution, with a fallback so the window never exceeds the usable area even on very small screens; if monitor info is unavailable it falls back to the original 1100x720

2026-11-02 (v1.9.9)
[Bug fixes]
- Fixed "Install ToDesk" failing on reinstall with "could not commit transaction (conflicting files) / exists in filesystem /opt/todesk/bin/..."
  - Root cause: the machine was in an orphaned state where pacman no longer had a todesk-bin record (interrupted uninstall, pruned database, or a manual extraction install) but files such as /opt/todesk were still on disk. The old cleanup only ran "if pacman has a record", which was false here, so cleanup was skipped entirely and `pacman -U` refused because the files it wanted to write already existed
  - The installer now clears orphaned leftovers first: when the package is unregistered but files remain, it stops the service, kills holding processes, then removes /opt/todesk, /usr/bin/todesk, todeskd.service, todesk.desktop, the licenses directory, ToDesk icons under hicolor, and any stale pacman db.lck before installing
  - Cleanup is verified afterwards: any remaining leftovers are listed explicitly with a manual-removal hint instead of letting pacman raise a cryptic conflict
  - Only ToDesk's own icons are removed (other software under hicolor is untouched), and machines with a properly registered pacman package skip this logic entirely

2026-11-02 (v1.9.8)
[UI improvements]
- Main window is now a SteamOS / OLED-style master-detail layout: a persistent left category rail and an immediate right-hand detail pane (no more 3×3 home tiles then a second page)
- Dark theme uses near-black charcoal with purple/magenta selection and cyan accents; light theme remains fully usable
- Function row cards no longer sit under the vertical scrollbar (chevron and scrollbar stay apart)
- On launch, "Support & maintenance" is selected by default and its about/maintenance content is shown right away (same as clicking the rail item)
[Notes]
- Language switching, themes, global search, danger confirms, the task window, and script logic are unchanged
- Made by: Zhucy

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
