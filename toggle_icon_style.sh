#!/usr/bin/env bash
# Script đổi nhanh giữa các kiểu icon mềm mại cho Kubuntu
set -e

THEME="${1:-colloid}"

case "$THEME" in
  colloid|squircle)
    ICON_NAME="Colloid-Light"
    echo ">> Đang chuyển sang icon Colloid-Light (Dáng Squircle bo góc mềm)..."
    ;;
  tela|circle)
    ICON_NAME="Tela-circle-light"
    echo ">> Đang chuyển sang icon Tela-circle-light (Dáng tròn mềm thanh thoát)..."
    ;;
  breeze|default)
    ICON_NAME="breeze"
    echo ">> Đang chuyển về icon Breeze mặc định..."
    ;;
  *)
    echo "Lựa chọn không hợp lệ. Hãy dùng:"
    echo "  $0 colloid    # Icon khối bo tròn squircle"
    echo "  $0 tela       # Icon hình tròn mềm mại"
    echo "  $0 breeze     # Icon mặc định"
    exit 1
    ;;
esac

# 1. Cập nhật KDE Plasma icon config
kwriteconfig6 --file kdeglobals --group Icons --key Theme "$ICON_NAME"

# 2. Cập nhật GTK apps (Firefox, Chrome...)
sed -i "s/gtk-icon-theme-name=.*/gtk-icon-theme-name=$ICON_NAME/" ~/.config/gtk-3.0/settings.ini 2>/dev/null || true
sed -i "s/gtk-icon-theme-name=.*/gtk-icon-theme-name=$ICON_NAME/" ~/.config/gtk-4.0/settings.ini 2>/dev/null || true
sed -i "s/Net\/IconThemeName \".*\"/Net\/IconThemeName \"$ICON_NAME\"/" ~/.config/xsettingsd/xsettingsd.conf 2>/dev/null || true
killall -HUP xsettingsd 2>/dev/null || true

# 3. Làm mới Sycoca & Khởi động lại Plasmashell để áp dụng tức thì
kbuildsycoca6 >/dev/null 2>&1
systemctl --user restart plasma-plasmashell

echo "==> Đã chuyển sang $ICON_NAME thành công!"
