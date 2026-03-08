# -*- coding: utf-8 -*-
"""
抖音爬虫 GUI 界面  v2.0
- 多关键词拼成一条搜索词同时搜索
- 断点续传（关键词完全相同时复用上次 CSV）
- 爬完后可在 GUI 内一键导出 xlsx（仅国外 / 仅国内 / 全部）
"""
import tkinter as tk
from tkinter import scrolledtext, messagebox
import threading
import sys
import os
import queue
import re as _re
import datetime as _dt

# ── 路径 ─────────────────────────────────────────────────────────────────────
_SRC_DIR = os.path.dirname(os.path.abspath(__file__))
if _SRC_DIR not in sys.path:
    sys.path.insert(0, _SRC_DIR)
_ROOT_DIR = os.path.dirname(_SRC_DIR)
os.chdir(_ROOT_DIR)


# ══════════════════════════════════════════════════════════
#  stdout 重定向
# ══════════════════════════════════════════════════════════
class _QueueWriter:
    def __init__(self, q: queue.Queue):
        self._q = q
    def write(self, text):
        if text:
            self._q.put(text)
    def flush(self):
        pass


# ══════════════════════════════════════════════════════════
#  文件名 / 断点续传工具
# ══════════════════════════════════════════════════════════
def _kw_safe(keywords: list) -> str:
    raw = "+".join(keywords)
    return _re.sub(r'[\\/:*?"<>|]', '_', raw)


def _find_resume_csv(keywords: list) -> str | None:
    """在 cache/ 里查找关键词组合完全相同的最新 CSV，找不到返回 None"""
    folder = os.path.join(_ROOT_DIR, "cache")
    if not os.path.exists(folder):
        return None
    target = _kw_safe(keywords)
    matched = []
    for fname in os.listdir(folder):
        if not fname.endswith("_Result.csv"):
            continue
        body  = fname[:-len("_Result.csv")]
        parts = body.split("_", 2)
        if len(parts) == 3 and parts[2] == target:
            matched.append(os.path.join(folder, fname))
    return sorted(matched)[-1] if matched else None


def _new_csv_path(keywords: list) -> str:
    ts   = _dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    name = f"{ts}_{_kw_safe(keywords)}_Result.csv"
    return os.path.join(_ROOT_DIR, "cache", name)


def _xlsx_from_csv(csv_path: str, suffix: str) -> str:
    """根据 CSV 路径生成对应 xlsx 路径，suffix 是过滤模式标签"""
    base = os.path.basename(csv_path).replace("_Result.csv", f"_Result_{suffix}.xlsx")
    return os.path.join(_ROOT_DIR, "Output", base)


# ══════════════════════════════════════════════════════════
#  颜色常量
# ══════════════════════════════════════════════════════════
BG          = "#1e1e2e"
PANEL       = "#2a2a3d"
ACCENT      = "#7c3aed"
ACCENT_DARK = "#5b21b6"
BTN_GREEN   = "#059669"
BTN_RED     = "#dc2626"
BTN_BLUE    = "#2563eb"
BTN_GRAY    = "#374151"
FG          = "#e2e8f0"
FG_DIM      = "#94a3b8"
LOG_BG      = "#0f172a"
LOG_FG      = "#a3e635"


# ══════════════════════════════════════════════════════════
#  主窗口
# ══════════════════════════════════════════════════════════
class SpiderGUI:

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("抖音用户爬虫  ·  GUI v2.0")
        self.root.configure(bg=BG)
        self.root.resizable(True, True)
        self.root.minsize(960, 660)

        self._running    = False
        self._stop_flag  = threading.Event()
        self._log_q: queue.Queue = queue.Queue()

        # 当前正在使用的 CSV 路径（爬完后导出用）
        self._current_csv: str | None = None

        self._build_ui()
        self._redirect_stdout()
        self._poll_log()
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

    # ─────────────────────────────────────────────────────
    #  构建界面
    # ─────────────────────────────────────────────────────
    def _build_ui(self):
        # 顶部标题
        title_bar = tk.Frame(self.root, bg=ACCENT, height=48)
        title_bar.pack(fill=tk.X)
        title_bar.pack_propagate(False)
        tk.Label(title_bar,
                 text="  🕷  抖音用户爬虫  ·  多关键词同时搜索 + 一键导出",
                 bg=ACCENT, fg="white",
                 font=("微软雅黑", 13, "bold")).pack(side=tk.LEFT, padx=12, pady=8)

        # 主体：左栏 + 右栏日志
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill=tk.BOTH, expand=True, padx=12, pady=10)

        left = tk.Frame(body, bg=PANEL, width=300)
        left.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        left.pack_propagate(False)
        self._build_left(left)

        right = tk.Frame(body, bg=PANEL)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self._build_right(right)

        # 底部状态栏
        self._status_var   = tk.StringVar(value="就绪")
        self._progress_var = tk.StringVar(value="")
        bar = tk.Frame(self.root, bg=BTN_GRAY, height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        tk.Label(bar, textvariable=self._status_var,
                 bg=BTN_GRAY, fg=FG_DIM,
                 font=("微软雅黑", 9)).pack(side=tk.LEFT, padx=10, pady=4)
        tk.Label(bar, textvariable=self._progress_var,
                 bg=BTN_GRAY, fg=ACCENT,
                 font=("微软雅黑", 9, "bold")).pack(side=tk.RIGHT, padx=10, pady=4)

    # ── 左栏 ─────────────────────────────────────────────
    def _build_left(self, parent):

        # ① 关键词区
        tk.Label(parent, text="搜索关键词（多个词同时搜索）",
                 bg=PANEL, fg=FG,
                 font=("微软雅黑", 10, "bold")).pack(anchor="w", padx=12, pady=(10, 4))

        row = tk.Frame(parent, bg=PANEL)
        row.pack(fill=tk.X, padx=12, pady=(0, 4))
        self._kw_entry = tk.Entry(row, font=("微软雅黑", 10),
                                  bg="#3b3b52", fg=FG,
                                  insertbackground=FG,
                                  relief="flat", bd=4)
        self._kw_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self._kw_entry.bind("<Return>", lambda e: self._add_keyword())
        tk.Button(row, text="添加",
                  bg=ACCENT, fg="white",
                  font=("微软雅黑", 9, "bold"),
                  relief="flat", bd=0,
                  activebackground=ACCENT_DARK,
                  cursor="hand2",
                  command=self._add_keyword).pack(side=tk.LEFT, padx=(6, 0))

        lf = tk.Frame(parent, bg=PANEL)
        lf.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 4))
        sb = tk.Scrollbar(lf, orient=tk.VERTICAL, bg=PANEL)
        self._kw_listbox = tk.Listbox(lf,
                                      yscrollcommand=sb.set,
                                      bg="#3b3b52", fg=FG,
                                      selectbackground=ACCENT,
                                      selectforeground="white",
                                      font=("微软雅黑", 10),
                                      relief="flat", bd=0,
                                      activestyle="none")
        sb.config(command=self._kw_listbox.yview)
        sb.pack(side=tk.RIGHT, fill=tk.Y)
        self._kw_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        btn_row = tk.Frame(parent, bg=PANEL)
        btn_row.pack(fill=tk.X, padx=12, pady=(0, 4))
        tk.Button(btn_row, text="删除选中",
                  bg=BTN_GRAY, fg=FG, font=("微软雅黑", 9),
                  relief="flat", bd=0, activebackground="#4b5563",
                  cursor="hand2",
                  command=self._delete_keyword).pack(side=tk.LEFT)
        tk.Button(btn_row, text="清空",
                  bg=BTN_GRAY, fg=FG, font=("微软雅黑", 9),
                  relief="flat", bd=0, activebackground="#4b5563",
                  cursor="hand2",
                  command=self._clear_keywords).pack(side=tk.LEFT, padx=(6, 0))

        # 断点续传提示
        self._resume_var = tk.StringVar(value="")
        tk.Label(parent, textvariable=self._resume_var,
                 bg=PANEL, fg="#fbbf24",
                 font=("微软雅黑", 8),
                 wraplength=268, justify="left").pack(anchor="w", padx=12, pady=(0, 2))

        # ② 分隔线
        tk.Frame(parent, bg="#44445a", height=1).pack(fill=tk.X, padx=12, pady=6)

        # ③ 爬取数量限制
        tk.Label(parent, text="最多爬取博主数量（0 = 不限制）",
                 bg=PANEL, fg=FG,
                 font=("微软雅黑", 10, "bold")).pack(anchor="w", padx=12, pady=(0, 4))
        count_row = tk.Frame(parent, bg=PANEL)
        count_row.pack(fill=tk.X, padx=12, pady=(0, 8))
        self._max_count_var = tk.StringVar(value="0")
        vcmd = parent.register(lambda s: s == "" or s.isdigit())
        self._max_count_entry = tk.Spinbox(
            count_row,
            from_=0, to=99999, increment=10,
            textvariable=self._max_count_var,
            validate="key", validatecommand=(vcmd, "%P"),
            font=("微软雅黑", 11),
            bg="#3b3b52", fg=FG,
            buttonbackground=PANEL,
            insertbackground=FG,
            relief="flat", bd=4,
            width=8,
        )
        self._max_count_entry.pack(side=tk.LEFT)
        tk.Label(count_row, text="个博主",
                 bg=PANEL, fg=FG_DIM,
                 font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(8, 0))

        # ④ 爬取控制
        self._start_btn = tk.Button(parent, text="▶  开始爬取",
                                    bg=BTN_GREEN, fg="white",
                                    font=("微软雅黑", 11, "bold"),
                                    relief="flat", bd=0,
                                    activebackground="#047857",
                                    cursor="hand2", height=2,
                                    command=self._start_spider)
        self._start_btn.pack(fill=tk.X, padx=12, pady=(0, 6))

        self._stop_btn = tk.Button(parent, text="⏹  停止",
                                   bg=BTN_RED, fg="white",
                                   font=("微软雅黑", 11, "bold"),
                                   relief="flat", bd=0,
                                   activebackground="#b91c1c",
                                   cursor="hand2", height=2,
                                   state=tk.DISABLED,
                                   command=self._stop_spider)
        self._stop_btn.pack(fill=tk.X, padx=12, pady=(0, 4))

        # ⑤ 分隔线
        tk.Frame(parent, bg="#44445a", height=1).pack(fill=tk.X, padx=12, pady=6)

        # ⑥ 导出区
        tk.Label(parent, text="导出结果",
                 bg=PANEL, fg=FG,
                 font=("微软雅黑", 10, "bold")).pack(anchor="w", padx=12, pady=(0, 4))

        # 过滤模式选择（单选）
        self._filter_var = tk.StringVar(value="仅国外")
        filter_frame = tk.Frame(parent, bg=PANEL)
        filter_frame.pack(fill=tk.X, padx=12, pady=(0, 6))
        for label in ["仅国外", "仅国内", "全部"]:
            tk.Radiobutton(filter_frame,
                           text=label,
                           variable=self._filter_var,
                           value=label,
                           bg=PANEL, fg=FG,
                           selectcolor="#3b3b52",
                           activebackground=PANEL,
                           activeforeground=FG,
                           font=("微软雅黑", 10)).pack(side=tk.LEFT, padx=(0, 8))

        # 来源 CSV 提示（显示将导出哪个文件）
        self._export_src_var = tk.StringVar(value="⚠️  请先完成爬取，或等待选择来源")
        tk.Label(parent, textvariable=self._export_src_var,
                 bg=PANEL, fg=FG_DIM,
                 font=("微软雅黑", 8),
                 wraplength=268, justify="left").pack(anchor="w", padx=12, pady=(0, 4))

        self._export_btn = tk.Button(parent, text="📤  导出 xlsx",
                                     bg=BTN_BLUE, fg="white",
                                     font=("微软雅黑", 11, "bold"),
                                     relief="flat", bd=0,
                                     activebackground="#1d4ed8",
                                     cursor="hand2", height=2,
                                     state=tk.DISABLED,
                                     command=self._export)
        self._export_btn.pack(fill=tk.X, padx=12, pady=(0, 12))

    # ── 右栏：日志 ───────────────────────────────────────
    def _build_right(self, parent):
        hdr = tk.Frame(parent, bg=PANEL)
        hdr.pack(fill=tk.X, padx=12, pady=(10, 0))
        tk.Label(hdr, text="运行日志",
                 bg=PANEL, fg=FG,
                 font=("微软雅黑", 11, "bold")).pack(side=tk.LEFT)
        tk.Button(hdr, text="清空日志",
                  bg=BTN_GRAY, fg=FG_DIM,
                  font=("微软雅黑", 9), relief="flat", bd=0,
                  activebackground="#4b5563", cursor="hand2",
                  command=self._clear_log).pack(side=tk.RIGHT)

        self._log_text = scrolledtext.ScrolledText(
            parent, bg=LOG_BG, fg=LOG_FG,
            font=("Consolas", 10),
            relief="flat", bd=8,
            state=tk.DISABLED, wrap=tk.WORD)
        self._log_text.pack(fill=tk.BOTH, expand=True, padx=12, pady=(6, 12))
        self._log_text.tag_config("ERROR", foreground="#f87171")
        self._log_text.tag_config("WARN",  foreground="#fbbf24")
        self._log_text.tag_config("INFO",  foreground="#a3e635")
        self._log_text.tag_config("SKIP",  foreground="#60a5fa")
        self._log_text.tag_config("DONE",  foreground="#34d399")

    # ─────────────────────────────────────────────────────
    #  关键词管理
    # ─────────────────────────────────────────────────────
    def _add_keyword(self):
        kw = self._kw_entry.get().strip()
        if not kw:
            return
        if kw in self._get_keywords():
            messagebox.showinfo("提示", f"关键词「{kw}」已在列表中")
            return
        self._kw_listbox.insert(tk.END, kw)
        self._kw_entry.delete(0, tk.END)
        self._on_kw_change()

    def _delete_keyword(self):
        for idx in reversed(self._kw_listbox.curselection()):
            self._kw_listbox.delete(idx)
        self._on_kw_change()

    def _clear_keywords(self):
        if messagebox.askyesno("确认", "清空所有关键词？"):
            self._kw_listbox.delete(0, tk.END)
            self._on_kw_change()

    def _get_keywords(self) -> list:
        return list(self._kw_listbox.get(0, tk.END))

    def _on_kw_change(self):
        """关键词变动时更新断点续传提示"""
        kws = self._get_keywords()
        if not kws:
            self._resume_var.set("")
            return
        existing = _find_resume_csv(kws)
        if existing:
            self._resume_var.set(f"⚡ 断点续传：{os.path.basename(existing)}")
        else:
            self._resume_var.set("🆕 新建文件")

    # ─────────────────────────────────────────────────────
    #  日志
    # ─────────────────────────────────────────────────────
    def _redirect_stdout(self):
        w = _QueueWriter(self._log_q)
        sys.stdout = w
        sys.stderr = w

    def _poll_log(self):
        try:
            while True:
                self._append_log(self._log_q.get_nowait())
        except queue.Empty:
            pass
        self.root.after(150, self._poll_log)

    def _append_log(self, text: str):
        self._log_text.configure(state=tk.NORMAL)
        tl  = text.lower()
        tag = "INFO"
        if "error" in tl or "错误" in tl or "失败" in tl or "traceback" in tl:
            tag = "ERROR"
        elif "warn" in tl or "警告" in tl:
            tag = "WARN"
        elif "跳过" in tl or "已查询" in tl:
            tag = "SKIP"
        elif "完成" in tl or "written" in tl or "获取到用户" in tl or "✅" in text:
            tag = "DONE"
        self._log_text.insert(tk.END, text, tag)
        self._log_text.see(tk.END)
        self._log_text.configure(state=tk.DISABLED)

    def _clear_log(self):
        self._log_text.configure(state=tk.NORMAL)
        self._log_text.delete("1.0", tk.END)
        self._log_text.configure(state=tk.DISABLED)

    # ─────────────────────────────────────────────────────
    #  爬取控制
    # ─────────────────────────────────────────────────────
    def _start_spider(self):
        kws = self._get_keywords()
        if not kws:
            messagebox.showwarning("警告", "请先添加至少一个关键词！")
            return
        if self._running:
            return

        # 确定 CSV 路径（断点续传 or 新建）
        existing = _find_resume_csv(kws)
        if existing:
            csv_path = existing
            print(f"⚡ 断点续传：{os.path.basename(csv_path)}\n")
        else:
            csv_path = _new_csv_path(kws)
            print(f"🆕 新建文件：{os.path.basename(csv_path)}\n")

        self._current_csv = csv_path
        self._update_export_src()

        self._running = True
        self._stop_flag.clear()
        self._start_btn.configure(state=tk.DISABLED)
        self._stop_btn.configure(state=tk.NORMAL)
        self._export_btn.configure(state=tk.DISABLED)
        self._set_status("爬取中…")
        self._set_progress(f"搜索词：{' '.join(kws)}")

        # 读取数量限制
        try:
            max_count = int(self._max_count_var.get() or "0")
        except ValueError:
            max_count = 0

        threading.Thread(
            target=self._run_spider,
            args=(kws, csv_path, max_count),
            daemon=True
        ).start()

    def _stop_spider(self):
        if not self._running:
            return
        self._stop_flag.set()
        self._set_status("正在停止…")
        self._append_log("\n⏹ 用户请求停止…\n")

    def _run_spider(self, kws: list, csv_path: str, max_count: int = 0):
        try:
            from main import run_keywords
            if not self._stop_flag.is_set():
                run_keywords(kws, csv_path,
                             stop_event=self._stop_flag,
                             max_count=max_count)
            if not self._stop_flag.is_set():
                self._set_status("✅ 爬取完成，可导出")
                print("\n✅ 爬取完成！请在左侧选择过滤方式后点击「导出 xlsx」\n")
            else:
                self._set_status("⏹ 已停止，可导出当前结果")
                print("\n⏹ 爬取已停止，可导出已采集的数据\n")
        except Exception as e:
            import traceback
            print(f"[FATAL ERROR] {e}\n{traceback.format_exc()}")
            self._set_status("❌ 出错")
        finally:
            self._running = False
            self._set_progress("")
            self.root.after(0, self._on_spider_done)

    def _on_spider_done(self):
        self._start_btn.configure(state=tk.NORMAL)
        self._stop_btn.configure(state=tk.DISABLED)
        self._running = False
        # 有数据才启用导出按钮（无论是正常完成还是手动停止）
        if self._current_csv and os.path.exists(self._current_csv):
            self._export_btn.configure(state=tk.NORMAL)
        self._on_kw_change()

    # ─────────────────────────────────────────────────────
    #  导出
    # ─────────────────────────────────────────────────────
    def _update_export_src(self):
        if self._current_csv:
            self._export_src_var.set(f"来源：{os.path.basename(self._current_csv)}")
        else:
            self._export_src_var.set("⚠️  请先完成爬取，或等待选择来源")

    def _export(self):
        if not self._current_csv:
            messagebox.showwarning("警告", "没有可导出的数据，请先运行爬虫！")
            return
        if not os.path.exists(self._current_csv):
            messagebox.showerror("错误", f"CSV 文件不存在：\n{self._current_csv}")
            return

        mode = self._filter_var.get()           # "仅国外" / "仅国内" / "全部"
        suffix_map = {"仅国外": "国外", "仅国内": "国内", "全部": "全部"}
        xlsx_path = _xlsx_from_csv(self._current_csv, suffix_map[mode])

        self._export_btn.configure(state=tk.DISABLED)
        self._set_status("导出中…")

        threading.Thread(
            target=self._run_export,
            args=(self._current_csv, xlsx_path, mode),
            daemon=True
        ).start()

    def _run_export(self, csv_path: str, xlsx_path: str, mode: str):
        try:
            from change_data import export
            ok = export(csv_path, xlsx_path, mode)
            if ok:
                self._set_status("✅ 导出完成")
            else:
                self._set_status("⚠️  导出：无匹配数据")
        except Exception as e:
            import traceback
            print(f"[导出错误] {e}\n{traceback.format_exc()}")
            self._set_status("❌ 导出出错")
        finally:
            self.root.after(0, lambda: self._export_btn.configure(state=tk.NORMAL))

    # ─────────────────────────────────────────────────────
    #  状态栏
    # ─────────────────────────────────────────────────────
    def _set_status(self, text: str):
        self.root.after(0, lambda: self._status_var.set(text))

    def _set_progress(self, text: str):
        self.root.after(0, lambda: self._progress_var.set(text))

    # ─────────────────────────────────────────────────────
    #  关闭
    # ─────────────────────────────────────────────────────
    def _on_close(self):
        if self._running:
            if not messagebox.askyesno("确认退出", "爬虫正在运行，确定要退出吗？\n（将发送停止信号后关闭窗口）"):
                return
            self._stop_flag.set()
        try:
            self.root.destroy()
        except Exception:
            pass


# ══════════════════════════════════════════════════════════
#  入口
# ══════════════════════════════════════════════════════════
def main():
    root = tk.Tk()
    SpiderGUI(root)
    root.update_idletasks()
    w, h = 1020, 700
    sw, sh = root.winfo_screenwidth(), root.winfo_screenheight()
    root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    root.mainloop()


if __name__ == "__main__":
    main()

