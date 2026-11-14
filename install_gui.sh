#!/bin/bash

TOOLBOX_URL="https://raw.githubusercontent.com/Zhucy123/steamdeck_toolbox/main/steamdeck_gui.py"
TOOLBOX_NAME="$HOME/steamdeck_gui.py"
PYTHON_BIN="$(command -v python3 || true)"

# 记录进入时的只读状态：只有脚本自己把只读关掉，退出才恢复。
# 用户原本就可写（disabled）时绝不擅自 enable 覆盖其设置。
# 同时统一清理下载临时文件；所有成功 / 失败路径都走这一个 EXIT trap。
# 注意：不能用 grep -q "enabled" 判断只读，因为 "disabled" 本身也包含 "enabled"。
RO_ORIGINALLY_ENABLED=0
RO_DISABLED_BY_US=0
TMP_TOOLBOX=""
cleanup() {
    if [ "${RO_DISABLED_BY_US:-0}" -eq 1 ] && [ "${RO_ORIGINALLY_ENABLED:-0}" -eq 1 ]; then
        if command -v steamos-readonly &>/dev/null; then
            if sudo -n steamos-readonly enable 2>/dev/null; then
                echo "✅ 已恢复只读模式（脚本退出前的状态）"
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

# 必须整行匹配：disabled 里包含 enabled 子串，绝不能用 grep "enabled"。
steamos_ro_status() {
    local out
    out="$(sudo steamos-readonly status 2>/dev/null || true)"
    if echo "$out" | grep -qiE '^[[:space:]]*enabled[[:space:]]*$'; then
        echo enabled
    elif echo "$out" | grep -qiE '^[[:space:]]*disabled[[:space:]]*$'; then
        echo disabled
    else
        echo unknown
    fi
}

# 与 steamdeck_gui.py 一致：真正能用的是 Python 能否 import Vte，而不只是 pacman -Q
vte_python_ok() {
    if [ -z "$PYTHON_BIN" ]; then
        return 1
    fi
    "$PYTHON_BIN" - <<'VTEPY' >/dev/null 2>&1
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Vte", "2.91")
from gi.repository import Vte  # noqa: F401
VTEPY
}

ensure_pacman_keys() {
    # 注意：SteamOS 同时使用 archlinux 与 holo 两个钥匙环。
    # 889B5EBD... 属于 holo-keyring，只 populate archlinux 时该密钥不会被导入，
    # 后续 --lsign-key 必然报“无法在本地签署”，因此两个钥匙环都必须导入。
    if [ ! -f /etc/pacman.d/gnupg/pubring.gpg ]; then
        echo "正在初始化 Pacman 密钥..."
        sudo pacman-key --init || {
            echo "❌ pacman keyring 初始化失败，无法安装 vte3。"
            return 1
        }
    fi
    sudo chown -R root:root /etc/pacman.d/gnupg 2>/dev/null || true
    sudo chmod 700 /etc/pacman.d/gnupg 2>/dev/null || true
    echo "正在填充 Arch 官方与 SteamOS Holo 密钥..."
    sudo pacman-key --populate archlinux || {
        echo "❌ archlinux 钥匙环填充失败。"
        return 1
    }
    if [ -f /usr/share/pacman/keyrings/holo.gpg ]; then
        sudo pacman-key --populate holo || {
            echo "❌ holo 钥匙环填充失败。"
            return 1
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
            return 1
        }
    fi
    return 0
}

install_vte_packages() {
    local force_reinstall="${1:-0}"
    ensure_pacman_keys || return 1

    # 同步 pacman 数据库：这一步失败会让后面所有 pacman -S 报「无法找到数据库」。
    # 原来用 2>/dev/null || true 把错误和返回码都吞了，用户只看到含糊的报错。
    # 这里改为：先提示废弃的 community 段残留，再保留 stderr、检查返回码。
    echo "正在同步 pacman 数据库..."
    if grep -qE '^\[community' /etc/pacman.conf 2>/dev/null; then
        echo "⚠️ 检测到 /etc/pacman.conf 中残留废弃的 [community] 仓库段。"
        echo "   SteamOS 3.9 已把 community 合并进 extra，服务器不再提供 community-3.9.db，"
        echo "   残留会导致同步失败、vte3 安装时报「无法找到数据库」。"
        echo "   如后续安装失败，请先注释掉该段，例如："
        echo "     sudo steamos-readonly disable"
        echo "     sudo sed -i 's/^\[community-3.9\]/#[community-3.9]/' /etc/pacman.conf"
        echo "     sudo pacman -Sy"
    fi
    if ! sudo pacman -Sy --noconfirm; then
        if [ -e /var/lib/pacman/db.lck ]; then
            if pgrep -x pacman >/dev/null 2>&1 || pgrep -x packagekitd >/dev/null 2>&1; then
                echo "❌ 另有软件安装或更新正在进行，pacman 数据库被锁定。"
                echo "   请等待其结束后重新运行安装命令。"
                return 1
            fi
            echo "⚠️ 发现残留的 pacman 锁文件，且没有正在运行的 pacman，正在清除后重试..."
            sudo rm -f /var/lib/pacman/db.lck
        fi
        if command -v steamos-readonly &>/dev/null && [ "$(steamos_ro_status)" = "enabled" ]; then
            echo "⚠️ 系统仍处于只读，正在再次解除后重试同步..."
            if sudo steamos-readonly disable; then
                RO_ORIGINALLY_ENABLED=1
                RO_DISABLED_BY_US=1
            fi
        fi
        if sudo pacman -Sy --noconfirm; then
            echo "✅ 数据库同步已在重试后成功。"
        else
            echo "❌ 同步 pacman 数据库失败，无法继续安装 vte3。"
            echo "   若提示「无法锁定数据库」：请确认已解除只读（sudo steamos-readonly disable），"
            echo "   并检查是否有其他安装/更新占用，或 /var/lib/pacman 是否可写。"
            echo "   其他情况请检查："
            echo "     · 网络是否正常、系统 pacman 源是否可用（可先换源）"
            echo "     · 是否有废弃仓库残留：grep -n community /etc/pacman.conf"
            echo "   修复后重新运行安装命令即可。"
            return 1
        fi
    fi

    # python-gobject 是 GUI 用 gi 的前提；缺了也会表现为“没有 VTE”
    if ! pacman -Q python-gobject &>/dev/null; then
        echo "正在安装 python-gobject..."
        sudo pacman -S --needed --noconfirm python-gobject || {
            echo "❌ python-gobject 安装失败。"
            return 1
        }
    fi

    if [ "$force_reinstall" = "1" ]; then
        echo "正在强制重装 vte3（包在，但 Python 无法 import）..."
        sudo pacman -S --noconfirm vte3 || {
            echo "❌ vte3 重装失败。"
            return 1
        }
    else
        echo "正在安装 vte3..."
        sudo pacman -S --needed --noconfirm vte3 || {
            echo "❌ vte3 安装失败。"
            return 1
        }
    fi

    pacman -Q vte3 >/dev/null 2>&1 || {
        echo "❌ vte3 安装后 pacman 仍查不到该包。"
        return 1
    }
    return 0
}

echo "正在检查系统只读状态（如需密码，只需输入一次）..."
if ! sudo -v; then
    echo "❌ 未能获取管理员权限，无法继续安装。"
    exit 1
fi
if command -v steamos-readonly &>/dev/null; then
    ro_now="$(steamos_ro_status)"
    if [ "$ro_now" = "enabled" ]; then
        RO_ORIGINALLY_ENABLED=1
        if sudo steamos-readonly disable; then
            RO_DISABLED_BY_US=1
            echo "✅ 已临时解除只读模式（退出时自动恢复）"
        else
            echo "❌ 解除只读模式失败，无法安装系统组件。"
            exit 1
        fi
    elif [ "$ro_now" = "disabled" ]; then
        echo "系统已处于可写状态，保持不变。"
    else
        echo "⚠️ 无法确认只读状态，尝试解除只读后继续..."
        if sudo steamos-readonly disable; then
            echo "✅ 已尝试解除只读模式（因原状态不明确，退出时不会自动恢复）。"
        else
            echo "❌ 解除只读模式失败，无法继续安装。"
            exit 1
        fi
    fi
else
    echo "未检测到 steamos-readonly，跳过只读处理。"
fi

if [ -z "$PYTHON_BIN" ]; then
    echo "❌ 未找到 python3，无法安装/验证工具箱。"
    exit 1
fi

echo "正在检查 VTE 终端组件（与工具箱相同：Python import Vte）..."
if vte_python_ok; then
    echo "✅ VTE 可用（vte3 + Python 绑定正常）。"
else
    if pacman -Q vte3 &>/dev/null; then
        echo "⚠️ pacman 显示已安装 vte3，但 Python 无法 import Vte，准备修复..."
        install_vte_packages 1 || exit 1
    else
        echo "未找到可用的 VTE，正在安装..."
        install_vte_packages 0 || exit 1
    fi

    if vte_python_ok; then
        echo "✅ VTE 安装/修复成功，Python 已能 import Vte。"
    else
        echo "❌ vte3 已处理，但 Python 仍无法 import Vte。"
        echo "   请检查: $PYTHON_BIN -c 'import gi; gi.require_version(\"Vte\",\"2.91\"); from gi.repository import Vte'"
        echo "   未通过验证前不会当作安装成功。"
        exit 1
    fi
fi

echo "正在从 GitHub 下载 Steam Deck GUI 工具箱..."

# 先下载到目标同目录下的临时文件，完整校验通过后才原子 mv 到目标。
# 直接 curl -o "$TOOLBOX_NAME" 会在失败 / 拿到错误页时截断或删掉已有安装，
# 导致工具箱再也打不开。临时文件放同目录，mv 才是真正的原子 rename。
TMP_TOOLBOX="$(mktemp "$(dirname "$TOOLBOX_NAME")/.steamdeck_gui.XXXXXX")" || {
    echo "❌ 无法创建临时文件，安装中止（已保留原有文件）"
    exit 1
}

if curl -L --fail --connect-timeout 15 --max-time 120 --progress-bar "$TOOLBOX_URL" -o "$TMP_TOOLBOX"; then
    # 校验 1：标记齐全（TOOLBOX_URL 指向 steamdeck_gui.py，本身含这两处）
    if ! grep -q 'BASH_SCRIPT = ' "$TMP_TOOLBOX" || ! grep -q '^VERSION = ' "$TMP_TOOLBOX"; then
        echo "❌ 下载内容校验失败（不是有效的工具箱脚本），已保留原有文件"
        exit 1
    fi
    # 校验 2：文件大小下限，挡住错误页 / 半截文件
    local_size=$(wc -c < "$TMP_TOOLBOX" 2>/dev/null || echo 0)
    if [ "$local_size" -lt 50000 ]; then
        echo "❌ 下载内容不完整（${local_size} 字节），已保留原有文件"
        exit 1
    fi
    # 校验 3：python3 语法编译，挡住被改坏的脚本
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
    echo "下载完成！"
    echo "✅ 安装成功！"
    echo ""

    # 桌面快捷方式：目录可能不存在，先建；已存在也要自愈校验 Exec。
    DESKTOP_DIR="$HOME/Desktop"
    if ! mkdir -p "$DESKTOP_DIR"; then
        echo "⚠️ 无法创建桌面目录 $DESKTOP_DIR，跳过快捷方式"
    fi
    DESKTOP_FILE="$DESKTOP_DIR/Deck工具箱.desktop"
    EXPECTED_EXEC="$PYTHON_BIN \"$TOOLBOX_NAME\""
    need_write=1
    if [ -f "$DESKTOP_FILE" ]; then
        if grep -qF "Exec=$EXPECTED_EXEC" "$DESKTOP_FILE"; then
            need_write=0
            echo "桌面快捷方式已存在且指向当前工具箱。"
        else
            echo "⚠️ 桌面快捷方式指向旧路径，正在更新..."
        fi
    fi
    if [ "$need_write" -eq 1 ] && [ -d "$DESKTOP_DIR" ]; then
        if cat > "$DESKTOP_FILE" << EOF
[Desktop Entry]
Type=Application
Name=Deck工具箱
Exec=$EXPECTED_EXEC
Icon=input-gamepad-symbolic
Terminal=false
StartupNotify=true
Categories=Utility;
EOF
        then
            chmod +x "$DESKTOP_FILE"
            echo "✅ 已创建/更新桌面快捷方式：Deck工具箱.desktop"
        else
            echo "⚠️ 桌面快捷方式写入失败（不影响工具箱本体）"
        fi
    fi

    echo "请单击或双击桌面上的 'Deck工具箱' 图标来启动程序。"
    echo "若仍提示缺少 VTE，请完全退出工具箱后重新打开（VTE 只在启动时检测一次）。"
    echo ""
    sudo -n -v 2>/dev/null || true
    exit 0
else
    echo "❌ 下载失败，请检查网络后重试（已保留原有文件）"
    exit 1
fi
