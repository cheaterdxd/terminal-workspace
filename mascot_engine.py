#!/usr/bin/env python3
"""
Kubi - Smart Reactive Mascot & Habitat Engine for Kubuntu Terminal
Hệ thống Linh vật Kaomoji thông minh:
- Đi qua đi lại tự nhiên (Pacing / Walking Animation)
- Phản ứng theo ngữ cảnh hành động người dùng (Event-Driven Reactive System)
- Nhận diện CVE, tin tức bảo mật, sự kiện Pomodoro, Streak hoàn thành task
- Cơ chế chống lặp lời thoại (Anti-repetition history)
"""

import os
import random
import re
import json
from datetime import datetime
from collections import deque

CONFIG_FILE = os.path.expanduser("~/.workspace_mascot_config.json")

def load_mascot_config() -> dict:
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"style": "cat"}

def save_mascot_config(cfg: dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2)
    except Exception:
        pass

# ------------------------------------------------------------------------------
# Bộ Sprite Đồ Họa Pixel Retro Nghệ Thuật (Block Pixel Art Sprites)
# Mỗi sprite có đúng 5 dòng (height: 5 lines, 10-12 chars wide)
# ------------------------------------------------------------------------------

# 1. PIXEL CYBER CAT (NEKO)
SPRITES_CAT = {
    "walk_r1": [
        "[bold cyan] ▄▄     ▄▄ [/bold cyan]",
        "[bold cyan]████[/bold cyan][bold white]▄▄[/bold white][bold cyan]████[/bold cyan]",
        "[bold cyan]██[/bold cyan][bold white] █[/bold white][bold cyan]█[/bold cyan][bold white]█ [/bold white][bold cyan]██[/bold cyan][bold magenta] ▄[/bold magenta]",
        "[bold cyan] ▀███████▀ [/bold cyan][bold magenta]█[/bold magenta]",
        "[bold cyan]   █   █   [/bold cyan]"
    ],
    "walk_r2": [
        "[bold cyan] ▄▄     ▄▄ [/bold cyan]",
        "[bold cyan]████[/bold cyan][bold white]▄▄[/bold white][bold cyan]████[/bold cyan]",
        "[bold cyan]██[/bold cyan][bold white] █[/bold white][bold cyan]█[/bold cyan][bold white]█ [/bold white][bold cyan]██[/bold cyan][bold magenta] ▀[/bold magenta]",
        "[bold cyan] ▀███████▀ [/bold cyan][bold magenta]█[/bold magenta]",
        "[bold cyan]  ▀     ▀  [/bold cyan]"
    ],
    "walk_l1": [
        "[bold cyan] ▄▄     ▄▄ [/bold cyan]",
        "[bold cyan]████[/bold cyan][bold white]▄▄[/bold white][bold cyan]████[/bold cyan]",
        "[bold magenta]▄ [/bold magenta][bold cyan]██[/bold cyan][bold white] █[/bold white][bold cyan]█[/bold cyan][bold white]█ [/bold white][bold cyan]██[/bold cyan]",
        "[bold magenta]█ [/bold magenta][bold cyan]▀███████▀ [/bold cyan]",
        "[bold cyan]   █   █   [/bold cyan]"
    ],
    "walk_l2": [
        "[bold cyan] ▄▄     ▄▄ [/bold cyan]",
        "[bold cyan]████[/bold cyan][bold white]▄▄[/bold white][bold cyan]████[/bold cyan]",
        "[bold magenta]▀ [/bold magenta][bold cyan]██[/bold cyan][bold white] █[/bold white][bold cyan]█[/bold cyan][bold white]█ [/bold white][bold cyan]██[/bold cyan]",
        "[bold magenta]█ [/bold magenta][bold cyan]▀███████▀ [/bold cyan]",
        "[bold cyan]  ▀     ▀  [/bold cyan]"
    ],
    "alert": [
        "[bold red]     ▄█▄   [/bold red]",
        "[bold cyan] ▄▄     ▄▄ [/bold cyan]",
        "[bold cyan]██[/bold cyan][bold red] ◉[/bold red][bold cyan]█[/bold cyan][bold red]◉ [/bold red][bold cyan]██[/bold cyan][bold magenta] █[/bold magenta]",
        "[bold cyan] ▀███████▀ [/bold cyan][bold magenta]█[/bold magenta]",
        "[bold cyan]   █   █   [/bold cyan]"
    ],
    "celebrate": [
        "[bold yellow]   ★     ★ [/bold yellow]",
        "[bold cyan] ▄▄     ▄▄ [/bold cyan]",
        "[bold cyan]██[/bold cyan][bold white] ▄[/bold white][bold cyan]█[/bold cyan][bold white]▄ [/bold white][bold cyan]██[/bold cyan][bold magenta] █[/bold magenta]",
        "[bold cyan] ▀███████▀ [/bold cyan][bold magenta]▀[/bold magenta]",
        "[bold yellow]   ▀   ▀   [/bold yellow]"
    ],
    "focus": [
        "[bold cyan] ▄█▀▀▀▀▀█▄ [/bold cyan]",
        "[bold cyan]█▄▄     ▄▄█[/bold cyan]",
        "[bold cyan]██[/bold cyan][bold white] ■[/bold white][bold cyan]█[/bold cyan][bold white]■ [/bold white][bold cyan]██[/bold cyan][bold magenta] █[/bold magenta]",
        "[bold cyan] ▀███████▀ [/bold cyan][bold magenta]█[/bold magenta]",
        "[bold cyan]   █   █   [/bold cyan]"
    ],
    "sleep": [
        "[bold blue]       z Z [/bold blue]",
        "[bold cyan]  ▄▄   ▄▄  [/bold cyan]",
        "[bold cyan] █████████ [/bold cyan]",
        "[bold cyan]  ▀██- -██▀[/bold cyan]",
        "[bold cyan]   ▀▀▀▀▀   [/bold cyan]"
    ]
}

# 2. PIXEL CYBER BOT (ROBO)
SPRITES_ROBO = {
    "walk_r1": [
        "[bold yellow]     ▄█▄   [/bold yellow]",
        "[bold magenta]   ▄█████▄ [/bold magenta]",
        "[bold magenta]  █ [/bold magenta][bold cyan]▀█ █▀[/bold cyan][bold magenta] █ [/bold magenta]",
        "[bold magenta]  █▄▄▄▄▄▄▄█[/bold magenta]",
        "[bold magenta]    █   █  [/bold magenta]"
    ],
    "walk_r2": [
        "[bold yellow]     ▄█▄   [/bold yellow]",
        "[bold magenta]   ▄█████▄ [/bold magenta]",
        "[bold magenta]  █ [/bold magenta][bold cyan]▀█ █▀[/bold cyan][bold magenta] █ [/bold magenta]",
        "[bold magenta]  █▄▄▄▄▄▄▄█[/bold magenta]",
        "[bold magenta]   ▀     ▀ [/bold magenta]"
    ],
    "walk_l1": [
        "[bold yellow]   ▄█▄     [/bold yellow]",
        "[bold magenta] ▄█████▄   [/bold magenta]",
        "[bold magenta] █ [/bold magenta][bold cyan]▀█ █▀[/bold cyan][bold magenta] █  [/bold magenta]",
        "[bold magenta] █▄▄▄▄▄▄▄█ [/bold magenta]",
        "[bold magenta]   █   █   [/bold magenta]"
    ],
    "walk_l2": [
        "[bold yellow]   ▄█▄     [/bold yellow]",
        "[bold magenta] ▄█████▄   [/bold magenta]",
        "[bold magenta] █ [/bold magenta][bold cyan]▀█ █▀[/bold cyan][bold magenta] █  [/bold magenta]",
        "[bold magenta] █▄▄▄▄▄▄▄█ [/bold magenta]",
        "[bold magenta]  ▀     ▀  [/bold magenta]"
    ],
    "alert": [
        "[bold red]   ⚡ ▄█▄ ⚡ [/bold red]",
        "[bold magenta]   ▄█████▄ [/bold magenta]",
        "[bold magenta]  █ [/bold magenta][bold red]◉█ █◉[/bold red][bold magenta] █ [/bold magenta]",
        "[bold magenta]  █▄▄▄▄▄▄▄█[/bold magenta]",
        "[bold magenta]    █   █  [/bold magenta]"
    ],
    "focus": [
        "[bold cyan]  ▄█▀▀▀▀▀█▄[/bold cyan]",
        "[bold cyan] █[/bold cyan][bold magenta]▄█████▄[/bold magenta][bold cyan]█[/bold cyan]",
        "[bold magenta]  █ [/bold magenta][bold cyan]■█ █■[/bold cyan][bold magenta] █ [/bold magenta]",
        "[bold magenta]  █▄▄▄▄▄▄▄█[/bold magenta]",
        "[bold magenta]    █   █  [/bold magenta]"
    ],
    "celebrate": [
        "[bold yellow]   ★ ▄█▄ ★ [/bold yellow]",
        "[bold magenta]   \█████/ [/bold magenta]",
        "[bold magenta]  █ [/bold magenta][bold yellow]▀█ █▀[/bold yellow][bold magenta] █ [/bold magenta]",
        "[bold magenta]  █▄▄▄▄▄▄▄█[/bold magenta]",
        "[bold yellow]    ▀   ▀  [/bold yellow]"
    ],
    "sleep": [
        "[bold blue]       z Z [/bold blue]",
        "[bold yellow]     ▄█▄   [/bold yellow]",
        "[bold magenta]   ▄█████▄ [/bold magenta]",
        "[bold magenta]  █ [/bold magenta][bold dim]-█ █-[/bold dim][bold magenta] █ [/bold magenta]",
        "[bold magenta]   ▀▀▀▀▀▀▀ [/bold magenta]"
    ]
}

# 3. PIXEL CYBER SLIME (SLIME)
SPRITES_SLIME = {
    "walk_r1": [
        "[bold green]    ▄████▄   [/bold green]",
        "[bold green]   ████████  [/bold green]",
        "[bold green]   █ [/bold green][bold white]●[/bold white][bold green]  [/bold green][bold white]●[/bold white][bold green] █  [/bold green]",
        "[bold green]   ██[/bold green][bold pink]▄[/bold pink][bold green]██[/bold green][bold pink]▄[/bold pink][bold green]██  [/bold green]",
        "[bold green]   ▀ ▀  ▀ ▀  [/bold green]"
    ],
    "walk_r2": [
        "[bold green]   ▄██████▄  [/bold green]",
        "[bold green]  ██████████ [/bold green]",
        "[bold green]  █ [/bold green][bold white]●[/bold white][bold green]    [/bold green][bold white]●[/bold white][bold green] █ [/bold green]",
        "[bold green]  ███[/bold green][bold pink]▄[/bold pink][bold green]██[/bold green][bold pink]▄[/bold pink][bold green]███ [/bold green]",
        "[bold green]   ▀  ▀▀  ▀  [/bold green]"
    ],
    "walk_l1": [
        "[bold green]   ▄████▄    [/bold green]",
        "[bold green]  ████████   [/bold green]",
        "[bold green]  █ [/bold green][bold white]●[/bold white][bold green]  [/bold green][bold white]●[/bold white][bold green] █   [/bold green]",
        "[bold green]  ██[/bold green][bold pink]▄[/bold pink][bold green]██[/bold green][bold pink]▄[/bold pink][bold green]██   [/bold green]",
        "[bold green]  ▀ ▀  ▀ ▀   [/bold green]"
    ],
    "walk_l2": [
        "[bold green]  ▄██████▄   [/bold green]",
        "[bold green] ██████████  [/bold green]",
        "[bold green] █ [/bold green][bold white]●[/bold white][bold green]    [/bold green][bold white]●[/bold white][bold green] █  [/bold green]",
        "[bold green] ███[/bold green][bold pink]▄[/bold pink][bold green]██[/bold green][bold pink]▄[/bold pink][bold green]███  [/bold green]",
        "[bold green]  ▀  ▀▀  ▀   [/bold green]"
    ],
    "alert": [
        "[bold red]     !  !    [/bold red]",
        "[bold green]   ▄██████▄  [/bold green]",
        "[bold green]  █ [/bold green][bold red]◉[/bold red][bold green]    [/bold green][bold red]◉[/bold red][bold green] █ [/bold green]",
        "[bold green]  ██████████ [/bold green]",
        "[bold green]   ▀  ▀▀  ▀  [/bold green]"
    ],
    "celebrate": [
        "[bold yellow]   ★      ★  [/bold yellow]",
        "[bold green]    ▄████▄   [/bold green]",
        "[bold green]   █ [/bold green][bold yellow]^[/bold yellow][bold green]  [/bold green][bold yellow]^[/bold yellow][bold green] █   [/bold green]",
        "[bold green]   ████████  [/bold green]",
        "[bold yellow]    ▀ ▀  ▀   [/bold yellow]"
    ],
    "focus": [
        "[bold cyan]   ▄█▀▀▀▀█▄  [/bold cyan]",
        "[bold cyan]  █[/bold cyan][bold green]▄████▄[/bold green][bold cyan]█  [/bold cyan]",
        "[bold green]  █ [/bold green][bold white]■[/bold white][bold green]  [/bold green][bold white]■[/bold white][bold green] █  [/bold green]",
        "[bold green]  ████████   [/bold green]",
        "[bold green]   ▀ ▀  ▀ ▀  [/bold green]"
    ],
    "sleep": [
        "[bold blue]       z Z   [/bold blue]",
        "[bold green]   ▄██████▄  [/bold green]",
        "[bold green]  ██- - - -██[/bold green]",
        "[bold green]  ██████████ [/bold green]",
        "[bold green]   ▀▀▀▀▀▀▀▀  [/bold green]"
    ]
}

# 4. PIXEL CYBER DINO (DINO)
SPRITES_DINO = {
    "walk_r1": [
        "[bold green]     ▄████▄ [/bold green]",
        "[bold green]     ███████[/bold green]",
        "[bold green]   ▄██[/bold green][bold white] ▀ ▀[/bold white][bold green]   [/bold green]",
        "[bold green] ▄██████    [/bold green]",
        "[bold green]   █   █    [/bold green]"
    ],
    "walk_r2": [
        "[bold green]     ▄████▄ [/bold green]",
        "[bold green]     ███████[/bold green]",
        "[bold green]   ▄██[/bold green][bold white] ▀ ▀[/bold white][bold green]   [/bold green]",
        "[bold green] ▄██████    [/bold green]",
        "[bold green]  ▀     ▀   [/bold green]"
    ],
    "walk_l1": [
        "[bold green] ▄████▄     [/bold green]",
        "[bold green]███████     [/bold green]",
        "[bold green]   [/bold green][bold white]▀ ▀ [/bold white][bold green]██▄   [/bold green]",
        "[bold green]    ██████▄ [/bold green]",
        "[bold green]    █   █   [/bold green]"
    ],
    "walk_l2": [
        "[bold green] ▄████▄     [/bold green]",
        "[bold green]███████     [/bold green]",
        "[bold green]   [/bold green][bold white]▀ ▀ [/bold white][bold green]██▄   [/bold green]",
        "[bold green]    ██████▄ [/bold green]",
        "[bold green]   ▀     ▀  [/bold green]"
    ],
    "alert": [
        "[bold red]     ▄█▄    [/bold red]",
        "[bold green]     ▄████▄ [/bold green]",
        "[bold green]   ▄██[/bold green][bold red] ◉ ◉[/bold red][bold green]   [/bold green]",
        "[bold green] ▄██████    [/bold green]",
        "[bold green]   █   █    [/bold green]"
    ],
    "celebrate": [
        "[bold yellow]   ★     ★  [/bold yellow]",
        "[bold green]     ▄████▄ [/bold green]",
        "[bold green]   ▄██[/bold green][bold yellow] ^ ^[/bold yellow][bold green]   [/bold green]",
        "[bold green] ▄██████    [/bold green]",
        "[bold yellow]  ▀     ▀   [/bold yellow]"
    ],
    "focus": [
        "[bold cyan]   ▄█▀▀▀▀█▄ [/bold cyan]",
        "[bold cyan]  █[/bold cyan][bold green]▄████▄[/bold green][bold cyan]█ [/bold cyan]",
        "[bold green]   ▄██[/bold green][bold white] ■ ■[/bold white][bold green]   [/bold green]",
        "[bold green] ▄██████    [/bold green]",
        "[bold green]   █   █    [/bold green]"
    ],
    "sleep": [
        "[bold blue]       z Z  [/bold blue]",
        "[bold green]     ▄████▄ [/bold green]",
        "[bold green]   ▄██- -   [/bold green]",
        "[bold green] ▄██████    [/bold green]",
        "[bold green]  ▀▀▀▀▀▀    [/bold green]"
    ]
}

ALL_PIXEL_SPRITES = {
    "cat": SPRITES_CAT,
    "robo": SPRITES_ROBO,
    "slime": SPRITES_SLIME,
    "dino": SPRITES_DINO
}

# ------------------------------------------------------------------------------
# Sprite Kaomoji theo Chuyển Động & Tâm Trạng
# ------------------------------------------------------------------------------
WALK_RIGHT_SPRITES = [
    "(ง ˶•ᴗ•˶ )ง ⁾⁾",
    "( ˶•ᴗ•˶ )ง ⁾⁾",
    "(ง ˶ᵔ ᵕ ᵔ˶ )ง ⁾⁾",
    "( ˶ᵔ ᵕ ᵔ˶ )ง ⁾⁾"
]

WALK_LEFT_SPRITES = [
    "₍₍ ٩( ˶•ᴗ•˶ )۶",
    "₍₍ ( ˶•ᴗ•˶ )۶",
    "₍₍ ٩( ˶ᵔ ᵕ ᵔ˶ )۶",
    "₍₍ ( ˶ᵔ ᵕ ᵔ˶ )۶"
]

IDLE_SPRITES = [
    "( ˶•ᴗ•˶ ) ~♪",
    "( •‿• )",
    "( ˘ᴗ˘ )",
    "( ˶ᵔ ᵕ ᵔ˶ )",
    "( '◡' ) ☕",
    "( ◕‿◕ )"
]

BLINK_SPRITES = [
    "( ˶-.-˶ )",
    "( -‿- )",
    "( ˘-˘ )",
    "( ˶- ᵕ -˶ )"
]

FOCUS_SPRITES = [
    "🎧( •̀_•́ )୨",
    "💻( •̀ω•́ )",
    "🎧( •̀ω•́ )✧",
    "(ง •̀_•́)ง 💻",
    "🔥( •̀ω•́ )و"
]

CELEBRATE_SPRITES = [
    "＼(＾O＾)／ 🎉",
    "( ＾◡＾)っ ✨",
    "( ๑‾̀◡‾́)و✧",
    "(ﾉ◕ヮ◕)ﾉ*:･ﾟ✧",
    "٩(ˊᗜˋ*)و 🌟",
    "(★^O^★) 🔥"
]

CVE_ALERT_SPRITES = [
    "🔎( ◉_◉ ) !",
    "🛡️( •̀_•́ )",
    "(⊙_☉) ⚠️",
    "🔎(・_・ ) ⚡"
]

THINKING_SPRITES = [
    "( ˘･_･˘ ) 💭",
    "(・_・;) 💭",
    "🧠( ◉_◉ ) ⚡",
    "( ˘_˘ ) 💭"
]

SLEEPY_SPRITES = [
    "( ˘ω˘ )zzZ",
    "( - . - )~zZ",
    "( ᴗ ̫ ᴗ ) zZ",
    "( -ω- )zzZ"
]

WEB_BYE_SPRITES = [
    "( ^_^)／ 🌐",
    "( ＾◡＾)っ 🔗",
    "＼(•‿•)／ 🌍"
]

# ------------------------------------------------------------------------------
# Danh mục Thoại Thông Minh Theo Sự Kiện Thực Tế (Event-Driven Dialogues)
# ------------------------------------------------------------------------------
EVENT_DIALOGUES = {
    "cve_found": [
        "Úi, phát hiện mã lỗ hổng {cve} kìa! Xem kỹ khuyến nghị phòng thủ nhé!",
        "Mã {cve} này nhìn căng đét! Bấm [x] để tôi nhờ AI bóc tách chi tiết nha!",
        "Cảnh báo lỗ hổng an ninh: {cve}! Bạn kiểm tra xem hệ thống có bị dính không?",
        "Lại có CVE mới ({cve})! Đọc xem hacker khai thác qua ngõ nào nhé!"
    ],
    "cisa_alert": [
        "CISA vừa phát cảnh báo an ninh khẩn! Đọc ngay xem có dính 0-day không bạn ơi!",
        "Tin từ cơ quan an ninh CISA thường rất nóng và có rủi ro cao đấy!",
        "Cảnh báo cấp nhà nước từ CISA! Đừng bỏ qua chi tiết này nhé!"
    ],
    "unit42_intel": [
        "Báo cáo chuyên sâu từ Palo Alto Unit 42! Toàn phân tích mã độc xịn sò!",
        "Unit 42 lên bài mới kìa! Đọc xem chiến dịch tấn công APT diễn ra thế nào nha!"
    ],
    "cluster_news": [
        "Vụ này lớn dữ! Nhiều nguồn bảo mật uy tín đều đồng loạt đưa tin!",
        "Sự kiện bảo mật trọng điểm! Cả làng an ninh mạng đang rôm rả bàn tán!",
        "Bài viết này được tổng hợp đa nguồn nè, đầy đủ góc nhìn luôn!"
    ],
    "open_web": [
        "Đang mở trình duyệt Chrome... Tôi ở đây trông nhà, bạn đọc tin vui vẻ nhé! 🌐",
        "Bay ra web đọc tài liệu gốc nhé! Xong việc quay lại tôi vẫn đợi ở đây! ( ^_^)／",
        "Mở tab web rồi nè! Đọc kỹ bài phân tích nhé bạn ơi!"
    ],
    "task_done_single": [
        "Gạch thêm 1 việc! Từng bước một đưa danh sách việc về con số 0! ＼(＾O＾)／",
        "Xong một mục tiêu! Năng suất làm việc của bạn đang tăng vọt đấy!",
        "Quá mượt mà! Thêm 1 việc được giải quyết gọn gàng!",
        "Tiến độ tăng lên vù vù! Cứ giữ vững phong độ này nhé bạn! ✨"
    ],
    "task_done_streak": [
        "COMBO {count} TASK LIÊN TIẾP! 🚀 Năng lượng hôm nay đỉnh chóp thực sự!",
        "Không thể ngăn cản! {count} việc đã được giải quyết liên tù tì! (★^O^★)",
        "Đỉnh quá bạn ơi! Chuỗi {count} task hoàn thành trong một nốt nhạc! 🔥"
    ],
    "all_tasks_done": [
        "HOÀN THÀNH 100% CÔNG VIỆC! 🎉 Ngày làm việc hoàn hảo không tì vết! (⌐■_■)",
        "Hết sạch danh sách việc hôm nay rồi! Bạn xứng danh Cao thủ Kubuntu! 🏆"
    ],
    "task_in_progress": [
        "Bắt tay vào làm việc này thôi! Tập trung 1 mạch là xong ngay! (ง •̀_•́)ง",
        "Chuyển trạng thái đang làm! Cố lên nhé, việc khó mấy cũng qua thôi!",
        "Tập trung giải quyết dứt điểm task này nào!"
    ],
    "task_delete": [
        "Đã dẹp bớt task thừa! Danh sách việc gọn gàng nhìn dễ thở hẳn! ( •_• )/🗑️",
        "Xóa việc không cần thiết! Giữ sự tập trung vào những mục tiêu then chốt nha!"
    ],
    "task_add": [
        "Đã ghi vào sổ tay! Một mục tiêu mới đã sẵn sàng để chinh phục! 📝",
        "Có thêm đầu việc mới! Lên kế hoạch xử lý ngăn nắp nha bạn!"
    ],
    "focus_start": [
        "25 phút vàng son bắt đầu! Đeo tai nghe vào, tôi giữ im lặng cho bạn code! 🎧",
        "Chế độ tập trung cao độ! Đừng để bất kỳ xao nhãng nào chen ngang nhé!",
        "Bắt đầu đếm giờ! 25 phút này sẽ giải quyết xong khối việc đỉnh!"
    ],
    "focus_pause": [
        "Tạm dừng đếm giờ! Đứng dậy vươn vai, uống ngụm nước rồi quay lại nha! ☕",
        "Nghỉ tay một nhịp ngắn, hít thở sâu nào!"
    ],
    "focus_done": [
        "CHUÔNG REO HẾT 25 PHÚT! 🎉 Bạn đã tập trung cực kỳ xuất sắc! Vươn vai nào!",
        "Hoàn thành trọn vẹn 1 phiên Focus! Bạn xứng đáng nhận 10 điểm kỷ luật! ☕",
        "Nghỉ giải lao 5 phút thôi! Não bộ vừa có một phiên làm việc siêu chất lượng!"
    ],
    "kickstart_start": [
        "CHẾ ĐỘ PHÁ BĂNG 5 PHÚT BẮT ĐẦU! 🔥 Chỉ cần tập trung 5 phút này, không nghĩ gì xa xôi! Tôi ngồi đây trông bạn! (ง •̀_•́)ง",
        "Thỏa thuận 5 phút vàng! Vượt qua 5 phút đầu tiên này là bạn sẽ vào guồng Flow state ngay! Cố lên bạn ơi! 🚀",
        "Đừng sợ việc lớn! Làm bước 0 ngay bây giờ nào! 5 phút đánh tan sức ì tâm lý! ✨"
    ],
    "kickstart_decomposed": [
        "AI đã bẻ nhỏ việc này thành 3 bước siêu dễ rồi nè! Bước 1 chỉ tốn 2 phút thôi, làm luôn nào! (★^O^★)",
        "Bẻ khóa sức ì thành công! Bước 1 nhẹ như lông hồng, gõ phím ngay thôi bạn ơi! ＼(＾O＾)／",
        "Đã có bước khởi động 2 phút! Đừng suy nghĩ nữa, bắt tay vào ngay thôi! 🔥"
    ],
    "kickstart_done": [
        "XONG 5 PHÚT PHÁ BĂNG! 🎉 Sức ì đã bị đánh bại hoàn toàn! Bạn có đà rồi, làm tiếp luôn nhé! 🔥",
        "Tuyệt vời! Bạn thấy chưa, bắt tay vào làm là mọi thứ trôi chảy ngay! Tiếp tục giữ đà nào! ( ¯꒳¯ )b",
        "5 phút khởi động xuất sắc! Não bộ đã vào guồng làm việc rồi, tiến lên nào! 🚀"
    ],
    "ai_thinking": [
        "Đang triệu hồi AI (agy/codex)... Bộ não AI đang phân tích dữ liệu 100%! 🧠⚡",
        "Đang bóc tách IoC và tổng hợp khuyến nghị kỹ thuật, chờ tôi xíu nhé...",
        "Đang quét sâu bài viết an ninh mạng, bản tóm tắt sắp xuất hiện rồi!"
    ],
    "ai_done": [
        "Xong rồi nè! Báo cáo phân tích chuyên sâu đã sẵn sàng, mời bạn thẩm định! ( ¯꒳¯ )b",
        "AI đã tổng hợp xong! Toàn thông tin cốt lõi, bấm xem ngay nha! ✨"
    ],
    "idle_pacing": [
        "Đang dạo một vòng kiểm tra tiến độ làm việc... ( ˶•ᴗ•˶ )",
        "Hôm nay hệ thống chạy êm ru, terminal mượt mà ghê!",
        "Bạn cứ thoải mái gõ lệnh nhé, tôi ở đây đồng hành cùng bạn!",
        "Code một cách bình tĩnh và chỉn chu, chất lượng hơn số lượng nha!",
        "Cố gắng lên nhé, từng dòng lệnh của bạn đều rất giá trị!"
    ],
    "night": [
        "Đã khuya rồi đó bạn ơi! Nhớ giữ gìn sức khỏe, nghỉ ngơi sớm mai chiến tiếp nha! ( ˘ω˘ )",
        "Khuya rồi nè, cho đôi mắt nghỉ ngơi chút đi bạn ơi!",
        "Lập trình viên thông minh là người biết ngủ đủ giấc để mai code không bug! ☕"
    ]
}

# ------------------------------------------------------------------------------
# Mascot State & Habitat Manager (Class Quản Lý Trạng Thái Toàn Diện)
# ------------------------------------------------------------------------------
class MascotHabitat:
    def __init__(self, stage_width: int = 56, style: str = None):
        self.stage_width = stage_width
        self.pos_x = 4
        self.walk_dir = 1
        self.mood = "idle"
        self.current_face = "( ˶•ᴗ•˶ )"
        self.current_msg = "Chào bạn! Tôi là Kubi, sẵn sàng đồng hành cùng bạn!"
        self.lock_ticks = 0
        self.is_walking = True
        self.task_streak = 0
        self.history = deque(maxlen=6)
        
        # Cấu hình phong cách linh vật (Mặc định: Pixel Cyber Cat)
        cfg = load_mascot_config()
        self.style = style or cfg.get("style", "cat")
        self.step_frame = 0
        
        # Thiết lập ban đầu theo giờ
        self._set_time_greeting()

    def set_style(self, new_style: str):
        """Chuyển đổi linh hoạt giữa các phong cách: cat, robo, slime, dino, kaomoji."""
        if new_style in ("cat", "robo", "slime", "dino", "kaomoji"):
            self.style = new_style
            save_mascot_config({"style": new_style})

    def _set_time_greeting(self):
        hour = datetime.now().hour
        if hour >= 22 or hour < 5:
            self.mood = "sleepy"
            self.current_msg = random.choice(EVENT_DIALOGUES["night"])
        elif 5 <= hour < 12:
            self.mood = "idle"
            self.current_msg = "Chào buổi sáng năng lượng! Cùng tạo nên một ngày làm việc tuyệt vời nhé!"
        elif 12 <= hour < 18:
            self.mood = "idle"
            self.current_msg = "Buổi chiều năng suất! Tập trung làm chủ từng dòng code nhé!"
        else:
            self.mood = "idle"
            self.current_msg = "Buổi tối an lành! Rà soát lại công việc và hoàn tất mục tiêu hôm nay nhé!"

    def react_to_event(self, event_type: str, data: dict = None, lock_seconds: float = 6.0):
        """Phản ứng tức thì theo sự kiện từ hành vi người dùng."""
        data = data or {}
        template_list = EVENT_DIALOGUES.get(event_type, EVENT_DIALOGUES["idle_pacing"])
        
        # Chọn câu thoại không trùng với 6 câu gần nhất
        available = [t for t in template_list if t not in self.history]
        chosen = random.choice(available if available else template_list)
        
        # Điền tham số vào câu thoại
        msg = chosen
        if "{cve}" in msg:
            cve_val = data.get("cve", "CVE")
            msg = msg.replace("{cve}", cve_val)
        if "{count}" in msg:
            count_val = str(data.get("count", self.task_streak))
            msg = msg.replace("{count}", count_val)
            
        self.current_msg = msg
        self.history.append(msg)
        self.lock_ticks = max(1, int(lock_seconds / 1.5))
        
        # Cập nhật Sprite và Mood tương ứng
        if event_type == "cve_found":
            self.mood = "cve"
            self.current_face = random.choice(CVE_ALERT_SPRITES)
            self.is_walking = False
        elif event_type in ("cisa_alert", "unit42_intel", "cluster_news"):
            self.mood = "cve"
            self.current_face = random.choice(CVE_ALERT_SPRITES)
            self.is_walking = False
        elif event_type == "open_web":
            self.mood = "web"
            self.current_face = random.choice(WEB_BYE_SPRITES)
            self.is_walking = False
        elif event_type in ("task_done_single", "task_done_streak", "all_tasks_done"):
            self.mood = "celebrate"
            self.current_face = random.choice(CELEBRATE_SPRITES)
            self.is_walking = False
        elif event_type in ("focus_start", "task_in_progress"):
            self.mood = "focus"
            self.current_face = random.choice(FOCUS_SPRITES)
            self.is_walking = False
        elif event_type == "focus_done":
            self.mood = "celebrate"
            self.current_face = random.choice(CELEBRATE_SPRITES)
            self.is_walking = False
        elif event_type == "ai_thinking":
            self.mood = "thinking"
            self.current_face = random.choice(THINKING_SPRITES)
            self.is_walking = False
        elif event_type == "ai_done":
            self.mood = "celebrate"
            self.current_face = random.choice(CELEBRATE_SPRITES)
            self.is_walking = False
        elif event_type == "task_delete":
            self.mood = "idle"
            self.current_face = "( •_• )/🗑️"
            self.is_walking = False
        elif event_type == "task_add":
            self.mood = "idle"
            self.current_face = "( •̀ω•́ )و"
            self.is_walking = False

    def tick(self, stage_width: int = None):
        """Mỗi tick (~1.5s): Quản lý bước chân đi qua đi lại hoặc chớp mắt."""
        if stage_width:
            self.stage_width = max(30, stage_width)
            
        max_x = max(6, self.stage_width - 24)
        
        # Nếu đang có phản ứng khóa (ví dụ vừa ăn mừng task xong)
        if self.lock_ticks > 0:
            self.lock_ticks -= 1
            if self.lock_ticks == 0:
                self.is_walking = True
                self.mood = "idle"
            return
            
        # Kiểm tra ban đêm
        hour = datetime.now().hour
        if (hour >= 23 or hour < 5) and random.random() < 0.4:
            self.mood = "sleepy"
            self.current_face = random.choice(SLEEPY_SPRITES)
            self.is_walking = False
            return
            
        # Di chuyển bước chân (Walking)
        self.is_walking = True
        self.step_frame = 1 - self.step_frame
        step = 2
        self.pos_x += self.walk_dir * step
        
        # Đổi hướng khi chạm tường
        if self.pos_x >= max_x:
            self.pos_x = max_x
            self.walk_dir = -1
            self.current_face = random.choice(IDLE_SPRITES)
            # Thỉnh thoảng đổi câu thoại dạo chơi
            if random.random() < 0.35:
                self._pick_idle_message()
        elif self.pos_x <= 2:
            self.pos_x = 2
            self.walk_dir = 1
            self.current_face = random.choice(IDLE_SPRITES)
            if random.random() < 0.35:
                self._pick_idle_message()
        else:
            # Chọn sprite bước đi theo hướng
            if self.walk_dir == 1:
                self.current_face = random.choice(WALK_RIGHT_SPRITES)
            else:
                self.current_face = random.choice(WALK_LEFT_SPRITES)

    def _pick_idle_message(self):
        hour = datetime.now().hour
        if hour >= 22 or hour < 5:
            cands = EVENT_DIALOGUES["night"]
        else:
            cands = EVENT_DIALOGUES["idle_pacing"]
            
        avail = [c for c in cands if c not in self.history]
        msg = random.choice(avail if avail else cands)
        self.current_msg = msg
        self.history.append(msg)

    def get_current_sprite(self) -> list[str]:
        """Lấy 5 dòng sprite tương ứng theo mood, style và hướng đi."""
        if self.style == "kaomoji":
            face = self.current_face
            return [
                " ",
                " ",
                f"       [bold magenta]{face}[/bold magenta] [bold cyan]Kubi[/bold cyan]",
                " ",
                " "
            ]

        sprites_dict = ALL_PIXEL_SPRITES.get(self.style, SPRITES_CAT)

        if self.mood == "cve":
            return sprites_dict.get("alert", sprites_dict["walk_r1"])
        elif self.mood == "celebrate":
            return sprites_dict.get("celebrate", sprites_dict["walk_r1"])
        elif self.mood == "focus":
            return sprites_dict.get("focus", sprites_dict["walk_r1"])
        elif self.mood == "sleepy":
            return sprites_dict.get("sleep", sprites_dict["walk_r1"])
        elif self.mood == "thinking":
            return sprites_dict.get("focus", sprites_dict["walk_r1"])
        elif self.mood == "web":
            return sprites_dict.get("celebrate", sprites_dict["walk_r1"])

        # Trạng thái dạo bước (Walking)
        if self.walk_dir == 1:
            return sprites_dict["walk_r1"] if self.step_frame == 0 else sprites_dict["walk_r2"]
        else:
            return sprites_dict["walk_l1"] if self.step_frame == 0 else sprites_dict["walk_l2"]

    def render_tui(self, width: int = None) -> str:
        """Render 7 dòng nội dung cho Textual TUI Widget (đã có border từ Textual)."""
        w = max(34, (width or self.stage_width) - 4)
        
        # 1. Rút gọn text nếu quá dài
        msg_text = self.current_msg
        max_msg_len = w - 6
        if len(msg_text) > max_msg_len:
            msg_text = msg_text[:max_msg_len - 3] + "..."
            
        speech_line = f"[yellow]💬 \"{msg_text}\"[/yellow]"
        
        # 2. Vệt sàn & Vị trí chân (floor track)
        floor_len = max(10, w - 4)
        track = ['─'] * floor_len
        clamped_x = min(max(0, self.pos_x), floor_len - 1)
        track[clamped_x] = '●'
        floor_str = "".join(track)
        
        # 3. Lấy 5 dòng Pixel Sprite và căn lề theo pos_x
        sprite_rows = self.get_current_sprite()
        max_pad = max(0, floor_len - 16)
        pad_len = min(self.pos_x, max_pad)
        pad = " " * pad_len
        
        rendered_sprite_lines = [f"{pad}{r}" for r in sprite_rows]
        
        lines = [speech_line] + rendered_sprite_lines + [f"[dim cyan]{floor_str}[/dim cyan]"]
        return "\n".join(lines)

    def render(self, width: int = None) -> str:
        """Render giao diện Stage 9 dòng có khung hộp Unicode cho CLI standalone."""
        w = max(36, (width or self.stage_width) - 2)
        inner = self.render_tui(w - 2).split("\n")
        
        style_titles = {
            "cat": "🐾 KUBI THE PIXEL CYBER CAT",
            "robo": "🤖 KUBI THE PIXEL CYBER BOT",
            "slime": "👾 KUBI THE PIXEL CYBER SLIME",
            "dino": "🦖 KUBI THE PIXEL CYBER DINO",
            "kaomoji": "🐾 KUBI THE KAOMOJI COMPANION"
        }
        title = f" {style_titles.get(self.style, '🐾 KUBI THE PIXEL COMPANION')} "
        top_dash = max(2, w - len(title) - 4)
        top_line = f"[dim]╭──{title}{'─' * top_dash}╮[/dim]"
        bot_line = f"[dim]╰{'─' * (w - 2)}╯[/dim]"
        
        box_lines = [top_line]
        for line in inner:
            box_lines.append(f"[dim]│[/dim] {line}")
        box_lines.append(bot_line)
        return "\n".join(box_lines)

# ------------------------------------------------------------------------------
# Helper Functions & Global Habitat Instance
# ------------------------------------------------------------------------------
_habitat = None

def get_habitat(width: int = 56) -> MascotHabitat:
    global _habitat
    if _habitat is None:
        _habitat = MascotHabitat(width)
    return _habitat

def get_random_face(mood: str = "idle") -> str:
    """Hàm phụ trợ lấy Kaomoji ngẫu nhiên theo mood."""
    mood_map = {
        "idle": IDLE_SPRITES,
        "walk_right": WALK_RIGHT_SPRITES,
        "walk_left": WALK_LEFT_SPRITES,
        "blink": BLINK_SPRITES,
        "focus": FOCUS_SPRITES,
        "celebrate": CELEBRATE_SPRITES,
        "happy": CELEBRATE_SPRITES,
        "proud": CELEBRATE_SPRITES,
        "cve": CVE_ALERT_SPRITES,
        "thinking": THINKING_SPRITES,
        "sleepy": SLEEPY_SPRITES,
        "web": WEB_BYE_SPRITES
    }
    sprites = mood_map.get(mood, IDLE_SPRITES)
    return random.choice(sprites)

def get_dialogue(event_key: str, **kwargs) -> str:
    """Hàm phụ trợ lấy câu thoại theo sự kiện."""
    dialogues = EVENT_DIALOGUES.get(event_key, EVENT_DIALOGUES.get("idle_pacing", ["Kubi chào bạn!"]))
    msg = random.choice(dialogues)
    for k, v in kwargs.items():
        msg = msg.replace(f"{{{k}}}", str(v))
    return msg

def get_time_greeting():
    """Hàm phụ trợ lấy lời chào theo thời gian trong ngày."""
    hour = datetime.now().hour
    if hour >= 22 or hour < 5:
        return "sleepy", "night"
    elif 5 <= hour < 12:
        return "idle", "idle_pacing"
    elif 12 <= hour < 18:
        return "idle", "idle_pacing"
    else:
        return "idle", "idle_pacing"

if __name__ == "__main__":
    import time
    print("=== LIVE TEST MASCOT STAGE WALK ===")
    h = MascotHabitat(50)
    for _ in range(6):
        os.system("clear" if os.name == "posix" else "cls")
        h.tick(50)
        print(h.render(50))
        time.sleep(0.4)
    
    print("\n--- TEST EVENT: CVE FOUND ---")
    h.react_to_event("cve_found", {"cve": "CVE-2024-38077"})
    print(h.render(50))
