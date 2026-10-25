#!/usr/bin/env bash
# ==============================================================================
# Script chuyển giao diện Kubuntu sang phong cách macOS (Top Bar + Centered Dock)
# ==============================================================================
set -e

BACKUP_FILE="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc.bak"
CONFIG_FILE="$HOME/.config/plasma-org.kde.plasma.desktop-appletsrc"

# 1. Sao lưu cấu hình hiện tại nếu chưa có
if [ ! -f "$BACKUP_FILE" ]; then
    echo ">> Đang tạo bản sao lưu cấu hình thanh bar ban đầu tại $BACKUP_FILE..."
    cp "$CONFIG_FILE" "$BACKUP_FILE"
fi

echo ">> Đang thiết lập giao diện macOS Style..."

# 2. Chạy kịch bản Plasma Scripting qua DBus
qdbus6 org.kde.plasmashell /PlasmaShell evaluateScript '
// 1. Tìm hoặc tạo Top Bar (Thanh trạng thái phía trên)
var topPanel = null;
var bottomPanel = null;

for (var i = 0; i < panels().length; i++) {
    var p = panels()[i];
    if (p.location === "top") {
        topPanel = p;
    } else if (p.location === "bottom") {
        bottomPanel = p;
    }
}

// Nếu chưa có Top Panel, tạo mới
if (!topPanel) {
    topPanel = new Panel;
    topPanel.location = "top";
    topPanel.height = 32;
    topPanel.floating = false;
    topPanel.lengthMode = "fill";

    // Application Launcher (Menu góc trái)
    var kickoff = topPanel.addWidget("org.kde.plasma.kickoff");
    kickoff.currentConfigGroup = ["General"];
    kickoff.writeConfig("icon", "start-here-kubuntu");

    // Global Menu (Menu File, Edit... kiểu Mac)
    topPanel.addWidget("org.kde.plasma.appmenu");

    // Spacer đẩy cụm khay hệ thống sang phải
    topPanel.addWidget("org.kde.plasma.panelspacer");

    // Khay hệ thống
    topPanel.addWidget("org.kde.plasma.systemtray");

    // Đồng hồ số tinh gọn 1 dòng
    var clock = topPanel.addWidget("org.kde.plasma.digitalclock");
    clock.currentConfigGroup = ["Appearance"];
    clock.writeConfig("showDate", "false");
    clock.writeConfig("showSeconds", "false");
}

// 2. Tinh chỉnh Bottom Panel thành Centered Floating Dock
if (bottomPanel) {
    bottomPanel.alignment = "center";
    bottomPanel.floating = true;
    bottomPanel.lengthMode = "fit";
    bottomPanel.minimumLength = 0;
    bottomPanel.maximumLength = 2560;
    bottomPanel.height = 58;
    bottomPanel.hiding = "none"; // Hoặc "dodgewindows" nếu muốn ẩn khi cửa sổ đè lên

    var ws = bottomPanel.widgets();
    var hasIconTasks = false;
    var hasTrash = false;

    for (var j = 0; j < ws.length; j++) {
        var widget = ws[j];
        if (widget.type === "org.kde.plasma.icontasks") {
            hasIconTasks = true;
            var cleanLaunchers = "applications:org.kde.dolphin.desktop,preferred://browser,applications:code.desktop,applications:org.kde.konsole.desktop,applications:systemsettings.desktop";
            widget.currentConfigGroup = [];
            widget.writeConfig("launchers", cleanLaunchers);
            widget.currentConfigGroup = ["General"];
            widget.writeConfig("launchers", cleanLaunchers);
        } else if (widget.type === "org.kde.plasma.trash") {
            hasTrash = true;
        } else {
            widget.remove();
        }
    }

    if (!hasTrash) {
        bottomPanel.addWidget("org.kde.plasma.trash");
    }
}
'

echo "==> Đã áp dụng giao diện macOS (Top Bar + Centered Floating Dock) thành công!"
