"""API 配置、缓存管理、关于 等设置对话框 (Mixin)"""

import os
import platform
import webbrowser
import tkinter as tk
from tkinter import messagebox, ttk

from ai_generator import SteamAIGenerator


class SettingsMixin:
    """API Key 设置、缓存管理、关于 等 UI 方法"""

    def _ui_api_key_settings(self):
        """API Key 与 AI 配置管理窗口 — 支持多令牌管理"""
        win = tk.Toplevel(self.root)
        win.title("🔑 API Key 与 AI 配置")
        win.resizable(False, False)
        win.grab_set()

        tk.Label(win, text="🔑 API Key 与 AI 配置", font=("", 13, "bold")).pack(pady=(15, 5))
        config_info_frame = tk.Frame(win)
        config_info_frame.pack(pady=(0, 5))
        tk.Label(config_info_frame, text="管理多个 AI 令牌，在 AI 生成页面可自由切换。",
                 font=("", 9), fg="#666").pack()
        config_path_row = tk.Frame(config_info_frame)
        config_path_row.pack()
        tk.Label(config_path_row, text="配置存储于: ",
                 font=("", 9), fg="#666").pack(side=tk.LEFT)
        config_link = tk.Label(config_path_row, text="~/.steam_notes_gen/",
                               font=("", 9, "underline"), fg="#4a90d9", cursor="hand2")
        config_link.pack(side=tk.LEFT)
        config_link.bind("<Button-1>", lambda e: self._open_config_dir())

        # ══════════ 已保存的令牌列表 ══════════
        tokens_frame = tk.LabelFrame(win, text="🔑 已保存的 AI 令牌", font=("", 10),
                                      padx=10, pady=5)
        tokens_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

        tokens_data = list(self._get_ai_tokens())  # 可变副本
        active_idx = [self._get_active_token_index()]

        tokens_listbox = tk.Listbox(tokens_frame, font=("", 9), height=4,
                                     exportselection=False)
        tokens_listbox.pack(fill=tk.X, pady=(0, 5))

        def _refresh_token_list():
            tokens_listbox.delete(0, tk.END)
            for i, t in enumerate(tokens_data):
                prefix = "★ " if i == active_idx[0] else "   "
                key_preview = t.get("key", "")
                if len(key_preview) > 10:
                    key_preview = key_preview[:6] + "..." + key_preview[-4:]
                prov_name = SteamAIGenerator.PROVIDERS.get(
                    t.get("provider", ""), {}).get("name", t.get("provider", ""))
                tokens_listbox.insert(tk.END,
                    f"{prefix}{t.get('name', '未命名')}  |  {prov_name}  |  "
                    f"{t.get('model', '')}  |  Key: {key_preview}")
                if i == active_idx[0]:
                    tokens_listbox.itemconfig(i, fg="#1a73e8")

        _refresh_token_list()

        tokens_btn_row = tk.Frame(tokens_frame)
        tokens_btn_row.pack(fill=tk.X)

        def _delete_token():
            sel = tokens_listbox.curselection()
            if not sel:
                messagebox.showwarning("提示", "请先选择要删除的令牌。", parent=win)
                return
            idx = sel[0]
            name = tokens_data[idx].get("name", "")
            if not messagebox.askyesno("确认", f"确定删除令牌「{name}」？", parent=win):
                return
            tokens_data.pop(idx)
            if active_idx[0] >= len(tokens_data):
                active_idx[0] = max(0, len(tokens_data) - 1)
            elif active_idx[0] > idx:
                active_idx[0] -= 1
            _refresh_token_list()

        def _set_default():
            sel = tokens_listbox.curselection()
            if not sel:
                return
            active_idx[0] = sel[0]
            _refresh_token_list()

        def _load_to_form():
            """将选中令牌加载到编辑表单"""
            sel = tokens_listbox.curselection()
            if not sel:
                return
            t = tokens_data[sel[0]]
            name_var.set(t.get("name", ""))
            pk = t.get("provider", "anthropic")
            pn = provider_names.get(pk, provider_names.get("anthropic", ""))
            provider_var.set(pn)
            ai_key_var.set(t.get("key", ""))
            model_var.set(t.get("model", ""))
            url_var.set(t.get("api_url", ""))
            _on_provider_changed()

        tk.Button(tokens_btn_row, text="🗑️ 删除", font=("", 9), relief=tk.FLAT,
                  command=_delete_token).pack(side=tk.LEFT, padx=(0, 5))
        tk.Button(tokens_btn_row, text="★ 设为默认", font=("", 9), relief=tk.FLAT,
                  command=_set_default).pack(side=tk.LEFT, padx=5)
        tk.Button(tokens_btn_row, text="📝 加载到表单", font=("", 9), relief=tk.FLAT,
                  command=_load_to_form).pack(side=tk.LEFT, padx=5)

        # ══════════ 令牌编辑表单 ══════════
        form_frame = tk.LabelFrame(win, text="➕ 添加 / 修改令牌", font=("", 10),
                                    padx=10, pady=5)
        form_frame.pack(fill=tk.X, padx=20, pady=(5, 5))

        form = tk.Frame(form_frame)
        form.pack(fill=tk.X)
        row = 0

        # ── 令牌名称 ──
        tk.Label(form, text="令牌名称:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        name_var = tk.StringVar()
        tk.Entry(form, textvariable=name_var, width=30,
                 font=("", 9)).grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0),
                                     columnspan=2)
        row += 1

        # ── AI 提供商 ──
        tk.Label(form, text="AI 提供商:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        provider_names = {k: v['name'] for k, v in SteamAIGenerator.PROVIDERS.items()}
        provider_var = tk.StringVar(value=provider_names.get("anthropic", ""))
        provider_combo = ttk.Combobox(form, textvariable=provider_var, width=30,
                                       values=list(provider_names.values()), state='readonly')
        provider_combo.grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0), columnspan=2)
        row += 1

        def _provider_key_from_name(display_name):
            for k, v in provider_names.items():
                if v == display_name:
                    return k
            return 'anthropic'

        # ── AI API Key ──
        tk.Label(form, text="API Key:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        ai_key_var = tk.StringVar()
        ai_key_entry = tk.Entry(form, textvariable=ai_key_var, width=40,
                                 font=("", 9), show="•")
        ai_key_entry.grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0))

        def toggle_show_ai():
            if ai_key_entry.cget("show") == "•":
                ai_key_entry.config(show="")
                show_ai_btn.config(text="🙈")
            else:
                ai_key_entry.config(show="•")
                show_ai_btn.config(text="👁️")
        show_ai_btn = tk.Button(form, text="👁️", font=("", 9), relief=tk.FLAT,
                                 command=toggle_show_ai)
        show_ai_btn.grid(row=row, column=2, padx=3)
        row += 1

        # ── 模型 ──
        tk.Label(form, text="模型:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        model_var = tk.StringVar()
        model_combo = ttk.Combobox(form, textvariable=model_var, width=35,
                                    values=[])
        model_combo.grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0), columnspan=2)
        row += 1

        # ── 自定义 API URL ──
        tk.Label(form, text="API URL:", font=("", 10)).grid(
            row=row, column=0, sticky=tk.W, pady=3)
        url_var = tk.StringVar()
        tk.Entry(form, textvariable=url_var, width=40,
                 font=("", 9)).grid(row=row, column=1, sticky=tk.W, pady=3, padx=(10, 0),
                                     columnspan=2)
        row += 1

        url_hint = tk.Label(form, text="", font=("", 8), fg="#888")
        url_hint.grid(row=row, column=0, sticky=tk.W, columnspan=3)
        row += 1

        def _on_provider_changed(*_):
            pk = _provider_key_from_name(provider_combo.get())
            pi = SteamAIGenerator.PROVIDERS.get(pk, {})
            model_combo['values'] = pi.get('models', [])
            if not model_var.get() or model_var.get() not in pi.get('models', []):
                dm = pi.get('default_model', '')
                if dm:
                    model_var.set(dm)
            du = pi.get('api_url', '')
            url_hint.config(text=f"留空使用默认: {du}" if du else "⚠️ 请填写 API URL")
            # 自动填充名称
            if not name_var.get().strip():
                name_var.set(pi.get('name', pk))
        provider_combo.bind("<<ComboboxSelected>>", _on_provider_changed)
        _on_provider_changed()

        # 表单按钮
        form_btn_row = tk.Frame(form_frame)
        form_btn_row.pack(fill=tk.X, pady=(5, 0))

        def _save_as_new():
            key = ai_key_var.get().strip()
            if not key:
                messagebox.showwarning("提示", "请输入 API Key。", parent=win)
                return
            token = {
                "name": name_var.get().strip() or "未命名",
                "key": key,
                "provider": _provider_key_from_name(provider_var.get()),
                "model": model_var.get().strip(),
                "api_url": url_var.get().strip(),
            }
            tokens_data.append(token)
            if len(tokens_data) == 1:
                active_idx[0] = 0
            _refresh_token_list()
            messagebox.showinfo("✅", f"已添加令牌「{token['name']}」", parent=win)

        def _update_selected():
            sel = tokens_listbox.curselection()
            if not sel:
                messagebox.showwarning("提示", "请先在上方列表中选择要更新的令牌。", parent=win)
                return
            key = ai_key_var.get().strip()
            if not key:
                messagebox.showwarning("提示", "请输入 API Key。", parent=win)
                return
            idx = sel[0]
            tokens_data[idx] = {
                "name": name_var.get().strip() or "未命名",
                "key": key,
                "provider": _provider_key_from_name(provider_var.get()),
                "model": model_var.get().strip(),
                "api_url": url_var.get().strip(),
            }
            _refresh_token_list()
            messagebox.showinfo("✅", "已更新所选令牌。", parent=win)

        ttk.Button(form_btn_row, text="➕ 添加为新令牌",
                   command=_save_as_new).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(form_btn_row, text="💾 更新选中令牌",
                   command=_update_selected).pack(side=tk.LEFT, padx=5)

        # ══════════ Steam Web API Key ══════════
        ttk.Separator(win, orient=tk.HORIZONTAL).pack(fill=tk.X, padx=20, pady=8)

        steam_frame = tk.LabelFrame(win, text="🎮 Steam Web API Key", font=("", 10),
                                     padx=10, pady=5)
        steam_frame.pack(fill=tk.X, padx=20, pady=(0, 5))

        steam_row = tk.Frame(steam_frame)
        steam_row.pack(fill=tk.X)
        steam_var = tk.StringVar(value=self._get_saved_key("steam_web_api_key"))
        steam_entry = tk.Entry(steam_row, textvariable=steam_var, width=40,
                                font=("", 9), show="•")
        steam_entry.pack(side=tk.LEFT, pady=2)

        def toggle_show_steam():
            if steam_entry.cget("show") == "•":
                steam_entry.config(show="")
                show_s_btn.config(text="🙈")
            else:
                steam_entry.config(show="•")
                show_s_btn.config(text="👁️")
        show_s_btn = tk.Button(steam_row, text="👁️", font=("", 9), relief=tk.FLAT,
                                command=toggle_show_steam)
        show_s_btn.pack(side=tk.LEFT, padx=3)

        def clear_steam():
            steam_var.set("")
            self._clear_saved_key("steam_web_api_key")
        tk.Button(steam_row, text="🗑️ 清除", font=("", 9), relief=tk.FLAT,
                  command=clear_steam).pack(side=tk.LEFT, padx=3)

        steam_status = tk.Label(steam_frame, text="", font=("", 8))
        steam_status.pack(anchor=tk.W)
        if self._get_saved_key("steam_web_api_key"):
            steam_status.config(text="✅ 已保存", fg="green")

        tk.Label(steam_frame, text="用于在线扫描游戏库 — 从 steamcommunity.com/dev/apikey 获取",
                 font=("", 8), fg="#888").pack(anchor=tk.W, pady=(0, 3))

        # ── 保存全部按钮 ──
        def do_save_all():
            # 保存令牌列表
            self._save_ai_tokens(tokens_data, active_idx[0])
            # 保存 Steam Key
            sk = steam_var.get().strip()
            if sk:
                self._config["steam_web_api_key"] = sk
            elif "steam_web_api_key" in self._config:
                del self._config["steam_web_api_key"]
            self._save_config(self._config)
            steam_status.config(text="✅ 已保存" if sk else "", fg="green")
            messagebox.showinfo("✅ 成功", "所有配置已保存。", parent=win)

        btn_frame = tk.Frame(win, padx=20)
        btn_frame.pack(fill=tk.X, pady=(5, 15))
        ttk.Button(btn_frame, text="💾 保存全部", command=do_save_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭", command=win.destroy).pack(side=tk.RIGHT, padx=5)

        self._center_window(win)

    # ────────────────────── AI 批量生成 ──────────────────────

    def _ui_manage_cache(self):
        """弹出本地缓存数据管理窗口"""
        cache_win = tk.Toplevel(self.root)
        cache_win.title("🗑️ 本地缓存管理")
        cache_win.resizable(False, False)
        cache_win.transient(self.root)

        tk.Label(cache_win, text="本地缓存数据管理",
                 font=("", 12, "bold")).pack(padx=20, pady=(15, 5))
        tk.Label(cache_win, text="缓存数据存储在配置文件中，清理后将在下次使用时重建。",
                 font=("", 9), fg="#666").pack(padx=20, pady=(0, 10))

        info_frame = tk.Frame(cache_win, padx=15)
        info_frame.pack(fill=tk.X)

        # 配置文件路径和大小
        config_path = self._CONFIG_FILE
        try:
            config_size = os.path.getsize(config_path) if os.path.exists(config_path) else 0
        except Exception:
            config_size = 0
        size_str = (f"{config_size / 1024 / 1024:.1f} MB" if config_size > 1024 * 1024
                    else f"{config_size / 1024:.1f} KB" if config_size > 1024
                    else f"{config_size} B")

        path_label = tk.Label(info_frame,
                              text=f"📂 {config_path}  ({size_str})",
                              font=("", 8), fg="#888", cursor="hand2")
        path_label.pack(anchor=tk.W, pady=(0, 8))
        path_label.bind("<Button-1>",
                        lambda e: self._open_directory(self._CONFIG_DIR))

        # 游戏名称缓存
        name_cache = self._config.get("game_name_cache", {})
        name_count = len(name_cache)
        row1 = tk.Frame(info_frame)
        row1.pack(fill=tk.X, pady=2)
        tk.Label(row1, text=f"🎮 游戏名称缓存: {name_count} 条",
                 font=("", 10)).pack(side=tk.LEFT)

        def _clear_name_cache():
            self._config.pop("game_name_cache", None)
            self._config.pop("game_name_bulk_cache_ts", None)
            self._game_name_cache = {}
            self._game_name_cache_loaded = False
            self._save_config(self._config)
            name_count_lbl.config(text="0 条")
            _refresh_size()
            messagebox.showinfo("✅", "游戏名称缓存已清除", parent=cache_win)

        ttk.Button(row1, text="清除", width=5,
                   command=_clear_name_cache).pack(side=tk.RIGHT)
        name_count_lbl = tk.Label(row1, text="", font=("", 9), fg="#888")

        # 上传哈希记录
        hash_keys = [k for k in self._config if k.startswith("uploaded_hashes_")]
        total_hashes = sum(len(self._config.get(k, {})) for k in hash_keys)
        row2 = tk.Frame(info_frame)
        row2.pack(fill=tk.X, pady=2)
        tk.Label(row2, text=f"☁️ 上传哈希记录: {total_hashes} 条 ({len(hash_keys)} 个账号)",
                 font=("", 10)).pack(side=tk.LEFT)

        def _clear_upload_hashes():
            for k in list(self._config.keys()):
                if k.startswith("uploaded_hashes_"):
                    del self._config[k]
            self._save_config(self._config)
            # 重建当前 manager 的 dirty 状态
            if self.manager:
                self.manager._uploaded_hashes = {}
                self.manager._dirty_apps = set()
                self.manager._rebuild_dirty_from_hashes()
            _refresh_size()
            messagebox.showinfo("✅", "上传哈希记录已清除（所有笔记将标记为需上传）",
                                parent=cache_win)

        ttk.Button(row2, text="清除", width=5,
                   command=_clear_upload_hashes).pack(side=tk.RIGHT)

        # 免费游戏缓存
        free_cache = self._config.get("free_apps_cache", {})
        free_count = len(free_cache)
        row3 = tk.Frame(info_frame)
        row3.pack(fill=tk.X, pady=2)
        tk.Label(row3, text=f"🆓 免费游戏缓存: {free_count} 条",
                 font=("", 10)).pack(side=tk.LEFT)

        def _clear_free_cache():
            self._config.pop("free_apps_cache", None)
            self._save_config(self._config)
            _refresh_size()
            messagebox.showinfo("✅", "免费游戏缓存已清除", parent=cache_win)

        ttk.Button(row3, text="清除", width=5,
                   command=_clear_free_cache).pack(side=tk.RIGHT)

        # 家庭库扫描缓存
        flib_cache = self._config.get("family_library_cache", {})
        flib_games = len(flib_cache.get("library_games", []))
        flib_family = len(flib_cache.get("family_owned_ids", []))
        row3b = tk.Frame(info_frame)
        row3b.pack(fill=tk.X, pady=2)
        flib_text = (f"👨‍👩‍👧‍👦 家庭库缓存: {flib_games} 款游戏，家庭库 {flib_family} 款"
                     if flib_cache else "👨‍👩‍👧‍👦 家庭库缓存: 无")
        tk.Label(row3b, text=flib_text, font=("", 10)).pack(side=tk.LEFT)

        def _clear_family_lib_cache():
            self._config.pop("family_library_cache", None)
            self._save_config(self._config)
            _refresh_size()
            messagebox.showinfo("✅", "家庭库缓存已清除（下次打开 AI 生成窗口将重新扫描）",
                                parent=cache_win)

        ttk.Button(row3b, text="清除", width=5,
                   command=_clear_family_lib_cache).pack(side=tk.RIGHT)

        # AI 令牌配置（不可清除，仅展示）
        tokens = self._config.get("ai_tokens", [])
        family_codes = self._config.get("family_friend_codes", [])
        row4 = tk.Frame(info_frame)
        row4.pack(fill=tk.X, pady=2)
        tk.Label(row4, text=f"🔑 AI 令牌: {len(tokens)} 个  |  "
                           f"👨‍👩‍👧‍👦 家庭组: {len(family_codes)} 人",
                 font=("", 10), fg="#555").pack(side=tk.LEFT)

        # 大小刷新
        size_label = tk.Label(info_frame, text="", font=("", 9), fg="#888")
        size_label.pack(anchor=tk.W, pady=(8, 0))

        def _refresh_size():
            try:
                s = os.path.getsize(config_path) if os.path.exists(config_path) else 0
            except Exception:
                s = 0
            ss = (f"{s / 1024 / 1024:.1f} MB" if s > 1024 * 1024
                  else f"{s / 1024:.1f} KB" if s > 1024 else f"{s} B")
            size_label.config(text=f"当前配置文件大小: {ss}")
            path_label.config(text=f"📂 {config_path}  ({ss})")

        _refresh_size()

        # 清除全部
        btn_frame = tk.Frame(cache_win)
        btn_frame.pack(pady=(10, 15))

        def _clear_all():
            if not messagebox.askyesno("确认",
                    "确定要清除所有缓存数据？\n（AI 令牌和家庭组配置不会被清除）",
                    parent=cache_win):
                return
            _clear_name_cache()
            for k in list(self._config.keys()):
                if k.startswith("uploaded_hashes_"):
                    del self._config[k]
            self._config.pop("free_apps_cache", None)
            self._config.pop("family_library_cache", None)
            self._save_config(self._config)
            if self.manager:
                self.manager._uploaded_hashes = {}
                self.manager._dirty_apps = set()
                self.manager._rebuild_dirty_from_hashes()
            _refresh_size()
            messagebox.showinfo("✅", "所有缓存已清除", parent=cache_win)

        ttk.Button(btn_frame, text="🗑️ 清除全部缓存",
                   command=_clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="关闭",
                   command=cache_win.destroy).pack(side=tk.LEFT, padx=5)

        self._center_window(cache_win)

    def _open_directory(self, path):
        """跨平台打开目录"""
        try:
            if platform.system() == "Darwin":
                os.system(f'open "{path}"')
            elif platform.system() == "Windows":
                os.startfile(path)
            else:
                os.system(f'xdg-open "{path}"')
        except Exception:
            pass

    def _ui_show_about(self):
        """弹出关于作者窗口"""
        about = tk.Toplevel(self.root)
        about.title("关于")
        about.resizable(False, False)

        tk.Label(about, text="Steam 笔记管理器 v5.7.2",
                 font=("", 12, "bold")).pack(padx=20, pady=(15, 8))

        info_frame = tk.Frame(about)
        info_frame.pack(padx=20, pady=(0, 5))

        tk.Label(info_frame, text="作者: ", font=("", 10),
                 anchor=tk.E).grid(row=0, column=0, sticky=tk.E)
        author_link = tk.Label(info_frame, text="dtq1997", font=("", 10, "underline"),
                               fg="#1a73e8", cursor="hand2")
        author_link.grid(row=0, column=1, sticky=tk.W)
        author_link.bind("<Button-1>",
                         lambda e: webbrowser.open("https://steamcommunity.com/id/dtq1997/"))

        tk.Label(info_frame, text="邮箱: ", font=("", 10),
                 anchor=tk.E).grid(row=1, column=0, sticky=tk.E)
        tk.Label(info_frame, text="919130201@qq.com", font=("", 10),
                 fg="#555").grid(row=1, column=1, sticky=tk.W)

        tk.Label(info_frame, text="", font=("", 10),
                 anchor=tk.E).grid(row=2, column=0, sticky=tk.E)
        tk.Label(info_frame, text="dtq1997@pku.edu.cn", font=("", 10),
                 fg="#555").grid(row=2, column=1, sticky=tk.W)

        motto_label = tk.Label(about, text="「总有一天人人都会控大喷菇的」",
                               font=("", 10), fg="#5599cc", cursor="hand2")
        motto_label.pack(pady=(5, 3))
        motto_label.bind("<Button-1>",
                         lambda e: webbrowser.open("https://aweidao1.com/t/986949"))

        ttk.Button(about, text="确定", command=about.destroy).pack(pady=(5, 15))
        self._center_window(about)

    def _ui_open_dir(self):
        d = self.current_account['notes_dir']
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        self._open_folder(d)

    def _open_config_dir(self):
        """打开配置文件所在目录"""
        d = self._CONFIG_DIR
        if not os.path.exists(d):
            os.makedirs(d, exist_ok=True)
        self._open_folder(d)

    @staticmethod
    def _open_folder(d):
        """跨平台打开文件夹"""
        system = platform.system()
        try:
            if system == "Windows":
                os.startfile(d)
            elif system == "Darwin":
                os.system(f'open "{d}"')
            else:
                os.system(f'xdg-open "{d}" 2>/dev/null || open "{d}" 2>/dev/null')
        except:
            messagebox.showinfo("目录路径", f"路径:\n{d}")
