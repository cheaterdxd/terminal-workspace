#!/usr/bin/env bash
# ==============================================================================
# Script khôi phục giao diện thanh Taskbar mặc định của Kubuntu
# ==============================================================================
set -e

BACKUP_FILE="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc.bak"
CONFIG_FILE="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"

if [ ! -f "$BACKUP_FILE" ]; then
    echo "Lỗi: Không tìm thấy file sao lưu $BACKUP_FILE"
    exit 1
fi

echo ">> Đang khôi phục lại thanh bar mặc định của Kubuntu..."
cp "$BACKUP_FILE" "$CONFIG_FILE"

# Khởi động lại plasmashell để áp dụng
systemctl --user restart plasma-plasmashell

echo "==> Đã khôi phục thanh bar mặc định thành công!"
