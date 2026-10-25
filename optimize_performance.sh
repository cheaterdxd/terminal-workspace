#!/usr/bin/env bash
# ==============================================================================
# Script Tối ưu Hiệu năng Toàn diện cho Kubuntu (Xeon + 32GB RAM + NVMe + Wayland)
# ==============================================================================
set -e

GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}======================================================${NC}"
echo -e "${BLUE}   🚀 BẮT ĐẦU TỐI ƯU HIỆU NĂNG CHO KUBUNTU WORKSTATION ${NC}"
echo -e "${BLUE}======================================================${NC}"

# Kiểm tra quyền root
if [ "$EUID" -ne 0 ]; then
    echo -e "${YELLOW}>> Script này cần quyền sudo để cấu hình tham số nhân Linux (sysctl) và ZRAM.${NC}"
    echo -e "Vui lòng chạy lại với lệnh: ${GREEN}sudo ./optimize_performance.sh${NC}"
    exit 1
fi

# ------------------------------------------------------------------------------
# 1. Cấu hình Sysctl tối ưu cho máy trạm 32GB RAM + NVMe + Lập trình
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}[1/4] Cấu hình tham số nhân Linux tối ưu (/etc/sysctl.d/99-performance.conf)...${NC}"

SYSCTL_CONF="/etc/sysctl.d/99-performance.conf"

cat << 'EOF' > "$SYSCTL_CONF"
# --- 1. Tối ưu Bộ nhớ RAM & Ổ cứng NVMe (Cho máy 32GB RAM) ---
# Ưu tiên dùng 32GB RAM, chỉ swap khi thực sự cấp bách
vm.swappiness = 10
# Giữ cache cây thư mục và file attributes lâu hơn trong RAM (Tăng tốc duyệt file & git status)
vm.vfs_cache_pressure = 50
# Ghi dữ liệu bẩn xuống đĩa đều đặn ở luồng nền, tránh giật lag khi ghi file nặng
vm.dirty_background_ratio = 5
vm.dirty_ratio = 15

# --- 2. Tăng giới hạn cho Lập trình viên (VS Code, Bun, Node, Python) ---
# Tăng giới hạn theo dõi file cho các IDE và công cụ dev
fs.inotify.max_user_watches = 524288
fs.inotify.max_user_instances = 8192
# Tăng số lượng file mở đồng thời
fs.file-max = 2097152

# --- 3. Tối ưu Mạng Internet với thuật toán Google BBR ---
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr
# Bật TCP Fast Open cho cả gửi và nhận
net.ipv4.tcp_fastopen = 3
EOF

# Tải module BBR vào kernel nếu chưa có
modprobe tcp_bbr 2>/dev/null || true
echo "tcp_bbr" > /etc/modules-load.d/bbr.conf

# Áp dụng ngay lập tức mà không cần khởi động lại
sysctl --system >/dev/null 2>&1
echo -e "${GREEN}✓ Đã kích hoạt vm.swappiness=10, cache pressure=50, inotify 524K và Google BBR!${NC}"

# ------------------------------------------------------------------------------
# 2. Cài đặt và cấu hình ZRAM (Swap nén siêu tốc trong RAM)
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}[2/4] Thiết lập ZRAM (Bộ nhớ Swap nén ZSTD siêu tốc)...${NC}"

# Cài đặt zram-tools nếu chưa có
if ! command -v zramctl >/dev/null 2>&1 || ! dpkg -s zram-tools >/dev/null 2>&1; then
    echo ">> Đang cài đặt zram-tools..."
    DEBIAN_FRONTEND=noninteractive apt-get update -qq
    DEBIAN_FRONTEND=noninteractive apt-get install -y -qq zram-tools
fi

# Cấu hình zram dùng thuật toán zstd (nhanh nhất và tỉ lệ nén cao nhất)
cat << 'EOF' > /etc/default/zramswap
# Tỉ lệ RAM dùng cho ZRAM (50% của 32GB = 16GB zram, nén được ~40-50GB dữ liệu)
PERCENT=50
# Thuật toán nén tối ưu nhất hiện nay
ALGO=zstd
# Mức ưu tiên swap cao hơn swap trên ổ cứng
PRIORITY=100
EOF

systemctl restart zramswap.service 2>/dev/null || true
echo -e "${GREEN}✓ Đã kích hoạt ZRAM với thuật toán ZSTD!${NC}"

# ------------------------------------------------------------------------------
# 3. Kích hoạt dọn dẹp SSD NVMe tự động (FSTRIM)
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}[3/4] Kiểm tra định kỳ dọn dẹp ổ cứng SSD NVMe (fstrim)...${NC}"
systemctl enable --now fstrim.timer >/dev/null 2>&1
# Chạy fstrim thử 1 lần ngay bây giờ
fstrim -av 2>/dev/null || true
echo -e "${GREEN}✓ Đã kích hoạt fstrim.timer duy trì tốc độ đọc ghi đỉnh cao cho NVMe!${NC}"

# ------------------------------------------------------------------------------
# 4. Hiển thị kết quả kiểm tra
# ------------------------------------------------------------------------------
echo -e "\n${BLUE}[4/4] Kiểm tra các thông số vừa tối ưu:${NC}"
echo -n "• Thuật toán mạng (TCP Congestion): "
sysctl -n net.ipv4.tcp_congestion_control
echo -n "• Mức ưu tiên RAM (Swappiness): "
sysctl -n vm.swappiness
echo -n "• Giới hạn File Watchers (Inotify): "
sysctl -n fs.inotify.max_user_watches
echo "• Trạng thái Swap & ZRAM hiện tại:"
swapon --show 2>/dev/null || free -h

echo -e "\n${GREEN}======================================================${NC}"
echo -e "${GREEN}   ✨ ĐÃ HOÀN TẤT TỐI ƯU HIỆU NĂNG HỆ THỐNG THÀNH CÔNG!${NC}"
echo -e "${GREEN}======================================================${NC}"
