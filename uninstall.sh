#!/usr/bin/env bash
# ==============================================================================
# Trình Gỡ Cài Đặt: Cyber Threat Intel Workspace
# ==============================================================================
set -e

BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
KONSOLE_DIR="$HOME/.local/share/konsole"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "======================================================================"
echo "   🗑️ GỠ BỎ CYBER WORKSPACE & BỘ CÔNG CỤ                           "
echo "======================================================================"

# 1. Gỡ symlinks
echo ">> Gỡ các liên kết trong $BIN_DIR..."
rm -f "$BIN_DIR/workspace" \
      "$BIN_DIR/dashboard" \
      "$BIN_DIR/buddy" \
      "$BIN_DIR/toggle_autostart"

# 2. Gỡ Desktop entries
echo ">> Xóa ứng dụng khỏi Application Menu..."
rm -f "$APPS_DIR/cyber-workspace.desktop" \
      "$APPS_DIR/cyber-dashboard.desktop"

# 3. Gỡ Autostart
echo ">> Tắt tự khởi động khi mở máy..."
rm -f "$AUTOSTART_DIR/cyber-workspace.desktop"

# 4. Gỡ Konsole Profile
echo ">> Xóa profile Konsole..."
rm -f "$KONSOLE_DIR/CyberDashboard.profile"

# 5. Cập nhật sycoca & systemd
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 >/dev/null 2>&1 || true
fi
systemctl --user daemon-reload 2>/dev/null || true

echo "==> [Thành công] Đã gỡ bỏ toàn bộ tích hợp hệ thống của Cyber Workspace."
echo "    (Thư mục mã nguồn và nhật ký làm việc ~/work_logs vẫn được giữ nguyên)."
echo "======================================================================"
