#!/usr/bin/env bash
# ==============================================================================
# Trình Cài Đặt 1-Chạm: Cyber Threat Intel Workspace & Kubuntu Enhancements
# ==============================================================================
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BIN_DIR="$HOME/.local/bin"
APPS_DIR="$HOME/.local/share/applications"
KONSOLE_DIR="$HOME/.local/share/konsole"
AUTOSTART_DIR="$HOME/.config/autostart"

echo "======================================================================"
echo "   🛡️ CÀI ĐẶT CYBER WORKSPACE & BỘ CÔNG CỤ TỐI ƯU KUBUNTU           "
echo "======================================================================"
echo ">> Thư mục nguồn: $REPO_DIR"

# 1. Tạo các thư mục cần thiết
mkdir -p "$BIN_DIR" "$APPS_DIR" "$KONSOLE_DIR" "$AUTOSTART_DIR"

# 2. Kiểm tra Python 3
if ! command -v python3 >/dev/null 2>&1; then
    echo "❌ Lỗi: Chưa cài đặt Python 3. Vui lòng cài: sudo apt install -y python3"
    exit 1
fi

# 3. Kiểm tra hoặc cài đặt UV package manager (cực nhanh)
if ! command -v uv >/dev/null 2>&1 && [ ! -f "$BIN_DIR/uv" ]; then
    echo ">> Đang cài đặt công cụ Python UV..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

UV_CMD="$BIN_DIR/uv"
if command -v uv >/dev/null 2>&1; then
    UV_CMD="uv"
fi

# 4. Tải trước gói Textual để khởi động tức thì
echo ">> Đang chuẩn bị môi trường chạy Textual UI..."
"$UV_CMD" pip install --quiet textual 2>/dev/null || true

# 5. Phân quyền thực thi cho tất cả script
echo ">> Cấp quyền thực thi các script..."
chmod +x "$REPO_DIR"/dashboard \
         "$REPO_DIR"/workspace \
         "$REPO_DIR"/buddy \
         "$REPO_DIR"/toggle_autostart.sh \
         "$REPO_DIR"/set_wallpaper.sh \
         "$REPO_DIR"/toggle_icon_style.sh \
         "$REPO_DIR"/setup_macos_layout.sh \
         "$REPO_DIR"/restore_default_layout.sh \
         "$REPO_DIR"/optimize_performance.sh \
         "$REPO_DIR"/fix_screen_freeze.sh 2>/dev/null || true

# 6. Cấu hình Profile Konsole
echo ">> Thiết lập Konsole profile 'CyberDashboard'..."
cat << EOF > "$KONSOLE_DIR/CyberDashboard.profile"
[General]
Name=CyberDashboard
Parent=FALLBACK/
Command=$REPO_DIR/dashboard
EOF

# 7. Tạo Symlinks vào ~/.local/bin/
echo ">> Tạo liên kết lệnh vào $BIN_DIR..."
ln -sf "$REPO_DIR/workspace" "$BIN_DIR/workspace"
ln -sf "$REPO_DIR/dashboard" "$BIN_DIR/dashboard"
ln -sf "$REPO_DIR/buddy" "$BIN_DIR/buddy"
ln -sf "$REPO_DIR/toggle_autostart.sh" "$BIN_DIR/toggle_autostart"

# 8. Cài đặt Desktop Applications
echo ">> Đăng ký ứng dụng vào KDE Application Menu..."
cat << EOF > "$APPS_DIR/cyber-workspace.desktop"
[Desktop Entry]
Type=Application
Name=Cyber Workspace
GenericName=Workspace & Cyber Dashboard
Comment=Không Gian Làm Việc Cyber Workspace (Bash Shell + Threat Intel Dashboard)
Exec=$REPO_DIR/workspace
Icon=utilities-terminal
Terminal=false
Categories=Development;
Keywords=workspace;dashboard;threat;intel;konsole;terminal;
StartupNotify=false
EOF

cat << EOF > "$APPS_DIR/cyber-dashboard.desktop"
[Desktop Entry]
Type=Application
Name=Cyber Threat Dashboard
GenericName=Threat Intel & Personal Dashboard
Comment=Bảng điều khiển Cyber Threat Intelligence & Quản lý công việc cá nhân
Exec=konsole -e $REPO_DIR/dashboard
Icon=utilities-system-monitor
Terminal=false
Categories=Development;
Keywords=dashboard;threat;intel;cve;todo;pomodoro;
StartupNotify=false
EOF

# 9. Cấu hình Autostart mặc định (Tự bung khi mở máy)
echo ">> Kích hoạt tự động mở Cyber Workspace khi đăng nhập..."
"$REPO_DIR/toggle_autostart.sh" workspace >/dev/null 2>&1 || true

# 10. Làm mới cache KDE Sycoca
if command -v kbuildsycoca6 >/dev/null 2>&1; then
    kbuildsycoca6 >/dev/null 2>&1 || true
fi

# 11. Kiểm tra PATH trong ~/.bashrc
if [[ ":$PATH:" != *":$BIN_DIR:"* ]]; then
    if ! grep -q 'PATH="$HOME/.local/bin:$PATH"' "$HOME/.bashrc" 2>/dev/null; then
        echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
    fi
fi

echo ""
echo "======================================================================"
echo "   🎉 CÀI ĐẶT THÀNH CÔNG! HỆ THỐNG ĐÃ SẴN SÀNG! ( ˶ᵔ ᵕ ᵔ˶ )          "
echo "======================================================================"
echo "Các lệnh nhanh bạn có thể sử dụng ở bất kỳ terminal nào:"
echo "  • workspace        : Mở không gian làm việc chia đôi (Bash + Dashboard)"
echo "  • dashboard        : Mở bảng điều khiển độc lập toàn màn hình"
echo "  • buddy [cheer]    : Tương tác cùng linh vật Kubi Buddy"
echo "  • toggle_autostart : Quản lý bật/tắt tự bung workspace khi mở máy"
echo ""
echo "💡 Mẹo: Bấm phím '/' trong dashboard để kích hoạt Omnibar Vạn Năng!"
echo "======================================================================"
