# Changelog

> Full release history. The in-app "About / Changelog" page shows the same content.

2026-11-10 (v2.1.2)
[Bug fixes: installer]
- Fixed `install_gui.sh` swallowing both the failure and the stderr of `pacman -Sy`,
  which made a failed vte3 install show only a vague "cannot find database" error.
  Sync output is now shown and the return code is checked; on failure, concrete
  troubleshooting steps are printed.
- Added detection for a stale `[community-3.9]` repository in `/etc/pacman.conf`
  (SteamOS 3.9 merged community into extra, so community-3.9.db no longer exists on the
  server). It now warns early with the fix commands, so users do not mistake it for a
  toolbox or "switch software source" problem.

2026-11-10 (v2.1.1)
[Bug fixes]
- Fixed "Update All Apps" flooding the screen with progress lines: percentage,
  download speed, the progress bar and "Updating X/Y" transition frames now refresh
  in place on a single line, while normal log lines and the completion message still
  get their own lines.

2026-11-09 (v2.1.0)
[Repo-wide audit and fixes]
- Reviewed every toolbox feature (system optimization, dual boot, plugins, software
  installs, network tools, UI and self-update). The confirmed issues below were fixed,
  and missing cross-device dependencies were checked.

[Security: downloads and root execution]
- UU / Xunyou / Qiyou accelerators no longer pipe plaintext-HTTP content straight into a
  root shell: they now use HTTPS, timeouts and HTTP status checks, validate a temporary
  download as shell text, show its origin, then let sudo prompt for the password directly.
  The script preview and extra confirmation were removed to restore the "start installing
  immediately" experience.
- Qiyou: sd.qiyou.cn only serves HTTP (port 443 closed), so the previous HTTPS-only
  change broke it. It now fetches the real installer from static.qiyou.cn over HTTPS, and
  the download helper gained a generic "fall back to HTTP with an explicit warning" path.
- Watt certificate trust no longer makes /etc/hosts world-writable: original permissions
  are saved and restored, CA:TRUE and the SHA256 fingerprint are verified, cleanup is
  fingerprint-based and still runs when the program directory is gone.
- Epic / Battle.net / Ubisoft uninstalls now list the paths to be removed and ask for
  confirmation, so games in default folders are not deleted by accident.

[Installer and task window]
- Installer: temporary file + marker/size/syntax checks before an atomic replace; a
  failure keeps the old version. Read-only mode is restored only when this script
  disabled it, never overriding the user's own writable setting.
- Cancelling a task now shows "Task cancelled" instead of "Task completed"; switching
  features while a task runs asks for confirmation; closing a Flatpak window really
  terminates the process, and a failed addon no longer hides behind a successful main app.
- Added XDG desktop dirs, more terminal emulators, explicit messages when Flatpak is
  missing or a query fails, and more permissive dual-boot detection so Clover users can
  still see the boot and shared-disk repairs.

[Boot and system]
- Fixed the Clover file-check return code being swallowed by `local`, which could
  register a boot entry for a missing file.
- Swap operations no longer delete the old swap when deactivation fails; Steam / Gamescope
  emergency reset aborts immediately if the backup fails, instead of deleting data that
  cannot be restored.
- "Clean Virtual Memory Config" now judges by the actual post-reset ZRAM state, fixing
  the false "ZRAM reset failed" when it had in fact succeeded; NTFS repair failures are
  now reported honestly.
- "Switch Flatpak Software Source" shows the matching preset name (e.g. "USTC - China
  Unicom node") when the current URL matches one of the 5 sources, instead of a raw URL.
- The boot configuration tool now follows the toolbox language: the Chinese UI keeps
  the translated script, the English UI keeps the original community English version.

[Watt Toolkit / software installs]
- Fixed the Watt installer removing its own working directory, which made every later
  sudo print hundreds of "getcwd: cannot access parent directory" lines. Backups now
  live on the same filesystem and copies drop security.capability xattrs, fixing
  "mv: setting attribute ... operation not permitted".
- Certificate trust now writes explicitly to the system anchors dir, refreshes the CA
  bundle and verifies with openssl verify that it really took effect (previously it
  reported success while HTTPS acceleration still failed). hosts and the overall result
  are judged by actual state, no more false success.
- The same version is no longer reported as an update (v3.1.0 vs 3.1.0). ToDesk /
  AnyDesk / Lossless Scaling no longer "remove the old version first" and leave a
  half-install; download, extraction, service start, uninstall and update failures are
  reported honestly.
- "Update All Apps" shows download percentage and speed again: dropped --noninteractive,
  enabled FLATPAK_TTY_PROGRESS, and added a filter that turns in-place redraws into
  clean lines without reintroducing the old garbage characters.

[Plugin Store]
- The Decky service user is no longer hardcoded to deck and the official fields are
  filled in; uninstall stops, disables and removes the systemd unit and CEF markers;
  plugin installs validate a temporary directory before replacing, keeping the old
  plugin on failure.

[Dependencies and compatibility]
- Added checks and hints for GTK3/VTE3, flatpak, p11-kit, openssl, ntfs-3g/ntfsprogs,
  efibootmgr, 7z, jupiter-hw-support and others; these are no longer assumed to exist
  on every distro.

2026-11-08 (v2.0.4)
[Bug fixes: Fix Shared Disk]
- No more "false success" on dirty volumes: when a volume carries the NTFS dirty flag, or Windows used Fast Startup / hibernation and never really shut down, the Linux NTFS driver does not fail -- it quietly mounts the partition read-only. The old code only checked the mount command's exit code, so it reported "✓ Mounted successfully" for a volume where not a single file could be written. It now re-reads the real mount options and, when read-only, says so plainly and gives the steps that actually fix it
- Fixed "Fix Shared Disk" claiming "all partitions are mounted, no action needed" when a partition was mounted read-only: that message made dirty-volume users think everything was fine. A read-only mount now counts as not ready, so the repair continues
- A failed mount no longer just prints "please check the dmesg output": it now reads only the kernel messages produced by this operation (old boot-time errors are no longer surfaced as if they were current) and, on recognising "dirty volume / hibernated / not cleanly unmounted", gives the matching steps -- turn off Fast Startup in Windows and shut down fully, clear the flag with ntfsfix, or mount read-only / forced as an emergency
- The password is now asked once up front and the NTFS tools are checked automatically: a missing ntfs-3g is installed for you (nothing can be mounted without it), while a missing ntfsfix only produces a warning (it is needed solely to clear the dirty flag). You no longer have to install anything by hand
- Fixed the fstab line hardcoding the mount user as uid=1000,gid=1000: on a machine whose user is not deck or whose UID is not 1000, partitions mounted but could not be written to. The ids now come from the current user
- Each volume is pre-checked with ntfs-3g.probe before mounting: if it can be mounted read-write it mounts normally, and if not the reason and remedy are explained up front instead of after discovering a read-only mount

[Bug fixes: Fix Disk Write Errors]
- The flow is now "enter the admin password -> disable SteamOS read-only mode as needed -> install missing tools automatically" instead of immediately telling you that ntfsfix is not installed and leaving the install to you
- Fixed the wrong package name in the install hint: the old version pointed at ntfs-3g, but on Arch/SteamOS ntfsfix and ntfsinfo belong to ntfsprogs, so following that hint left them still missing. The correct package is now installed automatically, and the package-name difference between the two distro families is handled
- ntfsfix is now called with -d (clear the dirty flag), so the flag does not survive the repair and make ntfs3 refuse the mount again
[Repo-wide bug fixes]
- Security: UU / Xunyou / Qiyou no longer pipe a plaintext-HTTP remote script straight into a root shell; they now use HTTPS, timeouts and HTTP status checks, validate a temporary download, show its origin and ask for confirmation before executing
- Security: Watt certificate trust no longer makes /etc/hosts world-writable; original permissions are saved and restored, CA constraints and fingerprints are verified, cleanup is fingerprint-based and still runs when the program directory is already gone
- Security: Epic / Battle.net / Ubisoft uninstalls now list the paths to be removed and ask for confirmation, so games in default folders are not deleted by accident
- Installer: downloads go to a temporary file and only atomically replace the target after marker / size / syntax checks pass; a failure keeps the old version. Read-only mode is restored only when this script disabled it, never overriding the user's own writable setting
- Task window: cancelling now shows "Task cancelled" instead of "Task completed"; switching features while a task runs asks for confirmation; closing a Flatpak window really terminates the process, and a failed addon no longer hides behind a successful main package
- Boot: fixed the Clover file-check return code being swallowed by `local`, which could register a boot entry for a missing file; swap operations no longer delete the old swap when deactivation fails
- Emergency reset: Steam / Gamescope reset aborts immediately if the backup fails, instead of deleting data that cannot be restored
- Plugin Store: the service user is no longer hardcoded to deck and the official fields are filled in; uninstall stops, disables and removes the systemd unit; plugin installs validate a temporary directory before replacing, keeping the old plugin on failure
- Software installs: ToDesk / AnyDesk / Watt / Lossless Scaling no longer "remove the old version first" and leave a half-install; download, extraction, service start, uninstall and update failures are now reported honestly
- Compatibility: added XDG desktop dirs, more terminal emulators, explicit messages when Flatpak is missing or a query fails, and more permissive dual-boot detection so Clover users can still see the boot and shared-disk repairs


2026-11-07 (v2.0.3)
[Bug fixes]
- Fixed "clicking a feature does nothing": when a GTK callback raised, the traceback only went to the terminal, which is invisible when launched from a desktop shortcut — so clicks appeared to do nothing. Any uncaught exception now shows "This action failed and was skipped" and writes the full traceback to ~/.cache/steamdeck_toolbox_error.log; send that file with any bug report
- Fixed the "install vte3?" prompt swallowing every click on the main window when VTE is missing: that dialog was modal with no parent window, so on some desktops it landed behind the main window — the toolbox window was there but nothing responded. It is now non-modal and always kept on top, so the main window stays usable even if the dialog ends up behind it
- Feature windows now raise themselves to the front, so they are not hidden behind the main window on some desktops

2026-11-05 (v2.0.2)
[UI rework: native GTK windows]
- "Install Flatpak Apps" and "Uninstall Other Installed Apps" are now native GTK windows; zenity is no longer used
  - The app list, checkboxes, progress bar and results all live in the tool's own window, matching the main UI theme
  - The "delete local data?" prompt is part of the same window instead of a separate dialog
  - Fully fixes "install keeps running in the background after cancel/close": Python now starts flatpak directly, so cancelling terminates that very process -- measured 0.5s to exit, with nothing installed
  - New search box: matches the built-in catalog instantly, and falls back to searching flathub when nothing matches; remote results are installable too
  - Buttons are reduced to a single primary button that switches with the stage (install / cancel / done / back to list) and hides itself when nothing is selected
  - After finishing you return to the list and can keep going instead of re-entering the entry each time
  - The search box hides itself during install; it only matters while picking apps
  - Selections survive searching, switching queries and late remote results instead of being wiped by a redraw
- "Steam Cache Manager" is now a native GTK window
  - Opening it lists shader cache and compat data; pick a type and it scans every Steam library (the default one plus any registered in libraryfolders.vdf)
  - The list shows app names and sizes, sorted by size, with a live count and total at the bottom
  - A separate confirmation page lists what will be deleted; during deletion it shows "Deleting 2/3: app name" with live progress and can be cancelled at any point
- "Compatibility Layer Manager" is now a native GTK window, and one window handles install and uninstall for all three families (GE-Proton, Proton-CachyOS, DW Proton)
  - Version lists are read from GitHub Releases; the install list skips versions already present and the uninstall list only shows installed directories
  - The confirmation page offers a download mirror (gh-proxy.com / gh.3w.pm / cors.isteed.cc / ghproxy.net / GitHub official), shared by the whole batch
  - Downloads show real byte progress (e.g. "128.0 MB / 540.6 MB") instead of an idle animation
  - Two checks after downloading: compare the file size first, then the sha512 digest. If either fails the version is reported as failed with the reason, and a bad archive is never unpacked into Steam; extraction goes to a temporary directory first and is only moved into place after validation, so cancelling leaves no half-finished folder
  - Failures are listed one per line ("· version: reason"), e.g. "sha512 mismatch, archive is corrupt" or "this version has no x86_64 package for the Deck"
  - Cancel responds in about 0.5s (read1 chunked reads plus a socket shutdown)
  - Mirrors now have failure detection and automatic failover: unreachable hosts, dropped connections,
    size mismatches and sha512 mismatches all move on to the next mirror; only when every mirror fails
    does it report an error, listing the specific reason for each one
  - Cancelling works while fetching the version list, the download info, the archive and the checksum;
    before this only an in-progress download could be cancelled
  - Cancelling returns to the version list instead of the first page, keeping the current selection so a
    different mirror or version can be tried right away

[Install / uninstall consolidation]
- The 8 Flatpak apps under Software are merged into one "Install Flatpak Apps" entry, and the 8 Flatpak uninstall entries are merged into "Uninstall Other Installed Apps"
  - Key fix: that uninstall screen used to list those 8 apps as exclusions (because each had its own dedicated uninstall entry). With the dedicated entries gone, leaving the list intact would have made those apps impossible to uninstall forever; the list is now emptied, keeping only the Fcitx 5 Chinese add-on hidden as an internal component removed together with the main program
  - The listing is now read live from flatpak list instead of a fixed name list, so whatever is installed can be uninstalled

[Feature expansion]
- "Install Flatpak Apps" grows from 8 apps to 37, covering everyday, office, media, creative, remote and gaming tools
  - Messaging 7, browsers 3, media 4, cloud storage and downloads 2, office and notes 5, creative tools 6, remote control 2, gaming tools 6, system tools 2
- All 37 app IDs are built in, so opening the list no longer queries the network; it also shows the full list offline, and opens in under a second instead of over 3
  - Related fix: `flatpak remote-add` contacts the network (~1.1s) even when flathub already exists, so the code now checks locally first and skips it

[Bug fixes]
- Fixed installs always failing with "failed IDs: 飞书"
  - Root cause: the first column of a zenity checklist must be the tick state; omitting it shifts every following column, and without an explicit return column the value returned is the display name rather than the app ID -- so the command run was `flatpak install flathub 飞书`
  - Fix: put the tick state in column one and the real app ID in a hidden second column so the output is plain IDs; a whitelist check rejects anything unexpected
- Fixed the bar showing 100% while the download was still running
  - Root cause: installing one app is split into several subtasks (runtime, locales, the app itself...), each running 0 to 100%; the old code took only the sub-task percentage, so the bar filled during the first one
  - Fix: parse "step N of M" and fold it into one continuous total
- Fixed failures showing no reason, or just a single letter
  - Non-progress output was discarded, hiding flatpak's real error; the window now lists the original message, e.g. "no match for xxx found in remote flathub"
- Fixed desktop shortcuts not being removed on uninstall
  - Root cause: shortcuts are named after the display name (飞书.desktop, Google Chrome.desktop) but uninstall matched on the app ID, so they never lined up
  - Fix: read the Exec line of each .desktop file and delete any that runs `flatpak run <that ID>`, regardless of filename
- Fixed the whole feature exiting instead of returning to the app list after cancel or closing the progress window
  - Root cause: the INT/TERM trap at the top of the embedded script (meant for "close the terminal and the tool quits") fired on the signal from closing the progress window
- Fixed flatpak not actually being terminated after cancel, leaving it downloading in the background (now cleans up the whole process group, grandchildren included)
- Fixed the list going blank after "back to list" on uninstall (rows were rebuilt without calling show_all, so new rows stayed hidden)
- Fixed "No such file or directory" when creating a shortcut and the desktop directory does not exist (now resolves it per XDG and creates it)
- Fixed an empty percentage, a duplicated percentage and a progress bar that went backwards
- Fixed every app being treated as "missing" and hidden when offline (an empty screen that looks broken)

[Other]
- Removed the "System Health Check" feature (not needed for now): its sidebar entry, search index and dangerous-operation confirmation are gone too, along with the six check groups and their repair flows in the embedded scripts; "Fix Boot" and "Fix Shared Disk" are unaffected
- Deleted 50 bash functions superseded by the GTK windows (100 definitions across both language scripts, about 4,160 lines)
  - 14 health check, 19 Flatpak install/uninstall, 1 Steam cache manager, 16 compatibility layer
  - Python now opens the corresponding GTK window directly, so these functions can no longer be reached

2026-11-03 (v2.0.1)
[Bug fixes]
- Fixed AskLink dpkg install conflicting with leftover `/var/lib/dpkg` files; failed tasks no longer show "Task completed"
[UX]
- Default to Chinese when no language preference is saved; top-bar language control shows "语言" / Language
- Slightly smaller default window on Deck-class screens; startup update reuses the same check window/size

2026-11-02 (v2.0.0)
[Bug fixes]
- Fixed the garbage characters appearing after the "Update all apps" progress line (`^[[20;68R^[[20;68R^[[20;77R`)
  - Root cause: before drawing its progress bar flatpak sends `ESC[6n` to ask the terminal where the cursor is, and VTE answers with `ESC[row;colR` on the terminal's *input* side. The PTY has ECHO enabled by default, so the kernel echoes that reply back to the screen, where it shows up as visible garbage
  - Fix: pass `--noninteractive` to `flatpak update` so it emits plain line-by-line text instead of an ANSI progress bar. No progress bar means no cursor query, removing the garbage at the source
  - Measured on the same machine in the same state (nothing to update): default produced 31 escape sequences including ANSI bold and cursor control; with the flag, 0
  - Why not simply disable terminal ECHO: that merely hides the reply while its bytes stay in the input buffer, so later reads pick them up (measured: `read -n1` returned ESC instead of the key the user pressed), which is worse than the garbage
  - Tradeoff: terser output with no percentage progress bar, but every step still prints a line

[Version]
- Version bumped to **2.0.0**: features and stability have accumulated well beyond 1.x, marking it as a stable release

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
