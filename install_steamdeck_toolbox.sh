#!/bin/bash

TOOLBOX_URL="https://gitee.com/Zhucy2100/steamdeck_toolbox/raw/master/steamdeck_toolbox.sh"
TOOLBOX_NAME="$HOME/steamdeck_toolbox.sh"

if curl -L --progress-bar "$TOOLBOX_URL" -o "$TOOLBOX_NAME"; then
    chmod +x "$TOOLBOX_NAME"
    exec "$TOOLBOX_NAME"
else
    echo "下载失败，请检查网络后重试"
    exit 1
fi