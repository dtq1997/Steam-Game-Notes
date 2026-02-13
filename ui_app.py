"""GUI 界面 — SteamNotesApp 主窗口框架、游戏列表、Cloud 管理"""

import json
import os
import platform
import re
import string
import threading
import time
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox, ttk, simpledialog
import tkinter.font as tkfont
from datetime import datetime

from core import (
    NOTES_APPID,
    AI_NOTE_PREFIX,
    AI_NOTE_LEGACY_KEYWORD,
    CONFIDENCE_EMOJI,
    INFO_VOLUME_EMOJI,
    QUALITY_EMOJI,
    INFO_SOURCE_WEB,
    INFO_SOURCE_LOCAL,
    INSUFFICIENT_INFO_MARKER,
    is_ai_note,
    extract_ai_model_from_note,
    extract_ai_confidence_from_note,
    extract_ai_info_volume_from_note,
    extract_ai_info_source_from_note,
    extract_ai_quality_from_note,
    is_insufficient_info_note,
    SteamNotesManager,
)
from account_manager import SteamAccountScanner
from cloud_uploader import SteamCloudUploader
from ai_generator import (
    SteamAIGenerator,
    AI_SYSTEM_PROMPT,
    AI_WEB_SEARCH_ADDENDUM,
)
from rich_text_editor import SteamRichTextEditor
from ui_notes_viewer import NotesViewerMixin
from ui_ai_batch import AIBatchMixin
from ui_import_export import ImportExportMixin
from ui_settings import SettingsMixin

from rich_text_editor import SteamRichTextEditor
from steam_data import get_game_name_from_steam


# ═══════════════════════════════════════════════════════════════════════════════
#  主应用类
# ═══════════════════════════════════════════════════════════════════════════════

class SteamNotesApp(NotesViewerMixin, AIBatchMixin, ImportExportMixin, SettingsMixin):
    """Steam 笔记管理器 GUI"""

    # API Key 配置文件路径（跨平台）
    _CONFIG_DIR = os.path.join(os.path.expanduser("~"), ".steam_notes_gen")
    _CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.json")

    def __init__(self):
        self.current_account = None
        self.accounts = []
        self.manager = None  # SteamNotesManager
        self.cloud_uploader = None  # SteamCloudUploader
        self.root = None
        self._games_data = []
        self._game_name_cache = {}  # {app_id: name} — 缓存在线解析的游戏名
        self._game_name_cache_loaded = False
        self._config = self._load_config()

    @classmethod
    def _load_config(cls) -> dict:
        """从配置文件加载已保存的设置"""
        try:
            if os.path.exists(cls._CONFIG_FILE):
                with open(cls._CONFIG_FILE, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception:
            pass
        return {}

    @classmethod
    def _save_config(cls, config: dict):
        """保存设置到配置文件"""
        try:
            os.makedirs(cls._CONFIG_DIR, exist_ok=True)
            with open(cls._CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _get_saved_key(self, key_name: str) -> str:
        """获取已保存的 API Key"""
        return self._config.get(key_name, "")

    def _set_saved_key(self, key_name: str, value: str):
        """保存 API Key 到配置文件"""
        if value:
            self._config[key_name] = value
        elif key_name in self._config:
            del self._config[key_name]
        self._save_config(self._config)

    def _clear_saved_key(self, key_name: str):
        """清除已保存的 API Key"""
        if key_name in self._config:
            del self._config[key_name]
            self._save_config(self._config)

    def _get_ai_tokens(self) -> list:
        """获取已保存的 AI 令牌列表（含向后兼容）
        每个令牌: {name, key, provider, model, api_url}
        """
        tokens = self._config.get("ai_tokens", [])
        if tokens:
            return tokens
        # 向后兼容：从旧的单 key 配置迁移
        old_key = (self._config.get("ai_api_key") or
                   self._config.get("anthropic_api_key") or "")
        if old_key:
            prov = self._config.get("ai_provider", "anthropic")
            pinfo = SteamAIGenerator.PROVIDERS.get(prov, {})
            return [{
                "name": pinfo.get("name", prov),
                "key": old_key,
                "provider": prov,
                "model": self._config.get("ai_model", pinfo.get("default_model", "")),
                "api_url": self._config.get("ai_api_url", ""),
            }]
        return []

    def _save_ai_tokens(self, tokens: list, active_index: int = 0):
        """保存 AI 令牌列表到配置文件"""
        self._config["ai_tokens"] = tokens
        self._config["ai_active_token_index"] = active_index
        # 同步旧字段（保持向后兼容）
        if tokens and 0 <= active_index < len(tokens):
            t = tokens[active_index]
            self._config["ai_api_key"] = t.get("key", "")
            self._config["anthropic_api_key"] = t.get("key", "")
            self._config["ai_provider"] = t.get("provider", "anthropic")
            self._config["ai_model"] = t.get("model", "")
            self._config["ai_api_url"] = t.get("api_url", "")
        self._save_config(self._config)

    def _get_active_token_index(self) -> int:
        return self._config.get("ai_active_token_index", 0)

    def set_current_account(self, account):
        """设置当前账号"""
        self.current_account = account
        # 从配置中加载该账号的上传哈希
        fc = account.get('friend_code', '')
        hashes = self._config.get(f"uploaded_hashes_{fc}", {})
        self.manager = SteamNotesManager(
            account['notes_dir'], self.cloud_uploader,
            uploaded_hashes=hashes)
        # 切换账号时清空游戏名称缓存
        self._game_name_cache = {}
        self._game_name_cache_loaded = False

    def _save_uploaded_hashes(self):
        """持久化当前账号的上传哈希到配置文件"""
        if not self.current_account or not self.manager:
            return
        fc = self.current_account.get('friend_code', '')
        self._config[f"uploaded_hashes_{fc}"] = self.manager.get_uploaded_hashes()
        self._save_config(self._config)

    # ────────────────────── 启动流程 ──────────────────────

    def run(self):
        """主入口"""
        self.accounts = SteamAccountScanner.scan_accounts()

        if not self.accounts:
            self._show_no_account_ui()
        elif len(self.accounts) == 1:
            self.set_current_account(self.accounts[0])
            self._show_main_window()
        else:
            self._show_account_selector()

    def _show_no_account_ui(self):
        """未找到账号时的界面"""
        root = tk.Tk()
        root.title("Steam 笔记管理器")
        root.resizable(False, False)

        tk.Label(root, text="❌ 未找到 Steam 账号",
                 font=("", 14, "bold"), fg="red").pack(pady=20)
        tk.Label(root, text=(
            "请确保:\n"
            "1. Steam 已安装\n"
            "2. 至少登录过一个 Steam 账号\n"
            "3. 若 Steam 安装在非默认路径，请手动指定"
        ), font=("", 10), justify=tk.LEFT).pack(padx=30, pady=10)

        def manual_select():
            path = filedialog.askdirectory(title="选择 Steam 安装目录（含 userdata 的那个）")
            if path and os.path.exists(path):
                userdata = os.path.join(path, "userdata")
                if not os.path.exists(userdata):
                    messagebox.showerror("错误", "该目录下没有 userdata 文件夹。")
                    return
                for entry in os.listdir(userdata):
                    ep = os.path.join(userdata, entry)
                    if os.path.isdir(ep) and entry.isdigit():
                        notes_dir = os.path.join(ep, NOTES_APPID, "remote")
                        persona = SteamAccountScanner._get_persona_name(ep, entry)
                        nc = 0
                        if os.path.exists(notes_dir):
                            nc = len([f for f in os.listdir(notes_dir)
                                      if f.startswith("notes_")])
                        self.accounts.append({
                            'friend_code': entry,
                            'userdata_path': ep,
                            'notes_dir': notes_dir,
                            'persona_name': persona,
                            'steam_path': path,
                            'notes_count': nc,
                        })
                if self.accounts:
                    root.destroy()
                    if len(self.accounts) == 1:
                        self.set_current_account(self.accounts[0])
                        self._show_main_window()
                    else:
                        self._show_account_selector()
                else:
                    messagebox.showerror("错误", "该目录下未找到有效的 Steam 账号。")

        ttk.Button(root, text="📂 手动选择 Steam 目录", command=manual_select).pack(pady=20)
        self._center_window(root)
        root.mainloop()

    def _show_account_selector(self):
        """多账号选择界面"""
        sel = tk.Tk()
        sel.title("选择 Steam 账号")
        sel.resizable(False, False)

        tk.Label(sel, text="🎮 检测到多个 Steam 账号",
                 font=("", 12, "bold")).pack(pady=(20, 10))
        tk.Label(sel, text="请选择要管理笔记的账号：", font=("", 10)).pack()

        list_frame = tk.Frame(sel)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        listbox = tk.Listbox(list_frame, width=60, height=min(10, len(self.accounts)),
                             font=("", 10))
        listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        listbox.config(yscrollcommand=scrollbar.set)

        for acc in self.accounts:
            listbox.insert(tk.END,
                           f"{acc['persona_name']}  |  ID: {acc['friend_code']}  "
                           f"|  📝 {acc['notes_count']} 个游戏有笔记")

        listbox.selection_set(0)

        def on_select():
            idx = listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请选择一个账号。")
                return
            self.set_current_account(self.accounts[idx[0]])
            sel.destroy()
            self._show_main_window()

        ttk.Button(sel, text="✅ 确认选择", command=on_select).pack(pady=15)
        self._center_window(sel)
        sel.mainloop()

    # ────────────────────── 主界面 ──────────────────────

    def _show_main_window(self):
        """主功能窗口"""
        self.root = tk.Tk()
        self.root.title("Steam 笔记管理器")
        root = self.root

        # ── 顶部: 账号信息栏 ──
        acc_frame = tk.Frame(root, bg="#4a90d9", pady=6)
        acc_frame.pack(fill=tk.X)

        acc_info = (f"👤 {self.current_account['persona_name']}  |  "
                    f"ID: {self.current_account['friend_code']}  |  "
                    f"📂 .../{NOTES_APPID}/remote/")
        tk.Label(acc_frame, text=acc_info, font=("", 11, "bold"),
                 bg="#4a90d9", fg="white").pack(side=tk.LEFT, padx=15)

        if len(self.accounts) > 1:
            def switch():
                root.destroy()
                self._show_account_selector()
            tk.Button(acc_frame, text="🔄 切换账号", command=switch,
                      font=("", 9)).pack(side=tk.RIGHT, padx=15)

        # ── 主体: 左笔记列表 + 右控制区 ──
        main = tk.Frame(root)
        main.pack(fill=tk.BOTH, expand=True)

        # ═══════ 左侧: 笔记列表（主视图） ═══════
        left = tk.Frame(main, bg="#f0f0f0", padx=8, pady=8)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0), pady=8)

        tk.Label(left, text="📝 游戏笔记列表", font=("", 11, "bold"),
                 bg="#f0f0f0").pack(anchor=tk.W)

        # ── 搜索栏 ──
        search_frame = tk.Frame(left, bg="#f0f0f0")
        search_frame.pack(fill=tk.X, pady=(4, 0))

        self._main_search_var = tk.StringVar()
        self._main_search_mode = tk.StringVar(value="name")

        tk.Radiobutton(search_frame, text="名称/ID", variable=self._main_search_mode,
                        value="name", font=("", 8), bg="#f0f0f0",
                        command=lambda: self._on_main_search_changed()
                        ).pack(side=tk.LEFT)
        tk.Radiobutton(search_frame, text="笔记内容", variable=self._main_search_mode,
                        value="content", font=("", 8), bg="#f0f0f0",
                        command=lambda: self._on_main_search_changed()
                        ).pack(side=tk.LEFT)
        search_entry = ttk.Entry(search_frame, textvariable=self._main_search_var, width=18)
        search_entry.pack(side=tk.LEFT, padx=(4, 0), fill=tk.X, expand=True)
        self._main_search_var.trace_add("write", lambda *_: self._on_main_search_changed())

        # 紧凑工具栏
        toolbar = tk.Frame(left, bg="#f0f0f0")
        toolbar.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(toolbar, text="✅全选", width=6,
                   command=self._select_all_games).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="📋ID", width=5,
                   command=self._copy_selected_appid).pack(side=tk.LEFT, padx=(0, 2))
        self._upload_sel_btn = ttk.Button(toolbar, text="☁️选中", width=7,
                                           command=self._cloud_upload_selected)
        self._upload_sel_btn.pack(side=tk.LEFT, padx=(0, 2))
        self._upload_all_btn = ttk.Button(toolbar, text="☁️全部", width=9,
                                           command=self._cloud_upload_all)
        self._upload_all_btn.pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(toolbar, text="📤导出", width=6,
                   command=self._ui_export_dialog).pack(side=tk.LEFT, padx=(0, 2))

        # 筛选行1: 有改动勾选 + AI 状态 + 模型二级筛选
        filter_frame1 = tk.Frame(left, bg="#f0f0f0")
        filter_frame1.pack(fill=tk.X, pady=(4, 0))

        self._dirty_filter_var = tk.BooleanVar(value=False)
        tk.Checkbutton(filter_frame1, text="⬆有改动", variable=self._dirty_filter_var,
                        font=("", 8), bg="#f0f0f0",
                        command=lambda: self._refresh_games_list()
                        ).pack(side=tk.LEFT)

        self._uploading_filter_var = tk.BooleanVar(value=False)
        tk.Checkbutton(filter_frame1, text="☁️⬆上传中", variable=self._uploading_filter_var,
                        font=("", 8), bg="#f0f0f0",
                        command=lambda: self._refresh_games_list()
                        ).pack(side=tk.LEFT)

        self._ai_filter_var = tk.StringVar(value="全部")
        self._ai_filter_combo = ttk.Combobox(
            filter_frame1, textvariable=self._ai_filter_var, width=12,
            values=["全部", "🤖 AI 处理过", "📝 未 AI 处理",
                    "⛔ 信息过少"], state='readonly')
        self._ai_filter_combo.pack(side=tk.LEFT, padx=(4, 0))
        self._ai_filter_combo.bind("<<ComboboxSelected>>",
                                    lambda e: self._on_filter_changed())

        # 模型二级筛选（仅"AI 处理过"时可见）
        self._model_filter_var = tk.StringVar(value="全部")
        self._model_filter_combo = ttk.Combobox(
            filter_frame1, textvariable=self._model_filter_var, width=14,
            values=["全部"], state='readonly')
        self._model_filter_combo.bind("<<ComboboxSelected>>",
                                       lambda e: self._refresh_games_list())
        self._model_filter_visible = False

        # 筛选行2: 信息来源 + 确信度 + 信息量
        filter_frame2 = tk.Frame(left, bg="#f0f0f0")
        filter_frame2.pack(fill=tk.X, pady=(2, 0))

        self._source_filter_var = tk.StringVar(value="全部")
        self._source_filter_combo = ttk.Combobox(
            filter_frame2, textvariable=self._source_filter_var, width=8,
            values=["全部", "📡 联网", "📚 本地"], state='readonly')
        self._source_filter_combo.pack(side=tk.LEFT)
        self._source_filter_combo.bind("<<ComboboxSelected>>",
                                        lambda e: self._refresh_games_list())

        self._conf_filter_var = tk.StringVar(value="全部确信度")
        self._conf_filter_combo = ttk.Combobox(
            filter_frame2, textvariable=self._conf_filter_var, width=10,
            values=["全部确信度", "很高", "较高", "中等", "较低", "很低"], state='readonly')
        self._conf_filter_combo.pack(side=tk.LEFT, padx=(3, 0))
        self._conf_filter_combo.bind("<<ComboboxSelected>>",
                                      lambda e: self._refresh_games_list())

        # 第三行筛选：信息量 + 质量（避免单行过多控件溢出）
        filter_frame3 = tk.Frame(left, bg="#f0f0f0")
        filter_frame3.pack(fill=tk.X, pady=(2, 0))

        self._vol_filter_var = tk.StringVar(value="全部信息量")
        self._vol_filter_combo = ttk.Combobox(
            filter_frame3, textvariable=self._vol_filter_var, width=10,
            values=["全部信息量", "相当多", "较多", "中等", "较少", "相当少"], state='readonly')
        self._vol_filter_combo.pack(side=tk.LEFT)
        self._vol_filter_combo.bind("<<ComboboxSelected>>",
                                     lambda e: self._refresh_games_list())

        self._qual_filter_var = tk.StringVar(value="全部质量")
        self._qual_filter_combo = ttk.Combobox(
            filter_frame3, textvariable=self._qual_filter_var, width=10,
            values=["全部质量", "💎相当好", "✨较好", "➖中等", "👎较差", "💀相当差"], state='readonly')
        self._qual_filter_combo.pack(side=tk.LEFT, padx=(3, 0))
        self._qual_filter_combo.bind("<<ComboboxSelected>>",
                                      lambda e: self._refresh_games_list())

        # 提示
        tk.Label(left, text="🤖=AI 🟢🔵🟡🟠🔴=确信度 💎✨➖👎💀=质量 📡=联网 📚=本地 ⬆=改动 ☁️⬆=上传中 ⛔=信息过少",
                 font=("", 8), fg="#555", bg="#f0f0f0",
                 wraplength=380, justify=tk.LEFT).pack(anchor=tk.W, pady=(3, 0))

        list_container = tk.Frame(left, bg="#f0f0f0")
        list_container.pack(fill=tk.BOTH, expand=True, pady=(5, 5))

        # 使用 Treeview 实现高性能列表（多选模式）
        style = ttk.Style()
        style.configure("GameList.Treeview", rowheight=24, font=("", 9))
        self._games_tree = ttk.Treeview(
            list_container, columns=("notes",), show="tree",
            style="GameList.Treeview", selectmode="extended", height=20)
        self._games_tree.column("#0", width=320, minwidth=200)
        self._games_tree.column("notes", width=45, minwidth=35, anchor=tk.CENTER)
        self._games_tree.tag_configure("dirty", foreground="#b8860b", background="#fffff0")
        self._games_tree.tag_configure("uploading", foreground="#2e7d32", background="#e8f5e9")
        self._games_tree.tag_configure("ai", foreground="#1a73e8")
        self._games_tree.tag_configure("insufficient", foreground="#cc3333", background="#fff5f5")
        self._games_tree.tag_configure("normal", foreground="#333")
        self._games_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        tree_scroll = ttk.Scrollbar(list_container, orient=tk.VERTICAL,
                                     command=self._games_tree.yview)
        tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self._games_tree.config(yscrollcommand=tree_scroll.set)

        # 双击查看
        self._games_tree.bind("<Double-1>", lambda e: self._on_tree_double_click())
        # 右键菜单
        self._games_tree.bind("<Button-2>" if platform.system() == "Darwin" else "<Button-3>",
                              self._on_tree_right_click)

        # 选中状态
        self._selected_game_idx = None

        btn_bottom = tk.Frame(left, bg="#f0f0f0")
        btn_bottom.pack(fill=tk.X, pady=(5, 0))
        ttk.Button(btn_bottom, text="🔄 刷新", width=8,
                   command=self._force_refresh_games_list).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_bottom, text="📋 查看", width=8,
                   command=self._ui_view_selected).pack(side=tk.LEFT, padx=2)

        # ═══════ 右侧: 控制面板 ═══════
        right = tk.Frame(main, padx=4, pady=8)
        right.pack(side=tk.RIGHT, fill=tk.Y, padx=(0, 6), pady=8)

        # ── Cloud 状态（单行） ──
        self._cloud_status_frame = tk.Frame(right)
        self._cloud_status_frame.pack(fill=tk.X)

        self._cloud_status_text = tk.Text(self._cloud_status_frame, font=("", 10), height=1,
                                          width=30,
                                          bg=root.cget("bg"), relief=tk.FLAT, wrap=tk.WORD)
        self._cloud_status_text.tag_config("red", foreground="red", font=("", 10, "bold"))
        self._cloud_status_text.tag_config("green", foreground="green", font=("", 10, "bold"))
        self._cloud_status_text.tag_config("gray", foreground="#888")
        self._cloud_status_text.pack(fill=tk.X)

        self._cloud_connect_btn = ttk.Button(right, text="☁️ 连接 Steam Cloud",
                                              command=self._toggle_cloud_connection)
        self._cloud_connect_btn.pack(anchor=tk.W, pady=(2, 6))

        self._update_cloud_status_display()

        # ── 功能按钮 ──
        style = ttk.Style()
        style.configure("TButton", font=("", 10), padding=6)

        btn_row1 = tk.Frame(right)
        btn_row1.pack(fill=tk.X, pady=(0, 3))
        ttk.Button(btn_row1, text="📝 新建", width=7,
                   command=self._ui_create_note).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(btn_row1, text="📋 查看", width=7,
                   command=self._ui_view_notes).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row1, text="🗑️ 删除", width=7,
                   command=self._ui_delete_notes).pack(side=tk.LEFT, padx=2)

        btn_row2 = tk.Frame(right)
        btn_row2.pack(fill=tk.X, pady=3)
        ttk.Button(btn_row2, text="📥 导入", width=7,
                   command=self._ui_import).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(btn_row2, text="📂 目录", width=7,
                   command=self._ui_open_dir).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_row2, text="🔑 AI 配置", width=7,
                   command=self._ui_api_key_settings).pack(side=tk.LEFT, padx=2)

        btn_row3 = tk.Frame(right)
        btn_row3.pack(fill=tk.X, pady=(3, 3))
        ttk.Button(btn_row3, text="🤖 AI 批量生成", width=11,
                   command=self._ui_ai_batch_generate).pack(side=tk.LEFT, padx=(0, 2))
        ttk.Button(btn_row3, text="🔍 去重", width=6,
                   command=self._ui_dedup_notes).pack(side=tk.LEFT, padx=2)

        # ── 路径信息 + 关于 ──
        bottom_row = tk.Frame(right)
        bottom_row.pack(fill=tk.X, pady=(4, 0))
        path_label = tk.Label(bottom_row, text=f"📂 {self.current_account['notes_dir']}",
                              font=("", 8), fg="#888", cursor="hand2", anchor=tk.W,
                              wraplength=180)
        path_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        path_label.bind("<Button-1>", lambda e: self._ui_open_dir())
        ttk.Button(bottom_row, text="ℹ️ 关于", width=5,
                   command=self._ui_show_about).pack(side=tk.RIGHT)
        ttk.Button(bottom_row, text="🗑️ 缓存", width=5,
                   command=self._ui_manage_cache).pack(side=tk.RIGHT, padx=(0, 3))

        # ── 游戏名称加载进度条 ──
        self._name_progress_frame = tk.Frame(right)
        self._name_progress_frame.pack(fill=tk.X, pady=(2, 0))
        self._name_progress_label = tk.Label(
            self._name_progress_frame,
            text="📥 正在获取游戏名称...", font=("", 8), fg="#666", anchor=tk.W)
        self._name_progress_label.pack(fill=tk.X)
        self._name_progress_bar = ttk.Progressbar(
            self._name_progress_frame, mode='indeterminate', length=180)
        self._name_progress_bar.pack(fill=tk.X)
        self._name_progress_bar.start(15)

        # 初始加载 — 先用缓存快速刷新，再后台加载全量名称
        self._refresh_games_list_fast()
        # 如果已有持久化缓存且未过期，隐藏进度条
        bulk_cache_ts = self._config.get("game_name_bulk_cache_ts", 0)
        if self._config.get("game_name_cache", {}) and (time.time() - bulk_cache_ts < 86400):
            self._name_progress_frame.pack_forget()

        # 后台加载全量游戏名称缓存 + 解析未知名称
        threading.Thread(target=self._bg_init_game_names, daemon=True).start()

        # 启动 Steam 进程监控定时器
        self._steam_monitor_id = None
        self._start_steam_monitor()

        self._center_window(root)
        root.mainloop()

    # ────────────────────── Steam 进程监控 ──────────────────────

    def _start_steam_monitor(self):
        """启动后台定时器，每 5 秒检测 Steam 是否在运行"""
        self._check_steam_alive()

    def _check_steam_alive(self):
        """定时检测 Steam 进程，若 Cloud 已连接但 Steam 不在则自动断开；
        同时检测子进程是否意外退出。"""
        if self.cloud_uploader and self.cloud_uploader.initialized:
            # 检测子进程是否意外退出
            if not self.cloud_uploader.is_alive():
                self.cloud_uploader.initialized = False
                self.cloud_uploader.logged_in_friend_code = None
                self.cloud_uploader = None
                self.manager.cloud_uploader = None
                self._update_cloud_status_display()
            elif not SteamCloudUploader.is_steam_running():
                # Steam 已关闭，自动断开 Cloud
                self.cloud_uploader.shutdown()
                self.cloud_uploader = None
                self.manager.cloud_uploader = None
                self._update_cloud_status_display()
        # 5 秒后再次检测
        try:
            self._steam_monitor_id = self.root.after(5000, self._check_steam_alive)
        except Exception:
            pass  # root 已销毁

    # ────────────────────── 右侧列表操作 ──────────────────────

    def _ensure_game_name_cache(self, force=False, progress_callback=None):
        """确保游戏名称缓存已加载 — 持久化 + 全量列表 + 本地扫描 + 后台补全"""
        if self._game_name_cache_loaded and not force:
            return
        # 1. 从配置文件加载已持久化的名称缓存
        persisted = self._config.get("game_name_cache", {})
        self._game_name_cache = dict(persisted)
        # 2. 尝试从 ISteamApps/GetAppList/v2/ 获取全量名称列表（无需 API Key）
        #    此列表约 15 万条，覆盖几乎所有 Steam 应用
        #    使用单独的缓存键来避免每次启动都重新请求
        bulk_cache_ts = self._config.get("game_name_bulk_cache_ts", 0)
        now = time.time()
        # 每 24 小时更新一次全量列表
        if now - bulk_cache_ts > 86400 or not persisted:
            try:
                # 使用已有缓存数作为估计总数
                est_total = len(persisted) if persisted else 0
                bulk_names = SteamAccountScanner.fetch_all_steam_app_names(
                    api_key=self._config.get("steam_web_api_key", ""),
                    progress_callback=progress_callback,
                    estimated_total=est_total)
                if bulk_names:
                    self._game_name_cache.update(bulk_names)
                    self._config["game_name_bulk_cache_ts"] = now
                    print(f"[游戏名称] 全量列表已更新: {len(bulk_names)} 条")
            except Exception as e:
                print(f"[游戏名称] 全量列表获取失败: {e}")
        # 3. 本地扫描（已安装游戏，可能有更准确的本地化名称）
        try:
            library_games = SteamAccountScanner.scan_library(
                self.current_account['steam_path'])
            for g in library_games:
                self._game_name_cache[g['app_id']] = g['name']
        except Exception:
            pass
        # 4. 持久化合并后的缓存
        self._persist_name_cache()
        self._game_name_cache_loaded = True

    def _ensure_game_name_cache_fast(self):
        """仅从持久化缓存快速加载游戏名称（不做任何网络请求），用于启动时快速显示"""
        if self._game_name_cache_loaded:
            return
        persisted = self._config.get("game_name_cache", {})
        if persisted:
            self._game_name_cache = dict(persisted)
            # 标记为"部分加载"——不设 _game_name_cache_loaded，后台线程会做完整加载
        # 本地扫描很快，也做一下
        try:
            library_games = SteamAccountScanner.scan_library(
                self.current_account['steam_path'])
            for g in library_games:
                self._game_name_cache[g['app_id']] = g['name']
        except Exception:
            pass

    def _refresh_games_list_fast(self):
        """启动时快速刷新列表：仅使用持久化缓存，不做网络请求"""
        self._ensure_game_name_cache_fast()
        self._refresh_games_list()

    def _bg_init_game_names(self):
        """后台线程：完整加载游戏名称缓存（含网络请求），完成后刷新列表"""
        def _on_progress(fetched, page, is_done, estimated_total=0):
            """在主线程更新进度条"""
            try:
                self.root.after(0, lambda: self._update_name_progress(
                    fetched, page, is_done, estimated_total))
            except Exception:
                pass
        try:
            self._ensure_game_name_cache(force=False, progress_callback=_on_progress)
            # 完整缓存已加载，隐藏进度条并刷新列表
            try:
                self.root.after(0, lambda: self._hide_name_progress())
                self.root.after(0, lambda: self._refresh_games_list())
            except Exception:
                pass
            # 继续解析仍缺失的名称
            self._bg_resolve_missing_names()
        except Exception as e:
            print(f"[后台] 游戏名称初始化失败: {e}")
            try:
                self.root.after(0, lambda: self._hide_name_progress())
            except Exception:
                pass

    def _update_name_progress(self, fetched, page, is_done, estimated_total=0):
        """更新游戏名称获取进度条（主线程调用）"""
        try:
            if is_done:
                self._name_progress_label.config(
                    text=f"✅ 已获取 {fetched} 个游戏名称（已缓存到本地，下次启动无需重新获取）")
                self._name_progress_bar.stop()
                self._name_progress_bar.config(mode='determinate', value=100)
            else:
                if estimated_total > 0:
                    pct = min(int(fetched / estimated_total * 100), 99)
                    self._name_progress_label.config(
                        text=f"📥 正在获取游戏名称... {fetched} / ~{estimated_total}（第 {page} 页）")
                    self._name_progress_bar.stop()
                    self._name_progress_bar.config(mode='determinate', value=pct)
                else:
                    self._name_progress_label.config(
                        text=f"📥 正在获取游戏名称... 已获取 {fetched} 个（第 {page} 页）")
            self._name_progress_frame.pack(fill=tk.X, pady=(2, 0))
        except Exception:
            pass

    def _hide_name_progress(self):
        """隐藏游戏名称获取进度条"""
        try:
            self._name_progress_frame.pack_forget()
        except Exception:
            pass

    def _persist_name_cache(self):
        """将游戏名称缓存持久化到配置文件"""
        self._config["game_name_cache"] = dict(self._game_name_cache)
        self._save_config(self._config)

    def _bg_resolve_missing_names(self):
        """后台线程：解析仍显示为 AppID 的游戏名称
        优先使用全量列表缓存，仅对缓存中也找不到的才逐个调 Store API"""
        games = self.manager.list_all_games()
        missing = [g['app_id'] for g in games
                   if g['app_id'] not in self._game_name_cache]
        if not missing:
            return
        # 先尝试批量获取（如果缓存中不够）
        resolved_any = False
        bulk_names = SteamAccountScanner.fetch_all_steam_app_names(
            api_key=self._config.get("steam_web_api_key", ""))
        if bulk_names:
            for aid in missing:
                if aid in bulk_names:
                    self._game_name_cache[aid] = bulk_names[aid]
                    resolved_any = True
            # 更新 missing 列表
            missing = [aid for aid in missing
                       if aid not in self._game_name_cache]
        # 对仍缺失的逐个调 Store API
        for aid in missing:
            try:
                name = get_game_name_from_steam(aid)
                if name and not name.startswith("AppID "):
                    self._game_name_cache[aid] = name
                    resolved_any = True
                time.sleep(0.3)  # 避免请求过快
            except Exception:
                pass
        if resolved_any:
            self._persist_name_cache()
            # 在主线程刷新列表
            try:
                self.root.after(0, lambda: self._refresh_games_list())
            except Exception:
                pass

    def _get_game_name(self, app_id: str) -> str:
        """获取游戏名称，优先缓存，否则返回 AppID"""
        return self._game_name_cache.get(app_id, f"AppID {app_id}")

    def _parse_remotecache_syncstates(self) -> dict:
        """解析 remotecache.vdf 获取每个笔记文件的 syncstate
        返回 {app_id: syncstate_int}，例如 {'570': 3} 表示 notes_570 正在上传
        syncstate=1 表示已同步，syncstate=3 表示上传中
        """
        if not self.current_account:
            return {}
        notes_dir = self.current_account.get('notes_dir', '')
        vdf_path = os.path.join(os.path.dirname(notes_dir), 'remotecache.vdf')
        if not os.path.isfile(vdf_path):
            return {}
        try:
            with open(vdf_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
        except Exception:
            return {}
        # 简易 VDF 解析：提取每个 "notes_<appid>" 块中的 "syncstate" 值
        result = {}
        # 找所有 notes_XXX 的块
        block_pat = re.compile(
            r'"(notes_(?:shortcut_)?[^"]+)"\s*\{([^}]*)\}', re.DOTALL)
        sync_pat = re.compile(r'"syncstate"\s+"(\d+)"')
        for m in block_pat.finditer(content):
            fname = m.group(1)  # e.g. "notes_570"
            block = m.group(2)
            sm = sync_pat.search(block)
            if sm:
                syncstate = int(sm.group(1))
                # 从文件名提取 app_id（与 list_all_games 一致，去掉 notes_ 前缀）
                if fname.startswith("notes_"):
                    aid = fname[6:]  # "notes_570" → "570", "notes_shortcut_X" → "shortcut_X"
                else:
                    continue
                result[aid] = syncstate
        return result

    def is_app_uploading(self, app_id: str) -> bool:
        """判断指定 app_id 的笔记是否正在上传中（syncstate=3）"""
        syncstates = self._parse_remotecache_syncstates()
        return syncstates.get(app_id) == 3

    def _refresh_games_list(self, force_cache=False):
        """刷新右侧游戏列表（Treeview 实现，支持并列筛选 + dirty 状态）"""
        tree = self._games_tree
        tree.delete(*tree.get_children())

        games = self.manager.list_all_games()

        # 解析 remotecache.vdf 获取 syncstate（3=上传中）
        syncstate_map = self._parse_remotecache_syncstates()

        # 确保游戏名称缓存已加载（避免在主线程做网络请求）
        if force_cache:
            self._ensure_game_name_cache(force=True)
        elif not self._game_name_cache_loaded:
            self._ensure_game_name_cache_fast()

        # 扫描 AI 笔记
        ai_notes_map = self.manager.scan_ai_notes()
        all_models = set()
        for info in ai_notes_map.values():
            for m in info.get('models', []):
                all_models.add(m)

        # 更新 AI 筛选器 — 只含 AI 状态
        ai_filter_values = ["全部", "🤖 AI 处理过", "📝 未 AI 处理", "⛔ 信息过少"]
        if hasattr(self, '_ai_filter_combo'):
            self._ai_filter_combo['values'] = ai_filter_values

        filter_mode = self._ai_filter_var.get() if hasattr(self, '_ai_filter_var') else "全部"

        # 更新模型二级筛选可见性
        is_ai_selected = (filter_mode == "🤖 AI 处理过")
        if hasattr(self, '_model_filter_combo'):
            if is_ai_selected:
                if not self._model_filter_visible:
                    self._model_filter_combo.pack(side=tk.LEFT, padx=(3, 0))
                    self._model_filter_visible = True
                model_values = ["全部"] + sorted(all_models)
                self._model_filter_combo['values'] = model_values
            else:
                if self._model_filter_visible:
                    self._model_filter_combo.pack_forget()
                    self._model_filter_visible = False
                self._model_filter_var.set("全部")

        model_filter = self._model_filter_var.get() if hasattr(self, '_model_filter_var') else "全部"
        dirty_only = self._dirty_filter_var.get() if hasattr(self, '_dirty_filter_var') else False
        uploading_only = self._uploading_filter_var.get() if hasattr(self, '_uploading_filter_var') else False
        source_filter = self._source_filter_var.get() if hasattr(self, '_source_filter_var') else "全部"
        conf_filter = self._conf_filter_var.get() if hasattr(self, '_conf_filter_var') else "全部确信度"
        vol_filter = self._vol_filter_var.get() if hasattr(self, '_vol_filter_var') else "全部信息量"
        qual_filter = self._qual_filter_var.get() if hasattr(self, '_qual_filter_var') else "全部质量"

        # 过滤
        filtered_games = []
        for g in games:
            aid = g['app_id']
            has_ai = aid in ai_notes_map
            is_dirty = self.manager.is_dirty(aid)

            # 有改动全局勾选
            if dirty_only and not is_dirty:
                continue

            # 上传中勾选
            if uploading_only and syncstate_map.get(aid) != 3:
                continue

            # AI 状态筛选
            if filter_mode == "🤖 AI 处理过" and not has_ai:
                continue
            if filter_mode == "📝 未 AI 处理" and has_ai:
                continue
            if filter_mode == "⛔ 信息过少":
                if not has_ai or not ai_notes_map.get(aid, {}).get('has_insufficient', False):
                    continue

            # 模型二级筛选
            if is_ai_selected and model_filter != "全部":
                models = ai_notes_map.get(aid, {}).get('models', [])
                if model_filter not in models:
                    continue

            # 信息来源筛选
            if source_filter == "📡 联网":
                if not has_ai or 'web' not in ai_notes_map.get(aid, {}).get('info_sources', []):
                    continue
            elif source_filter == "📚 本地":
                if not has_ai or 'local' not in ai_notes_map.get(aid, {}).get('info_sources', []):
                    continue

            # 确信度筛选
            if conf_filter != "全部确信度":
                confs = ai_notes_map.get(aid, {}).get('confidences', [])
                if conf_filter not in confs:
                    continue

            # 信息量筛选
            if vol_filter != "全部信息量":
                vols = ai_notes_map.get(aid, {}).get('info_volumes', [])
                if vol_filter not in vols:
                    continue

            # 质量筛选
            if qual_filter != "全部质量":
                # 去掉 emoji 前缀（如 "💎相当好" → "相当好"）
                qual_key = qual_filter
                for q_emoji in QUALITY_EMOJI.values():
                    qual_key = qual_key.replace(q_emoji, "")
                quals = ai_notes_map.get(aid, {}).get('qualities', [])
                if qual_key not in quals:
                    continue

            g['has_ai'] = has_ai
            g['ai_models'] = ai_notes_map.get(aid, {}).get('models', [])
            g['game_name'] = self._get_game_name(aid)
            g['is_dirty'] = is_dirty
            g['is_uploading'] = syncstate_map.get(aid) == 3

            # 搜索过滤
            search_q = ""
            search_mode = "name"
            if hasattr(self, '_main_search_var'):
                search_q = self._main_search_var.get().strip().lower()
            if hasattr(self, '_main_search_mode'):
                search_mode = self._main_search_mode.get()
            if search_q:
                if search_mode == "name":
                    # 按游戏名 / AppID 搜索
                    if (search_q not in g['game_name'].lower()
                            and search_q not in aid.lower()):
                        continue
                else:
                    # 按笔记内容搜索
                    try:
                        note_data = self.manager.read_notes(aid)
                        all_text = " ".join(
                            n.get("content", "") + " " + n.get("title", "")
                            for n in note_data.get("notes", []))
                        if search_q not in all_text.lower():
                            continue
                    except Exception:
                        continue

            filtered_games.append(g)

        self._games_data = filtered_games

        # 插入到 Treeview
        for g in filtered_games:
            aid = g['app_id']
            is_dirty = g.get('is_dirty', False)
            has_ai = g.get('has_ai', False)
            display_name = g['game_name']
            if len(display_name) > 38:
                display_name = display_name[:35] + "..."
            ai_tag = ""
            if has_ai:
                ai_info = ai_notes_map.get(aid, {})
                confs = ai_info.get('confidences', [])
                conf_emoji = CONFIDENCE_EMOJI.get(confs[0], "") if confs else ""
                quals = ai_info.get('qualities', [])
                qual_emoji = QUALITY_EMOJI.get(quals[0], "") if quals else ""
                has_insuf = ai_info.get('has_insufficient', False)
                # 信息来源 emoji
                sources = ai_info.get('info_sources', [])
                source_emoji = ""
                if 'web' in sources:
                    source_emoji = "📡"
                elif 'local' in sources:
                    source_emoji = "📚"
                if has_insuf:
                    ai_tag = " ⛔"
                else:
                    ai_tag = f" 🤖{conf_emoji}{qual_emoji}"
                if source_emoji:
                    ai_tag += source_emoji
            dirty_tag = ""
            is_uploading = g.get('is_uploading', False)
            if is_uploading:
                dirty_tag = " ☁️⬆"
            elif is_dirty:
                dirty_tag = " ⬆"
            text = f"{display_name}{ai_tag}{dirty_tag}"
            notes_col = f"📝{g['note_count']}"

            if is_uploading:
                tag = "uploading"
            elif is_dirty:
                tag = "dirty"
            elif has_ai and ai_notes_map.get(aid, {}).get('has_insufficient', False):
                tag = "insufficient"
            elif has_ai:
                tag = "ai"
            else:
                tag = "normal"
            tree.insert("", tk.END, iid=aid, text=text, values=(notes_col,), tags=(tag,))

        # 更新上传按钮状态
        dirty_n = self.manager.dirty_count()
        if hasattr(self, '_upload_all_btn'):
            if dirty_n > 0:
                self._upload_all_btn.config(text=f"☁️全部({dirty_n})")
            else:
                self._upload_all_btn.config(text="☁️全部")

    def _force_refresh_games_list(self):
        """刷新按钮：强制重建游戏名称缓存（后台执行，不阻塞 UI）"""
        self._game_name_cache_loaded = False
        # 显示进度条
        self._name_progress_frame.pack(fill=tk.X, pady=(2, 0))
        self._name_progress_bar.config(mode='indeterminate')
        self._name_progress_bar.start(15)
        self._name_progress_label.config(text="📥 正在刷新游戏名称...")

        # 先用现有缓存刷一次列表
        self._refresh_games_list()

        def _on_progress(fetched, page, is_done, estimated_total=0):
            try:
                self.root.after(0, lambda: self._update_name_progress(
                    fetched, page, is_done, estimated_total))
            except Exception:
                pass

        def _bg():
            try:
                self._ensure_game_name_cache(force=True, progress_callback=_on_progress)
                try:
                    self.root.after(0, lambda: self._hide_name_progress())
                    self.root.after(0, lambda: self._refresh_games_list())
                except Exception:
                    pass
                self._bg_resolve_missing_names()
            except Exception as e:
                print(f"[后台] 强制刷新游戏名称失败: {e}")
                try:
                    self.root.after(0, lambda: self._hide_name_progress())
                except Exception:
                    pass

        threading.Thread(target=_bg, daemon=True).start()

    def _on_main_search_changed(self):
        """主界面搜索框内容或模式变化时刷新列表（带防抖）"""
        if hasattr(self, '_search_debounce_id') and self._search_debounce_id:
            self.root.after_cancel(self._search_debounce_id)
        delay = 300 if (hasattr(self, '_main_search_mode')
                        and self._main_search_mode.get() == "content") else 100
        self._search_debounce_id = self.root.after(delay, self._refresh_games_list)

    def _on_filter_changed(self):
        """主 AI 状态筛选器变更时，重置模型筛选并刷新"""
        self._model_filter_var.set("全部")
        self._refresh_games_list()

    def _on_tree_double_click(self):
        """Treeview 双击 → 查看笔记（取第一个选中项）"""
        sel = self._games_tree.selection()
        if sel:
            self._open_notes_viewer(sel[0])

    def _on_tree_right_click(self, event):
        """右键弹出菜单"""
        iid = self._games_tree.identify_row(event.y)
        if not iid:
            return
        # 如果右键的项不在当前选中集中，则设为单选
        current_sel = self._games_tree.selection()
        if iid not in current_sel:
            self._games_tree.selection_set(iid)
        menu = tk.Menu(self.root, tearoff=0)
        sel = self._games_tree.selection()
        if len(sel) == 1:
            menu.add_command(label="📋 查看笔记", command=lambda: self._open_notes_viewer(sel[0]))
            menu.add_command(label="📋 复制 AppID", command=lambda: self._copy_appid_silent(sel[0]))
            menu.add_separator()
            menu.add_command(label="📤 导出笔记", command=self._ui_export_dialog)
            if self.manager.is_dirty(sel[0]):
                menu.add_separator()
                menu.add_command(label="☁️ 上传到 Steam Cloud",
                                 command=lambda: self._cloud_upload_single(sel[0]))
                menu.add_command(label="✅ 标记为已同步（消除改动标记）",
                                 command=lambda: self._mark_synced_selected())
        else:
            menu.add_command(label=f"📤 导出 ({len(sel)} 个游戏)",
                             command=self._ui_export_dialog)
            dirty_sel = [a for a in sel if self.manager.is_dirty(a)]
            if dirty_sel:
                menu.add_command(label=f"☁️ 上传选中 ({len(dirty_sel)} 个)",
                                 command=self._cloud_upload_selected)
                menu.add_command(label=f"✅ 标记选中为已同步 ({len(dirty_sel)} 个)",
                                 command=self._mark_synced_selected)
        menu.tk_popup(event.x_root, event.y_root)

    def _get_selected_app_id(self):
        """获取 Treeview 选中的第一个 AppID"""
        sel = self._games_tree.selection()
        return sel[0] if sel else None

    def _get_selected_app_ids(self):
        """获取 Treeview 选中的所有 AppID"""
        return list(self._games_tree.selection())

    def _copy_selected_appid(self):
        """复制选中游戏的 AppID（多选时用逗号分隔）"""
        aids = self._get_selected_app_ids()
        if aids:
            self._copy_appid_silent(",".join(aids))
        else:
            messagebox.showinfo("提示", "请先在列表中选择游戏。")

    def _cloud_upload_selected(self):
        """上传选中游戏的笔记（支持多选）"""
        aids = self._get_selected_app_ids()
        if not aids:
            messagebox.showinfo("提示", "请先在列表中选择游戏。")
            return
        if not self.cloud_uploader or not self.cloud_uploader.initialized:
            messagebox.showwarning("提示", "请先连接 Steam Cloud。", parent=self.root)
            return
        ok = fail = 0
        for aid in aids:
            if self.manager.is_dirty(aid):
                if self.manager.cloud_upload(aid):
                    ok += 1
                else:
                    fail += 1
        self._refresh_games_list()
        self._save_uploaded_hashes()
        if ok + fail == 0:
            messagebox.showinfo("提示", "选中的游戏没有需要上传的改动。", parent=self.root)
        elif fail == 0:
            messagebox.showinfo("✅ 成功", f"已上传 {ok} 个游戏。", parent=self.root)
        else:
            messagebox.showwarning("⚠️", f"成功 {ok}，失败 {fail}。", parent=self.root)

    def _mark_synced_selected(self):
        """将选中游戏的 dirty 状态手动标记为已同步（不实际上传）"""
        aids = self._get_selected_app_ids()
        if not aids:
            messagebox.showinfo("提示", "请先在列表中选择游戏。")
            return
        dirty_aids = [a for a in aids if self.manager.is_dirty(a)]
        if not dirty_aids:
            messagebox.showinfo("提示", "选中的游戏没有需要同步的改动。", parent=self.root)
            return
        if not messagebox.askyesno("确认标记为已同步",
                f"即将把 {len(dirty_aids)} 个游戏标记为已同步。\n\n"
                "这将消除改动标记，让程序认为本地版本即云版本。\n"
                "适用于：本地文件是从云端下载的，但程序误判为有改动的情况。\n\n"
                "确认继续？", parent=self.root):
            return
        count = 0
        for aid in dirty_aids:
            if self.manager.mark_as_synced(aid):
                count += 1
        self._save_uploaded_hashes()
        self._refresh_games_list()
        messagebox.showinfo("✅ 完成", f"已将 {count} 个游戏标记为已同步。", parent=self.root)

    def _select_all_games(self):
        """全选/取消全选当前筛选下的所有游戏"""
        tree = self._games_tree
        all_items = tree.get_children()
        current_sel = tree.selection()
        if len(current_sel) == len(all_items) and len(all_items) > 0:
            # 已全选 → 取消全选
            tree.selection_remove(*all_items)
        else:
            # 全选
            tree.selection_set(all_items)

    def _copy_appid_silent(self, app_id: str):
        """复制 AppID 到剪贴板（无弹窗）"""
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(app_id)
            self.root.update()
        except:
            pass

    def _cloud_upload_single(self, app_id: str):
        """上传单个游戏的笔记到 Steam Cloud"""
        if not self.cloud_uploader or not self.cloud_uploader.initialized:
            messagebox.showwarning("提示", "请先连接 Steam Cloud。", parent=self.root)
            return
        if self.manager.cloud_upload(app_id):
            self._save_uploaded_hashes()
            self._refresh_games_list()
        else:
            messagebox.showerror("❌", f"上传 AppID {app_id} 失败。", parent=self.root)

    def _cloud_upload_all(self):
        """上传所有有改动的笔记到 Steam Cloud"""
        if not self.cloud_uploader or not self.cloud_uploader.initialized:
            messagebox.showwarning("提示", "请先连接 Steam Cloud。", parent=self.root)
            return
        n = self.manager.dirty_count()
        if n == 0:
            messagebox.showinfo("提示", "没有需要上传的改动。", parent=self.root)
            return
        ok, fail = self.manager.cloud_upload_all_dirty()
        self._save_uploaded_hashes()
        self._refresh_games_list()
        if fail == 0:
            messagebox.showinfo("✅ 成功",
                                f"已上传 {ok} 个游戏的笔记到 Steam Cloud。\n\n"
                                "💡 这些改动仍需等待 Steam 客户端自动同步到云端，\n"
                                "通常在几秒到几分钟内完成。",
                                parent=self.root)
        else:
            messagebox.showwarning("⚠️ 部分失败",
                                    f"成功 {ok} 个，失败 {fail} 个。",
                                    parent=self.root)

    def _on_game_double_click(self, event):
        app_id = self._get_selected_app_id()
        if app_id:
            self._open_notes_viewer(app_id)

    # ────────────────────── Steam Cloud 连接 ──────────────────────

    def _update_cloud_status_display(self):
        """更新主界面的云同步状态显示"""
        t = self._cloud_status_text
        t.config(state=tk.NORMAL)
        t.delete("1.0", tk.END)
        t.insert(tk.END, "✅ 已定位到笔记目录  ", "green")
        if self.cloud_uploader and self.cloud_uploader.initialized:
            # 检查账号是否匹配
            logged_in = self.cloud_uploader.logged_in_friend_code
            selected = self.current_account.get('friend_code', '')
            if logged_in and logged_in != selected:
                t.insert(tk.END, "⚠️ Cloud 已连接 (账号不匹配!)", "red")
            else:
                t.insert(tk.END, "☁️ Steam Cloud 已连接", "green")
            self._cloud_connect_btn.config(text="🔌 断开 Steam Cloud")
        else:
            t.insert(tk.END, "☁️ Cloud 未连接", "red")
            self._cloud_connect_btn.config(text="☁️ 连接 Steam Cloud")
        t.config(state=tk.DISABLED)

    def _toggle_cloud_connection(self):
        """连接或断开 Steam Cloud"""
        if self.cloud_uploader and self.cloud_uploader.initialized:
            # 断开
            self.cloud_uploader.shutdown()
            self.cloud_uploader = None
            self.manager.cloud_uploader = None
            self._update_cloud_status_display()
            return

        # 连接
        self._cloud_connect_btn.config(state=tk.DISABLED)
        self.root.update_idletasks()

        uploader = SteamCloudUploader()
        steam_path = self.current_account.get('steam_path', '')
        ok, msg = uploader.auto_init(steam_path)

        if ok:
            # 检查登录账号是否匹配当前选择的账号
            logged_in = uploader.logged_in_friend_code
            selected = self.current_account.get('friend_code', '')
            if logged_in and logged_in != selected:
                # 账号不匹配 — 拒绝连接
                logged_name = None
                for acc in self.accounts:
                    if acc['friend_code'] == logged_in:
                        logged_name = acc['persona_name']
                        break
                logged_desc = (f"「{logged_name}」(ID: {logged_in})"
                               if logged_name else f"ID: {logged_in}")
                selected_name = self.current_account.get('persona_name', selected)
                uploader.shutdown()
                messagebox.showerror("❌ 账号不匹配，已拒绝连接",
                    f"Steam 客户端当前登录的账号是 {logged_desc}，\n"
                    f"但程序中选择的账号是「{selected_name}」(ID: {selected})。\n\n"
                    f"上传到 Steam Cloud 的笔记会同步到登录账号，\n"
                    f"而非程序中选择的账号！\n\n"
                    f"如果要为「{selected_name}」上传笔记，\n"
                    f"请先在 Steam 客户端切换到该账号后重新连接。",
                    parent=self.root)
                self._cloud_connect_btn.config(state=tk.NORMAL)
                self._update_cloud_status_display()
                return
            self.cloud_uploader = uploader
            self.manager.cloud_uploader = uploader
            self._update_cloud_status_display()
        else:
            messagebox.showerror("❌ 连接失败",
                f"无法连接 Steam Cloud:\n{msg}\n\n"
                "请确保:\n"
                "1. Steam 客户端正在运行\n"
                "2. 库中至少有一个已安装的游戏（需要其中的 libsteam_api）\n"
                "3. macOS 用户首次使用可能需要在系统设置中允许加载",
                parent=self.root)
            self._cloud_connect_btn.config(state=tk.NORMAL)
            self._update_cloud_status_display()
            return

        self._cloud_connect_btn.config(state=tk.NORMAL)

    # ────────────────────── 工具方法 ──────────────────────

    @staticmethod
    def _center_window(win):
        win.update_idletasks()
        cw, ch = win.winfo_reqwidth(), win.winfo_reqheight()
        sw, sh = win.winfo_screenwidth(), win.winfo_screenheight()
        win.geometry(f"{cw}x{ch}+{int((sw - cw) / 2)}+{int((sh - ch) / 2)}")

