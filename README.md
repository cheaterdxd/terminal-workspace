# Kubuntu Post-Install & Development Environment Setup

Hệ thống đã được thiết lập giao diện sáng mềm mại và cài đặt đầy đủ tất cả các ứng dụng phục vụ công việc của bạn.

## ⚡ Cài Đặt Nhanh 1-Chạm (Quick Install)

Chỉ cần clone repository và chạy lệnh cài đặt:
```bash
git clone https://github.com/<username>/make_Kubuntu_better.git
cd make_Kubuntu_better
./install.sh
```
Script sẽ tự động cấu hình môi trường Python UV, Textual UI, profile Konsole chia đôi tab, đăng ký ứng dụng vào KDE Menu và kích hoạt tự bung Workspace khi mở máy!

*(Để gỡ bỏ sạch sẽ mọi tích hợp, chỉ cần chạy: `./uninstall.sh`)*

---

## 🎨 1. Giao diện & Trải nghiệm người dùng (Light Aesthetic)

* **Phong cách tổng thể:** Nền sáng (**Breeze Light**), đồng bộ cả cửa sổ, thanh công cụ, menu và thanh taskbar.
* **Bộ Icon mềm mại:** Đã cài đặt **Colloid-Light** (dáng squircle bo góc tròn thanh thoát) và **Tela-circle-light** (icon tròn đều).
* **Font chữ:** Bộ font **Inter** hiển thị sắc nét, bo mềm cho toàn bộ giao diện và ứng dụng GTK.
* **Bố cục macOS Style:** 
  * **Top Bar (Thanh trên cùng):** Tinh gọn 32px gồm Menu Kubuntu, Global Menu (`File`, `Edit`...), khay hệ thống và đồng hồ 1 dòng.
  * **Bottom Dock (Thanh dock ở dưới):** Căn giữa, nổi bo tròn (floating), tự co giãn ôm khít các icon ứng dụng (Dolphin, Chrome, VS Code, Konsole, Settings, Trash).
* **Không Gian Làm Việc Tích Hợp (Cyber Workspace - Split Terminal):** Gõ `workspace` ở bất kỳ terminal nào:
  * **Bên trái (55%):** Cửa sổ dòng lệnh Bash thật 100% để bạn thoải mái gõ lệnh (`ls`, `git`, `code`, script...).
  * **Bên phải (45%):** Bảng điều khiển tinh gọn, chạy song song:
    * **Tiến trình công việc cá nhân:** Quản lý to-do với thanh % tiến độ trực quan. Bấm `a` để thêm task nhanh, `Space` để đổi trạng thái, `d` để xóa. Bấm `t` để chuyển focus nhanh về danh sách việc.
    * **Phiên Phá Băng Tâm Lý (Kickstart 5p) & Tập Trung (Focus 25p):** Bấm `k` để kích hoạt chế độ "Phá Băng 5 Phút" (Micro-Pomodoro không áp lực để vượt qua sức ì ban đầu). Chọn task và bấm `p` để bắt đầu Pomodoro 25 phút. Đếm lùi trực quan trên tiến độ, phát chuông terminal `\a` và tự động đổi task sang `done` khi hoàn tất. Bấm `P` để dừng sớm.
    * **Bản tin Threat Intelligence đa nguồn & Khử trùng lặp (Cross-feed Clustering):** Tự động gom cụm các bài viết cùng chung sự kiện/mã CVE giữa The Hacker News, Unit 42, CISA, Krebs, HN thành một thẻ đại diện có huy hiệu đa nguồn (ví dụ `[THN + CISA]`), liệt kê đầy đủ nguồn liên quan trong khung chi tiết.
    * **Tích hợp AI Agent CLI (agy / codex):**
      * Bấm `v`: AI CLI tự động tóm tắt bài viết bằng tiếng Việt chuẩn kỹ thuật (sự cố, đối tượng ảnh hưởng, khuyến nghị phòng thủ).
      * Bấm `x`: AI CLI phân tích chuyên sâu (vector tấn công, IoC, biện pháp remediation) qua pop-up Markdown cuộn được.
      * Bấm `c` trong pop-up AI để chuyển bài phân tích thành task hành động ngay lập tức.
    * **Omnibar Vạn Năng (Trung tâm điều khiển tất cả trong một):** Bấm phím `/` ở bất kỳ đâu để kích hoạt Omnibar:
      * **Trợ lý AI Đa Năng:** Gõ `ai: <câu hỏi>`, `hỏi: <câu hỏi>` hoặc hỏi tự nhiên (`tại sao...`, `là gì...`) để AI giải đáp mọi lĩnh vực; nhắc đến `bài này`, `lỗ hổng này` để AI phân tích theo bài báo.
      * **Phá Băng Chống Trì Hoãn (Anti-Inertia):** Gõ `kick: <tên việc>` để AI tự động phân rã việc bạn đang ngại làm thành 3 bước siêu nhỏ (Bước 1 < 2 phút), nạp thẳng vào danh sách việc và kích hoạt đồng hồ 5 phút làm ngay.
      * **Thực thi lệnh Shell:** `! <lệnh>` hoặc `sh: <lệnh>` (ví dụ: `! df -h`, `! uptime`, `! ping -c 3 8.8.8.8`) để chạy nhanh lệnh bash và xem kết quả trực tiếp.
      * **Mở ứng dụng hệ thống:** `open code`, `open chrome`, `open dolphin`, `open settings`...
      * **Điều khiển hệ thống & giao diện:** `wall: <tên>` đổi hình nền 4K, `icon: <tên>` đổi icon, `autostart: on/off` bật/tắt tự khởi động.
      * **Máy tính nhanh:** Nhập biểu thức toán học (`125 * 8`, `sqrt(144) + 2^10`) để nhận kết quả tức thì.
      * **Lọc tin tức tại chỗ:** `filter: <từ khóa>` để lọc danh sách bản tin trên màn hình, `clear` để xem lại toàn bộ.
      * **Quản lý Task linh hoạt:** `task: [TAG] việc`, `done: <id>` (xong task), `del: <id>` (xóa task).
      * **Tra cứu chuyên sâu:** `cve: <mã>`, `gh: <repo>`, `so: <query>`, `shodan: <query>`.
      * **Bảng tra cứu nhanh:** Gõ `help` hoặc `?` trong Omnibar để mở cheatsheet toàn bộ lệnh.
    * **Bản tin tóm lược đầu ngày (Morning Briefing):** Bấm `b` (hoặc gõ `brief` trong Omnibar) để xem 3–5 tin khẩn cấp/trọng điểm nhất được chấm điểm tự động theo bộ quy tắc (0-day, CVE, CISA Alert, Ransomware).
    * **Báo cáo tổng kết ngày & Xuất Markdown (Daily Wrap-up):** Bấm `w` (hoặc gõ `wrapup`/`eod`) để xem tỷ lệ hoàn thành công việc, danh sách việc dở dang, và bấm `s` để tự động xuất file nhật ký `~/work_logs/daily_YYYY-MM-DD.md`.
    * **Trích dẫn định hướng tư duy theo ngữ cảnh (Contextual Quotes):** Tích hợp danh mục trích dẫn chọn lọc (Unix philosophy, Zero Trust, kỷ luật thực thi) xuất hiện đúng lúc khi bắt đầu/kết thúc phiên Focus hoặc khi xuất báo cáo cuối ngày.
    * **Phím tắt điều hướng nhanh:**
      * `n`: Focus vào Bản tin │ `t`: Focus vào Công việc │ `/`: Focus Omnibar.
      * `b`: Điểm tin đầu ngày │ `k`: Phá băng 5p │ `p` / `P`: Bật / Tắt Focus │ `w`: Tổng kết ngày.
      * `v`: AI Tóm tắt tiếng Việt │ `x`: AI Phân tích chuyên sâu │ `Enter` / `o`: Mở web.
      * `q`: Thoát dashboard.
  * **Phím tắt chuyển qua lại giữa 2 bên:** `Alt + Mũi tên trái/phải` hoặc bấm chuột trực tiếp vào pane muốn làm việc. Thoát bằng `Ctrl + q`.
* **Mở riêng Dashboard độc lập (toàn màn hình):** Gõ lệnh `dashboard`.
* **Công cụ đổi bố cục thanh bar:**
  * `./setup_macos_layout.sh` : Kích hoạt bố cục macOS (Top Bar + Centered Dock).
  * `./restore_default_layout.sh` : Khôi phục lại thanh Taskbar mặc định của Kubuntu.
* **Công cụ tối ưu hiệu năng toàn diện:** `sudo ./optimize_performance.sh` (Swappiness 10, Google BBR, ZRAM nén zstd, Inotify 524K, NVMe Trim).
* **Công cụ đổi hình nền 4K nhanh:** Chạy `./set_wallpaper.sh [whitesur|sonoma|ventura|monterey|altai|cascade|pastel]` trong thư mục này.
* **Công cụ đổi icon nhanh:** Chạy `./toggle_icon_style.sh [colloid|tela|breeze]` trong thư mục này.
* **Linh vật Kaomoji Terminal (Kubi Buddy):** Gõ `buddy` ở bất kỳ terminal nào để chào hỏi, xem tiến độ task và nhận lời động viên; `buddy cheer` để giải tỏa căng thẳng khi fix bug; `buddy focus [phút]` để đếm giờ tập trung cùng linh vật; hoặc `buddy watch` để linh vật ngồi bàn làm việc cùng bạn.
* **Tự khởi động Workspace khi mở máy (Autostart):** Chạy `./toggle_autostart.sh [workspace|dashboard|disable|status]` (hoặc gõ `toggle_autostart` ở bất kỳ đâu) để quản lý cấu hình tự động bung ra mỗi khi đăng nhập Kubuntu (mặc định đã BẬT chế độ Cyber Workspace).

---

## 🛠️ 2. Các ứng dụng & Công cụ phát triển đã cài đặt

| Ứng dụng / Công cụ | Phiên bản | Lệnh Terminal | Vị trí / Menu ứng dụng |
| :--- | :--- | :--- | :--- |
| **Google Chrome** | 156.0.8078.47 | `google-chrome-stable` | Có trong Menu ứng dụng & Desktop |
| **Visual Studio Code** | 1.143.1 | `code` | Có trong Menu ứng dụng & Desktop |
| **Tailscale** | 1.104.2 | `tailscale` / `tailscaled` | `~/.local/bin/tailscale` |
| **Codex CLI** | 0.164.0 | `codex` | `~/.local/bin/codex` |
| **Pi (Coding Agent)** | 1.4.0 | `pi` | `~/.local/bin/pi` |
| **Oh My Pi (OMP)** | 18.12.6 | `omp` | `~/.local/bin/omp` |
| **Python UV** | 0.13.5 | `uv` / `uvx` | `~/.local/bin/uv` |
| **Node.js LTS** | v24.22.1 | `node` / `npm` / `npx` | `~/.local/bin/node` |
| **Bun** | 1.4.4 | `bun` / `bunx` | `~/.local/bin/bun` |

---

## 🚀 3. Hướng dẫn sử dụng nhanh

### Quản lý Python với UV:
```bash
uv venv                       # Tạo môi trường ảo siêu tốc
uv pip install <package>      # Cài đặt package với tốc độ tối đa
uv run script.py              # Chạy script trực tiếp không cần kích hoạt venv
```

### Sử dụng AI Coding Agents:
* **Pi**: Gõ `pi` trong thư mục dự án để bắt đầu phiên tương tác.
* **Oh My Pi**: Gõ `omp` để sử dụng terminal agent với tích hợp LSP và sửa code thông minh.
* **Codex CLI**: Gõ `codex` để dịch prompt hoặc tương tác với OpenAI Codex.

### Sử dụng Tailscale:
* **Chế độ mạng người dùng (Userspace, không cần root):**
  ```bash
  tailscaled --tun=userspace-networking --socks5-server=localhost:1055 &
  tailscale up
  ```
* **Chế độ VPN toàn hệ thống (Cần sudo 1 lần để tạo card mạng ảo):**
  ```bash
  sudo tailscaled &
  sudo tailscale up
  ```
