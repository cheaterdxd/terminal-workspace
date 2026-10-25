#!/usr/bin/env python3
"""
Kubuntu Cyber Threat Intel & Personal Workspace Dashboard
Phiên bản Tinh gọn & Năng suất cao cho Pane Workspace:
- Tối ưu bố cục dọc 45% cho Split Terminal Zellij.
- Quản lý công việc (To-do, Tiến độ, Phím tắt).
- Bản tin Threat Intel đa nguồn (The Hacker News, Unit 42, CISA, Krebs, HN).
- Gom cụm và khử trùng lặp tin đa nguồn (Cross-feed Deduplication & Clustering).
- Bản tin tóm lược đầu ngày theo quy tắc (Morning Technical Briefing).
- Phiên tập trung có hẹn giờ gắn với Task (Task-bound Focus / Pomodoro 25p).
- Báo cáo tổng kết cuối ngày & xuất file Markdown (Daily Wrap-up / Work Log).
- Trích dẫn định hướng tư duy theo ngữ cảnh kỹ thuật (Contextual Quotes).
- Tích hợp AI Agent CLI (agy, codex) phân tích & tóm tắt kỹ thuật tiếng Việt.
"""

import os
import sys
import json
import re
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import subprocess
import threading
import concurrent.futures
import shutil
import random
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

from textual.app import App, ComposeResult
from textual.screen import ModalScreen
from textual.containers import Vertical, Container, Horizontal, VerticalScroll
from textual.widgets import Static, Input, ListView, ListItem, Label, ProgressBar, Markdown
from textual.binding import Binding
from textual.reactive import reactive

try:
    import mascot_engine
except ImportError:
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import mascot_engine

TASKS_FILE = os.path.expanduser("~/.workspace_tasks.json")
QUOTES_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "quotes.json")

FEEDS = [
    {
        "id": "thn",
        "name": "The Hacker News",
        "badge": "THN",
        "color": "cyan",
        "url": "https://feeds.feedburner.com/TheHackersNews"
    },
    {
        "id": "unit42",
        "name": "Unit 42 (Palo Alto)",
        "badge": "Unit42",
        "color": "magenta",
        "url": "https://unit42.paloaltonetworks.com/feed/"
    },
    {
        "id": "cisa",
        "name": "CISA Advisories",
        "badge": "CISA",
        "color": "red",
        "url": "https://www.cisa.gov/cybersecurity-advisories/all.xml"
    },
    {
        "id": "krebs",
        "name": "Krebs on Security",
        "badge": "Krebs",
        "color": "yellow",
        "url": "https://krebsonsecurity.com/feed/"
    },
    {
        "id": "hn",
        "name": "Hacker News (YC)",
        "badge": "HN",
        "color": "orange",
        "url": "https://news.ycombinator.com/rss"
    }
]

# ------------------------------------------------------------------------------
# Contextual Reflection Quotes
# ------------------------------------------------------------------------------
DEFAULT_QUOTES = [
    {
        "quote": "Make each program do one thing well.",
        "author": "Doug McIlroy",
        "context": "focus_start",
        "note": "Triết lý Unix: Tập trung làm tốt một việc duy nhất."
    },
    {
        "quote": "Simplicity is prerequisite for reliability.",
        "author": "Rob Pike",
        "context": "focus_start",
        "note": "Nguyên lý thiết kế: Đơn giản là điều kiện tiên quyết cho độ tin cậy."
    },
    {
        "quote": "Controlling complexity is the essence of computer programming.",
        "author": "Brian Kernighan",
        "context": "focus_start",
        "note": "Tập trung tinh giản và làm chủ độ phức tạp của bài toán."
    },
    {
        "quote": "Talk is cheap. Show me the code.",
        "author": "Linus Torvalds",
        "context": "focus_done",
        "note": "Kỷ luật thực thi: Giá trị nằm ở kết quả cụ thể đã hoàn thành."
    },
    {
        "quote": "Security is a process, not a product.",
        "author": "Bruce Schneier",
        "context": "wrapup",
        "note": "Bảo mật và chất lượng công việc là một quy trình cải tiến liên tục."
    },
    {
        "quote": "Given enough eyeballs, all bugs are shallow.",
        "author": "Eric S. Raymond",
        "context": "wrapup",
        "note": "Rà soát cẩn thận cuối ngày để nhận diện sớm các thiếu sót."
    },
    {
        "quote": "If you can't measure it, you can't manage it.",
        "author": "Dan Geer",
        "context": "wrapup",
        "note": "Đo lường và ghi nhận tiến độ là chìa khóa để duy trì hiệu suất."
    }
]

def load_quotes() -> list[dict]:
    if os.path.exists(QUOTES_FILE):
        try:
            with open(QUOTES_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list) and data:
                    return data
        except Exception:
            pass
    return DEFAULT_QUOTES

def get_random_quote(context: str = None) -> dict:
    quotes = load_quotes()
    if context:
        filtered = [q for q in quotes if q.get("context") == context]
        if filtered:
            return random.choice(filtered)
    return random.choice(quotes) if quotes else DEFAULT_QUOTES[0]

# ------------------------------------------------------------------------------
# AI CLI Agent Helpers (agy, omp, pi, codex)
# ------------------------------------------------------------------------------
def get_ai_clis() -> list[tuple[str, list[str]]]:
    """Danh sách các công cụ AI CLI khả dụng trên máy theo thứ tự ưu tiên."""
    tools = []
    if shutil.which("agy"):
        tools.append(("agy", ["agy", "--effort", "low", "-p"]))
    if shutil.which("omp"):
        tools.append(("omp", ["omp", "--no-session", "--no-tools", "-p"]))
    if shutil.which("pi"):
        tools.append(("pi", ["pi", "-p", "--no-session", "--no-tools"]))
    if shutil.which("codex"):
        tools.append(("codex", ["codex", "exec", "--skip-git-repo-check"]))
    return tools

def get_ai_cli() -> tuple[str, list[str]]:
    """Dò tìm công cụ AI CLI khả dụng hàng đầu trên máy."""
    clis = get_ai_clis()
    return clis[0] if clis else ("", [])

def call_ai_cli(prompt: str, timeout: float = 90.0) -> tuple[bool, str, str]:
    """Thực thi câu lệnh AI CLI bất đồng bộ trong background thread với cơ chế tự động fallback."""
    clis = get_ai_clis()
    if not clis:
        return False, "Không tìm thấy công cụ AI CLI (agy, omp, pi hoặc codex) trong hệ thống PATH.", ""
    last_err = ""
    for cli_name, base_cmd in clis:
        try:
            cmd = base_cmd + [prompt]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, cwd="/tmp")
            if res.returncode == 0 and res.stdout.strip():
                out = res.stdout.strip()
                if cli_name == "omp" and out.startswith("Working...\n"):
                    out = out[len("Working...\n"):].strip()
                return True, out, cli_name
            err = res.stderr.strip() or res.stdout.strip() or f"Mã thoát {res.returncode}"
            last_err = f"Lỗi từ {cli_name}: {err}"
        except subprocess.TimeoutExpired:
            last_err = f"Quá thời gian phản hồi ({timeout}s) từ công cụ {cli_name}."
        except Exception as e:
            last_err = f"Lỗi thực thi {cli_name}: {e}"
    return False, last_err, clis[0][0]

# ------------------------------------------------------------------------------
# Quick Math Calculator Helper
# ------------------------------------------------------------------------------
import math

def safe_calc(expr: str):
    """Tính toán biểu thức toán học an toàn, không thực thi mã độc."""
    expr = expr.strip()
    if not expr or len(expr) > 80:
        return None
    has_operator = any(op in expr for op in ["+", "-", "*", "/", "%", "^", "×", "÷"])
    has_math_word = any(fn in expr.lower() for fn in ["sqrt", "sin", "cos", "tan", "log", "pow", "abs", "round"])
    if not (has_operator or has_math_word):
        return None
    allowed_names = {k: v for k, v in math.__dict__.items() if not k.startswith("_")}
    allowed_names.update({"abs": abs, "round": round, "min": min, "max": max})
    cleaned = expr.replace("^", "**").replace("x", "*").replace("×", "*").replace("÷", "/")
    try:
        code = compile(cleaned, "<calc>", "eval")
        for name in code.co_names:
            if name not in allowed_names:
                return None
        res = eval(code, {"__builtins__": {}}, allowed_names)
        if isinstance(res, (int, float)):
            if isinstance(res, float) and res.is_integer():
                return int(res)
            return round(res, 4) if isinstance(res, float) else res
        return None
    except Exception:
        return None
# ------------------------------------------------------------------------------
# RSS Date & Text Clustering Helpers
# ------------------------------------------------------------------------------
STOP_WORDS = {
    "the", "a", "an", "in", "on", "at", "to", "for", "of", "and", "is",
    "with", "by", "from", "as", "new", "how", "why", "after", "over",
    "about", "into", "it", "that", "this", "are", "was", "were", "be"
}

def parse_pubdate(date_str: str) -> tuple[float, str]:
    if not date_str:
        return 0.0, "Mới"
    try:
        dt = parsedate_to_datetime(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        diff = max(0.0, (now - dt).total_seconds())

        if diff < 3600:
            rel = f"{max(1, int(diff // 60))}p trước"
        elif diff < 86400:
            rel = f"{int(diff // 3600)}h trước"
        elif diff < 172800:
            rel = "Hôm qua"
        else:
            rel = dt.strftime("%d/%m")
        return dt.timestamp(), rel
    except Exception:
        return 0.0, date_str[:10]

def extract_cves(text: str) -> set[str]:
    return set(re.findall(r"CVE-\d{4}-\d{4,7}", text, re.IGNORECASE))

def get_tokens(text: str) -> set[str]:
    clean = re.sub(r"[^\w\s-]", " ", text.lower())
    return {w for w in clean.split() if len(w) >= 3 and w not in STOP_WORDS}

def cluster_and_deduplicate(items: list[dict]) -> list[dict]:
    """Gom cụm và khử trùng lặp tin tức giữa các nguồn RSS (STT 02)."""
    clusters = []
    for item in items:
        cves = extract_cves(item["title"] + " " + item.get("desc", ""))
        tokens = get_tokens(item["title"])
        matched_cluster = None

        for cl in clusters:
            # 1. Trùng mã CVE
            cl_cves = extract_cves(cl["title"] + " " + cl.get("desc", ""))
            if cves and cl_cves and (cves & cl_cves):
                matched_cluster = cl
                break

            # 2. Trùng độ tương đồng tiêu đề (Jaccard >= 0.40) trong vòng 72 giờ
            cl_tokens = get_tokens(cl["title"])
            if tokens and cl_tokens:
                inter = len(tokens & cl_tokens)
                union = len(tokens | cl_tokens)
                if union > 0 and (inter / union) >= 0.40 and abs(item["timestamp"] - cl["timestamp"]) <= 72 * 3600:
                    matched_cluster = cl
                    break

        if matched_cluster:
            matched_cluster["related_sources"].append({
                "source": item["source"],
                "vendor": item["vendor"],
                "color": item["color"],
                "title": item["title"],
                "link": item["link"],
                "desc": item["desc"]
            })
            if item["source"] not in matched_cluster["combined_sources"]:
                matched_cluster["combined_sources"].append(item["source"])
                matched_cluster["combined_badge"] = " + ".join(matched_cluster["combined_sources"])
        else:
            item["related_sources"] = []
            item["combined_sources"] = [item["source"]]
            item["combined_badge"] = item["source"]
            clusters.append(item)

    return clusters

def get_morning_briefing(articles: list[dict], max_items: int = 5) -> list[dict]:
    """Lọc danh sách bài viết nổi bật đầu ngày theo bộ quy tắc rõ ràng (STT 01)."""
    scored = []
    now_ts = datetime.now(timezone.utc).timestamp()
    for art in articles:
        score = 0
        reasons = []
        text_lower = (art["title"] + " " + art.get("desc", "")).lower()

        # Rule 1: 0-day, Actively Exploited, RCE
        if any(k in text_lower for k in ["0-day", "zero-day", "actively exploited", "rce", "remote code execution"]):
            score += 40
            reasons.append("0-Day / RCE Khẩn cấp")

        # Rule 2: CVE xác định
        cves = extract_cves(art["title"] + " " + art.get("desc", ""))
        if cves:
            score += 30
            reasons.append(f"Mã {list(cves)[0]}")

        # Rule 3: Cảnh báo chính phủ CISA
        if art.get("source") == "CISA" or "cisa" in art.get("vendor", "").lower():
            score += 25
            reasons.append("Cảnh báo CISA")

        # Rule 4: Ransomware, Supply Chain, Backdoor
        if any(k in text_lower for k in ["ransomware", "supply chain", "backdoor", "breach", "leak"]):
            score += 20
            reasons.append("Mã độc / Supply Chain")

        # Rule 5: Critical / High Severity
        if any(k in text_lower for k in ["critical", "high severity", "urgent", "advisory"]):
            score += 20
            reasons.append("Lỗ hổng nghiêm trọng")

        # Rule 6: Độ mới trong 24h
        if art.get("timestamp") and (now_ts - art["timestamp"] <= 86400):
            score += 15

        if score > 0:
            art_copy = dict(art)
            art_copy["briefing_score"] = score
            art_copy["briefing_reason"] = " │ ".join(reasons) if reasons else "Tin quan trọng"
            scored.append(art_copy)

    scored.sort(key=lambda x: x["briefing_score"], reverse=True)
    return scored[:max_items]

# ------------------------------------------------------------------------------
# Task Storage Helpers
# ------------------------------------------------------------------------------
def load_tasks():
    if not os.path.exists(TASKS_FILE):
        default_tasks = [
            {"id": 1, "tag": "SYSTEM", "title": "Tối ưu hóa nhân Linux & bộ nhớ ZRAM", "status": "done"},
            {"id": 2, "tag": "DESKTOP", "title": "Cấu hình Floating Dock macOS & icon Colloid", "status": "done"},
            {"id": 3, "tag": "SEC-INTEL", "title": "Phân tích báo cáo CVE & APT Threat Brief mới", "status": "in_progress"},
            {"id": 4, "tag": "DEV", "title": "Kiểm tra VPN Tailscale và môi trường coding AI", "status": "todo"}
        ]
        save_tasks(default_tasks)
        return default_tasks
    try:
        with open(TASKS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_tasks(tasks):
    try:
        with open(TASKS_FILE, "w", encoding="utf-8") as f:
            json.dump(tasks, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

# ------------------------------------------------------------------------------
# Custom ListItems (Avoid Textual ID collisions)
# ------------------------------------------------------------------------------
class TaskItem(ListItem):
    def __init__(self, task_data: dict, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.task_data = task_data

class NewsItem(ListItem):
    def __init__(self, article_data: dict, *children, **kwargs):
        super().__init__(*children, **kwargs)
        self.article_data = article_data

class NewsListView(ListView):
    """ListView tùy chỉnh cho Bản tin: click chuột chỉ để chọn/xem tóm tắt, không mở browser."""
    def _on_list_item__child_clicked(self, event: ListItem._ChildClicked) -> None:
        event.stop()
        event.prevent_default()
        self.focus()
        self.index = self._nodes.index(event.item)

# ------------------------------------------------------------------------------
# Modals (Briefing, Wrap-Up, AI Result)
# ------------------------------------------------------------------------------
class BriefingModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss", "Đóng"),
        Binding("o", "open_first", "Mở bài đầu"),
        Binding("enter", "open_first", "Mở bài đầu"),
        Binding("v", "ai_first", "AI Tóm tắt"),
    ]

    def __init__(self, briefing_items: list[dict], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.briefing_items = briefing_items

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-box"):
            yield Label("🛡️ BẢN TIN TÓM LƯỢC ĐẦU NGÀY (MORNING TECHNICAL BRIEFING)", classes="modal-title")
            with VerticalScroll(classes="modal-content"):
                if not self.briefing_items:
                    yield Static("[dim]Chưa có bài viết nào khớp với tiêu chuẩn cảnh báo khẩn cấp hôm nay.[/dim]")
                else:
                    for i, art in enumerate(self.briefing_items, 1):
                        rule = art.get("briefing_reason", "Quy tắc an ninh")
                        vendor = art.get("vendor", "")
                        color = art.get("color", "cyan")
                        title = art.get("title", "")
                        desc = art.get("desc", "")
                        link = art.get("link", "")
                        rel_time = art.get("rel_time", "")

                        card_text = (
                            f"[bold yellow]#{i:02d}[/bold yellow] [{color} bold]\\[{vendor}][/{color} bold] "
                            f"[bold red]\\[{rule}][/bold red] [dim]({rel_time})[/dim]\n"
                            f"[bold white]{title}[/bold white]\n"
                            f"[yellow]{desc[:240]}...[/yellow]\n"
                            f"[blue underline]{link}[/blue underline]\n"
                        )
                        yield Static(card_text, classes="briefing-card")

            yield Static(
                "[bold cyan][Enter/o][/bold cyan] Mở bài viết đầu tiên │ "
                "[bold cyan][v][/bold cyan] AI Tóm tắt bài đầu │ "
                "[bold cyan][Esc][/bold cyan] Đóng",
                classes="modal-footer"
            )

    def action_open_first(self):
        if self.briefing_items:
            link = self.briefing_items[0].get("link", "")
            if link:
                subprocess.Popen(["xdg-open", link], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.dismiss()

    def action_ai_first(self):
        if self.briefing_items:
            art = self.briefing_items[0]
            self.dismiss()
            self.app._trigger_ai_analysis(art, mode="summary")

class WrapUpModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss", "Đóng"),
        Binding("s", "export_log", "Xuất file"),
        Binding("enter", "export_log", "Xuất file"),
    ]

    def __init__(self, tasks: list[dict], quote: dict, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tasks = tasks
        self.quote = quote

    def compose(self) -> ComposeResult:
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.get("status") == "done")
        in_progress = sum(1 for t in self.tasks if t.get("status") == "in_progress")
        todo = total - done - in_progress
        pct = int(done / total * 100) if total > 0 else 0

        with Vertical(classes="modal-box"):
            yield Label("📊 BÁO CÁO TỔNG KẾT NGÀY LÀM VIỆC (DAILY WORK LOG)", classes="modal-title")
            with VerticalScroll(classes="modal-content"):
                yield Static(
                    f"[bold white]Tiến độ tổng thể:[/bold white] [bold green]{pct}%[/bold green] "
                    f"[dim]({done} đã xong, {in_progress} đang làm, {todo} chờ xử lý)[/dim]\n"
                )

                yield Label("[bold green]✓ CÔNG VIỆC ĐÃ HOÀN TẤT:[/bold green]")
                done_tasks = [t for t in self.tasks if t.get("status") == "done"]
                if done_tasks:
                    for t in done_tasks:
                        yield Static(f"  [green]✓[/green] [blue]\\[{t.get('tag','TASK')}][/blue] {t.get('title','')}")
                else:
                    yield Static("  [dim]Chưa có task nào hoàn tất hôm nay.[/dim]")

                yield Label("\n[bold yellow]⏳ CÔNG VIỆC DỞ DANG CẦN THEO DÕI:[/bold yellow]")
                active_tasks = [t for t in self.tasks if t.get("status") != "done"]
                if active_tasks:
                    for t in active_tasks:
                        st_icon = "[yellow]⏳[/yellow]" if t.get("status") == "in_progress" else "[dim]•[/dim]"
                        yield Static(f"  {st_icon} [blue]\\[{t.get('tag','TASK')}][/blue] {t.get('title','')}")
                else:
                    yield Static("  [dim]Không có việc tồn đọng. Ngày làm việc hoàn hảo![/dim]")

                if self.quote:
                    yield Static(
                        f"\n[italic cyan]\"{self.quote.get('quote','')}\"[/italic cyan]\n"
                        f"[bold dim]— {self.quote.get('author','')} ({self.quote.get('note','')})[/bold dim]"
                    )

            yield Static(
                "[bold cyan][s / Enter][/bold cyan] Xuất Markdown (~/work_logs/) │ "
                "[bold cyan][Esc][/bold cyan] Đóng",
                classes="modal-footer"
            )

    def action_export_log(self):
        log_dir = os.path.expanduser("~/work_logs")
        os.makedirs(log_dir, exist_ok=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        filepath = os.path.join(log_dir, f"daily_{today_str}.md")

        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.get("status") == "done")
        in_progress = sum(1 for t in self.tasks if t.get("status") == "in_progress")
        todo = total - done - in_progress
        pct = int(done / total * 100) if total > 0 else 0

        lines = [
            f"# Báo Cáo Công Việc Cyber Workspace - {today_str}",
            f"*Thời gian xuất:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "## 1. Tổng quan tiến độ",
            f"- **Tỷ lệ hoàn thành:** {pct}%",
            f"- **Đã hoàn thành:** {done}",
            f"- **Đang thực hiện:** {in_progress}",
            f"- **Chờ xử lý:** {todo}\n",
            "## 2. Chi tiết công việc",
            "### Đã hoàn thành:",
        ]
        for t in self.tasks:
            if t.get("status") == "done":
                lines.append(f"- [x] [{t.get('tag', 'TASK')}] {t.get('title', '')}")
        lines.append("\n### Tồn đọng & Đang xử lý:")
        for t in self.tasks:
            if t.get("status") != "done":
                lines.append(f"- [ ] [{t.get('tag', 'TASK')}] ({t.get('status')}) {t.get('title', '')}")

        if self.quote:
            lines.append("\n## 3. Trích dẫn định hướng")
            lines.append(f"> \"{self.quote.get('quote', '')}\"\n>\n> — **{self.quote.get('author', '')}** *({self.quote.get('note', '')})*")

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write("\n".join(lines) + "\n")
            self.app.notify(f"Đã lưu: ~/work_logs/daily_{today_str}.md", title="Xuất Báo Cáo")
        except Exception as e:
            self.app.notify(f"Lỗi khi ghi tệp: {e}", title="Lỗi", severity="error")
        self.dismiss()

class AIResultModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss", "Đóng"),
        Binding("c", "convert_to_task", "Tạo task"),
        Binding("o", "open_link", "Mở web"),
    ]

    def __init__(self, article: dict, result_text: str, mode_title: str, is_general: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.article = article
        self.result_text = result_text
        self.mode_title = mode_title
        self.is_general = is_general

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-box"):
            if self.is_general:
                header_title = f"🤖 TRỢ LÝ AI ({self.mode_title.upper()})"
                title_line = ""
            else:
                vendor = self.article.get("vendor", "")
                header_title = f"🤖 AI PHÂN TÍCH ({self.mode_title.upper()}) │ {vendor}"
                title_line = f"[bold cyan]{self.article.get('title', '')}[/bold cyan]\n"

            yield Label(header_title, classes="modal-title")
            with VerticalScroll(classes="modal-content"):
                if title_line:
                    yield Static(title_line)
                yield Markdown(self.result_text)
            
            footer_parts = ["[bold cyan][c][/bold cyan] Tạo Task"]
            if self.article.get("link"):
                footer_parts.append("[bold cyan][o][/bold cyan] Mở Web")
            footer_parts.append("[bold cyan][Esc][/bold cyan] Đóng")
            yield Static(" │ ".join(footer_parts), classes="modal-footer")

    def action_convert_to_task(self):
        title = self.article.get("title") or self.mode_title or "Ghi chú từ AI"
        task_title = f"AI Note: {title[:50]}"
        self.app.add_task_from_article(task_title, tag="AI-TASK")
        self.notify(f"Đã tạo task mới: {task_title}", title="Task Added")
        self.dismiss()

    def action_open_link(self):
        link = self.article.get("link", "")
        if link:
            subprocess.Popen(["xdg-open", link], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.dismiss()

class CommandResultModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss", "Đóng"),
    ]

    def __init__(self, cmd: str, output: str, is_error: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.cmd = cmd
        self.output = output
        self.is_error = is_error

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-box"):
            status_tag = "[red]LỖI[/red]" if self.is_error else "[green]THÀNH CÔNG[/green]"
            yield Label(f"💻 KẾT QUẢ SHELL │ {status_tag}", classes="modal-title")
            with VerticalScroll(classes="modal-content"):
                yield Static(f"[bold cyan]$ {self.cmd}[/bold cyan]\n")
                yield Static(f"[white]{self.output}[/white]")
            yield Static("[bold cyan][Esc][/bold cyan] Đóng", classes="modal-footer")

class OmniHelpModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss", "Đóng"),
    ]

    def compose(self) -> ComposeResult:
        help_markdown = """
### ⚡ OMNIBAR VẠN NĂNG - HƯỚNG DẪN ĐIỀU KHIỂN HỆ THỐNG

Bấm `/` bất kỳ lúc nào để mở Omnibar và gõ các lệnh sau:

---

#### 🤖 1. Trợ Lý AI & Tìm Kiếm Tri Thức
* `ai: <câu hỏi>` hoặc `hỏi: <câu hỏi>` : Đặt câu hỏi tự do cho trợ lý AI (hoặc gõ tự nhiên: *là gì*, *tại sao*, *làm sao*...)
* `cve: <mã>` : Tra cứu lỗ hổng bảo mật trực tiếp trên NVD (VD: `cve: CVE-2024-3094`)
* `gh: <repo/query>` : Tra cứu kho mã nguồn GitHub (VD: `gh: textualize/textual`)
* `so: <query>` : Tra cứu giải pháp kỹ thuật trên StackOverflow
* `shodan: <query>` : Tìm kiếm thiết bị và cổng mở trên Shodan

#### 💻 2. Thực Thi Lệnh Shell & Mở Ứng Dụng
* `! <lệnh>` hoặc `sh: <lệnh>` : Chạy lệnh bash tức thì và xem kết quả (VD: `! df -h`, `! uptime`, `! ping -c 3 8.8.8.8`)
* `open <app>` : Mở nhanh ứng dụng hệ thống (VD: `open code`, `open chrome`, `open dolphin`, `open settings`)

#### 🎨 3. Điều Khiển Giao Diện & Hệ Thống Kubuntu
* `wall: <tên>` hoặc `bg: <tên>` : Đổi hình nền 4K (`whitesur`, `sonoma`, `ventura`, `monterey`, `altai`, `cascade`)
* `icon: <tên>` : Đổi bộ icon (`colloid`, `tela`, `breeze`)
* `autostart: <on|off|status>` : Bật/tắt tự bung Workspace khi mở máy

#### 📋 4. Quản Lý Công Việc & Chống Trì Hoãn (Anti-Inertia)
* `kick: <tên việc>` : AI tự động bẻ nhỏ việc thành 3 micro-steps (Bước 1 < 2p) & tự động đếm giờ
* `Phím k` hoặc `kickstart` : Kích hoạt phiên phá băng tâm lý 5 phút (Micro-Pomodoro không áp lực)
* `task: [TAG] nội dung` : Thêm task mới (VD: `task: [DEV] Viết script kiểm thử`)
* `done: <id>` : Đánh dấu hoàn thành task theo ID
* `del: <id>` hoặc `rm: <id>` : Xóa task theo ID
* `focus [phút]` : Bắt đầu phiên làm việc Pomodoro (mặc định 25 phút)
* `focus stop` : Dừng phiên tập trung
* `wrapup` hoặc `log` : Mở báo cáo tổng kết ngày & xuất file Markdown
* `brief` : Xem điểm tin trọng điểm đầu ngày

#### 🔢 5. Máy Tính Nhanh & Linh Vật
* `<biểu thức>` : Tính toán số học tức thì (VD: `125 * 8`, `sqrt(144) + 2^10`, `sin(pi/2)`)
* `filter: <từ khóa>` : Lọc danh sách bài viết trên màn hình
* `reset` hoặc `clear` : Khôi phục toàn bộ danh sách tin tức
* `mascot: <kiểu>` : Đổi phong cách linh vật (`cat`, `robo`, `slime`, `dino`, `kaomoji`)
* `buddy: cheer / watch` : Tương tác cùng linh vật Kubi Buddy
"""
        with Vertical(classes="modal-box"):
            yield Label("⚡ OMNIBAR CHEAT SHEET │ TRUNG TÂM ĐIỀU KHIỂN VẠN NĂNG", classes="modal-title")
            with VerticalScroll(classes="modal-content"):
                yield Markdown(help_markdown)
            yield Static("[bold cyan][Esc][/bold cyan] Đóng", classes="modal-footer")

class KickstartDecomposeModal(ModalScreen):
    BINDINGS = [
        Binding("escape", "dismiss", "Đóng"),
        Binding("enter", "dismiss", "Bắt đầu ngay"),
    ]

    def __init__(self, task_name: str, step1: str, step2: str, step3: str, encouragement: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.task_name = task_name
        self.step1 = step1
        self.step2 = step2
        self.step3 = step3
        self.encouragement = encouragement

    def compose(self) -> ComposeResult:
        with Vertical(classes="modal-box"):
            yield Label("🔥 ANTI-INERTIA KICKSTART │ PHÁ VỠ SỨC LƯỜI TÂM LÝ", classes="modal-title")
            with VerticalScroll(classes="modal-content"):
                yield Static(f"[bold cyan]🎯 MỤC TIÊU LỚN:[/bold cyan] [bold white]{self.task_name}[/bold white]\n")
                yield Static("[dim]Đã phân rã thành 3 bước siêu nhỏ. Bước 1 chỉ tốn dưới 2 phút để khởi động:[/dim]\n")
                
                step1_card = (
                    f"[bold green]▶ BƯỚC 1 (DƯỚI 2 PHÚT - KHỞI ĐỘNG VẬT LÝ):[/bold green]\n"
                    f"[bold bright_white]{self.step1}[/bold bright_white]\n"
                )
                yield Static(step1_card)

                step2_card = (
                    f"[bold yellow]▶ BƯỚC 2 (5 PHÚT TIẾP THEO - TẠO ĐÀ QUÁN TÍNH):[/bold yellow]\n"
                    f"[white]{self.step2}[/white]\n"
                )
                yield Static(step2_card)

                step3_card = (
                    f"[bold cyan]▶ BƯỚC 3 (VÀO GUỒNG FLOW STATE):[/bold cyan]\n"
                    f"[white]{self.step3}[/white]\n"
                )
                yield Static(step3_card)

                if self.encouragement:
                    yield Static(f"[bold magenta]💡 LỜI NHẮC:[/bold magenta] [italic yellow]\"{self.encouragement}\"[/italic yellow]")

            yield Static(
                "[bold green][Enter / Esc][/bold green] Bắt đầu ngay 5 phút phá băng! (Đồng hồ đếm giờ đã bật)",
                classes="modal-footer"
            )
# ------------------------------------------------------------------------------
# Main Application
# ------------------------------------------------------------------------------
class CyberDashboardApp(App):
    CSS = """
    Screen {
        background: #0d1117;
        color: #d1d5db;
        overflow: hidden;
    }

    #top-bar {
        height: 1;
        background: #171a23;
        color: #9ca3af;
        padding: 0 1;
        border-bottom: solid #334155;
    }

    #main-container {
        height: 1fr;
        padding: 0 1;
    }

    #mascot-stage {
        height: 9;
        background: #141721;
        color: #e2e8f0;
        padding: 0 1;
        border: round #38bdf8;
        margin-bottom: 0;
        overflow: hidden hidden;
    }

    #tasks-container {
        height: 35%;
        margin-bottom: 0;
    }

    #news-container {
        height: 1fr;
        margin-bottom: 0;
    }

    .section-title {
        text-style: bold;
        color: #38bdf8;
        padding: 0;
        margin: 0;
    }

    #progress-text {
        height: 1;
    }

    #task-progress {
        height: 1;
        margin-bottom: 0;
    }

    #focus-timer-text {
        height: 1;
        margin-bottom: 0;
    }

    #tasks-list {
        height: 1fr;
        border: round #334155;
        background: #13161f;
    }

    #news-list {
        height: 68%;
        border: round #334155;
        background: #13161f;
        margin-bottom: 0;
    }

    #news-list ListItem {
        padding: 0 1;
        margin-bottom: 1;
        border-bottom: solid #1a1f2c;
        height: auto;
    }

    #news-list ListItem:hover {
        background: #1b202e;
    }

    #news-list ListItem.-selected {
        background: #1e293b;
        border-left: thick #38bdf8;
    }

    #detail-box {
        height: 32%;
        border: round #334155;
        background: #13161f;
        padding: 0 1;
        overflow-y: scroll;
    }

    #omnibox {
        height: 3;
        margin-top: 1;
        border: solid #0284c7;
        background: #161922;
        color: #f3f4f6;
    }

    #omnibox:focus {
        border: solid #22c55e;
    }

    ListItem {
        padding: 0 1;
    }

    ListItem:hover {
        background: #1e2330;
    }

    ListItem.-selected {
        background: #283042;
        color: #ffffff;
    }

    /* Modal Styling */
    ModalScreen {
        align: center middle;
        background: rgba(15, 17, 23, 0.88);
    }

    .modal-box {
        width: 92%;
        max-width: 95;
        height: 86%;
        background: #13161f;
        border: solid #38bdf8;
        padding: 1 2;
    }

    .modal-title {
        text-style: bold;
        color: #38bdf8;
        border-bottom: solid #334155;
        padding-bottom: 1;
        margin-bottom: 1;
    }

    .modal-content {
        height: 1fr;
        overflow-y: scroll;
    }

    .modal-footer {
        height: 1;
        color: #9ca3af;
        border-top: solid #1f2430;
        margin-top: 1;
    }

    .briefing-card {
        padding: 0 0 1 0;
        margin-bottom: 1;
        border-bottom: dashed #1f2430;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Thoát"),
        Binding("r", "refresh_news", "Làm mới"),
        Binding("a", "focus_omnibox_task", "Thêm task"),
        Binding("slash", "focus_omnibox", "Omnibar"),
        Binding("space", "toggle_task", "Đổi trạng thái"),
        Binding("d", "delete_task", "Xóa task"),
        Binding("o", "open_selected_article", "Mở web"),
        Binding("n", "focus_news", "Bản tin"),
        Binding("t", "focus_tasks", "Công việc"),
        Binding("b", "open_briefing", "Điểm tin"),
        Binding("p", "toggle_focus", "Đếm giờ 25p"),
        Binding("P", "stop_focus", "Dừng đếm giờ"),
        Binding("k", "kickstart_focus", "Phá băng 5p"),
        Binding("w", "open_wrapup", "Tổng kết ngày"),
        Binding("v", "ai_summarize_vn", "AI Tóm tắt VN"),
        Binding("x", "ai_deep_analyze", "AI Phân tích"),
        Binding("escape", "unfocus_omnibox", "Quay lại"),
    ]

    tasks = reactive([])
    articles = reactive([])

    # Focus Session State (STT 07)
    focus_active = reactive(False)
    focus_paused = reactive(False)
    focus_task_id = None
    focus_task_title = ""
    focus_remaining_seconds = 25 * 60
    focus_total_seconds = 25 * 60
    focus_is_kickstart = False
    focus_timer = None

    def compose(self) -> ComposeResult:
        yield Static(
            "[bold cyan]🛡️ WORKSPACE[/bold cyan] [dim]│ [k] Phá băng 5p │ [p] Focus 25p │ [b] Điểm tin │ [v] AI Tóm tắt │ [x] AI Phân tích │ [w] Tổng kết │ [/] Omnibar │ [q] Thoát[/dim]",
            id="top-bar"
        )

        with Vertical(id="main-container"):
            # Mascot Stage: Không gian rộng rãi cho linh vật Kaomoji đi lại
            yield Static("", id="mascot-stage")

            # TOP: Personal Tasks
            with Vertical(id="tasks-container"):
                yield Label("📋 TIẾN TRÌNH CÔNG VIỆC", classes="section-title")
                yield Label("Tiến độ: 0%", id="progress-text")
                yield ProgressBar(id="task-progress", show_eta=False)
                yield Label("⏱ Focus: [bold cyan]25:00[/bold cyan] [dim]• Bấm [bold white]p[/bold white] (25p) hoặc [bold white]k[/bold white] (Phá băng 5p)[/dim]", id="focus-timer-text")
                yield ListView(id="tasks-list")

            # MIDDLE: Threat Intel & Details
            with Vertical(id="news-container"):
                yield Label("📡 BẢN TIN THREAT INTEL (Mũi tên: Chọn xem │ Enter/o: Mở web │ v: AI Tóm tắt │ x: AI Phân tích)", classes="section-title")
                yield NewsListView(id="news-list")
                yield Label("🔎 TÓM TẮT BÁO CÁO KỸ THUẬT", classes="section-title")
                yield Static(
                    "[dim]Chọn một bài viết ở danh sách phía trên để xem tóm tắt...[/dim]",
                    id="detail-box"
                )

            # BOTTOM: Omnibar
            yield Input(
                id="omnibox",
                placeholder="⚡ Omnibar vạn năng: Gõ 'help' hoặc '?' để xem tất cả lệnh (AI, Shell, Math, App, Task, News...)"
            )

    def on_mount(self):
        self.tasks = load_tasks()
        self.render_tasks()
        self.fetch_all_news()
        self.query_one("#tasks-list", ListView).focus()
        
        # Khởi tạo linh vật Pixel Habitat
        self.habitat = mascot_engine.MascotHabitat(stage_width=80)
        self.update_mascot_display()
        self.set_interval(1.5, self._on_mascot_tick)

    # --------------------------------------------------------------------------
    # Mascot Kubi Methods
    # --------------------------------------------------------------------------
    def mascot_react(self, event_type_or_mood: str, msg: str = None, duration_sec: float = 6.0):
        mood_to_event = {
            "focus": "focus_start",
            "celebrate": "task_done_single",
            "happy": "task_add",
            "proud": "ai_done",
            "idle": "idle_pacing"
        }
        event_key = mood_to_event.get(event_type_or_mood, event_type_or_mood)
        if msg:
            self.habitat.current_msg = msg
            self.habitat.lock_ticks = max(1, int(duration_sec / 1.5))
        else:
            self.habitat.react_to_event(event_key, lock_seconds=duration_sec)
        self.update_mascot_display()

    def _on_mascot_tick(self):
        try:
            widget = self.query_one("#mascot-stage", Static)
            w = widget.size.width if widget.size.width > 20 else 80
        except Exception:
            w = 80
        self.habitat.tick(stage_width=w)
        self.update_mascot_display()

    def update_mascot_display(self):
        try:
            widget = self.query_one("#mascot-stage", Static)
        except Exception:
            return

        style_titles = {
            "cat": "🐾 KUBI THE PIXEL CYBER CAT",
            "robo": "🤖 KUBI THE PIXEL CYBER BOT",
            "slime": "👾 KUBI THE PIXEL CYBER SLIME",
            "dino": "🦖 KUBI THE PIXEL CYBER DINO",
            "kaomoji": "🐾 KUBI THE KAOMOJI COMPANION"
        }
        widget.border_title = style_titles.get(self.habitat.style, "🐾 KUBI THE PIXEL COMPANION")

        w = widget.size.width if widget.size.width > 20 else 80
        widget.update(self.habitat.render_tui(width=w))

    # --------------------------------------------------------------------------
    # Task Management
    # --------------------------------------------------------------------------
    def update_progress_display(self):
        total = len(self.tasks)
        done = sum(1 for t in self.tasks if t.get("status") == "done")
        in_progress = sum(1 for t in self.tasks if t.get("status") == "in_progress")
        pct = int((done / total * 100)) if total > 0 else 0

        self.query_one("#task-progress", ProgressBar).update(total=100, progress=pct)

        progress_str = f"Tiến độ: [bold green]{pct}%[/bold green] [dim]({done} xong, {in_progress} đang làm, {total - done - in_progress} chờ)[/dim]"
        self.query_one("#progress-text", Label).update(progress_str)

        # Cập nhật thanh đồng hồ đếm ngược Focus riêng biệt, luôn hiển thị trực quan
        if self.focus_active:
            m = self.focus_remaining_seconds // 60
            s = self.focus_remaining_seconds % 60
            title_display = self.focus_task_title[:24] + ("…" if len(self.focus_task_title) > 24 else "")
            if self.focus_paused:
                timer_str = f"[bold yellow]⏸ TẠM DỪNG [{m:02d}:{s:02d}][/bold yellow] [dim]{title_display} (Bấm [p] để tiếp tục)[/dim]"
            else:
                is_kick = getattr(self, "focus_is_kickstart", False)
                mode_tag = "🔥 PHÁ BĂNG 5P" if is_kick else "⏱ ĐANG ĐẾM GIỜ"
                timer_str = f"[bold red]{mode_tag} [{m:02d}:{s:02d}][/bold red] [bold white]{title_display}[/bold white] [dim](Bấm [p] tạm dừng │ [P] hủy)[/dim]"
        else:
            timer_str = "[dim]⏱ Focus: [bold cyan]25:00[/bold cyan] (Chọn task rồi bấm [bold white]p[/bold white] (25p) hoặc [bold white]k[/bold white] (Phá băng 5p))[/dim]"

        self.query_one("#focus-timer-text", Label).update(timer_str)

    def render_tasks(self):
        task_list_widget = self.query_one("#tasks-list", ListView)
        saved_index = task_list_widget.index
        task_list_widget.clear()

        self.update_progress_display()
        for task in self.tasks:
            t_id = task.get("id")
            status = task.get("status", "todo")
            title = task.get("title", "")
            tag = task.get("tag", "TASK")

            if status == "done":
                icon = "[bold green]✓[/bold green]"
                title_fmt = f"[strike dim]{title}[/strike dim]"
            elif status == "in_progress":
                icon = "[bold yellow]⏳[/bold yellow]"
                title_fmt = f"[bold white]{title}[/bold white]"
            else:
                icon = "[dim]•[/dim]"
                title_fmt = f"{title}"

            tag_fmt = f"[blue]\\[{tag}][/blue]"

            # Huy hiệu Focus nếu task này đang được hẹn giờ
            focus_badge = ""
            if self.focus_active and self.focus_task_id == t_id:
                m = self.focus_remaining_seconds // 60
                s = self.focus_remaining_seconds % 60
                focus_badge = f" [bold red]⏱ {m:02d}:{s:02d}[/bold red]"

            label = Label(f"{icon} {tag_fmt} {title_fmt}{focus_badge}")
            task_list_widget.append(TaskItem(task, label))

        if saved_index is not None and len(self.tasks) > 0:
            task_list_widget.index = min(saved_index, len(self.tasks) - 1)

    def action_toggle_task(self):
        task_list = self.query_one("#tasks-list", ListView)
        highlighted = task_list.highlighted_child
        if isinstance(highlighted, TaskItem):
            task_id = highlighted.task_data.get("id")
            for t in self.tasks:
                if t.get("id") == task_id:
                    curr = t.get("status", "todo")
                    if curr == "todo":
                        t["status"] = "in_progress"
                        self.habitat.react_to_event("task_in_progress")
                    elif curr == "in_progress":
                        t["status"] = "done"
                        self.habitat.task_streak += 1
                        if len(self.tasks) > 0 and all(x.get("status") == "done" for x in self.tasks):
                            self.habitat.react_to_event("all_tasks_done", lock_seconds=10.0)
                        elif self.habitat.task_streak >= 2:
                            self.habitat.react_to_event("task_done_streak", {"count": self.habitat.task_streak})
                        else:
                            self.habitat.react_to_event("task_done_single")
                    else:
                        t["status"] = "todo"
                        self.habitat.task_streak = max(0, self.habitat.task_streak - 1)
                    break
            save_tasks(self.tasks)
            self.render_tasks()
            self.update_mascot_display()

    def add_task_from_article(self, title: str, tag: str = "SEC-INTEL"):
        """Tạo task mới từ bài báo kỹ thuật hoặc kết quả AI."""
        new_id = max([t.get("id", 0) for t in self.tasks], default=0) + 1
        self.tasks.append({"id": new_id, "tag": tag, "title": title, "status": "todo"})
        save_tasks(self.tasks)
        self.render_tasks()
        self.habitat.react_to_event("task_add")
        self.update_mascot_display()

    def action_delete_task(self):
        task_list = self.query_one("#tasks-list", ListView)
        highlighted = task_list.highlighted_child
        if isinstance(highlighted, TaskItem):
            task_id = highlighted.task_data.get("id")
            if self.focus_active and self.focus_task_id == task_id:
                self.action_stop_focus()
            self.tasks = [t for t in self.tasks if t.get("id") != task_id]
            save_tasks(self.tasks)
            self.render_tasks()
            self.habitat.react_to_event("task_delete")
            self.update_mascot_display()

    # --------------------------------------------------------------------------
    # Task-bound Focus Session / Pomodoro 25p (STT 07 & STT 10)
    # --------------------------------------------------------------------------
    def action_toggle_focus(self):
        if not self.focus_active:
            task_list = self.query_one("#tasks-list", ListView)
            highlighted = task_list.highlighted_child
            task = None
            if isinstance(highlighted, TaskItem):
                task = highlighted.task_data
            elif task_list.index is not None and task_list.children and isinstance(task_list.children[task_list.index], TaskItem):
                task = task_list.children[task_list.index].task_data
            else:
                # Ưu tiên task đang làm dở (in_progress), nếu không lấy task đầu tiên
                in_prog = [t for t in self.tasks if t.get("status") == "in_progress"]
                if in_prog:
                    task = in_prog[0]
                elif self.tasks:
                    task = self.tasks[0]

            if not task:
                self.notify("Vui lòng thêm một công việc vào danh sách để bắt đầu Focus!", title="Focus 25p")
                return
            self.focus_task_id = task.get("id")
            self.focus_task_title = task.get("title", "")
            self.focus_remaining_seconds = 25 * 60
            self.focus_total_seconds = 25 * 60
            self.focus_is_kickstart = False
            self.focus_active = True
            self.focus_paused = False
            # Tự động gán trạng thái in_progress cho task
            if task.get("status") == "todo":
                task["status"] = "in_progress"
                save_tasks(self.tasks)

            self.focus_timer = self.set_interval(1.0, self._on_focus_tick)
            self.render_tasks()
            self.habitat.react_to_event("focus_start")
            self.update_mascot_display()

            # Hiển thị trích dẫn định hướng ngữ cảnh bắt đầu (STT 10)
            quote = get_random_quote("focus_start")
            self.notify(
                f"Bắt đầu đếm giờ 25p: {self.focus_task_title[:30]}\n"
                f"\"{quote['quote']}\" — {quote['author']}",
                title="⏱ Focus Session Started"
            )
        else:
            # Tạm dừng hoặc tiếp tục phiên hiện hành
            self.focus_paused = not self.focus_paused
            if self.focus_paused:
                self.notify("Đã tạm dừng đếm giờ Focus. Bấm [p] để tiếp tục.", title="Focus Paused")
                self.habitat.react_to_event("focus_pause")
            else:
                self.notify("Tiếp tục đếm giờ Focus.", title="Focus Resumed")
                self.habitat.react_to_event("focus_start")
            self.update_mascot_display()
            self.update_progress_display()

    def action_stop_focus(self):
        if self.focus_active:
            if self.focus_timer:
                self.focus_timer.stop()
                self.focus_timer = None
            self.focus_active = False
            self.focus_paused = False
            self.notify("Đã dừng phiên Focus.", title="Focus Stopped")
            self.render_tasks()
            self.habitat.react_to_event("focus_pause")
            self.update_mascot_display()
    def action_kickstart_focus(self, minutes: int = 5):
        """Kích hoạt phiên làm việc 5 phút phá băng tâm lý (Anti-Inertia Kickstart)."""
        if self.focus_active and getattr(self, "focus_is_kickstart", False):
            self.action_toggle_focus()
            return

        if self.focus_active:
            self.action_stop_focus()

        task_list = self.query_one("#tasks-list", ListView)
        highlighted = task_list.highlighted_child
        task = None
        if isinstance(highlighted, TaskItem):
            task = highlighted.task_data
        elif task_list.index is not None and task_list.children and isinstance(task_list.children[task_list.index], TaskItem):
            task = task_list.children[task_list.index].task_data
        else:
            in_prog = [t for t in self.tasks if t.get("status") == "in_progress"]
            if in_prog:
                task = in_prog[0]
            elif self.tasks:
                task = self.tasks[0]

        if not task:
            new_id = max([t.get("id", 0) for t in self.tasks], default=0) + 1
            task = {"id": new_id, "tag": "START", "title": "5 phút khởi động phá băng tâm lý", "status": "in_progress"}
            self.tasks.append(task)
            save_tasks(self.tasks)
            self.render_tasks()

        self.focus_task_id = task.get("id")
        self.focus_task_title = task.get("title", "")
        self.focus_remaining_seconds = minutes * 60
        self.focus_total_seconds = minutes * 60
        self.focus_is_kickstart = True
        self.focus_active = True
        self.focus_paused = False

        if task.get("status") == "todo":
            task["status"] = "in_progress"
            save_tasks(self.tasks)

        if self.focus_timer:
            self.focus_timer.stop()
        self.focus_timer = self.set_interval(1.0, self._on_focus_tick)
        self.render_tasks()
        self.habitat.react_to_event("kickstart_start", lock_seconds=8.0)
        self.update_mascot_display()

        self.notify(
            f"🔥 Bắt đầu 5 phút phá băng: {self.focus_task_title[:30]}\n"
            f"\"Thỏa thuận 5 phút: Chỉ cần làm 5 phút này, không nghĩ gì xa xôi!\"",
            title="🔥 Kickstart Session Started (5m)"
        )

    def _on_focus_tick(self):
        if not self.focus_active or self.focus_paused:
            return

        self.focus_remaining_seconds -= 1
        if self.focus_remaining_seconds <= 0:
            if self.focus_timer:
                self.focus_timer.stop()
                self.focus_timer = None
            self.focus_active = False
            self.focus_paused = False

            # Phát chuông terminal
            try:
                sys.stdout.write("\a")
                sys.stdout.flush()
            except Exception:
                pass

            # Đổi trạng thái task sang hoàn thành
            for t in self.tasks:
                if t.get("id") == self.focus_task_id:
                    t["status"] = "done"
                    break
            save_tasks(self.tasks)
            self.render_tasks()
            if getattr(self, "focus_is_kickstart", False):
                self.habitat.react_to_event("kickstart_done", lock_seconds=10.0)
                self.update_mascot_display()
                self.notify(
                    f"🎉 XONG 5 PHÚT PHÁ BĂNG TÂM LÝ!\n"
                    f"Sức ì đã bị đánh bại! Bạn đã có đà quán tính, cứ tiếp tục giữ nhịp làm việc nhé!",
                    title="🔥 Phá Băng Thành Công",
                    severity="information"
                )
            else:
                self.habitat.react_to_event("focus_done", lock_seconds=10.0)
                self.update_mascot_display()
                quote = get_random_quote("focus_done")
                self.notify(
                    f"🎉 Hoàn thành xuất sắc 25 phút tập trung!\n"
                    f"\"{quote['quote']}\" — {quote['author']}",
                    title="Focus Complete",
                    severity="information"
                )
        else:
            self.update_progress_display()
            task_list_widget = self.query_one("#tasks-list", ListView)
            m = self.focus_remaining_seconds // 60
            s = self.focus_remaining_seconds % 60
            for child in task_list_widget.children:
                if isinstance(child, TaskItem) and child.task_data.get("id") == self.focus_task_id:
                    lbl = child.query_one(Label)
                    title = child.task_data.get("title", "")
                    tag = child.task_data.get("tag", "TASK")
                    is_kick = getattr(self, "focus_is_kickstart", False)
                    timer_color = "red" if is_kick else "yellow"
                    lbl.update(f"[bold yellow]⏳[/bold yellow] [blue]\\[{tag}][/blue] [bold white]{title}[/bold white] [bold {timer_color}]⏱ {m:02d}:{s:02d}[/bold {timer_color}]")
                    break

    def _trigger_ai_kickstart(self, task_desc: str):
        """Dùng AI phân rã công việc thành 3 micro-steps và tự động kích hoạt Bước 1."""
        cli_name, _ = get_ai_cli()
        if not cli_name:
            self.notify("Không tìm thấy công cụ AI để phân rã task!", title="Lỗi AI", severity="error")
            return

        detail_box = self.query_one("#detail-box", Static)
        detail_box.update(
            f"[bold cyan]🔥 ANTI-INERTIA ENGINE ({cli_name.upper()}):[/bold cyan]\n"
            f"[yellow]Đang bẻ nhỏ công việc '[bold white]{task_desc}[/bold white]' thành các bước siêu dễ...[/yellow]\n\n"
            f"[dim]Áp dụng nguyên lý năng lượng kích hoạt thấp (Low Activation Energy). Vui lòng đợi ~5s...[/dim]"
        )
        self.notify(f"AI đang bẻ nhỏ task: {task_desc[:25]}...", title="Phá Băng Tâm Lý")
        self.habitat.react_to_event("ai_thinking")
        self.update_mascot_display()

        prompt = (
            f"Bạn là chuyên gia tâm lý học hành vi và năng suất lao động. Người dùng đang bị trì hoãn và không thể bắt tay vào làm công việc này:\n"
            f"\"{task_desc}\"\n\n"
            f"Hãy phân rã công việc này thành đúng 3 bước hành động SIÊU NHỎ (Micro-steps) theo nguyên lý năng lượng kích hoạt thấp (Low Activation Energy):\n"
            f"- Bước 1 (Micro-Step 0 - CỰC KỲ DỄ, làm xong trong DƯỚI 2 PHÚT, chỉ là hành động khởi động vật lý không cần suy nghĩ sâu. Ví dụ: Mở file, tạo thư mục, gõ dòng đầu tiên).\n"
            f"- Bước 2 (Làm trong 5 phút tiếp theo để tạo đà quán tính).\n"
            f"- Bước 3 (Bắt đầu nội dung chính khi đã vào guồng Flow state).\n\n"
            f"YÊU CẦU: Trả về duy nhất JSON hợp lệ, không giải thích gì thêm, định dạng:\n"
            f"{{\n"
            f'  "step1": "Mô tả bước 1 (< 2 phút)",\n'
            f'  "step2": "Mô tả bước 2 (5 phút)",\n'
            f'  "step3": "Mô tả bước 3",\n'
            f'  "encouragement": "Lời động viên ngắn gọn, truyền cảm hứng hành động"\n'
            f"}}"
        )

        def worker():
            ok, text, tool = call_ai_cli(prompt, timeout=90.0)
            self.call_from_thread(self._on_kickstart_finish, task_desc, ok, text, tool)

        threading.Thread(target=worker, daemon=True).start()

    def _on_kickstart_finish(self, task_desc: str, ok: bool, text: str, tool: str):
        step1 = ""
        step2 = ""
        step3 = ""
        encouragement = "Chỉ cần bắt đầu bước 1 là bạn đã chiến thắng 80% sức ì rồi!"

        if ok:
            try:
                clean_json = text.strip()
                if "```" in clean_json:
                    clean_json = re.sub(r"^```[a-zA-Z]*\n", "", clean_json)
                    clean_json = re.sub(r"\n```$", "", clean_json)
                data = json.loads(clean_json)
                step1 = data.get("step1", "")
                step2 = data.get("step2", "")
                step3 = data.get("step3", "")
                encouragement = data.get("encouragement", encouragement)
            except Exception:
                pass

        if not step1:
            step1 = f"Mở công cụ / file liên quan đến: {task_desc[:40]}"
            step2 = f"Viết nháp 3 gạch đầu dòng sườn nội dung"
            step3 = f"Thực hiện nội dung cốt lõi của việc"

        # Thêm 3 bước vào danh sách Tasks
        base_id = max([t.get("id", 0) for t in self.tasks], default=0)
        t1 = {"id": base_id + 1, "tag": "BƯỚC 1", "title": step1, "status": "in_progress"}
        t2 = {"id": base_id + 2, "tag": "BƯỚC 2", "title": step2, "status": "todo"}
        t3 = {"id": base_id + 3, "tag": "BƯỚC 3", "title": step3, "status": "todo"}
        self.tasks.extend([t1, t2, t3])
        save_tasks(self.tasks)
        self.render_tasks()

        # Tự động kích hoạt đếm ngược 5 phút cho Bước 1!
        self.focus_task_id = t1["id"]
        self.focus_task_title = t1["title"]
        self.focus_remaining_seconds = 5 * 60
        self.focus_total_seconds = 5 * 60
        self.focus_is_kickstart = True
        self.focus_active = True
        self.focus_paused = False
        if self.focus_timer:
            self.focus_timer.stop()
        self.focus_timer = self.set_interval(1.0, self._on_focus_tick)
        self.render_tasks()

        # Linh vật phản xạ phấn khích
        self.habitat.react_to_event("kickstart_decomposed", lock_seconds=10.0)
        self.update_mascot_display()

        # Mở Pop-up Kickstart
        self.push_screen(KickstartDecomposeModal(task_desc, step1, step2, step3, encouragement))
    # --------------------------------------------------------------------------
    # Modals Triggers: Briefing, Wrap-Up (STT 01 & STT 08)
    # --------------------------------------------------------------------------
    def action_open_briefing(self):
        briefing = get_morning_briefing(self.articles, max_items=5)
        self.push_screen(BriefingModal(briefing))

    def action_open_wrapup(self):
        quote = get_random_quote("wrapup")
        self.push_screen(WrapUpModal(self.tasks, quote))

    # --------------------------------------------------------------------------
    # Navigation & Omnibar
    # --------------------------------------------------------------------------
    def action_focus_omnibox_task(self):
        omnibox = self.query_one("#omnibox", Input)
        omnibox.value = "task: "
        omnibox.focus()
        omnibox.cursor_position = len(omnibox.value)

    def action_focus_omnibox(self):
        omnibox = self.query_one("#omnibox", Input)
        omnibox.focus()

    def action_unfocus_omnibox(self):
        omnibox = self.query_one("#omnibox", Input)
        if omnibox.has_focus:
            omnibox.value = ""
        self.query_one("#tasks-list", ListView).focus()

    def action_focus_news(self):
        self.query_one("#news-list", NewsListView).focus()

    def action_focus_tasks(self):
        self.query_one("#tasks-list", ListView).focus()

    def action_open_selected_article(self):
        news_list = self.query_one("#news-list", NewsListView)
        highlighted = news_list.highlighted_child
        if isinstance(highlighted, NewsItem):
            link = highlighted.article_data.get("link", "")
            if link:
                self.notify(f"Đang mở: {highlighted.article_data.get('title', '')[:35]}...", title="Browser")
                subprocess.Popen(["xdg-open", link], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.habitat.react_to_event("open_web")
                self.update_mascot_display()

    def on_input_submitted(self, event: Input.Submitted):
        query = event.value.strip()
        event.input.value = ""
        if query:
            self._handle_omnibox_query(query)
        self.query_one("#tasks-list", ListView).focus()

    def _handle_omnibox_query(self, query: str):
        q = query.strip()
        if not q:
            return

        # 0. Hướng dẫn sử dụng Omnibar Vạn Năng
        if q.lower() in ["help", "?", "omni", "trogiup", "cheatsheet", "helpme"]:
            self.push_screen(OmniHelpModal())
            return

        # 1. Điểm tin đầu ngày
        if q.lower() in ["brief", "briefing", "diemtin"]:
            self.action_open_briefing()
            return

        # 2. Phiên Focus Pomodoro: "focus", "focus 15", "focus stop"
        if q.lower().startswith("focus"):
            if "stop" in q.lower() or "cancel" in q.lower():
                self.action_stop_focus()
            else:
                parts = q.split()
                if len(parts) >= 2 and parts[1].isdigit():
                    custom_mins = int(parts[1])
                    self.focus_seconds = custom_mins * 60
                    self.focus_total = self.focus_seconds
                    self.action_toggle_focus()
                else:
                    self.action_toggle_focus()
            return

        # Anti-Inertia Kickstart: "kick: <tên việc>" (AI bẻ việc thành 3 micro-steps & đếm giờ 5p)
        if q.lower().startswith("kick:") or q.lower().startswith("break:") or q.lower().startswith("micro:") or q.lower().startswith("phanra:"):
            task_arg = re.sub(r"^(kick|break|micro|phanra):\s*", "", q, flags=re.IGNORECASE).strip()
            if task_arg:
                self._trigger_ai_kickstart(task_arg)
            else:
                self.notify("Cú pháp: kick: <tên việc bạn đang ngại làm>", title="Anti-Inertia Kickstart")
            return

        # Lệnh phá băng 5 phút: "kickstart" hoặc "phabang"
        if q.lower() in ["kickstart", "phabang", "pha bang", "flow"]:
            self.action_kickstart_focus(5)
            return

        # 3. Báo cáo tổng kết ngày
        if q.lower() in ["wrapup", "eod", "tongket", "log"]:
            self.action_open_wrapup()
            return

        # 4. Lọc & Tìm kiếm tin tức tại chỗ: "filter: zero-day", "search: cisa", "find: ssh"
        if q.lower().startswith("filter:") or q.lower().startswith("search:") or q.lower().startswith("find:"):
            kw = re.sub(r"^(filter|search|find):\s*", "", q, flags=re.IGNORECASE).strip()
            if kw:
                self.filter_news(kw)
            return

        # 5. Khôi phục tin tức: "reset", "clear", "all"
        if q.lower() in ["reset", "clear", "all", "khoiphuc"]:
            self.reset_news_filter()
            return

        # 6. Đổi kiểu linh vật Pixel / Kaomoji: "mascot: cat", "style: robo"
        if q.lower().startswith("mascot:") or q.lower().startswith("style:"):
            target_style = re.sub(r"^(mascot|style):\s*", "", q, flags=re.IGNORECASE).strip().lower()
            if target_style in ("cat", "robo", "slime", "dino", "kaomoji"):
                self.habitat.set_style(target_style)
                self.notify(f"Đã đổi linh vật sang: {target_style.upper()}", title="Mascot Style")
                self.update_mascot_display()
            else:
                self.notify("Hỗ trợ: cat (mèo máy), robo (robot), slime, dino, kaomoji", title="Mascot Style")
            return

        # 7. Tương tác với Kubi Buddy: "buddy: cheer", "buddy: watch"
        if q.lower().startswith("buddy:"):
            b_act = re.sub(r"^buddy:\s*", "", q, flags=re.IGNORECASE).strip().lower()
            if b_act == "cheer":
                self.habitat.react_to_event("cheer")
                self.update_mascot_display()
                self.notify("( ˶ᵔ ᵕ ᵔ˶ ) Kubi chúc bạn một ngày làm việc tràn đầy cảm hứng!", title="Kubi Cheer")
            elif b_act == "watch":
                self.habitat.react_to_event("focus_start")
                self.update_mascot_display()
                self.notify("( ʘ ‿ ʘ ) Kubi đang ngồi bàn làm việc quan sát cùng bạn!", title="Kubi Watch")
            else:
                self.notify("Các lệnh buddy: cheer (cổ vũ), watch (quan sát)", title="Kubi Buddy")
            return

        # 8. Thực thi lệnh Shell tức thì: "! df -h" hoặc "sh: uptime"
        if q.startswith("!") or q.lower().startswith("sh:") or q.lower().startswith("run:"):
            cmd = re.sub(r"^(!|sh:|run:)\s*", "", q).strip()
            if cmd:
                self.notify(f"Đang chạy lệnh: {cmd[:30]}...", title="Shell Execution")
                def run_shell_worker():
                    try:
                        res = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
                        output = res.stdout if res.returncode == 0 else (res.stderr or res.stdout or f"Mã thoát {res.returncode}")
                        is_err = res.returncode != 0
                    except subprocess.TimeoutExpired:
                        output = "Quá thời gian thực thi (15s)."
                        is_err = True
                    except Exception as e:
                        output = f"Lỗi thực thi: {e}"
                        is_err = True
                    self.call_from_thread(self._on_shell_finish, cmd, output, is_err)
                threading.Thread(target=run_shell_worker, daemon=True).start()
            return

        # 9. Mở ứng dụng hệ thống: "open code", "open chrome", "open dolphin"...
        if q.lower().startswith("open "):
            target_app = q[5:].strip().lower()
            app_map = {
                "chrome": "google-chrome",
                "google-chrome": "google-chrome",
                "browser": "google-chrome",
                "code": "code",
                "vscode": "code",
                "terminal": "konsole",
                "konsole": "konsole",
                "dolphin": "dolphin",
                "files": "dolphin",
                "settings": "systemsettings",
            }
            bin_to_run = app_map.get(target_app, target_app)
            if shutil.which(bin_to_run):
                self.notify(f"Đang mở ứng dụng: {bin_to_run}...", title="App Launcher")
                subprocess.Popen([bin_to_run], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.habitat.react_to_event("open_web")
                self.update_mascot_display()
            else:
                self.notify(f"Không tìm thấy ứng dụng '{target_app}' trong PATH", title="Lỗi Mở App", severity="warning")
            return

        # 10. Đổi hình nền 4K: "wall: whitesur", "bg: sonoma"
        if q.lower().startswith("wall:") or q.lower().startswith("bg:") or q.lower().startswith("wallpaper:"):
            wall_name = re.sub(r"^(wall|bg|wallpaper):\s*", "", q, flags=re.IGNORECASE).strip()
            script_path = "/home/letuan/make_Kubuntu_better/set_wallpaper.sh"
            if os.path.exists(script_path):
                self.notify(f"Đang đổi hình nền sang: {wall_name}...", title="Wallpaper")
                def wall_worker():
                    subprocess.run([script_path, wall_name], capture_output=True)
                threading.Thread(target=wall_worker, daemon=True).start()
            return

        # 11. Đổi icon theme: "icon: colloid", "icon: tela", "icon: breeze"
        if q.lower().startswith("icon:"):
            icon_name = re.sub(r"^icon:\s*", "", q, flags=re.IGNORECASE).strip()
            script_path = "/home/letuan/make_Kubuntu_better/toggle_icon_style.sh"
            if os.path.exists(script_path):
                self.notify(f"Đang đổi icon sang: {icon_name}...", title="Icon Style")
                def icon_worker():
                    subprocess.run([script_path, icon_name], capture_output=True)
                threading.Thread(target=icon_worker, daemon=True).start()
            return

        # 12. Quản lý Autostart: "autostart: workspace", "autostart: disable"
        if q.lower().startswith("autostart:"):
            as_mode = re.sub(r"^autostart:\s*", "", q, flags=re.IGNORECASE).strip()
            script_path = "/home/letuan/make_Kubuntu_better/toggle_autostart.sh"
            if os.path.exists(script_path):
                self.notify(f"Đang thiết lập autostart: {as_mode}...", title="Autostart")
                def as_worker():
                    subprocess.run([script_path, as_mode], capture_output=True)
                threading.Thread(target=as_worker, daemon=True).start()
            return

        # 13. Quản lý Task: Thêm, Hoàn thành, Xóa
        if q.lower().startswith("done:"):
            try:
                t_id = int(re.sub(r"^done:\s*", "", q, flags=re.IGNORECASE).strip())
                for t in self.tasks:
                    if t.get("id") == t_id:
                        t["status"] = "done"
                        save_tasks(self.tasks)
                        self.render_tasks()
                        self.notify(f"Đã hoàn thành task #{t_id}: {t.get('title')}", title="Task Done")
                        self.habitat.react_to_event("task_done")
                        self.update_mascot_display()
                        return
                self.notify(f"Không tìm thấy task #{t_id}", title="Task", severity="warning")
            except ValueError:
                self.notify("Cú pháp: done: <id> (ví dụ: done: 1)", title="Task", severity="error")
            return

        if q.lower().startswith("del:") or q.lower().startswith("rm:"):
            try:
                t_id = int(re.sub(r"^(del|rm):\s*", "", q, flags=re.IGNORECASE).strip())
                before_len = len(self.tasks)
                self.tasks = [t for t in self.tasks if t.get("id") != t_id]
                if len(self.tasks) < before_len:
                    save_tasks(self.tasks)
                    self.render_tasks()
                    self.notify(f"Đã xóa task #{t_id}", title="Task Removed")
                    self.habitat.react_to_event("task_del")
                    self.update_mascot_display()
                else:
                    self.notify(f"Không tìm thấy task #{t_id}", title="Task", severity="warning")
            except ValueError:
                self.notify("Cú pháp: del: <id> (ví dụ: del: 1)", title="Task", severity="error")
            return

        if q.lower().startswith("task:") or q.lower().startswith("todo:"):
            task_text = re.sub(r"^(task|todo):\s*", "", q, flags=re.IGNORECASE).strip()
            if task_text:
                tag = "TASK"
                if task_text.startswith("[") and "]" in task_text:
                    tag = task_text[1:task_text.index("]")].upper()
                    task_text = task_text[task_text.index("]")+1:].strip()
                new_id = max([t.get("id", 0) for t in self.tasks], default=0) + 1
                self.tasks.append({"id": new_id, "tag": tag, "title": task_text, "status": "todo"})
                save_tasks(self.tasks)
                self.render_tasks()
                self.notify(f"Đã thêm task: [{tag}] {task_text}", title="Task Added")
                self.habitat.react_to_event("task_add")
                self.update_mascot_display()
            return

        # 14. Máy tính số học nhanh (Quick Math Calculator)
        calc_res = safe_calc(q)
        if calc_res is not None:
            self.notify(f"🔢 {q} = {calc_res}", title="Máy tính nhanh")
            detail_box = self.query_one("#detail-box", Static)
            detail_box.update(
                f"[bold cyan]🔢 MÁY TÍNH NHANH OMNIBAR[/bold cyan]\n\n"
                f"Biểu thức: [bold white]{q}[/bold white]\n"
                f"Kết quả:   [bold green]{calc_res}[/bold green]"
            )
            self.habitat.react_to_event("task_done")
            self.update_mascot_display()
            return

        # 15. Tra cứu CVE: "CVE-2024-xxxx" hoặc "cve: xxxx"
        cve_match = re.search(r"\b(CVE-\d{4}-\d{4,7})\b", q, re.IGNORECASE)
        if cve_match or q.lower().startswith("cve:"):
            cve_id = cve_match.group(1).upper() if cve_match else re.sub(r"^cve:\s*", "", q, flags=re.IGNORECASE).strip().upper()
            url = f"https://nvd.nist.gov/vuln/detail/{cve_id}"
            self.notify(f"Đang mở NVD: {cve_id}...", title="CVE Lookup")
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.habitat.react_to_event("cve_found", {"cve": cve_id})
            self.update_mascot_display()
            return

        # 16. Tra cứu GitHub, StackOverflow, Shodan
        if q.lower().startswith("gh:"):
            repo_q = re.sub(r"^gh:\s*", "", q, flags=re.IGNORECASE).strip()
            url = f"https://github.com/{repo_q}" if ("/" in repo_q and " " not in repo_q) else f"https://github.com/search?q={urllib.parse.quote_plus(repo_q)}"
            self.notify(f"Đang mở GitHub: {repo_q}...", title="GitHub Search")
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.habitat.react_to_event("open_web")
            self.update_mascot_display()
            return

        if q.lower().startswith("so:"):
            so_q = re.sub(r"^so:\s*", "", q, flags=re.IGNORECASE).strip()
            url = f"https://stackoverflow.com/search?q={urllib.parse.quote_plus(so_q)}"
            self.notify(f"Đang tìm StackOverflow: {so_q}...", title="StackOverflow")
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.habitat.react_to_event("open_web")
            self.update_mascot_display()
            return

        if q.lower().startswith("shodan:"):
            sho_q = re.sub(r"^shodan:\s*", "", q, flags=re.IGNORECASE).strip()
            url = f"https://www.shodan.io/search?query={urllib.parse.quote_plus(sho_q)}"
            self.notify(f"Đang tra Shodan: {sho_q}...", title="Shodan Search")
            subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.habitat.react_to_event("open_web")
            self.update_mascot_display()
            return

        # 17. Hỏi Trợ Lý AI: Bắt đầu bằng ai:, hỏi:, ask:, chat:, gpt: hoặc các câu hỏi tự nhiên
        ai_prefixes = ("ai:", "hỏi:", "ask:", "chat:", "gpt:")
        is_ai_cmd = any(q.lower().startswith(p) for p in ai_prefixes)
        natural_q = any(q.lower().startswith(w) for w in ["tại sao", "vì sao", "làm sao", "là gì", "thế nào", "hãy ", "giải thích", "hướng dẫn"]) or q.endswith("?")

        if is_ai_cmd or natural_q:
            custom_q = q
            for p in ai_prefixes:
                if q.lower().startswith(p):
                    custom_q = q[len(p):].strip()
                    break

            if not custom_q:
                self.notify("Vui lòng nhập câu hỏi sau lệnh AI!", title="AI Assistant")
                return

            news_list = self.query_one("#news-list", NewsListView)
            highlighted = news_list.highlighted_child
            art = highlighted.article_data if isinstance(highlighted, NewsItem) else None

            article_keywords = ["bài này", "bài viết", "bài báo", "tin này", "sự cố này", "lỗ hổng này", "tác giả", "link này", "nguồn này", "trong bài"]
            wants_article = any(k in custom_q.lower() for k in article_keywords)

            if wants_article and art:
                self._trigger_ai_custom(art, custom_q, is_general=False)
            elif art and not wants_article:
                self._trigger_ai_custom(art, custom_q, is_general=True)
            else:
                dummy_art = {"title": custom_q, "vendor": "Trợ lý AI", "desc": "", "link": ""}
                self._trigger_ai_custom(dummy_art, custom_q, is_general=True)
            return

        # 18. Fallback: Mở Google Search
        url = f"https://www.google.com/search?q={urllib.parse.quote_plus(q)}"
        self.notify(f"Tìm kiếm Google: {q[:30]}...", title="Google Search")
        subprocess.Popen(["xdg-open", url], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.habitat.react_to_event("open_web")
        self.update_mascot_display()
    # --------------------------------------------------------------------------
    # AI CLI Analysis for News (agy, codex)
    # --------------------------------------------------------------------------
    def action_ai_summarize_vn(self):
        news_list = self.query_one("#news-list", NewsListView)
        highlighted = news_list.highlighted_child
        art = None
        if isinstance(highlighted, NewsItem):
            art = highlighted.article_data
        elif news_list.children and isinstance(news_list.children[news_list.index or 0], NewsItem):
            art = news_list.children[news_list.index or 0].article_data
        elif self.articles:
            art = self.articles[0]

        if not art:
            self.notify("Vui lòng chọn một bài viết ở danh sách bản tin!", title="AI Intel")
            return
        self._trigger_ai_analysis(art, mode="summary")

    def action_ai_deep_analyze(self):
        news_list = self.query_one("#news-list", NewsListView)
        highlighted = news_list.highlighted_child
        art = None
        if isinstance(highlighted, NewsItem):
            art = highlighted.article_data
        elif news_list.children and isinstance(news_list.children[news_list.index or 0], NewsItem):
            art = news_list.children[news_list.index or 0].article_data
        elif self.articles:
            art = self.articles[0]

        if not art:
            self.notify("Vui lòng chọn một bài viết ở danh sách bản tin!", title="AI Intel")
            return
        self._trigger_ai_analysis(art, mode="deep")

    def _trigger_ai_analysis(self, art: dict, mode: str = "summary"):
        cli_name, _ = get_ai_cli()
        if not cli_name:
            self.notify("Không tìm thấy công cụ AI (agy, omp, pi, codex) trên hệ thống PATH!", title="Lỗi AI CLI", severity="error")
            return

        detail_box = self.query_one("#detail-box", Static)
        mode_label = "Tóm tắt tiếng Việt" if mode == "summary" else "Phân tích chuyên sâu"
        detail_box.update(
            f"[bold cyan]{art.get('title','')}[/bold cyan]\n\n"
            f"[bold yellow]🤖 AI ({cli_name.upper()}) đang {mode_label.lower()}... Vui lòng đợi trong giây lát.[/bold yellow]\n"
            f"[dim]Tiến trình đang chạy ngầm, terminal và dashboard hoàn toàn không bị gián đoạn.[/dim]"
        )
        self.notify(f"Đang gửi bài viết tới AI ({cli_name})...", title="AI Intel")
        self.habitat.react_to_event("ai_thinking")
        self.update_mascot_display()

        if mode == "summary":
            prompt = (
                f"Bạn là một chuyên gia an ninh mạng cao cấp. Hãy đọc thông tin bài viết sau và tóm tắt bằng tiếng Việt thật súc tích, chuẩn xác kỹ thuật:\n"
                f"- Bản chất lỗ hổng / sự cố (nêu rõ mã CVE nếu có)\n"
                f"- Mức độ tác động & đối tượng / hệ thống bị ảnh hưởng\n"
                f"- Khuyến nghị phòng thủ / vá lỗi cho quản trị viên và lập trình viên\n\n"
                f"Tiêu đề: {art.get('title', '')}\n"
                f"Nguồn: {art.get('vendor', '')}\n"
                f"Mô tả: {art.get('desc', '')}\n"
                f"Link: {art.get('link', '')}"
            )
        else:
            prompt = (
                f"Hãy phân tích kỹ thuật an ninh mạng chuyên sâu cho bài viết sau bằng tiếng Việt theo các mục rõ ràng:\n"
                f"1. Vector tấn công & Cơ chế khai thác kỹ thuật\n"
                f"2. Bề mặt tấn công & Hệ thống bị ảnh hưởng\n"
                f"3. Dấu hiệu nhận biết (IoC / Artifacts) nếu có\n"
                f"4. Biện pháp rà soát và khắc phục (Remediation)\n\n"
                f"Tiêu đề: {art.get('title', '')}\n"
                f"Nguồn: {art.get('vendor', '')}\n"
                f"Mô tả: {art.get('desc', '')}\n"
                f"Link: {art.get('link', '')}"
            )

        def worker():
            ok, text, tool = call_ai_cli(prompt, timeout=90.0)
            self.call_from_thread(self._on_ai_finish, art, ok, text, mode_label, tool)

        threading.Thread(target=worker, daemon=True).start()

    def _trigger_ai_custom(self, art: dict, custom_query: str, is_general: bool = False):
        cli_name, _ = get_ai_cli()
        if not cli_name:
            self.notify("Không tìm thấy công cụ AI (agy, omp, pi, codex)!", title="Lỗi AI CLI", severity="error")
            return

        detail_box = self.query_one("#detail-box", Static)
        if is_general:
            detail_box.update(
                f"[bold cyan]🤖 TRỢ LÝ AI ({cli_name.upper()}):[/bold cyan]\n"
                f"[italic white]'{custom_query}'[/italic white]...\n\n"
                f"[dim]Tiến trình đang chạy ngầm, vui lòng đợi trong giây lát.[/dim]"
            )
            mode_label = f"Hỏi AI: {custom_query[:25]}"
            prompt = (
                f"Bạn là một trợ lý AI thông minh trên hệ điều hành Kubuntu. "
                f"Hãy trả lời câu hỏi sau của người dùng bằng tiếng Việt chi tiết, mạch lạc, chính xác và có định dạng Markdown đẹp:\n\n"
                f"Câu hỏi: {custom_query}"
            )
        else:
            detail_box.update(
                f"[bold cyan]{art.get('title','')}[/bold cyan]\n\n"
                f"[bold yellow]🤖 AI ({cli_name.upper()}) đang trả lời yêu cầu: '{custom_query}'...[/bold yellow]\n"
            )
            mode_label = f"Phân tích tin: {custom_query[:20]}"
            prompt = (
                f"Người dùng có câu hỏi về bài viết an ninh mạng sau:\n"
                f"Yêu cầu: {custom_query}\n\n"
                f"Thông tin bài viết đính kèm:\n"
                f"Tiêu đề: {art.get('title', '')}\n"
                f"Nguồn: {art.get('vendor', '')}\n"
                f"Mô tả: {art.get('desc', '')}\n"
                f"Link: {art.get('link', '')}\n\n"
                f"Hãy trả lời bằng tiếng Việt chuyên nghiệp, súc tích."
            )

        self.notify(f"Đang hỏi AI ({cli_name}): {custom_query[:25]}...", title="AI Assistant")
        self.habitat.react_to_event("ai_thinking")
        self.update_mascot_display()

        def worker():
            ok, text, tool = call_ai_cli(prompt, timeout=90.0)
            self.call_from_thread(self._on_ai_finish, art, ok, text, mode_label, tool, is_general)

        threading.Thread(target=worker, daemon=True).start()

    def _on_ai_finish(self, art: dict, ok: bool, text: str, mode_label: str, tool: str, is_general: bool = False):
        detail_box = self.query_one("#detail-box", Static)
        if ok:
            if is_general:
                header_line = f"[bold cyan]🤖 TRỢ LÝ AI[/bold cyan] [green]({tool.upper()})[/green]\n[italic white]{mode_label}[/italic white]"
            else:
                header_line = f"[bold cyan]{art.get('title','')}[/bold cyan] [green]({tool.upper()} - {mode_label})[/green]"

            detail_box.update(
                f"{header_line}\n\n"
                f"[yellow]{text[:350]}...[/yellow]\n\n"
                f"[bold green]➔ Bấm [v] hoặc [x] để mở xem toàn bộ │ [Enter/o] Mở link gốc[/bold green]"
            )
            # Mở Pop-up xem toàn văn kết quả Markdown
            self.push_screen(AIResultModal(art, text, mode_label, is_general=is_general))
            self.habitat.react_to_event("ai_done", lock_seconds=8.0)
            self.update_mascot_display()
        else:
            detail_box.update(
                f"[bold red]❌ {text}[/bold red]\n\n"
                f"[dim]Bấm [Enter/o] để xem bài gốc trên trình duyệt.[/dim]"
            )
            self.notify(text, title="Lỗi AI", severity="error")

    # --------------------------------------------------------------------------
    # News & Detailed Intelligence Preview (STT 02 Gom cụm tin tức)
    # --------------------------------------------------------------------------
    def fetch_all_news(self):
        threading.Thread(target=self._background_fetch, daemon=True).start()

    def _fetch_single_feed(self, src: dict) -> list[dict]:
        items = []
        try:
            req = urllib.request.Request(src["url"], headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64)"})
            with urllib.request.urlopen(req, timeout=5.0) as resp:
                root = ET.fromstring(resp.read())
                for item in root.findall(".//item")[:8]:
                    t_el = item.find("title")
                    l_el = item.find("link")
                    d_el = item.find("description")
                    p_el = item.find("pubDate")

                    title = t_el.text.strip() if t_el is not None and t_el.text else ""
                    link = l_el.text.strip() if l_el is not None and l_el.text else ""
                    raw_desc = d_el.text.strip() if d_el is not None and d_el.text else ""
                    clean_desc = re.sub(r"<[^>]+>", " ", raw_desc)
                    clean_desc = re.sub(r"\s+", " ", clean_desc).strip()
                    pub_date = p_el.text.strip() if p_el is not None and p_el.text else ""

                    if title and link:
                        ts, rel_time = parse_pubdate(pub_date)
                        items.append({
                            "source": src["badge"],
                            "vendor": src["name"],
                            "color": src["color"],
                            "title": title,
                            "link": link,
                            "desc": clean_desc[:350] + ("..." if len(clean_desc) > 350 else ""),
                            "date": pub_date,
                            "timestamp": ts,
                            "rel_time": rel_time
                        })
        except Exception:
            pass
        return items

    def _background_fetch(self):
        fetched = []
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(FEEDS)) as executor:
            results = executor.map(self._fetch_single_feed, FEEDS)
            for res in results:
                fetched.extend(res)

        # Sắp xếp theo dòng thời gian thực: Mới nhất lên trên cùng
        fetched.sort(key=lambda x: x["timestamp"], reverse=True)

        # Gom cụm và khử trùng lặp tin đa nguồn (STT 02)
        clustered = cluster_and_deduplicate(fetched)

        # Đánh chỉ mục trực quan (#01, #02... #N)
        for i, art in enumerate(clustered):
            art["index"] = f"#{i+1:02d}"

        self.call_from_thread(self._update_news_ui, clustered)

    def _update_news_ui(self, articles, is_filtered: bool = False):
        if not is_filtered:
            self.all_articles = list(articles)
        self.articles = articles
        news_list = self.query_one("#news-list", ListView)
        news_list.clear()

        for art in articles:
            combined = art.get("combined_badge", art["source"])
            badge = f"[{art['color']} bold]\\[{combined}][/{art['color']} bold]"
            idx = f"[bold cyan]{art['index']}[/bold cyan]"
            time_str = f"[dim]{art['rel_time']}[/dim]"
            header_line = f"{idx}  {badge}  {time_str}"
            title_line = f"   [bold white]{art['title']}[/bold white]"
            card = Static(f"{header_line}\n{title_line}")
            news_list.append(NewsItem(art, card))

        if articles:
            self._display_article_detail(articles[0])
            news_list.index = 0

    def filter_news(self, keyword: str):
        all_arts = getattr(self, "all_articles", [])
        if not all_arts:
            self.notify("Chưa có danh sách tin tức để lọc!", title="Lọc tin tức", severity="warning")
            return
        kw = keyword.lower().strip()
        matched = [
            a for a in all_arts
            if kw in a.get("title", "").lower()
            or kw in a.get("desc", "").lower()
            or kw in a.get("vendor", "").lower()
            or kw in a.get("source", "").lower()
            or kw in a.get("combined_badge", "").lower()
        ]
        if matched:
            self._update_news_ui(matched, is_filtered=True)
            self.notify(f"Đã lọc: {len(matched)} bài viết khớp với '{keyword}'", title="Lọc Tin Tức")
        else:
            self.notify(f"Không có bài nào chứa từ khóa: '{keyword}'", title="Lọc Tin Tức", severity="warning")

    def reset_news_filter(self):
        all_arts = getattr(self, "all_articles", [])
        if all_arts:
            self._update_news_ui(all_arts, is_filtered=False)
            self.notify("Đã khôi phục toàn bộ danh sách tin tức!", title="Bản Tin")

    def _on_shell_finish(self, cmd: str, output: str, is_error: bool):
        detail_box = self.query_one("#detail-box", Static)
        status_tag = "[red]LỖI[/red]" if is_error else "[green]OK[/green]"
        detail_box.update(
            f"[bold cyan]$ {cmd}[/bold cyan] ({status_tag})\n\n"
            f"[white]{output[:350]}[/white]"
        )
        self.push_screen(CommandResultModal(cmd, output, is_error))
    def on_list_view_highlighted(self, event: ListView.Highlighted):
        if isinstance(event.item, NewsItem):
            art = event.item.article_data
            self._display_article_detail(art)
            
            # Phản ứng thông minh của Kubi khi duyệt bài báo
            full_text = f"{art.get('title', '')} {art.get('desc', '')}"
            cve_m = re.search(r'\b(CVE-\d{4}-\d{4,7})\b', full_text, re.IGNORECASE)
            vendor_low = art.get('vendor', '').lower()
            badge = art.get('badge', '')
            
            if cve_m:
                cve_val = cve_m.group(1).upper()
                self.habitat.react_to_event("cve_found", {"cve": cve_val})
                self.update_mascot_display()
            elif badge == "CISA" or "cisa" in vendor_low:
                self.habitat.react_to_event("cisa_alert")
                self.update_mascot_display()
            elif badge == "Unit42" or "unit 42" in vendor_low:
                self.habitat.react_to_event("unit42_intel")
                self.update_mascot_display()
            elif len(art.get("related_sources", [])) > 0:
                self.habitat.react_to_event("cluster_news")
                self.update_mascot_display()

    def on_list_view_selected(self, event: ListView.Selected):
        if isinstance(event.item, NewsItem):
            link = event.item.article_data.get("link", "")
            if link:
                self.notify(f"Đang mở: {event.item.article_data.get('title', '')[:35]}...", title="Browser")
                subprocess.Popen(["xdg-open", link], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                self.habitat.react_to_event("open_web")
                self.update_mascot_display()
        elif isinstance(event.item, TaskItem):
            self.action_toggle_task()

    def _display_article_detail(self, art: dict):
        detail_box = self.query_one("#detail-box", Static)
        idx = art.get("index", "#01")
        vendor = art.get("vendor", "")
        color = art.get("color", "cyan")
        title = art.get("title", "")
        desc = art.get("desc", "Không có tóm tắt chi tiết.")
        rel_time = art.get("rel_time", "")
        date = art.get("date", "")
        related = art.get("related_sources", [])

        rel_section = ""
        if related:
            rel_lines = []
            for r in related:
                r_vendor = r.get("vendor", "")
                r_badge = r.get("source", "")
                r_color = r.get("color", "cyan")
                r_title = r.get("title", "")
                rel_lines.append(f"  • [{r_color} bold]\\[{r_badge} - {r_vendor}][/{r_color} bold] {r_title}")
            rel_section = "\n[bold magenta]🔗 NGUỒN CÙNG ĐƯA TIN VỀ SỰ KIỆN NÀY:[/bold magenta]\n" + "\n".join(rel_lines) + "\n"

        detail_text = (
            f"[bold cyan]{idx}[/bold cyan] [{color} bold]{vendor}[/{color} bold] [dim]({rel_time} • {date})[/dim]\n"
            f"[bold white]{title}[/bold white]\n"
            f"[yellow]{desc}[/yellow]\n"
            f"{rel_section}"
            f"[bold green]➔ [Enter/o] Mở link gốc │ [v] AI Tóm tắt tiếng Việt │ [x] AI Phân tích chuyên sâu[/bold green]"
        )
        detail_box.update(detail_text)

    def action_refresh_news(self):
        self.notify("Đang tải lại dữ liệu...", title="Refresh")
        self.fetch_all_news()


if __name__ == "__main__":
    app = CyberDashboardApp()
    app.run()
