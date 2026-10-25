#!/usr/bin/env bash
# ==============================================================================
# Script bật/tắt hoặc đổi chế độ tự khởi động Workspace / Dashboard trên Kubuntu
# ==============================================================================
set -e

AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/cyber-workspace.desktop"
MODE="${1:-status}"

mkdir -p "$AUTOSTART_DIR"

check_status() {
    if [ ! -f "$AUTOSTART_FILE" ]; then
        echo " [Trạng thái]: Đang TẮT (Chưa cài đặt tự khởi động)"
        return 1
    fi

    if grep -q "Hidden=true" "$AUTOSTART_FILE" 2>/dev/null; then
        echo " [Trạng thái]: Đang TẮT (Hidden=true trong autostart)"
        return 1
    fi

    if grep -q "dashboard" "$AUTOSTART_FILE" && ! grep -q "workspace" "$AUTOSTART_FILE"; then
        echo " [Trạng thái]: Đang BẬT -> Chế độ: Dashboard Độc Lập (Toàn màn hình)"
        return 0
    else
        echo " [Trạng thái]: Đang BẬT -> Chế độ: Cyber Workspace (Split Terminal 55% Shell / 45% Dashboard)"
        return 0
    fi
}

case "$MODE" in
    workspace|ws|split)
        echo ">> Đang kích hoạt tự khởi động: Cyber Workspace (Split View)..."
        cat << 'EOF' > "$AUTOSTART_FILE"
[Desktop Entry]
Type=Application
Name=Cyber Workspace
GenericName=Workspace & Cyber Dashboard
Comment=Tự động khởi động Cyber Workspace khi đăng nhập Kubuntu
Exec=$HOME/.local/bin/workspace
Icon=utilities-terminal
Terminal=false
Categories=Development;
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
X-KDE-autostart-phase=2
EOF
        chmod +x "$AUTOSTART_FILE"
        systemctl --user daemon-reload 2>/dev/null || true
        kbuildsycoca6 >/dev/null 2>&1 || true
        echo "==> [Thành công] Cyber Workspace sẽ tự động bung ra mỗi khi bạn mở máy/đăng nhập! ( ˶ᵔ ᵕ ᵔ˶ )"
        ;;

    dashboard|db|standalone)
        echo ">> Đang kích hoạt tự khởi động: Cyber Dashboard (Độc lập)..."
        cat << 'EOF' > "$AUTOSTART_FILE"
[Desktop Entry]
Type=Application
Name=Cyber Threat Dashboard
GenericName=Threat Intel & Personal Dashboard
Comment=Tự động mở bảng tin Cyber Threat Dashboard khi đăng nhập Kubuntu
Exec=konsole -e $HOME/.local/bin/dashboard
Icon=utilities-system-monitor
Terminal=false
Categories=Development;
StartupNotify=false
X-GNOME-Autostart-enabled=true
X-KDE-autostart-after=panel
X-KDE-autostart-phase=2
EOF
        chmod +x "$AUTOSTART_FILE"
        systemctl --user daemon-reload 2>/dev/null || true
        kbuildsycoca6 >/dev/null 2>&1 || true
        echo "==> [Thành công] Cyber Dashboard độc lập sẽ tự động mở mỗi khi bạn mở máy/đăng nhập!"
        ;;

    disable|off|remove)
        echo ">> Đang tắt tự khởi động..."
        rm -f "$AUTOSTART_FILE"
        systemctl --user daemon-reload 2>/dev/null || true
        kbuildsycoca6 >/dev/null 2>&1 || true
        echo "==> [Đã tắt] Đã gỡ bỏ tự khởi động khi mở máy."
        ;;

    status)
        echo "=========================================================="
        echo "   Cấu hình Tự Khởi Động (Autostart) - Kubuntu Workspace  "
        echo "=========================================================="
        check_status || true
        echo ""
        echo "Cách sử dụng:"
        echo "  $0 workspace   # Tự động bung Cyber Workspace (Split 55% Shell / 45% Dashboard)"
        echo "  $0 dashboard   # Tự động bung Cyber Dashboard độc lập"
        echo "  $0 disable     # Tắt tự khởi động"
        echo "  $0 status      # Kiểm tra trạng thái hiện tại"
        echo "=========================================================="
        ;;

    *)
        echo "Lựa chọn không hợp lệ: '$MODE'"
        echo "Hãy dùng:"
        echo "  $0 workspace   # Bật tự khởi động Cyber Workspace (Khuyên dùng)"
        echo "  $0 dashboard   # Bật tự khởi động Dashboard độc lập"
        echo "  $0 disable     # Tắt tự khởi động"
        echo "  $0 status      # Xem trạng thái"
        exit 1
        ;;
esac
