#!/usr/bin/env bash
# ==============================================================================
# Script Khắc Phục Triệt Để Lỗi Treo / Đen Màn Hình (Screen Freeze) Trên Kubuntu
# Dành cho hệ thống: Workstation Xeon + NVIDIA GTX 1050 Ti + KDE Plasma 6 Wayland
# ==============================================================================
set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${BLUE}================================================================${NC}"
echo -e "${BLUE}   🛠️ KHẮC PHỤC TRIỆT ĐỂ LỖI TREO MÀN HÌNH SAU KHI LOCK (KUBUNTU)${NC}"
echo -e "${BLUE}================================================================${NC}"

if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}>> Script này cần quyền sudo để cấu hình systemd.${NC}"
    echo -e "Vui lòng chạy lại bằng: ${GREEN}sudo ./fix_screen_freeze.sh${NC}"
    exit 1
fi

echo -e "\n${BLUE}[1/3] Vô hiệu hóa tính năng Sleep/Suspend ở cấp hệ thống (systemd)...${NC}"
echo -e "  (Mainboard Xeon không hỗ trợ ACPI S3 sleep phần cứng; chỉ hỗ trợ S0, S4, S5."
echo -e "   Kernel fallback sang s2idle gây crash driver NVIDIA 580 + KWin Wayland)."

# 1. Mask các target sleep/suspend trong systemd
systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target

# 2. Cấu hình sleep.conf.d
mkdir -p /etc/systemd/sleep.conf.d
cat << 'EOF' > /etc/systemd/sleep.conf.d/disable-sleep.conf
[Sleep]
AllowSuspend=no
AllowHibernation=no
AllowSuspendThenHibernate=no
AllowHybridSleep=no
EOF

# 3. Cấu hình logind.conf.d
mkdir -p /etc/systemd/logind.conf.d
cat << 'EOF' > /etc/systemd/logind.conf.d/disable-sleep.conf
[Login]
HandleSuspendKey=ignore
HandleHibernateKey=ignore
HandleLidSwitch=ignore
HandleLidSwitchExternalPower=ignore
HandleLidSwitchDocked=ignore
IdleAction=ignore
EOF

systemctl daemon-reload
echo -e "${GREEN}✓ Đã khóa (mask) toàn bộ sleep, suspend, hibernate cấp hạt nhân.${NC}"

echo -e "\n${BLUE}[2/3] Cập nhật thiết lập PowerDevil (KDE Plasma)...${NC}"
TARGET_USER="${SUDO_USER:-$USER}"
USER_HOME=$(getent passwd "$TARGET_USER" | cut -d: -f6)

if [ -n "$USER_HOME" ] && [ -d "$USER_HOME/.config" ]; then
    sudo -u "$TARGET_USER" cat << 'EOF' > "$USER_HOME/.config/powerdevilrc"
[AC]
AutoSuspendAction=0
AutoSuspendIdleTimeoutSec=0

[AC][Display]
DimDisplayIdleTimeoutSec=0
DimDisplayWhenIdle=false
TurnOffDisplayIdleTimeoutSec=0
TurnOffDisplayIdleTimeoutWhenLockedSec=0
TurnOffDisplayWhenIdle=false

[AC][SuspendAndShutdown]
AutoSuspendAction=0
AutoSuspendIdleTimeoutSec=0

[Battery]
AutoSuspendAction=0
AutoSuspendIdleTimeoutSec=0

[Battery][Display]
DimDisplayIdleTimeoutSec=0
DimDisplayWhenIdle=false
TurnOffDisplayIdleTimeoutSec=0
TurnOffDisplayIdleTimeoutWhenLockedSec=0
TurnOffDisplayWhenIdle=false

[Battery][SuspendAndShutdown]
AutoSuspendAction=0
AutoSuspendIdleTimeoutSec=0

[LowBattery]
AutoSuspendAction=0
AutoSuspendIdleTimeoutSec=0

[LowBattery][Display]
DimDisplayIdleTimeoutSec=0
DimDisplayWhenIdle=false
TurnOffDisplayIdleTimeoutSec=0
TurnOffDisplayIdleTimeoutWhenLockedSec=0
TurnOffDisplayWhenIdle=false

[LowBattery][SuspendAndShutdown]
AutoSuspendAction=0
AutoSuspendIdleTimeoutSec=0
EOF
    echo -e "${GREEN}✓ Đã cấu hình powerdevilrc của user $TARGET_USER về chế độ an toàn.${NC}"
fi

echo -e "\n${BLUE}[3/3] Kiểm tra trạng thái áp dụng:${NC}"
systemctl status sleep.target suspend.target | grep "Loaded:" || true

echo -e "\n${GREEN}================================================================${NC}"
echo -e "${GREEN}   ✨ ĐÃ HOÀN TẤT! Máy tính giờ sẽ chỉ khóa màn hình thuần túy,${NC}"
echo -e "${GREEN}   không bao giờ tự động chuyển sang chế độ s2idle gây chết GPU.${NC}"
echo -e "${GREEN}================================================================${NC}"
