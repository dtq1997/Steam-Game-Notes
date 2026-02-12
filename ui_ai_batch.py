"""AI 批量生成窗口 (Mixin)"""

import json
import os
import re
import threading
import time
import tkinter as tk
from tkinter import messagebox, ttk

try:
    import urllib.request
    _HAS_URLLIB = True
except ImportError:
    _HAS_URLLIB = False

from core import (
    AI_NOTE_PREFIX,
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
)
from account_manager import SteamAccountScanner
from cloud_uploader import SteamCloudUploader
from ai_generator import SteamAIGenerator, AI_SYSTEM_PROMPT


class AIBatchMixin:
    """AI 批量生成相关 UI 方法"""

    def _ui_ai_batch_generate(self):
        """AI 批量生成游戏说明笔记窗口 — 紧凑版，配置从主界面读取"""
        if not _HAS_URLLIB:
            messagebox.showerror("❌ 缺少依赖",
                                 "AI 功能需要 urllib 模块（Python 标准库），当前环境不可用。")
            return

        # 读取保存的令牌列表
        all_tokens = self._get_ai_tokens()
        saved_steam_key = (self._config.get("steam_web_api_key") or
                           os.environ.get("STEAM_WEB_API_KEY", ""))

        if not all_tokens:
            messagebox.showwarning("⚠️ 未配置 AI 令牌",
                "请先在主界面点击「🔑 AI 配置」添加至少一个 AI 令牌。")
            return

        # 当前选中的令牌
        active_token_idx = [min(self._get_active_token_index(), len(all_tokens) - 1)]
        current_token = [all_tokens[active_token_idx[0]]]

        win = tk.Toplevel(self.root)
        win.title("🤖 AI 批量生成游戏说明")
        win.resizable(True, True)
        win.grab_set()
        win.minsize(880, 580)

        # ── 令牌选择器 + Cloud 按钮 ──
        config_frame = tk.LabelFrame(win, text="当前 AI 令牌 & Steam Cloud",
                                      font=("", 9), padx=8, pady=3)
        config_frame.pack(fill=tk.X, padx=10, pady=(8, 3))

        token_row = tk.Frame(config_frame)
        token_row.pack(fill=tk.X)

        tk.Label(token_row, text="🔑 令牌:", font=("", 9)).pack(side=tk.LEFT)
        token_names = [f"{t.get('name', '未命名')} ({SteamAIGenerator.PROVIDERS.get(t.get('provider', ''), {}).get('name', t.get('provider', ''))} / {t.get('model', '')})"
                       for t in all_tokens]
        _token_select_var = tk.StringVar(value=token_names[active_token_idx[0]] if token_names else "")
        token_combo = ttk.Combobox(token_row, textvariable=_token_select_var,
                                    values=token_names, state='readonly', width=55)
        token_combo.pack(side=tk.LEFT, padx=(5, 10))

        token_detail_label = tk.Label(config_frame, text="", font=("", 8), fg="#555",
                                       justify=tk.LEFT)
        token_detail_label.pack(anchor=tk.W)

        def _update_token_detail():
            t = current_token[0]
            pname = SteamAIGenerator.PROVIDERS.get(t.get('provider', ''), {}).get('name', t.get('provider', ''))
            key_preview = t.get('key', '')
            if len(key_preview) > 10:
                key_preview = key_preview[:6] + '...' + key_preview[-4:]
            detail = f"提供商: {pname}  |  模型: {t.get('model', '')}  |  Key: {key_preview}"
            if t.get('api_url'):
                detail += f"  |  自定义 URL: {t['api_url']}"
            detail += f"  |  Steam API Key: {'✅' if saved_steam_key else '❌'}"
            token_detail_label.config(text=detail)

        def _on_token_changed(*_):
            sel_text = _token_select_var.get()
            for i, name in enumerate(token_names):
                if name == sel_text:
                    active_token_idx[0] = i
                    current_token[0] = all_tokens[i]
                    break
            _update_token_detail()

        token_combo.bind("<<ComboboxSelected>>", _on_token_changed)
        _update_token_detail()

        # ── Cloud 连接按钮（嵌入令牌行右侧） ──
        _cloud_connect_btn_ai = ttk.Button(token_row, text="☁️ 连接 Steam Cloud",
                                            command=lambda: None)  # placeholder
        _cloud_connect_btn_ai.pack(side=tk.RIGHT, padx=(5, 0))

        _cloud_status_label = tk.Label(token_row, text="", font=("", 9))
        _cloud_status_label.pack(side=tk.RIGHT)

        def _update_ai_cloud_status():
            if self.cloud_uploader and self.cloud_uploader.initialized:
                logged_in = self.cloud_uploader.logged_in_friend_code
                selected = self.current_account.get('friend_code', '')
                if logged_in and logged_in != selected:
                    _cloud_status_label.config(
                        text="⚠️ Cloud 已连接 (账号不匹配!)", fg="red")
                else:
                    _cloud_status_label.config(
                        text="☁️ Steam Cloud 已连接", fg="green")
                _cloud_connect_btn_ai.config(text="🔌 断开")
            else:
                _cloud_status_label.config(text="☁️ Steam Cloud 未连接", fg="#888")
                _cloud_connect_btn_ai.config(text="☁️ 连接 Steam Cloud")

        def _toggle_cloud_ai():
            if self.cloud_uploader and self.cloud_uploader.initialized:
                self.cloud_uploader.shutdown()
                self.cloud_uploader = None
                self.manager.cloud_uploader = None
                _update_ai_cloud_status()
                # 同步更新主界面状态
                try:
                    self._update_cloud_status_display()
                except Exception:
                    pass
                return
            _cloud_connect_btn_ai.config(state=tk.DISABLED)
            win.update_idletasks()
            uploader = SteamCloudUploader()
            steam_path = self.current_account.get('steam_path', '')
            ok, msg = uploader.auto_init(steam_path)
            if ok:
                # 先检查账号匹配
                logged_in = uploader.logged_in_friend_code
                selected = self.current_account.get('friend_code', '')
                if logged_in and logged_in != selected:
                    logged_name = None
                    for acc in self.accounts:
                        if acc['friend_code'] == logged_in:
                            logged_name = acc['persona_name']
                            break
                    logged_desc = (f"「{logged_name}」(ID: {logged_in})"
                                   if logged_name else f"ID: {logged_in}")
                    selected_name = self.current_account.get(
                        'persona_name', selected)
                    uploader.shutdown()
                    messagebox.showerror("❌ 账号不匹配，已拒绝连接",
                        f"Steam 登录账号 {logged_desc} ≠ "
                        f"程序选择的「{selected_name}」\n\n"
                        f"请先在 Steam 客户端切换到正确账号后重新连接。",
                        parent=win)
                    _cloud_connect_btn_ai.config(state=tk.NORMAL)
                    return
                self.cloud_uploader = uploader
                self.manager.cloud_uploader = uploader
                _update_ai_cloud_status()
                try:
                    self._update_cloud_status_display()
                except Exception:
                    pass
            else:
                messagebox.showerror("❌ 连接失败",
                    f"无法连接 Steam Cloud:\n{msg}\n\n"
                    "请确保:\n"
                    "1. Steam 客户端正在运行\n"
                    "2. 库中至少有一个已安装的游戏\n"
                    "3. macOS 用户首次使用可能需要在系统设置中允许加载",
                    parent=win)
            _cloud_connect_btn_ai.config(state=tk.NORMAL)

        _cloud_connect_btn_ai.config(command=_toggle_cloud_ai)
        _update_ai_cloud_status()

        # 使用当前令牌的 provider/model 等信息
        def _get_current_provider(): return current_token[0].get("provider", "anthropic")
        def _get_current_model():
            m = current_token[0].get("model", "")
            if not m:
                pinfo = SteamAIGenerator.PROVIDERS.get(_get_current_provider(), {})
                m = pinfo.get("default_model", "claude-sonnet-4-5-20250929")
            return m
        def _get_current_key(): return current_token[0].get("key", "")
        def _get_current_url(): return current_token[0].get("api_url", "") or None

        # ═══════════════════════════════════════════════════════
        #  使用 PanedWindow 上下分割：上=提示词+游戏列表  下=进度区
        # ═══════════════════════════════════════════════════════
        main_paned = tk.PanedWindow(win, orient=tk.VERTICAL, sashwidth=5)
        main_paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=3)

        # ── 上半部分：左=提示词 右=游戏列表 ──
        top_paned = tk.PanedWindow(main_paned, orient=tk.HORIZONTAL, sashwidth=5)
        main_paned.add(top_paned, minsize=280)

        # ═══════════════ 左列：系统提示词 ═══════════════
        left_panel = tk.Frame(top_paned)
        top_paned.add(left_panel, minsize=300, width=380)

        # ── 系统提示词 ──
        prompt_frame = tk.LabelFrame(left_panel, text="系统提示词（可编辑）",
                                      font=("", 10), padx=8, pady=3)
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=3)

        prompt_collapsed = {'value': True}
        prompt_text = tk.Text(prompt_frame, font=("", 9), height=1, wrap=tk.WORD,
                               fg="#555")
        # 优先从配置加载保存的提示词，没有则用默认
        saved_prompt = self._config.get("ai_system_prompt", "").strip()
        prompt_text.insert("1.0", saved_prompt if saved_prompt else AI_SYSTEM_PROMPT)
        prompt_text.pack(fill=tk.BOTH, expand=True, pady=(0, 3))

        def toggle_prompt():
            if prompt_collapsed['value']:
                prompt_text.config(height=12)
                toggle_btn.config(text="🔼 收起")
                prompt_collapsed['value'] = False
            else:
                prompt_text.config(height=1)
                toggle_btn.config(text="🔽 展开")
                prompt_collapsed['value'] = True

        prompt_btn_frame = tk.Frame(prompt_frame)
        prompt_btn_frame.pack(fill=tk.X)
        toggle_btn = tk.Button(prompt_btn_frame, text="🔽 展开", font=("", 9),
                                relief=tk.FLAT, command=toggle_prompt)
        toggle_btn.pack(side=tk.LEFT)

        def reset_prompt():
            prompt_text.delete("1.0", tk.END)
            prompt_text.insert("1.0", AI_SYSTEM_PROMPT)
        tk.Button(prompt_btn_frame, text="↩️ 恢复默认", font=("", 9),
                  relief=tk.FLAT, command=reset_prompt).pack(side=tk.LEFT, padx=10)

        def save_prompt():
            current_prompt = prompt_text.get("1.0", tk.END).strip()
            self._config["ai_system_prompt"] = current_prompt
            self._save_config(self._config)
            messagebox.showinfo("✅", "提示词已保存", parent=win)
        tk.Button(prompt_btn_frame, text="💾 保存提示词", font=("", 9),
                  relief=tk.FLAT, command=save_prompt).pack(side=tk.LEFT, padx=5)

        tk.Label(prompt_frame,
                 text="💡 标题=内容模式：AI 输出同时作为笔记标题和内容",
                 font=("", 8), fg="#4a90d9").pack(anchor=tk.W)

        # ═══════════════ 右列：游戏列表 ═══════════════
        right_panel = tk.Frame(top_paned)
        top_paned.add(right_panel, minsize=380)

        games_frame = tk.LabelFrame(right_panel, text="游戏列表", font=("", 10),
                                     padx=8, pady=3)
        games_frame.pack(fill=tk.BOTH, expand=True)

        # 模式切换 — 注意 command 用 IntVar.set 延迟触发，避免 Python 3.13 闭包问题
        mode_frame = tk.Frame(games_frame)
        mode_frame.pack(fill=tk.X, pady=(0, 3))
        games_mode_var = tk.IntVar(value=1)

        # ── 模式1: 扫描库 ──
        scan_container = tk.Frame(games_frame)
        scan_container.pack(fill=tk.BOTH, expand=True)

        _library_games = []
        _family_owned_app_ids = set()  # 家庭组所有成员拥有的游戏 app_id 集合（并集）
        _family_intersection_app_ids = None  # 家庭组所有成员都拥有的游戏（交集），None=未扫描
        _family_scan_done = [False]  # 是否已完成家庭组扫描
        _loaded_from_cache = [False]  # 是否从缓存加载

        # ── 家庭库缓存：从配置文件加载上次扫描结果 ──
        def _save_library_cache():
            """将当前扫描结果保存到配置文件缓存"""
            cache = {
                'library_games': _library_games,
                'family_owned_ids': sorted(_family_owned_app_ids),
                'steam_id': steam_id_var.get().strip(),
                'family_codes': sorted(_family_codes),
                'family_scan_done': _family_scan_done[0],
            }
            self._config['family_library_cache'] = cache
            self._save_config(self._config)

        def _try_load_library_cache() -> bool:
            """尝试从缓存加载家庭库数据，成功返回 True"""
            nonlocal _library_games, _family_owned_app_ids, _family_scan_done
            cache = self._config.get('family_library_cache')
            if not cache:
                return False
            # 验证缓存是否仍然有效（Steam ID 和家庭组成员未变化）
            cached_sid = cache.get('steam_id', '')
            cached_codes = cache.get('family_codes', [])
            current_sid = steam_id_var.get().strip()
            current_codes = sorted(_family_codes)
            if cached_sid != current_sid or cached_codes != current_codes:
                return False
            cached_games = cache.get('library_games', [])
            if not cached_games:
                return False
            _library_games = cached_games
            _family_owned_app_ids = set(cache.get('family_owned_ids', []))
            _family_scan_done[0] = cache.get('family_scan_done', False)
            _loaded_from_cache[0] = True
            # 更新名称缓存
            for g in _library_games:
                if g['app_id'] not in self._game_name_cache:
                    self._game_name_cache[g['app_id']] = g['name']
            return True

        # Steam API 配置状态提示 + Steam ID 输入（合并为一行）
        steam_status_frame = tk.Frame(scan_container)
        steam_status_frame.pack(fill=tk.X, pady=(0, 2))

        steam_key_ok = "✅" if saved_steam_key else "❌"
        tk.Label(steam_status_frame,
                 text=f"Steam API Key: {steam_key_ok}",
                 font=("", 9), fg="#333").pack(side=tk.LEFT)

        tk.Label(steam_status_frame, text="  Steam ID:", font=("", 9)).pack(side=tk.LEFT)
        steam_id_var = tk.StringVar(
            value=self.current_account.get('friend_code', ''))
        tk.Entry(steam_status_frame, textvariable=steam_id_var, width=15,
                 font=("", 9)).pack(side=tk.LEFT, padx=(3, 0))
        tk.Label(steam_status_frame, text="（扫描该 ID 的游戏库）",
                 font=("", 8), fg="#888").pack(side=tk.LEFT, padx=3)

        # 家庭组成员好友代码管理
        family_frame = tk.Frame(scan_container)
        family_frame.pack(fill=tk.X, pady=(0, 2))
        tk.Label(family_frame, text="👨‍👩‍👧‍👦 家庭组:", font=("", 9)).pack(side=tk.LEFT)
        _family_codes = list(self._config.get("family_friend_codes", []))
        _family_display_var = tk.StringVar(
            value=f"{len(_family_codes)} 人" if _family_codes else "未设置")
        _family_display_label = tk.Label(family_frame,
                                          textvariable=_family_display_var,
                                          font=("", 9), fg="#1a73e8" if _family_codes else "#888")
        _family_display_label.pack(side=tk.LEFT, padx=(3, 0))

        def _manage_family_codes():
            """弹出窗口管理家庭组成员好友代码"""
            nonlocal _family_codes
            fam_win = tk.Toplevel(win)
            fam_win.title("👨‍👩‍👧‍👦 家庭组成员管理")
            fam_win.transient(win)
            fam_win.grab_set()
            fam_win.resizable(False, False)

            tk.Label(fam_win, text="家庭组成员的 Steam 好友代码",
                     font=("", 11, "bold")).pack(pady=(10, 5))
            tk.Label(fam_win, text="每行一个好友代码（32 位 Steam ID），用于筛选家庭组拥有的游戏",
                     font=("", 9), fg="#666").pack(padx=15)
            tk.Label(fam_win, text="注意：你自己的 ID 也需要填入（如果你希望包含自己拥有的游戏）",
                     font=("", 8), fg="#888").pack(padx=15, pady=(0, 5))

            txt = tk.Text(fam_win, font=("Consolas", 10), width=40, height=8)
            txt.pack(padx=15, pady=5)
            # 预填当前保存的代码
            if _family_codes:
                txt.insert("1.0", "\n".join(_family_codes))

            def _save_family():
                nonlocal _family_codes
                raw = txt.get("1.0", tk.END).strip()
                codes = []
                for line in raw.split("\n"):
                    code = line.strip()
                    if code and code.isdigit():
                        codes.append(code)
                _family_codes = codes
                self._config["family_friend_codes"] = codes
                self._save_config(self._config)
                _family_display_var.set(
                    f"{len(codes)} 人" if codes else "未设置")
                _family_display_label.config(
                    fg="#1a73e8" if codes else "#888")
                fam_win.grab_release()
                fam_win.destroy()
                messagebox.showinfo("✅", f"已保存 {len(codes)} 个家庭组成员",
                                    parent=win)

            btn_f = tk.Frame(fam_win)
            btn_f.pack(pady=(0, 10))
            ttk.Button(btn_f, text="💾 保存", command=_save_family).pack(
                side=tk.LEFT, padx=5)
            ttk.Button(btn_f, text="取消",
                       command=lambda: (fam_win.grab_release(), fam_win.destroy())).pack(
                side=tk.LEFT, padx=5)

        ttk.Button(family_frame, text="✏️ 管理", command=_manage_family_codes).pack(
            side=tk.LEFT, padx=(5, 0))
        tk.Label(family_frame,
                 text="（录入后：默认显示所有人拥有的游戏的并集）",
                 font=("", 8), fg="#888").pack(side=tk.LEFT, padx=3)

        # Steam 分类筛选
        collection_frame = tk.Frame(scan_container)
        collection_frame.pack(fill=tk.X, pady=(0, 2))
        tk.Label(collection_frame, text="📂 按分类筛选:", font=("", 9)).pack(side=tk.LEFT)
        _collections = []
        _collection_var = tk.StringVar(value="（家庭库所有游戏）")
        collection_combo = ttk.Combobox(collection_frame, textvariable=_collection_var,
                                         width=25, state='readonly',
                                         values=["（家庭库所有游戏）"])
        collection_combo.pack(side=tk.LEFT, padx=(5, 0))

        # 状态 + 搜索 — 必须在 _load_collections 之前创建
        info_search_frame = tk.Frame(scan_container)
        info_search_frame.pack(fill=tk.X, pady=(1, 1))

        scan_info_label = tk.Label(info_search_frame,
                                    text="正在加载...",
                                    font=("", 9), fg="#888")
        scan_info_label.pack(side=tk.LEFT)

        # 搜索框放右侧
        tk.Label(info_search_frame, text="🔎", font=("", 9)).pack(side=tk.LEFT, padx=(8, 0))
        search_var = tk.StringVar()
        search_entry = tk.Entry(info_search_frame, textvariable=search_var,
                                 width=18, font=("", 9))
        search_entry.pack(side=tk.LEFT, padx=(2, 0), fill=tk.X, expand=True)

        # ── 扫描进度条（默认隐藏，扫描时显示） ──
        _scan_progress_frame = tk.Frame(scan_container)
        _scan_progress_label = tk.Label(_scan_progress_frame, text="",
                                         font=("", 8), fg="#555", anchor=tk.W)
        _scan_progress_label.pack(fill=tk.X)
        _scan_progress_bar = ttk.Progressbar(
            _scan_progress_frame, mode='determinate', length=200)
        _scan_progress_bar.pack(fill=tk.X)

        # 游戏列表（占满剩余空间）
        list_frame = tk.Frame(scan_container)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        games_listbox = tk.Listbox(list_frame, font=("Consolas", 9),
                                    selectmode=tk.EXTENDED,
                                    exportselection=False)
        games_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        games_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
                                         command=games_listbox.yview)
        games_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        games_listbox.config(yscrollcommand=games_scrollbar.set)

        # 按钮行（合并为一行）
        scan_btn_row1 = tk.Frame(scan_container)
        scan_btn_row1.pack(fill=tk.X, pady=(2, 0))

        # AI 筛选器 — 在函数定义前创建 widget
        ai_filter_row = tk.Frame(scan_container)
        ai_filter_row.pack(fill=tk.X, pady=(1, 0))
        tk.Label(ai_filter_row, text="AI 筛选:", font=("", 9)).pack(side=tk.LEFT)
        _ai_gen_filter_var = tk.StringVar(value="全部")
        ai_gen_filter_combo = ttk.Combobox(
            ai_filter_row, textvariable=_ai_gen_filter_var, width=18,
            values=["全部", "☁️ 有改动", "🤖 AI 处理过", "📝 未 AI 处理",
                    "⛔ 信息过少", "📡 联网检索", "📚 非联网"], state='readonly')
        ai_gen_filter_combo.pack(side=tk.LEFT, padx=(3, 0))

        # 确信度二级筛选（默认隐藏，选中 AI 相关筛选后自动出现）
        _conf_gen_filter_var = tk.StringVar(value="全部确信度")
        conf_gen_filter_combo = ttk.Combobox(
            ai_filter_row, textvariable=_conf_gen_filter_var, width=10,
            values=["全部确信度"], state='readonly')
        _conf_gen_filter_visible = [False]

        # 质量二级筛选（默认隐藏，选中 AI 相关筛选后自动出现）
        _qual_gen_filter_var = tk.StringVar(value="全部质量")
        qual_gen_filter_combo = ttk.Combobox(
            ai_filter_row, textvariable=_qual_gen_filter_var, width=10,
            values=["全部质量", "💎相当好", "✨较好", "➖中等", "👎较差", "💀相当差"],
            state='readonly')
        _qual_gen_filter_visible = [False]

        _filtered_indices = []
        _ai_notes_map_cache = {}

        # ═══════ 所有内部函数定义（在 widget 全部创建后） ═══════

        def _show_scan_progress(text="", value=0, maximum=100):
            """显示扫描进度条并更新"""
            _scan_progress_frame.pack(fill=tk.X, pady=(1, 1),
                                       before=list_frame)
            _scan_progress_label.config(text=text)
            _scan_progress_bar.config(mode='determinate', maximum=maximum,
                                       value=value)
            win.update_idletasks()

        def _hide_scan_progress():
            """隐藏扫描进度条"""
            _scan_progress_frame.pack_forget()

        def _get_selected_collection_ids():
            """根据下拉框选中的分类名，返回该分类的 app_ids 集合，未选中返回 None"""
            sel = _collection_var.get()
            if sel == "（家庭库所有游戏）":
                return None
            for c in _collections:
                display_name = f"{c['name']} ({len(c['app_ids'])})"
                if display_name == sel:
                    return set(str(x) for x in c['app_ids'])
            return None

        def _populate_listbox(filter_text=""):
            nonlocal _filtered_indices, _ai_notes_map_cache
            games_listbox.delete(0, tk.END)
            _filtered_indices = []
            ft = filter_text.strip().lower()

            # 获取选中的分类
            col_app_ids = _get_selected_collection_ids()

            # 扫描 AI 笔记状态
            _ai_notes_map_cache = self.manager.scan_ai_notes()

            # AI 筛选模式 & 确信度筛选
            ai_mode = _ai_gen_filter_var.get()
            conf_filter = _conf_gen_filter_var.get()
            qual_filter = _qual_gen_filter_var.get()
            is_ai_mode = (ai_mode == "🤖 AI 处理过"
                          or (ai_mode.startswith("🤖 ")
                              and ai_mode != "🤖 AI 处理过")
                          or ai_mode in ("⛔ 信息过少", "📡 联网检索", "📚 非联网"))

            # 收集所有确信度（用于更新下拉框）
            all_confidences = set()

            # 用于统计的变量
            intersection = None

            def _make_display(app_id, name):
                """为列表项生成显示文本和颜色"""
                has_ai = app_id in _ai_notes_map_cache
                is_dirty = self.manager.is_dirty(app_id)
                ai_info = _ai_notes_map_cache.get(app_id, {})
                confs = ai_info.get('confidences', [])
                for c in confs:
                    all_confidences.add(c)
                # 确信度 emoji（取第一个，通常只有一条 AI 笔记）
                conf_emoji = ""
                quals = ai_info.get('qualities', [])
                qual_emoji = QUALITY_EMOJI.get(quals[0], "") if quals else ""
                has_insuf = ai_info.get('has_insufficient', False)
                if has_ai and has_insuf:
                    ai_tag = " ⛔"
                elif has_ai and confs:
                    conf_emoji = CONFIDENCE_EMOJI.get(confs[0], "")
                    ai_tag = f" 🤖{conf_emoji}{qual_emoji}"
                elif has_ai:
                    ai_tag = " 🤖"
                else:
                    ai_tag = ""
                dirty_tag = " ⬆" if is_dirty else ""
                return f" {app_id:>10s}  |  {name}{ai_tag}{dirty_tag}", has_ai, is_dirty

            def _should_include(app_id):
                """判断是否通过 AI 筛选 + 确信度筛选 + dirty 筛选"""
                has_ai = app_id in _ai_notes_map_cache
                ai_info = _ai_notes_map_cache.get(app_id, {})
                if ai_mode == "☁️ 有改动" and not self.manager.is_dirty(app_id):
                    return False
                if ai_mode == "🤖 AI 处理过" and not has_ai:
                    return False
                if ai_mode == "📝 未 AI 处理" and has_ai:
                    return False
                if ai_mode == "⛔ 信息过少":
                    if not has_ai or not ai_info.get('has_insufficient', False):
                        return False
                if ai_mode == "📡 联网检索":
                    if not has_ai or 'web' not in ai_info.get('info_sources', []):
                        return False
                if ai_mode == "📚 非联网":
                    if not has_ai or 'local' not in ai_info.get('info_sources', []):
                        return False
                if (ai_mode.startswith("🤖 ")
                        and ai_mode != "🤖 AI 处理过"):
                    target_model = ai_mode[2:]
                    if target_model not in ai_info.get('models', []):
                        return False
                # 确信度二级筛选
                if is_ai_mode and conf_filter != "全部确信度":
                    if conf_filter not in ai_info.get('confidences', []):
                        return False
                # 质量二级筛选
                if is_ai_mode and qual_filter != "全部质量":
                    qual_key = qual_filter
                    for q_emoji in QUALITY_EMOJI.values():
                        qual_key = qual_key.replace(q_emoji, "")
                    if qual_key not in ai_info.get('qualities', []):
                        return False
                return True

            # 构建要显示的游戏列表
            if col_app_ids is not None:
                # 如果有家庭组成员且已扫描，使用家庭组拥有的游戏（并集）进行交集
                if _family_codes and _family_scan_done[0] and _family_owned_app_ids:
                    family_set = _family_owned_app_ids
                    intersection = col_app_ids & family_set
                    # 名称：优先从 _library_games 取，其次从游戏名称缓存取
                    lib_name_map = {g['app_id']: g['name'] for g in _library_games}
                    def _get_name(aid):
                        if aid in lib_name_map:
                            return lib_name_map[aid]
                        return self._get_game_name(aid)
                    display_list = [{'app_id': a, 'name': _get_name(a)}
                                    for a in sorted(intersection)]
                else:
                    lib_app_ids = {g['app_id'] for g in _library_games}
                    intersection = col_app_ids & lib_app_ids
                    lib_name_map = {g['app_id']: g['name'] for g in _library_games}
                    display_list = [{'app_id': a, 'name': lib_name_map.get(a, f"AppID {a}")}
                                    for a in sorted(intersection)]

                display_list.sort(key=lambda x: x['name'].lower())
                for idx, g in enumerate(display_list):
                    if ft and ft not in g['name'].lower() and ft not in g['app_id']:
                        continue
                    if not _should_include(g['app_id']):
                        continue
                    _filtered_indices.append(('col', g['app_id'], g['name']))
                    text, has_ai, is_dirty = _make_display(g['app_id'], g['name'])
                    games_listbox.insert(tk.END, text)
                    if is_dirty:
                        games_listbox.itemconfig(games_listbox.size() - 1, fg="#b8860b")
                    elif has_ai:
                        games_listbox.itemconfig(games_listbox.size() - 1, fg="#1a73e8")
            else:
                # 无分类选中 — 默认显示游戏库
                # 如果家庭组已扫描，显示所有成员拥有的游戏（并集）
                if (_family_codes and _family_scan_done[0]
                        and _family_owned_app_ids):
                    lib_name_map = {g['app_id']: g['name'] for g in _library_games}
                    def _get_name_fb(aid):
                        if aid in lib_name_map:
                            return lib_name_map[aid]
                        return self._get_game_name(aid)
                    all_ids = sorted(_family_owned_app_ids)
                    family_display_list = [
                        {'app_id': a, 'name': _get_name_fb(a)} for a in all_ids]
                    family_display_list.sort(key=lambda x: x['name'].lower())
                    for g in family_display_list:
                        if ft and ft not in g['name'].lower() and ft not in g['app_id']:
                            continue
                        if not _should_include(g['app_id']):
                            continue
                        _filtered_indices.append(('col', g['app_id'], g['name']))
                        text, has_ai, is_dirty = _make_display(g['app_id'], g['name'])
                        games_listbox.insert(tk.END, text)
                        if is_dirty:
                            games_listbox.itemconfig(games_listbox.size() - 1, fg="#b8860b")
                        elif has_ai:
                            games_listbox.itemconfig(games_listbox.size() - 1, fg="#1a73e8")
                else:
                    for idx, g in enumerate(_library_games):
                        if ft and ft not in g['name'].lower() and ft not in g['app_id']:
                            continue
                        if not _should_include(g['app_id']):
                            continue
                        _filtered_indices.append(idx)
                        text, has_ai, is_dirty = _make_display(g['app_id'], g['name'])
                        games_listbox.insert(tk.END, text)
                        if is_dirty:
                            games_listbox.itemconfig(games_listbox.size() - 1, fg="#b8860b")
                        elif has_ai:
                            games_listbox.itemconfig(games_listbox.size() - 1, fg="#1a73e8")

            # 统计信息
            if intersection is not None:
                total_in_collection = len(col_app_ids)
                owned_count = len(intersection)
                source_label = "家庭组入库" if (_family_codes and _family_scan_done[0] and _family_owned_app_ids) else "该用户拥有"
                scan_info_label.config(
                    text=f"收藏夹共 {total_in_collection} 款，{source_label} {owned_count} 款"
                         + (f"，筛选 {len(_filtered_indices)} 款" if ft or ai_mode != "全部" else ""),
                    fg="#333"
                )
            elif (_family_codes and _family_scan_done[0]
                  and _family_owned_app_ids
                  and col_app_ids is None):
                # 无分类，显示家庭组并集统计
                total_union = len(_family_owned_app_ids)
                extra = ""
                if ft or ai_mode != "全部":
                    extra = f"，筛选 {len(_filtered_indices)} 款"
                scan_info_label.config(
                    text=f"家庭组所有人的游戏共 {total_union} 款{extra}",
                    fg="#333"
                )
            else:
                extra = ""
                if ft or ai_mode != "全部":
                    extra = f"，筛选 {len(_filtered_indices)} 款"
                scan_info_label.config(
                    text=f"共 {len(_library_games)} 款{extra}",
                    fg="#333"
                )

            # 更新 AI 筛选器下拉选项（加入检测到的模型名）
            all_models = set()
            for info in _ai_notes_map_cache.values():
                for m in info.get('models', []):
                    all_models.add(m)
            filter_values = ["全部", "☁️ 有改动", "🤖 AI 处理过", "📝 未 AI 处理"]
            for m in sorted(all_models):
                filter_values.append(f"🤖 {m}")
            ai_gen_filter_combo['values'] = filter_values

            # 更新确信度筛选器
            _update_conf_filter_visibility(all_confidences)

        def _update_conf_filter_visibility(all_confidences):
            """根据 AI 筛选模式显示/隐藏确信度和质量下拉框"""
            ai_mode = _ai_gen_filter_var.get()
            is_ai_mode = (ai_mode == "🤖 AI 处理过"
                          or (ai_mode.startswith("🤖 ")
                              and ai_mode != "🤖 AI 处理过"))
            if is_ai_mode:
                if not _conf_gen_filter_visible[0]:
                    conf_gen_filter_combo.pack(side=tk.LEFT, padx=(3, 0),
                                              after=ai_gen_filter_combo)
                    _conf_gen_filter_visible[0] = True
                conf_order = ["很高", "较高", "中等", "较低", "很低"]
                conf_gen_filter_combo['values'] = ["全部确信度"] + conf_order
                if not _qual_gen_filter_visible[0]:
                    qual_gen_filter_combo.pack(side=tk.LEFT, padx=(3, 0),
                                              after=conf_gen_filter_combo)
                    _qual_gen_filter_visible[0] = True
            else:
                if _conf_gen_filter_visible[0]:
                    conf_gen_filter_combo.pack_forget()
                    _conf_gen_filter_visible[0] = False
                _conf_gen_filter_var.set("全部确信度")
                if _qual_gen_filter_visible[0]:
                    qual_gen_filter_combo.pack_forget()
                    _qual_gen_filter_visible[0] = False
                _qual_gen_filter_var.set("全部质量")

        def _load_collections():
            nonlocal _collections
            raw = SteamAccountScanner.get_collections(
                self.current_account['userdata_path'])
            # 过滤掉空分类（0 个游戏的分类没意义）
            _collections = [c for c in raw if len(c['app_ids']) > 0]
            names = ["（家庭库所有游戏）"] + [
                f"{c['name']} ({len(c['app_ids'])})" for c in _collections]
            collection_combo['values'] = names
            if _collections:
                scan_info_label.config(
                    text=f"已加载 {len(_collections)} 个分类", fg="#333")

        # 分类变更时刷新列表
        def _on_collection_changed(*_):
            _populate_listbox(search_var.get())
        collection_combo.bind("<<ComboboxSelected>>", _on_collection_changed)

        def do_scan_library():
            scan_info_label.config(text="🔍 正在扫描本地已安装游戏...", fg="#333")
            win.update_idletasks()
            nonlocal _library_games
            _library_games = SteamAccountScanner.scan_library(
                self.current_account['steam_path'])
            if not _library_games:
                scan_info_label.config(
                    text="⚠️ 未扫描到本地游戏", fg="orange")
            _populate_listbox(search_var.get())

        _last_debug_info = {'text': ''}

        def _show_debug_info(info, parent=None):
            _last_debug_info['text'] = info
            dbg_win = tk.Toplevel(parent or win)
            dbg_win.title("🔍 调试信息")
            dbg_win.resizable(True, True)
            dbg_win.grab_set()
            dbg_win.focus_force()
            tk.Label(dbg_win, text="🔍 调试信息",
                     font=("", 12, "bold")).pack(pady=(10, 5))
            tk.Label(dbg_win, text="可选中文本复制，或点击下方按钮复制全部：",
                     font=("", 9), fg="#666").pack(pady=(0, 5))
            def copy_debug():
                dbg_win.clipboard_clear()
                dbg_win.clipboard_append(info)
                messagebox.showinfo("✅", "已复制到剪贴板", parent=dbg_win)
            def close_debug():
                dbg_win.grab_release()
                dbg_win.destroy()
            btn_frame_d = tk.Frame(dbg_win)
            btn_frame_d.pack(side=tk.BOTTOM, pady=(0, 10))
            ttk.Button(btn_frame_d, text="📋 复制", command=copy_debug).pack(
                side=tk.LEFT, padx=5)
            ttk.Button(btn_frame_d, text="关闭", command=close_debug).pack(
                side=tk.LEFT, padx=5)
            dbg_win.protocol("WM_DELETE_WINDOW", close_debug)
            txt = tk.Text(dbg_win, font=("Consolas", 9), width=80, height=25,
                          wrap=tk.WORD)
            txt.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
            txt.insert("1.0", info)
            def _block_edit(event):
                if event.state & 0x4:
                    if event.keysym.lower() in ('a', 'c'):
                        return
                if event.keysym in ('Left', 'Right', 'Up', 'Down',
                                     'Home', 'End', 'Prior', 'Next',
                                     'Shift_L', 'Shift_R', 'Control_L', 'Control_R'):
                    return
                return "break"
            txt.bind("<Key>", _block_edit)

        def do_scan_online():
            skey = saved_steam_key
            sid = steam_id_var.get().strip()
            if not skey:
                messagebox.showwarning("提示",
                    "请在主界面「🔑 AI 配置」中设置 Steam Web API Key。\n"
                    "可从 https://steamcommunity.com/dev/apikey 免费获取。",
                    parent=win)
                return
            if not sid:
                messagebox.showwarning("提示", "请输入 Steam ID 或好友代码。",
                                        parent=win)
                return
            # 清除缓存，强制重新扫描
            self._config.pop('family_library_cache', None)
            _loaded_from_cache[0] = False
            # 计算总扫描步骤数：1（主用户）+ 家庭组成员数
            total_steps = 1 + (len(_family_codes) if _family_codes and skey else 0)
            scan_info_label.config(text="🌐 正在通过 Steam API 获取...", fg="#333")
            _show_scan_progress(
                f"🌐 正在扫描主用户游戏库... (1/{total_steps})", 0, total_steps)
            win.update_idletasks()
            nonlocal _library_games, _family_owned_app_ids
            _family_scan_done[0] = False
            debug_info = "[初始化] 开始在线扫描...\n"
            try:
                debug_info += f"[调用] scan_library_online(sid='{sid}', key='{skey[:6]}...')\n"
                scan_result = SteamAccountScanner.scan_library_online(sid, skey)
                debug_info += f"[返回] type = {type(scan_result)}\n"
                if isinstance(scan_result, tuple) and len(scan_result) == 2:
                    _library_games, scan_debug = scan_result
                    debug_info += scan_debug
                elif isinstance(scan_result, list):
                    _library_games = scan_result
                    debug_info += "[注意] 返回了 list 而非 tuple\n"
                else:
                    _library_games = []
                    debug_info += f"[异常] 返回值类型不符: {type(scan_result)}\n"
                _last_debug_info['text'] = debug_info
                if not _library_games:
                    scan_info_label.config(
                        text="⚠️ 未获取到游戏，检查 ID/Key 或资料可能未公开",
                        fg="orange")
                    _show_debug_info(debug_info, parent=win)
                else:
                    _show_scan_progress(
                        f"✅ 主用户: {len(_library_games)} 款游戏 (1/{total_steps})",
                        1, total_steps)
            except Exception as e:
                import traceback
                tb_str = traceback.format_exc()
                debug_info += f"\n[异常] {type(e).__name__}: {e}\n{tb_str}\n"
                _last_debug_info['text'] = debug_info
                err_display = str(e)
                if hasattr(e, 'code'):
                    err_display = f"HTTP {e.code}"
                    try:
                        err_display += f" — {e.read().decode('utf-8')[:200]}"
                    except Exception:
                        pass
                scan_info_label.config(text=f"❌ 失败: {err_display}", fg="red")
                _library_games = []
                _show_debug_info(debug_info, parent=win)

            # 如果配置了家庭组成员，后台扫描所有成员的游戏库
            if _family_codes and skey:
                _scan_family_members(skey, total_steps)

            # 保存扫描结果到缓存
            if _library_games:
                _save_library_cache()

            _hide_scan_progress()
            _populate_listbox(search_var.get())

        def _scan_family_members(skey, total_steps=None):
            """扫描所有家庭组成员的游戏库，合并到 _family_owned_app_ids（并集），
            同时计算 _family_intersection_app_ids（交集）"""
            nonlocal _family_owned_app_ids, _family_intersection_app_ids
            _family_owned_app_ids = set()
            _family_intersection_app_ids = None
            per_member_sets = []
            total_members = len(_family_codes)
            if total_steps is None:
                total_steps = 1 + total_members
            total_games_fetched = 0
            for i, code in enumerate(_family_codes):
                step = i + 2  # 1 是主用户，从 2 开始
                scan_info_label.config(
                    text=f"🌐 正在扫描家庭组成员 {i+1}/{total_members} (ID: {code})...",
                    fg="#333")
                _show_scan_progress(
                    f"👨‍👩‍👧‍👦 扫描家庭组成员 {i+1}/{total_members} (ID: {code})... "
                    f"已获取 {total_games_fetched} 款",
                    step - 1, total_steps)
                win.update_idletasks()
                member_ids = set()
                try:
                    result = SteamAccountScanner.scan_library_online(code, skey)
                    if isinstance(result, tuple) and len(result) == 2:
                        games, _ = result
                    elif isinstance(result, list):
                        games = result
                    else:
                        games = []
                    for g in games:
                        member_ids.add(g['app_id'])
                        _family_owned_app_ids.add(g['app_id'])
                        # 顺便更新名称缓存
                        if g['app_id'] not in self._game_name_cache:
                            self._game_name_cache[g['app_id']] = g['name']
                    total_games_fetched += len(games)
                    _show_scan_progress(
                        f"✅ 成员 {i+1}/{total_members}: {len(games)} 款 | "
                        f"合计 {total_games_fetched} 款",
                        step, total_steps)
                except Exception as e:
                    print(f"[家庭组] 扫描成员 {code} 失败: {e}")
                    _show_scan_progress(
                        f"❌ 成员 {i+1}/{total_members} (ID: {code}) 扫描失败",
                        step, total_steps)
                per_member_sets.append(member_ids)
            # 计算交集（所有成员都拥有的游戏）
            if per_member_sets:
                _family_intersection_app_ids = set(per_member_sets[0])
                for ms in per_member_sets[1:]:
                    _family_intersection_app_ids &= ms
            else:
                _family_intersection_app_ids = set()
            # 也把当前扫描用户的游戏包含进并集
            for g in _library_games:
                _family_owned_app_ids.add(g['app_id'])
            _family_scan_done[0] = True
            print(f"[家庭组] 扫描完成，并集 {len(_family_owned_app_ids)} 款，"
                  f"交集 {len(_family_intersection_app_ids)} 款")

        def do_select_all():
            games_listbox.select_set(0, tk.END)
            _update_sel_count()

        def do_deselect_all():
            games_listbox.select_clear(0, tk.END)
            _update_sel_count()

        def on_search_changed(*_):
            _populate_listbox(search_var.get())
        search_var.trace_add("write", on_search_changed)

        def _on_ai_gen_filter(*_):
            """AI 筛选或确信度筛选变更时，刷新列表"""
            _populate_listbox(search_var.get())

        ai_gen_filter_combo.bind("<<ComboboxSelected>>", _on_ai_gen_filter)
        conf_gen_filter_combo.bind("<<ComboboxSelected>>", _on_ai_gen_filter)
        qual_gen_filter_combo.bind("<<ComboboxSelected>>", _on_ai_gen_filter)

        def _update_sel_count(event=None):
            n = len(games_listbox.curselection())
            sel_count_label.config(text=f"已选 {n} 款" if n else "")
        games_listbox.bind("<<ListboxSelect>>", _update_sel_count)

        def _on_double_click(event=None):
            """双击游戏条目，弹出笔记预览窗口"""
            sel = games_listbox.curselection()
            if not sel:
                return
            idx = sel[0]
            if idx >= len(_filtered_indices):
                return
            entry = _filtered_indices[idx]
            if isinstance(entry, tuple) and entry[0] == 'col':
                app_id, game_name = entry[1], entry[2]
            else:
                g = _library_games[entry]
                app_id, game_name = g['app_id'], g['name']

            # 读取笔记
            data = self.manager.read_notes(app_id)
            notes_list = data.get("notes", [])
            if not notes_list:
                messagebox.showinfo("无笔记",
                    f"{game_name} (AppID {app_id}) 暂无笔记。",
                    parent=win)
                return

            # 弹出预览窗口
            preview = tk.Toplevel(win)
            preview.title(f"📝 笔记预览 — {game_name}")
            preview.transient(win)
            preview.grab_set()

            def _close_preview():
                preview.grab_release()
                preview.destroy()

            # 标题栏
            hdr = tk.Frame(preview, padx=10, pady=5)
            hdr.pack(fill=tk.X)
            tk.Label(hdr, text=f"🎮 {game_name}",
                     font=("", 12, "bold")).pack(side=tk.LEFT)
            tk.Label(hdr, text=f"AppID: {app_id}",
                     font=("", 9), fg="#666").pack(side=tk.RIGHT)

            # AI 状态摘要
            ai_info = _ai_notes_map_cache.get(app_id, {})
            if ai_info:
                models = ai_info.get('models', [])
                confs = ai_info.get('confidences', [])
                quals = ai_info.get('qualities', [])
                status_parts = []
                if models:
                    status_parts.append(f"模型: {', '.join(models)}")
                if confs:
                    conf_str = ', '.join(
                        f"{CONFIDENCE_EMOJI.get(c, '')} {c}" for c in confs)
                    status_parts.append(f"确信度: {conf_str}")
                if quals:
                    qual_str = ', '.join(
                        f"{QUALITY_EMOJI.get(q, '')} {q}" for q in quals)
                    status_parts.append(f"质量: {qual_str}")
                if status_parts:
                    tk.Label(hdr, text="🤖 " + "  |  ".join(status_parts),
                             font=("", 9), fg="#1a73e8").pack(
                        side=tk.LEFT, padx=(15, 0))

            # 筛选出 AI 笔记和手动笔记
            ai_notes = [n for n in notes_list if is_ai_note(n)]
            manual_notes = [n for n in notes_list if not is_ai_note(n)]

            # 底部按钮（先 pack，保证 side=BOTTOM 优先占位，不被 expand 挤掉）
            btn_f = tk.Frame(preview, padx=10, pady=8)
            btn_f.pack(side=tk.BOTTOM, fill=tk.X)
            ttk.Button(btn_f, text="关闭",
                       command=_close_preview).pack(side=tk.RIGHT)
            preview.protocol("WM_DELETE_WINDOW", _close_preview)

            # 笔记内容区域
            txt_frame = tk.Frame(preview)
            txt_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 5))
            txt = tk.Text(txt_frame, font=("", 10), wrap=tk.WORD,
                          padx=10, pady=10)
            scrollbar = ttk.Scrollbar(txt_frame, orient=tk.VERTICAL,
                                       command=txt.yview)
            txt.config(yscrollcommand=scrollbar.set)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
            txt.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            # 优先显示 AI 笔记
            display_notes = ai_notes if ai_notes else manual_notes
            note_type_label = "AI 笔记" if ai_notes else "手动笔记（无 AI 笔记）"

            for i, note in enumerate(display_notes):
                content = note.get("content", note.get("title", ""))
                is_ai = is_ai_note(note)

                if i > 0:
                    txt.insert(tk.END, "\n" + "─" * 60 + "\n\n")

                tag_prefix = f"note_{i}"
                if is_ai:
                    is_insuf = is_insufficient_info_note(note)
                    conf = extract_ai_confidence_from_note(note)
                    vol = extract_ai_info_volume_from_note(note)
                    src = extract_ai_info_source_from_note(note)
                    emoji = CONFIDENCE_EMOJI.get(conf, "🤖")

                    if is_insuf:
                        txt.insert(tk.END, "⛔ 信息过少",
                                   f"{tag_prefix}_header")
                    else:
                        txt.insert(tk.END, f"{emoji} AI 笔记",
                                   f"{tag_prefix}_header")
                    if conf:
                        txt.insert(tk.END, f"（确信度: {conf}）",
                                   f"{tag_prefix}_header")
                    # 显示信息来源、信息量和质量（新版笔记）
                    meta_parts = []
                    if src == "web":
                        meta_parts.append("📡联网")
                    elif src == "local":
                        meta_parts.append("📚本地")
                    if vol:
                        vol_emoji = INFO_VOLUME_EMOJI.get(vol, "")
                        meta_parts.append(f"信息量:{vol}{vol_emoji}")
                    qual = extract_ai_quality_from_note(note)
                    if qual:
                        q_emoji = QUALITY_EMOJI.get(qual, "")
                        meta_parts.append(f"质量:{qual}{q_emoji}")
                    if meta_parts:
                        txt.insert(tk.END, f" [{' | '.join(meta_parts)}]",
                                   f"{tag_prefix}_meta")
                        txt.tag_config(f"{tag_prefix}_meta",
                                       foreground="#888",
                                       font=("", 9))
                    txt.insert(tk.END, "\n")
                    txt.tag_config(f"{tag_prefix}_header",
                                   foreground="#cc3333" if is_insuf else "#1a73e8",
                                   font=("", 10, "bold"))
                else:
                    txt.insert(tk.END, "📝 手动笔记\n",
                               f"{tag_prefix}_header")
                    txt.tag_config(f"{tag_prefix}_header",
                                   foreground="#333",
                                   font=("", 10, "bold"))

                # 显示内容（去掉 AI 前缀冗余信息，只保留正文）
                display_content = content
                # 先去除 BBCode 标签（content 经过 _wrap_content 包裹了 [p]...[/p]）
                display_content = re.sub(
                    r'\[/?[a-z0-9*]+(?:=[^\]]*)?\]', '', display_content
                ).strip()
                if is_ai:
                    # 新版前缀格式（含信息来源、信息量和游戏质量）
                    m = re.match(
                        r'🤖AI:\s*(?:⛔信息过少\s*)?'
                        r'(?:(?:📡联网检索|📚训练数据与Steam评测)\s*\|\s*)?'
                        r'(?:相关信息量[：:]\s*(?:相当多|较多|中等|较少|相当少)[🟢🔵🟡🟠🔴]?\s*(?:\|\s*)?)?'
                        r'(?:游戏总体质量[：:]\s*(?:相当好|较好|中等|较差|相当差)[💎✨➖👎💀]?\s*)?'
                        r'(?:⚠️\s*)?'
                        r'(?:以下内容由.+?确信程度[：:]\s*(?:很高|较高|中等|较低|很低)[🟢🔵🟡🟠🔴]?[。.]\s*)?',
                        display_content)
                    if m and m.end() > 0:
                        display_content = display_content[m.end():]
                    # 兼容旧版前缀格式（无信息来源和信息量）
                    if not m or m.end() == 0:
                        m_old = re.match(
                            r'🤖AI:\s*⚠️\s*以下内容由.+?确信程度[：:]\s*(?:很高|较高|中等|较低|很低)[。.]\s*',
                            display_content)
                        if m_old:
                            display_content = display_content[m_old.end():]
                txt.insert(tk.END, display_content.strip() + "\n")

            txt.config(state=tk.DISABLED)

            # 自适应窗口大小
            preview.update_idletasks()
            # 基于内容计算合适的高度，限制在合理范围内
            content_len = sum(len(n.get("content", "")) for n in display_notes)
            ideal_h = min(max(250, content_len // 2 + 150), 600)
            preview.geometry(f"700x{ideal_h}")
            # 居中
            preview.update_idletasks()
            pw, ph = preview.winfo_width(), preview.winfo_height()
            sx, sy = preview.winfo_screenwidth(), preview.winfo_screenheight()
            preview.geometry(f"+{(sx - pw) // 2}+{(sy - ph) // 2}")

        games_listbox.bind("<Double-1>", _on_double_click)

        # ═══════ 绑定按钮（所有函数已定义） ═══════

        ttk.Button(scan_btn_row1, text="🌐 在线扫描（不含免费游戏）",
                   command=do_scan_online).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(scan_btn_row1, text="📂 本地扫描（仅已安装）",
                   command=do_scan_library).pack(side=tk.LEFT, padx=(0, 3))

        # 按钮行2（调试+全选+取消全选）— 拆分为两行避免溢出
        scan_btn_row2 = tk.Frame(scan_container)
        scan_btn_row2.pack(fill=tk.X, pady=(1, 0))
        ttk.Button(scan_btn_row2, text="🔍 调试信息",
                   command=lambda: _show_debug_info(
                       _last_debug_info['text'] or "尚未执行在线扫描",
                       parent=win)).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(scan_btn_row2, text="全选",
                   command=do_select_all).pack(side=tk.LEFT, padx=(0, 3))
        ttk.Button(scan_btn_row2, text="取消全选",
                   command=do_deselect_all).pack(side=tk.LEFT, padx=(0, 3))

        sel_count_label = tk.Label(scan_btn_row2, text="", font=("", 9), fg="#666")
        sel_count_label.pack(side=tk.LEFT, padx=5)

        ttk.Button(collection_frame, text="🔄 刷新分类",
                   command=_load_collections).pack(side=tk.LEFT, padx=5)

        # ── 模式2: 手动输入 ──
        manual_container = tk.Frame(games_frame)

        tk.Label(manual_container,
                 text="每行一个: AppID 或 AppID:游戏名",
                 font=("", 9), fg="#555").pack(anchor=tk.W)
        games_text = tk.Text(manual_container, font=("Courier", 10), height=10,
                              wrap=tk.WORD)
        games_text.pack(fill=tk.BOTH, expand=True, pady=5)
        sel_id = self._get_selected_app_id()
        if sel_id:
            games_text.insert("1.0", f"{sel_id}\n")
        tk.Label(manual_container,
                 text="示例:  1245620:Elden Ring\n"
                      "       367520\n"
                      "       1086940:Baldur's Gate 3",
                 font=("Courier", 9), fg="#888", justify=tk.LEFT).pack(anchor=tk.W)

        def _switch_games_mode(mode):
            if mode == 1:
                manual_container.pack_forget()
                scan_container.pack(fill=tk.BOTH, expand=True)
            else:
                scan_container.pack_forget()
                manual_container.pack(fill=tk.BOTH, expand=True)

        # 模式切换按钮（在 _switch_games_mode 定义后创建）
        tk.Radiobutton(mode_frame, text="📚 从 Steam 库选择",
                       variable=games_mode_var, value=1, font=("", 9),
                       command=lambda: _switch_games_mode(1)).pack(side=tk.LEFT)
        tk.Radiobutton(mode_frame, text="✏️ 手动输入 AppID",
                       variable=games_mode_var, value=2, font=("", 9),
                       command=lambda: _switch_games_mode(2)).pack(side=tk.LEFT, padx=(10, 0))

        # 首次自动加载分类（所有 widget 已创建）
        _load_collections()

        # 首次自动加载：优先从缓存加载，否则在线扫描，最后本地扫描
        if saved_steam_key and steam_id_var.get().strip():
            if _try_load_library_cache():
                # 从缓存加载成功
                n = len(_library_games)
                f = len(_family_owned_app_ids)
                scan_info_label.config(
                    text=f"📦 已从缓存加载（{n} 款，家庭库 {f} 款）— 点击「在线扫描」刷新",
                    fg="#666")
                _populate_listbox(search_var.get())
            else:
                # 缓存不可用，自动触发在线扫描
                win.after(100, do_scan_online)
        else:
            # 否则触发本地扫描
            do_scan_library()

        # ═══════ 隐蔽调试：Ctrl+Shift+D 打开 AI 笔记识别调试面板 ═══════
        def _debug_ai_detection(event=None):
            """调试面板：显示所有笔记的 AI 识别结果"""
            dbg = "[AI 笔记识别调试]\n"
            dbg += f"notes_dir = {self.manager.notes_dir}\n\n"

            # 第一步：扫描所有笔记，找出 AI 笔记
            ai_map = self.manager.scan_ai_notes()
            dbg += f"=== 扫描结果：{len(ai_map)} 个游戏有 AI 笔记 ===\n\n"

            # 第二步：列出所有检测到的 AI 模型
            all_models = set()
            for info in ai_map.values():
                for m in info.get('models', []):
                    all_models.add(m)
            if all_models:
                dbg += f"检测到的 AI 模型: {', '.join(sorted(all_models))}\n\n"
            else:
                dbg += "未检测到任何 AI 模型名\n\n"

            # 第三步：列出 AI 笔记详情
            if ai_map:
                dbg += "── AI 笔记详情 ──\n"
                for app_id, info in sorted(ai_map.items()):
                    dbg += (f"  AppID {app_id}: "
                            f"{info['note_count']} 条 AI 笔记, "
                            f"模型={info['models']}\n")
                dbg += "\n"

            # 第四步：列出未被识别的笔记（供排查）
            dbg += "── 非 AI 笔记采样（前 10 个） ──\n"
            sample_count = 0
            for f in sorted(os.listdir(self.manager.notes_dir)):
                if sample_count >= 10:
                    break
                fp = os.path.join(self.manager.notes_dir, f)
                if not f.startswith("notes_") or not os.path.isfile(fp):
                    continue
                app_id = f.replace("notes_", "")
                if app_id in ai_map:
                    continue  # 跳过已检测为 AI 的
                try:
                    with open(fp, "r", encoding="utf-8") as fh:
                        data = json.load(fh)
                    notes = data.get("notes", [])
                    if not notes:
                        continue
                    title = notes[0].get("title", "")
                    title_hex = ' '.join(f'U+{ord(c):04X}' for c in title[:15])
                    dbg += (f"  AppID {app_id}: title[:60]={title[:60]!r}\n"
                            f"    hex[:15]={title_hex}\n")
                    sample_count += 1
                except Exception:
                    continue
            _show_debug_info(dbg, parent=win)
        win.bind("<Control-Shift-D>", _debug_ai_detection)
        win.bind("<Control-Shift-d>", _debug_ai_detection)

        # ═══════════════ 下半部分：进度区 ═══════════════
        bottom_panel = tk.Frame(main_paned)
        main_paned.add(bottom_panel, minsize=140)

        progress_frame = tk.LabelFrame(bottom_panel, text="进度", font=("", 10),
                                        padx=8, pady=3)
        progress_frame.pack(fill=tk.BOTH, expand=True)

        progress_top = tk.Frame(progress_frame)
        progress_top.pack(fill=tk.X)

        progress_var = tk.StringVar(value="等待开始...")
        tk.Label(progress_top, textvariable=progress_var, font=("", 9),
                 fg="#333").pack(side=tk.LEFT)

        progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        progress_bar.pack(fill=tk.X, pady=2)

        log_text = tk.Text(progress_frame, font=("Courier", 9), height=5,
                            state=tk.DISABLED, bg="#f8f8f8")
        log_text.pack(fill=tk.BOTH, expand=True, pady=(0, 2))

        def log(msg):
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, msg + "\n")
            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)

        # ── 底部按钮栏（含全局选项，两种模式下均可见）──
        btn_frame = tk.Frame(win, padx=10)
        btn_frame.pack(fill=tk.X, pady=(2, 6))

        # 第一行：全局选项
        options_row = tk.Frame(btn_frame)
        options_row.pack(fill=tk.X, pady=(0, 2))

        skip_existing_var = tk.BooleanVar(value=True)
        tk.Checkbutton(options_row, text="✅ 跳过已有 AI 笔记（取消则替换旧笔记）",
                        variable=skip_existing_var, font=("", 9)).pack(
            side=tk.LEFT, padx=(0, 15))

        web_search_var = tk.BooleanVar(value=False)
        ws_cb = tk.Checkbutton(
            options_row, text="🔍 联网搜索",
            variable=web_search_var, font=("", 9))
        ws_cb.pack(side=tk.LEFT)
        # 说明文字（不再锁定勾选框，仅提示）
        _cur_prov = _get_current_provider()
        _cur_url = current_token[0].get("api_url", "")
        if _cur_prov == 'anthropic' and not _cur_url:
            ws_tip = "（Anthropic 官方 API 额外收费 $10/1000次）"
        else:
            ws_tip = "（是否可用取决于 API 服务商）"
        tk.Label(options_row, text=ws_tip, font=("", 8),
                 fg="#888").pack(
            side=tk.LEFT, padx=(2, 0))

        # 第二行：按钮
        btn_row = tk.Frame(btn_frame)
        btn_row.pack(fill=tk.X)

        is_running = [False]
        is_paused = [False]
        is_stopped = [False]
        _worker_idle = [True]  # True when no worker thread is actively processing
        _remaining_queue = []  # 暂停时保存剩余队列

        def _save_queue(queue, token_idx, skip_existing, web_search):
            """保存未完成队列到配置"""
            self._config["ai_batch_queue"] = [[a, n] for a, n in queue]
            self._config["ai_batch_token_idx"] = token_idx
            self._config["ai_batch_skip_existing"] = skip_existing
            self._config["ai_batch_web_search"] = web_search
            self._save_config(self._config)

        def _clear_saved_queue():
            """清除已保存的队列"""
            for k in ("ai_batch_queue", "ai_batch_token_idx",
                      "ai_batch_skip_existing", "ai_batch_web_search"):
                self._config.pop(k, None)
            self._save_config(self._config)

        def _update_ctrl_buttons():
            """根据运行状态更新按钮可用性和文字"""
            if is_running[0] and not is_paused[0]:
                gen_btn.config(state=tk.DISABLED)
                pause_btn.config(state=tk.NORMAL, text="⏸️ 暂停")
                stop_btn.config(state=tk.NORMAL)
            elif is_running[0] and is_paused[0]:
                gen_btn.config(state=tk.DISABLED)
                pause_btn.config(state=tk.NORMAL, text="▶️ 继续")
                stop_btn.config(state=tk.NORMAL)
            else:
                gen_btn.config(state=tk.NORMAL)
                pause_btn.config(state=tk.DISABLED, text="⏸️ 暂停")
                stop_btn.config(state=tk.DISABLED)

        def do_pause():
            if not is_running[0]:
                return
            if is_paused[0]:
                # 继续 — 从保存的队列重新启动
                is_paused[0] = False
                resume_list = list(_remaining_queue)
                if not resume_list:
                    # 尝试从配置恢复
                    sq = self._config.get("ai_batch_queue", [])
                    resume_list = [(a, n) for a, n in sq]
                if resume_list:
                    is_running[0] = False  # reset so _start_generation can set it
                    _update_ctrl_buttons()
                    log("▶️ 继续生成...")
                    _start_generation(resume_list)
                else:
                    is_running[0] = False
                    _update_ctrl_buttons()
                    progress_var.set("队列为空")
            else:
                # 暂停
                is_paused[0] = True
                _update_ctrl_buttons()
                progress_var.set("⏸️ 正在暂停（等待当前游戏完成）...")
                log("⏸️ 正在暂停...")

        def do_stop():
            if not is_running[0]:
                return
            is_stopped[0] = True
            is_paused[0] = False
            _clear_saved_queue()
            progress_var.set("⏹️ 正在停止...")
            log("⏹️ 正在停止...（等待当前游戏完成）")

        def _start_generation(games_list):
            """启动生成线程（from do_generate or resume）"""
            is_running[0] = True
            is_paused[0] = False
            is_stopped[0] = False
            _worker_idle[0] = False
            _remaining_queue.clear()
            _remaining_queue.extend(games_list)
            _update_ctrl_buttons()
            progress_bar["maximum"] = len(games_list)
            progress_bar["value"] = 0
            total = len(games_list)

            api_key = _get_current_key()
            pkey = _get_current_provider()
            custom_url = _get_current_url()
            current_model = _get_current_model()

            def worker():
                generator = SteamAIGenerator(
                    api_key, current_model,
                    provider=pkey, api_url=custom_url)
                custom_prompt = prompt_text.get("1.0", tk.END).strip()
                success_count = 0
                fail_count = 0
                processed = 0

                while _remaining_queue:
                    # ── 检查停止 ──
                    if is_stopped[0]:
                        win.after(0, lambda s=success_count, f=fail_count: (
                            log(f"⏹️ 已停止。成功 {s} / 失败 {f}"),))
                        break

                    # ── 检查暂停：保存队列并退出线程 ──
                    if is_paused[0]:
                        _save_queue(
                            _remaining_queue, active_token_idx[0],
                            skip_existing_var.get(), web_search_var.get())
                        def _on_paused(s=success_count, f=fail_count, r=len(_remaining_queue)):
                            progress_var.set(f"⏸️ 已暂停 — 完成 {s}，失败 {f}，剩余 {r}")
                            log(f"⏸️ 已暂停，剩余 {r} 款待处理（已保存，可关闭窗口稍后继续）")
                            _populate_listbox(search_var.get())
                        win.after(0, _on_paused)
                        # 保持 is_running=True 以便"继续"按钮可用
                        _worker_idle[0] = True
                        return

                    aid, name = _remaining_queue[0]
                    idx = processed
                    win.after(0, lambda i=idx, a=aid, t=total: (
                        progress_var.set(f"正在处理 {i+1}/{t}: AppID {a}..."),
                        progress_bar.configure(value=i)
                    ))

                    if not name:
                        win.after(0, lambda a=aid: log(f"🔍 查询 AppID {a} 的游戏名..."))
                        try:
                            name = SteamAIGenerator.get_game_name_from_steam(aid)
                        except Exception:
                            name = f"AppID {aid}"

                    # 获取游戏详细信息作为 AI 参考资料
                    win.after(0, lambda a=aid, n=name: log(f"📋 获取 {n} 的详细信息..."))
                    game_context = ""
                    try:
                        details = SteamAIGenerator.get_game_details_from_steam(aid)
                        if details:
                            game_context = SteamAIGenerator.format_game_context(details)
                            if details.get("name") and name.startswith("AppID"):
                                name = details["name"]
                    except Exception:
                        pass

                    # 获取 Steam 玩家评测
                    win.after(0, lambda a=aid, n=name: log(
                        f"💬 获取 {n} 的玩家评测..."))
                    try:
                        reviews_data = (
                            SteamAIGenerator.get_game_reviews_from_steam(aid))
                        if reviews_data:
                            review_ctx = (
                                SteamAIGenerator.format_review_context(
                                    reviews_data))
                            if review_ctx:
                                game_context = (
                                    (game_context + "\n\n" + review_ctx)
                                    if game_context else review_ctx)
                    except Exception:
                        pass

                    # 是否启用联网搜索
                    _use_ws = web_search_var.get()

                    win.after(0, lambda a=aid, n=name, ws=_use_ws: log(
                        f"🤖 生成中: {n} (AppID {a})"
                        f"{' [🔍联网]' if ws else ''}..."))

                    try:
                        content, actual_model, confidence, info_volume, is_insufficient, quality = generator.generate_note(
                            name, aid, extra_context=game_context,
                            system_prompt=custom_prompt,
                            use_web_search=_use_ws)

                        # 构建信息来源和信息量标注
                        conf_emoji = CONFIDENCE_EMOJI.get(confidence, "")
                        vol_emoji = INFO_VOLUME_EMOJI.get(info_volume, "")
                        qual_emoji = QUALITY_EMOJI.get(quality, "")
                        if _use_ws:
                            info_source_tag = INFO_SOURCE_WEB
                        else:
                            info_source_tag = INFO_SOURCE_LOCAL

                        if is_insufficient:
                            # ── 信息过少：生成标注性笔记 ──
                            flat_content = (
                                f"🤖AI: {INSUFFICIENT_INFO_MARKER} "
                                f"{info_source_tag} | "
                                f"相关信息量：{info_volume}{vol_emoji} "
                                f"该游戏相关信息过少，无法生成有效的游戏说明。"
                                f"（由 {actual_model} 判定）")
                            self.manager.create_note(aid, flat_content, flat_content)
                            win.after(0, lambda a=aid, n=name, v=info_volume: log(
                                f"⛔ 信息过少: {n} (AppID {a}) "
                                f"[信息量: {v}] — 已生成标注性笔记"))
                            success_count += 1
                        elif content.strip():
                            flat_content = ' '.join(content.strip().splitlines())
                            flat_content = re.sub(
                                r'\[/?[a-z0-9*]+(?:=[^\]]*)?\]', '', flat_content)
                            flat_content = flat_content.strip()
                            ai_prefix = (
                                f"🤖AI: {info_source_tag} | "
                                f"相关信息量：{info_volume}{vol_emoji} | "
                                f"游戏总体质量：{quality}{qual_emoji} "
                                f"⚠️ 以下内容由 {actual_model} 生成，"
                                f"该模型对以下内容的确信程度："
                                f"{confidence}{conf_emoji}。")
                            flat_content = f"{ai_prefix} {flat_content}"

                            # 未跳过时自动替换旧 AI 笔记
                            if not skip_existing_var.get():
                                data = self.manager.read_notes(aid)
                                notes_list = data.get("notes", [])
                                had_old = False
                                for ni in reversed(range(len(notes_list))):
                                    if is_ai_note(notes_list[ni]):
                                        notes_list.pop(ni)
                                        had_old = True
                                if had_old:
                                    data["notes"] = notes_list
                                    self.manager.write_notes(aid, data)

                            self.manager.create_note(aid, flat_content, flat_content)
                            win.after(0, lambda a=aid, n=name, c=confidence, v=info_volume, q=quality: log(
                                f"✅ 完成: {n} (AppID {a}) "
                                f"[确信: {c}] [信息量: {v}] [质量: {q}]"))
                            success_count += 1
                        else:
                            win.after(0, lambda a=aid: log(
                                f"⚠️ AppID {a}: API 返回空内容"))
                            fail_count += 1
                    except urllib.error.HTTPError as e:
                        error_body = ""
                        try:
                            error_body = e.read().decode("utf-8")
                        except Exception:
                            pass
                        # 构建完整调试信息
                        debug_info = getattr(generator, '_last_debug_info', '(无调试信息)')
                        debug_info += (
                            f"\n--- 错误响应 ---\n"
                            f"HTTP 状态码: {e.code}\n"
                            f"错误原因: {e.reason}\n"
                            f"响应头: {dict(e.headers) if e.headers else '(无)'}\n"
                            f"响应体: {error_body[:500]}\n"
                        )
                        win.after(0, lambda a=aid, err=e, body=error_body, dbg=debug_info:
                                  log(f"❌ AppID {a}: HTTP {err.code} — {body[:200]}\n"
                                      f"--- 调试信息 ---\n{dbg}"))
                        fail_count += 1
                        if e.code == 401:
                            # 认证失败 — 给出具体排查建议
                            hint = "💡 401 认证失败排查：\n"
                            if custom_url:
                                hint += ("  · 当前使用第三方代理/中转 URL\n"
                                         "  · 请确认 API Key 对该代理有效（未过期、额度充足）\n"
                                         "  · 检查代理是否支持当前模型: "
                                         f"{current_model}\n")
                            else:
                                hint += ("  · 请检查 API Key 是否有效（未过期、未撤销）\n"
                                         "  · 确认 Key 有访问该模型的权限\n")
                            win.after(0, lambda h=hint: log(h))
                            break  # 认证失败无需重试后续游戏
                        elif e.code == 429:
                            win.after(0, lambda: log("⏳ 触发限速，等待 60 秒..."))
                            time.sleep(60)
                            # 不弹出队列头，重试当前游戏
                            continue
                    except urllib.error.URLError as e:
                        debug_info = getattr(generator, '_last_debug_info', '(无调试信息)')
                        win.after(0, lambda a=aid, err=e, dbg=debug_info:
                                  log(f"❌ AppID {a}: 连接错误 — {err}\n"
                                      f"--- 调试信息 ---\n{dbg}"))
                        fail_count += 1
                    except Exception as e:
                        win.after(0, lambda a=aid, err=e: log(f"❌ AppID {a}: {err}"))
                        fail_count += 1

                    # 成功或失败都弹出队头
                    _remaining_queue.pop(0)
                    processed += 1

                    if _remaining_queue and not is_stopped[0]:
                        time.sleep(2)

                def finish():
                    _clear_saved_queue()
                    progress_bar["value"] = progress_bar["maximum"]
                    if is_stopped[0]:
                        progress_var.set(
                            f"⏹️ 已停止 — 成功 {success_count} / 失败 {fail_count}")
                    else:
                        progress_var.set(
                            f"完成！成功 {success_count} / 失败 {fail_count}")
                    log(f"\n{'='*40}")
                    log(f"✅ 成功: {success_count}  ❌ 失败: {fail_count}")
                    is_running[0] = False
                    is_stopped[0] = False
                    _worker_idle[0] = True
                    _update_ctrl_buttons()
                    _populate_listbox(search_var.get())
                    self._refresh_games_list()

                # 只有非暂停退出时才 finish
                if not is_paused[0]:
                    win.after(0, finish)

            thread = threading.Thread(target=worker, daemon=True)
            thread.start()

        def do_generate():
            if is_running[0]:
                return

            api_key = _get_current_key()
            if not api_key:
                messagebox.showwarning("提示",
                    "当前令牌未配置 API Key，请在「🔑 AI 配置」中设置。", parent=win)
                return

            games_list = []
            if games_mode_var.get() == 1:
                selected = games_listbox.curselection()
                if not selected:
                    messagebox.showwarning("提示",
                        "请先扫描 Steam 库或选择分类，然后选择至少一个游戏。", parent=win)
                    return
                for sel_idx in selected:
                    if sel_idx < len(_filtered_indices):
                        entry = _filtered_indices[sel_idx]
                        if isinstance(entry, tuple) and entry[0] == 'col':
                            games_list.append((entry[1], entry[2]))
                        else:
                            real_idx = entry
                            g = _library_games[real_idx]
                            games_list.append((g['app_id'], g['name']))
            else:
                raw_lines = games_text.get("1.0", tk.END).strip().split('\n')
                for line in raw_lines:
                    line = line.strip()
                    if not line:
                        continue
                    if ':' in line:
                        parts = line.split(':', 1)
                        aid = parts[0].strip()
                        name = parts[1].strip()
                    else:
                        aid = line
                        name = ""
                    if aid:
                        games_list.append((aid, name))

            if not games_list:
                messagebox.showwarning("提示", "请至少选择一个游戏。", parent=win)
                return

            if skip_existing_var.get():
                filtered = []
                for aid, name in games_list:
                    existing = self.manager.read_notes(aid).get("notes", [])
                    has_ai_note = any(is_ai_note(n) for n in existing)
                    if has_ai_note:
                        log(f"⏭️ 跳过 AppID {aid} (已有 AI 笔记)")
                    else:
                        filtered.append((aid, name))
                games_list = filtered

            if not games_list:
                messagebox.showinfo("提示", "所有游戏都已有笔记。", parent=win)
                return

            _start_generation(games_list)

        gen_btn = ttk.Button(btn_row, text="🚀 开始生成", command=do_generate)
        gen_btn.pack(side=tk.LEFT, padx=3)
        pause_btn = ttk.Button(btn_row, text="⏸️ 暂停", command=do_pause,
                               state=tk.DISABLED)
        pause_btn.pack(side=tk.LEFT, padx=3)
        stop_btn = ttk.Button(btn_row, text="⏹️ 停止", command=do_stop,
                              state=tk.DISABLED)
        stop_btn.pack(side=tk.LEFT, padx=3)

        # ── 云同步按钮 ──
        def _ai_cloud_upload_selected():
            """上传 AI 批量生成界面中选中游戏的笔记"""
            if not self.cloud_uploader or not self.cloud_uploader.initialized:
                messagebox.showwarning("提示", "请先点击上方「☁️ 连接 Steam Cloud」按钮。", parent=win)
                return
            selected = games_listbox.curselection()
            if not selected:
                messagebox.showinfo("提示", "请先选择要上传的游戏。", parent=win)
                return
            ok = fail = 0
            for sel_idx in selected:
                if sel_idx < len(_filtered_indices):
                    entry = _filtered_indices[sel_idx]
                    if isinstance(entry, tuple) and entry[0] == 'col':
                        aid = entry[1]
                    else:
                        aid = _library_games[entry]['app_id']
                    if self.manager.is_dirty(aid):
                        if self.manager.cloud_upload(aid):
                            ok += 1
                        else:
                            fail += 1
            _populate_listbox(search_var.get())
            self._refresh_games_list()
            self._save_uploaded_hashes()
            if ok + fail == 0:
                messagebox.showinfo("提示", "选中的游戏没有需要上传的改动。", parent=win)
            elif fail == 0:
                messagebox.showinfo("✅ 成功", f"已上传 {ok} 个游戏。", parent=win)
            else:
                messagebox.showwarning("⚠️", f"成功 {ok}，失败 {fail}。", parent=win)

        def _ai_cloud_upload_all():
            """上传所有有改动的笔记"""
            if not self.cloud_uploader or not self.cloud_uploader.initialized:
                messagebox.showwarning("提示", "请先点击上方「☁️ 连接 Steam Cloud」按钮。", parent=win)
                return
            n = self.manager.dirty_count()
            if n == 0:
                messagebox.showinfo("提示", "没有需要上传的改动。", parent=win)
                return
            ok, fail = self.manager.cloud_upload_all_dirty()
            _populate_listbox(search_var.get())
            self._refresh_games_list()
            self._save_uploaded_hashes()
            if fail == 0:
                messagebox.showinfo("✅ 成功",
                                    f"已上传 {ok} 个游戏的笔记到 Steam Cloud。\n\n"
                                    "💡 这些改动仍需等待 Steam 客户端自动同步到云端。",
                                    parent=win)
            else:
                messagebox.showwarning("⚠️ 部分失败",
                                        f"成功 {ok} 个，失败 {fail} 个。", parent=win)

        ttk.Button(btn_row, text="☁️上传选中",
                   command=_ai_cloud_upload_selected).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_row, text="☁️全部上传",
                   command=_ai_cloud_upload_all).pack(side=tk.LEFT, padx=5)

        def _smart_close():
            """关闭窗口前检查运行状态和未上传笔记"""
            # 如果正在生成且未暂停，先暂停
            if is_running[0] and not is_paused[0]:
                is_paused[0] = True
                _worker_idle[0] = False
                _update_ctrl_buttons()
                progress_var.set("⏸️ 正在暂停（等待当前游戏完成后关闭）...")
                log("⏸️ 正在暂停以便关闭...")
                def _wait_and_close():
                    if not _worker_idle[0]:
                        win.after(200, _wait_and_close)
                        return
                    _do_close_checks()
                win.after(200, _wait_and_close)
                return
            _do_close_checks()

        def _do_close_checks():
            """执行关闭前的脏数据检查"""
            dirty_n = self.manager.dirty_count()
            if dirty_n > 0:
                ans = messagebox.askyesnocancel(
                    "☁️ 未上传的笔记",
                    f"有 {dirty_n} 个游戏的笔记尚未上传到 Steam Cloud。\n\n"
                    "是否在关闭前一键上传？\n\n"
                    "「是」→ 上传后关闭\n"
                    "「否」→ 不上传，直接关闭（本地文件已保存）\n"
                    "「取消」→ 返回",
                    parent=win)
                if ans is None:
                    # 取消 → 不关闭
                    return
                if ans:
                    # 是 → 尝试上传
                    if not (self.cloud_uploader and self.cloud_uploader.initialized):
                        # 自动尝试连接
                        progress_var.set("☁️ 正在自动连接 Steam Cloud...")
                        win.update_idletasks()
                        uploader = SteamCloudUploader()
                        steam_path = self.current_account.get('steam_path', '')
                        ok, msg = uploader.auto_init(steam_path)
                        if ok:
                            # 检查账号匹配
                            logged_in = uploader.logged_in_friend_code
                            selected = self.current_account.get(
                                'friend_code', '')
                            if logged_in and logged_in != selected:
                                selected_name = self.current_account.get(
                                    'persona_name', selected)
                                uploader.shutdown()
                                messagebox.showerror("❌ 账号不匹配，已拒绝连接",
                                    f"Steam 登录账号 (ID: {logged_in}) ≠ "
                                    f"程序选择的「{selected_name}」\n\n"
                                    f"请先在 Steam 客户端切换到正确账号后手动连接上传。",
                                    parent=win)
                                return  # 返回窗口
                            self.cloud_uploader = uploader
                            self.manager.cloud_uploader = uploader
                            _update_ai_cloud_status()
                            try:
                                self._update_cloud_status_display()
                            except Exception:
                                pass
                        else:
                            messagebox.showerror("❌ 连接失败",
                                f"无法自动连接 Steam Cloud:\n{msg}\n\n"
                                "请手动连接后再上传，或选择直接关闭。",
                                parent=win)
                            return  # 返回窗口
                    # 上传
                    ok_n, fail_n = self.manager.cloud_upload_all_dirty()
                    self._save_uploaded_hashes()
                    if fail_n > 0:
                        messagebox.showwarning("⚠️ 部分上传失败",
                            f"成功 {ok_n}，失败 {fail_n}。\n失败的笔记仍保留在本地。",
                            parent=win)
                    else:
                        log(f"☁️ 已上传 {ok_n} 个游戏的笔记")
            # 关闭
            try:
                self._refresh_games_list()
                self._update_cloud_status_display()
            except Exception:
                pass
            win.grab_release()
            win.destroy()

        ttk.Button(btn_row, text="关闭", command=_smart_close).pack(
            side=tk.RIGHT, padx=5)

        win.protocol("WM_DELETE_WINDOW", _smart_close)

        # 窗口打开时自动扫描已由上方条件逻辑处理

        # ── 检查是否有上次暂停保存的队列 ──
        saved_queue = self._config.get("ai_batch_queue", [])
        if saved_queue:
            n_saved = len(saved_queue)
            saved_tidx = self._config.get("ai_batch_token_idx", 0)
            saved_skip = self._config.get("ai_batch_skip_existing", True)
            saved_ws = self._config.get("ai_batch_web_search", False)
            ans = messagebox.askyesno(
                "▶️ 继续上次任务",
                f"检测到上次暂停的生成队列，还剩 {n_saved} 款游戏待处理。\n\n"
                "是否从断点继续？\n\n"
                "「是」→ 恢复令牌和选项，继续生成\n"
                "「否」→ 放弃队列，重新开始",
                parent=win)
            if ans:
                # 恢复令牌和选项
                if saved_tidx < len(all_tokens):
                    active_token_idx[0] = saved_tidx
                    current_token[0] = all_tokens[saved_tidx]
                    _token_select_var.set(
                        token_names[saved_tidx] if saved_tidx < len(token_names) else "")
                    _update_token_detail()
                skip_existing_var.set(saved_skip)
                web_search_var.set(saved_ws)
                # 恢复队列并启动
                resume_list = [(a, n) for a, n in saved_queue]
                log(f"▶️ 恢复上次暂停的队列：{n_saved} 款游戏")
                win.after(300, lambda: _start_generation(resume_list))
            else:
                _clear_saved_queue()

        self._center_window(win)

    # ────────────────────── 导入 ──────────────────────

