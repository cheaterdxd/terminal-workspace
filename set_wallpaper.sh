#!/usr/bin/env bash
# ==============================================================================
# Script đổi nhanh hình nền chất lượng cao 4K cho Kubuntu
# ==============================================================================
set -e

CHOICE="${1:-whitesur}"
WALLPAPER_DIR="$HOME/Pictures/Wallpapers"

case "$CHOICE" in
    whitesur|bigsur)
        IMG_PATH="$WALLPAPER_DIR/WhiteSur-light.jpg"
        DESC="macOS Big Sur Light (Thung lũng & Biển xanh - Tương phản cao, cực kỳ nịnh mắt)"
        ;;
    sonoma)
        IMG_PATH="$WALLPAPER_DIR/Sonoma-light.jpg"
        DESC="macOS Sonoma Light (Dải lụa màu sắc hiện đại, tươi sáng)"
        ;;
    ventura)
        IMG_PATH="$WALLPAPER_DIR/Ventura-light.jpg"
        DESC="macOS Ventura Light (Bông hoa trừu tượng rực rỡ sắc nét)"
        ;;
    monterey)
        IMG_PATH="$WALLPAPER_DIR/Monterey-light.jpg"
        DESC="macOS Monterey Light (Đường đồng mức tím hồng nhẹ nhàng, sang trọng)"
        ;;
    whitesur-dark|dark)
        IMG_PATH="$WALLPAPER_DIR/WhiteSur-dark.jpg"
        DESC="macOS Big Sur Dark (Phiên bản đêm huyền bí, làm nổi bật icon sáng)"
        ;;
    altai)
        IMG_PATH="/usr/share/wallpapers/Altai/contents/images/5120x2880.png"
        DESC="KDE Altai (Núi tuyết và mặt hồ xanh thẳm 5K)"
        ;;
    cascade)
        IMG_PATH="/usr/share/wallpapers/Cascade/contents/images/3840x2160.png"
        DESC="KDE Cascade (Đồ họa ngọc lam trừu tượng thanh lịch 4K)"
        ;;
    pastel|default)
        IMG_PATH="/usr/share/wallpapers/PastelHills/contents/images/3200x2000.jpg"
        DESC="PastelHills (Hình nền đồi pastel ban đầu)"
        ;;
    *)
        if [ -f "$CHOICE" ]; then
            IMG_PATH="$(realpath "$CHOICE")"
            DESC="Tùy chỉnh: $IMG_PATH"
        else
            echo "Lựa chọn không hợp lệ. Hãy dùng:"
            echo "  $0 whitesur      # macOS Big Sur Light (Khuyên dùng)"
            echo "  $0 sonoma        # macOS Sonoma Light"
            echo "  $0 ventura       # macOS Ventura Light"
            echo "  $0 monterey      # macOS Monterey Light"
            echo "  $0 whitesur-dark # macOS Big Sur Dark"
            echo "  $0 altai         # Núi tuyết & hồ nước KDE Altai 5K"
            echo "  $0 cascade       # Ngọc lam trừu tượng KDE Cascade"
            echo "  $0 pastel        # Trở về hình nền Pastel ban đầu"
            echo "  $0 /duong/dan/anh.jpg # Đặt hình nền từ file bất kỳ"
            exit 1
        fi
        ;;
esac

echo ">> Đang đổi hình nền sang: $DESC..."

qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript "
for (var i = 0; i < desktops().length; i++) {
    var d = desktops()[i];
    d.currentConfigGroup = ['Wallpaper', 'org.kde.image', 'General'];
    d.writeConfig('Image', 'file://$IMG_PATH');
}
"

echo "==> Đã áp dụng hình nền mới thành công trên toàn bộ màn hình!"
