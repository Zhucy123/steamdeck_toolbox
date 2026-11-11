#!/bin/bash
VERSION="1.3.9"

TOOLBOX_URL="https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/steamdeck_gui.py"
TOOLBOX_NAME="$HOME/steamdeck_gui.py"
PYTHON_BIN="$(command -v python3 || true)"

# 只清理本工具箱明确属于自己的旧版遗留文件（容错：不存在 / 无权限都忽略）。
# 不再无条件删除固定路径 /home/deck/steamdeck_toolbox.sh —— 那很可能就是本脚本自身，
# 或别的用户的文件，删掉会自毁 / 误删。
for _legacy in "$HOME/Desktop/SteamDeck工具箱.desktop"; do
    if [ -f "$_legacy" ]; then
        rm -f "$_legacy" 2>/dev/null || true
    fi
done

# ---- 前置检查：缺任何一个都没法正常下载 / 启动 GUI ----
_missing=0
if [ -z "$PYTHON_BIN" ]; then
    echo "❌ 未找到 python3，无法启动工具箱。"; _missing=1
fi
if ! command -v curl &>/dev/null; then
    echo "❌ 未找到 curl，无法下载工具箱。"; _missing=1
fi
if [ -n "$PYTHON_BIN" ] && ! "$PYTHON_BIN" -c "import gi; gi.require_version('Gtk','3.0'); from gi.repository import Gtk" >/dev/null 2>&1; then
    echo "❌ Python 无法 import gi / Gtk（缺少 python-gobject），工具箱无法启动。"; _missing=1
fi
if [ "$_missing" -eq 1 ]; then
    echo "   请先安装依赖后重试：sudo pacman -S python-gobject curl"
    exit 1
fi

# ---- 只读模式：先记录进入时状态，只有脚本自己 disable 过才在 EXIT 恢复 ----
# 绝不覆盖用户原本就可写（disabled）的设置；所有成功 / 失败路径统一走 EXIT trap。
RO_ORIGINALLY_ENABLED=0
RO_DISABLED_BY_US=0
TMP_TOOLBOX=""
cleanup() {
    if [ "${RO_DISABLED_BY_US:-0}" -eq 1 ] && [ "${RO_ORIGINALLY_ENABLED:-0}" -eq 1 ]; then
        if command -v steamos-readonly &>/dev/null; then
            if sudo -n steamos-readonly enable 2>/dev/null; then
                echo "✅ 已恢复只读模式"
            else
                echo "⚠️ 无法自动恢复只读模式，请手动执行: sudo steamos-readonly enable"
            fi
        fi
    fi
    if [ -n "${TMP_TOOLBOX:-}" ]; then
        rm -f "$TMP_TOOLBOX" 2>/dev/null
    fi
    return 0
}
trap cleanup EXIT

echo "正在检查系统只读状态..."
if command -v steamos-readonly &>/dev/null; then
    if sudo -n steamos-readonly status 2>/dev/null | grep -q "enabled"; then
        RO_ORIGINALLY_ENABLED=1
    fi
    if [ "${RO_ORIGINALLY_ENABLED}" -eq 1 ]; then
        if sudo steamos-readonly disable 2>/dev/null; then
            RO_DISABLED_BY_US=1
            echo "✅ 已临时解除只读模式（退出时自动恢复）"
        else
            echo "⚠️ 解除只读模式失败（需要 sudo 权限），vte3 安装可能无法写入系统目录。"
            echo "   可手动执行: sudo steamos-readonly disable 后重试。"
        fi
    else
        echo "系统已处于可写状态，保持不变。"
    fi
fi

# 与 install_gui.sh 一致：真正能用的是 Python 能否 import Vte，而不只是 pacman -Q
vte_python_ok() {
    "$PYTHON_BIN" - <<'VTEPY' >/dev/null 2>&1
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Vte  # noqa: F401
VTEPY
}
if vte_python_ok; then
    echo "✅ VTE 可用（vte3 + Python 绑定正常）。"
else
    echo "未找到可用的 VTE（Python 无法 import Vte），正在尝试安装..."
    # 注意：SteamOS 同时使用 archlinux 与 holo 两个钥匙环。
    # 889B5EBD... 属于 holo-keyring，只 populate archlinux 时该密钥不会被导入，
    # 后续 --lsign-key 必然报“无法在本地签署”，因此两个钥匙环都必须导入。
    if [ ! -f /etc/pacman.d/gnupg/pubring.gpg ]; then
        echo "正在初始化 Pacman 密钥..."
        sudo pacman-key --init || {
            echo "❌ pacman keyring 初始化失败，无法安装 vte3。"
            exit 1
        }
    fi
    sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null || true
    sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null || true
    echo "正在填充 Arch 官方与 SteamOS Holo 密钥..."
    sudo pacman-key --populate archlinux || {
        echo "❌ archlinux 钥匙环填充失败。"
        exit 1
    }
    if [ -f /usr/share/pacman/keyrings/holo.gpg ]; then
        sudo pacman-key --populate holo || {
            echo "❌ holo 钥匙环填充失败。"
            exit 1
        }
    fi
    echo "正在信任 SteamOS 打包者密钥..."
    if ! sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF; then
        echo "⚠️ 密钥签署失败，刷新钥匙环后重试..."
        sudo pacman-key --refresh-keys 2>/dev/null || true
        sudo pacman-key --populate archlinux holo 2>/dev/null || true
        sudo pacman-key --lsign-key 889B5EBDDD505A683621900DAF1D2199EF0A3CCF || {
            echo "❌ 密钥签署仍失败，无法安装 vte3。"
            echo "   可尝试手动执行: sudo pacman-key --init && sudo pacman-key --populate archlinux holo"
            exit 1
        }
    fi
    # python-gobject 是 gi 的前提；缺了也会表现为「没有 VTE」
    if ! pacman -Q python-gobject &>/dev/null; then
        if ! sudo pacman -S --needed --noconfirm python-gobject; then
            echo "⚠️ python-gobject 安装失败，VTE 可能无法被 Python 导入。"
        fi
    fi
    sudo pacman -Sy --noconfirm 2>/dev/null || true
    if sudo pacman -S --needed --noconfirm vte3; then
        echo "✅ vte3 安装成功！"
    else
        echo "⚠️ vte3 安装失败，GUI 将使用外部终端模式（功能仍可用）。"
    fi
    if vte_python_ok; then
        echo "✅ VTE 安装/修复成功，Python 已能 import Vte。"
    else
        echo "⚠️ vte3 已处理，但 Python 仍无法 import Vte，GUI 将使用外部终端模式。"
    fi
fi

echo "正在从 GitHub 下载 Steam Deck GUI 工具箱..."

# 与安装器一致：先下载到同目录临时文件，校验通过后才原子 mv，
# 避免 curl 失败 / 错误页把已有安装截断。
TMP_TOOLBOX="$(mktemp "$(dirname "$TOOLBOX_NAME")/.steamdeck_gui.XXXXXX")" || {
    echo "❌ 无法创建临时文件，已保留原有文件"
    exit 1
}

if curl -L --fail --connect-timeout 15 --max-time 120 --progress-bar "$TOOLBOX_URL" -o "$TMP_TOOLBOX"; then
    if ! grep -q 'BASH_SCRIPT = ' "$TMP_TOOLBOX" || ! grep -q '^VERSION = ' "$TMP_TOOLBOX"; then
        echo "❌ 下载内容校验失败（不是有效的工具箱脚本），已保留原有文件"
        exit 1
    fi
    local_size=$(wc -c < "$TMP_TOOLBOX" 2>/dev/null || echo 0)
    if [ "$local_size" -lt 50000 ]; then
        echo "❌ 下载内容不完整（${local_size} 字节），已保留原有文件"
        exit 1
    fi
    if ! "$PYTHON_BIN" -c "import sys; compile(open(sys.argv[1], encoding='utf-8').read(), sys.argv[1], 'exec')" "$TMP_TOOLBOX" 2>/dev/null; then
        echo "❌ 下载内容语法校验失败，已保留原有文件"
        exit 1
    fi
    if ! mv -f "$TMP_TOOLBOX" "$TOOLBOX_NAME"; then
        echo "❌ 无法写入 $TOOLBOX_NAME，已保留原有文件"
        exit 1
    fi
    TMP_TOOLBOX=""
    chmod +x "$TOOLBOX_NAME"
    echo "下载完成，正在启动..."
    # 不用 exec：exec 会绕过 EXIT trap，导致只读模式永远停在 disabled。
    # 正常退出后再 exit，让 cleanup 统一恢复。
    "$PYTHON_BIN" "$TOOLBOX_NAME"
    rc=$?
    echo "工具箱已退出（退出码 $rc）。"
    exit $rc
else
    echo "❌ 下载失败，请检查网络后重试（已保留原有文件）"
    exit 1
fi
