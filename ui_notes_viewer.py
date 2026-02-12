"""笔记查看/编辑/创建/删除窗口 (Mixin)"""

import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from datetime import datetime

from rich_text_editor import SteamRichTextEditor
from core import is_ai_note, extract_ai_model_from_note


class NotesViewerMixin:
    """笔记查看、编辑、创建、删除相关 UI 方法"""

    def _ui_view_selected(self):
        app_id = self._get_selected_app_id()
        if app_id:
            self._open_notes_viewer(app_id)
        else:
            messagebox.showinfo("提示", "请先在右侧列表中选择一个游戏。")

    def _copy_appid(self, app_id: str):
        """复制AppID到剪贴板（无弹窗）"""
        self._copy_appid_silent(app_id)

    # ────────────────────── 新建笔记 ──────────────────────

    def _ui_create_note(self):
        """新建笔记窗口 — 使用富文本编辑器"""
        win = tk.Toplevel(self.root)
        win.title("📝 新建 Steam 笔记")
        win.resizable(True, True)
        win.grab_set()

        tk.Label(win, text="📝 新建笔记", font=("", 13, "bold")).pack(pady=(15, 10))

        form = tk.Frame(win, padx=20)
        form.pack(fill=tk.X)

        # AppID
        tk.Label(form, text="游戏 AppID:", font=("", 10)).grid(
            row=0, column=0, sticky=tk.W, pady=5)
        app_id_var = tk.StringVar()
        sel_id = self._get_selected_app_id()
        if sel_id:
            app_id_var.set(sel_id)
        tk.Entry(form, textvariable=app_id_var, width=20, font=("", 10)).grid(
            row=0, column=1, sticky=tk.W, pady=5, padx=(10, 0))
        tk.Label(form, text="(如 1245620)", font=("", 9), fg="#888").grid(
            row=0, column=2, sticky=tk.W, padx=5)

        # 标题
        tk.Label(form, text="笔记标题:", font=("", 10)).grid(
            row=1, column=0, sticky=tk.W, pady=5)
        title_var = tk.StringVar()
        tk.Entry(form, textvariable=title_var, width=40, font=("", 10)).grid(
            row=1, column=1, columnspan=2, sticky=tk.W, pady=5, padx=(10, 0))

        # 富文本编辑器
        tk.Label(win, text="笔记内容:", font=("", 10), padx=20).pack(anchor=tk.W)
        editor = SteamRichTextEditor(win, height=12)
        editor.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 5))

        def do_create():
            aid = app_id_var.get().strip()
            title = title_var.get().strip()
            content = editor.get_content()

            if not aid:
                messagebox.showwarning("提示", "请输入游戏 AppID。", parent=win)
                return
            if not title:
                messagebox.showwarning("提示", "请输入笔记标题。", parent=win)
                return
            if not content.strip():
                messagebox.showwarning("提示", "请输入笔记内容。", parent=win)
                return

            try:
                self.manager.create_note(aid, title, content)
                messagebox.showinfo("✅ 成功",
                                    f"已为 AppID {aid} 创建笔记:\n「{title}」",
                                    parent=win)
                self._refresh_games_list()
                win.destroy()
            except Exception as e:
                messagebox.showerror("❌ 错误", f"写入失败:\n{e}", parent=win)

        ttk.Button(win, text="✅ 创建笔记", command=do_create).pack(pady=(5, 15))
        self._center_window(win)

    # ────────────────────── 查看/编辑笔记 ──────────────────────

    def _ui_view_notes(self):
        app_id = simpledialog.askstring("查看笔记", "请输入游戏 AppID:",
                                        parent=self.root)
        if app_id and app_id.strip():
            self._open_notes_viewer(app_id.strip())

    def _open_notes_viewer(self, app_id: str, select_index: int = 0):
        """笔记浏览/编辑窗口 — 使用富文本编辑器"""
        data = self.manager.read_notes(app_id)
        notes = data.get("notes", [])

        win = tk.Toplevel(self.root)
        win.title(f"📋 AppID {app_id} 的笔记 ({len(notes)} 条)")
        win.resizable(True, True)
        win.grab_set()

        if not notes:
            tk.Label(win, text=f"📭 AppID {app_id} 暂无笔记",
                     font=("", 12), fg="#888").pack(padx=40, pady=30)
            ttk.Button(win, text="📝 新建一条",
                       command=lambda: [win.destroy(), self._ui_create_note()]).pack(pady=10)
            self._center_window(win)
            return

        # 笔记列表 + 详情
        paned = tk.PanedWindow(win, orient=tk.HORIZONTAL, sashwidth=5)
        paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 左: 列表
        left_f = tk.Frame(paned)
        paned.add(left_f, width=250)

        tk.Label(left_f, text="笔记列表", font=("", 10, "bold")).pack(anchor=tk.W)
        note_listbox = tk.Listbox(left_f, width=30, height=15, font=("", 10))
        note_listbox.pack(fill=tk.BOTH, expand=True, pady=5)

        for i, n in enumerate(notes):
            ts = n.get("time_modified", 0)
            t_str = datetime.fromtimestamp(ts).strftime("%m/%d %H:%M") if ts else ""
            ai_mark = "🤖 " if is_ai_note(n) else ""
            note_listbox.insert(tk.END, f"[{i}] {ai_mark}{n.get('title', '(无标题)')[:40]}  {t_str}")
            if is_ai_note(n):
                note_listbox.itemconfig(i, fg="#1a73e8")

        # 右: 详情（使用富文本编辑器）
        right_f = tk.Frame(paned)
        paned.add(right_f, width=550)

        tk.Label(right_f, text="标题:", font=("", 10)).pack(anchor=tk.W)
        title_entry = tk.Entry(right_f, font=("", 11), width=50)
        title_entry.pack(fill=tk.X, pady=(0, 5))

        tk.Label(right_f, text="内容:", font=("", 10)).pack(anchor=tk.W)
        editor = SteamRichTextEditor(right_f, height=15)
        editor.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        ts_label = tk.Label(right_f, text="", font=("", 9), fg="#888")
        ts_label.pack(anchor=tk.W)

        ai_info_label = tk.Label(right_f, text="", font=("", 9), fg="#1a73e8")
        ai_info_label.pack(anchor=tk.W)

        # 用于跟踪原始文本显示状态
        _raw_mode = {'active': False}

        btn_frame = tk.Frame(right_f)
        btn_frame.pack(fill=tk.X, pady=5)

        # 第一行按钮
        btn_row1 = tk.Frame(btn_frame)
        btn_row1.pack(fill=tk.X)

        def do_save():
            idx = note_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选择一条笔记。", parent=win)
                return
            # 如果在原始文本模式，先退出
            if _raw_mode['active']:
                do_toggle_raw()
            i = idx[0]
            new_title = title_entry.get().strip()
            new_content = editor.get_content()
            if self.manager.update_note(app_id, i, new_title, new_content):
                self._refresh_games_list()
                messagebox.showinfo("✅ 成功", "笔记已保存。\n在主界面点击 ☁️ 上传到 Steam Cloud。", parent=win)

        def do_delete():
            idx = note_listbox.curselection()
            if not idx:
                return
            i = idx[0]
            if messagebox.askyesno("确认", f"确定删除笔记 [{i}] ？", parent=win):
                result = self.manager.delete_note(app_id, i)
                if not result:
                    messagebox.showwarning("提示", "删除失败。", parent=win)
                    return
                win.destroy()
                self._refresh_games_list()
                self._open_notes_viewer(app_id)

        def do_export_single():
            """导出当前选中的单条笔记"""
            idx = note_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选择一条笔记。", parent=win)
                return
            i = idx[0]
            note = notes[i]
            title = note.get("title", "untitled")
            safe_name = SteamNotesManager.sanitize_filename(title)
            path = filedialog.asksaveasfilename(
                title="导出笔记", defaultextension=".txt",
                initialfile=f"{safe_name}.txt",
                filetypes=[("文本文件", "*.txt"), ("所有文件", "*.*")],
                parent=win
            )
            if path:
                try:
                    self.manager.export_single_note(app_id, i, path)
                    messagebox.showinfo("✅ 成功", f"已导出笔记「{title}」到:\n{path}",
                                        parent=win)
                except Exception as e:
                    messagebox.showerror("❌ 错误", f"导出失败:\n{e}", parent=win)

        def do_toggle_raw():
            """就地切换原始文本/富文本显示"""
            idx = note_listbox.curselection()
            if not idx:
                messagebox.showwarning("提示", "请先选择一条笔记。", parent=win)
                return
            i = idx[0]
            if _raw_mode['active']:
                # 原始 → 富文本：重新渲染
                _raw_mode['active'] = False
                raw_toggle_btn.config(text="📄 原始文本")
                editor.set_content(notes[i].get("content", ""))
            else:
                # 富文本 → 原始：显示原始 BBCode
                _raw_mode['active'] = True
                raw_toggle_btn.config(text="👁️ 富文本")
                raw_content = notes[i].get("content", "")
                editor._text.config(state=tk.NORMAL)
                editor._text.delete("1.0", tk.END)
                editor._text.insert("1.0", raw_content)

        ttk.Button(btn_row1, text="💾 保存修改", command=do_save).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_row1, text="🗑️ 删除此条", command=do_delete).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_row1, text="📤 导出此条", command=do_export_single).pack(
            side=tk.LEFT, padx=5)
        raw_toggle_btn = ttk.Button(btn_row1, text="📄 原始文本",
                                      command=do_toggle_raw)
        raw_toggle_btn.pack(side=tk.LEFT, padx=5)

        # 第二行按钮
        btn_row2 = tk.Frame(btn_frame)
        btn_row2.pack(fill=tk.X, pady=(3, 0))

        def do_move(direction):
            idx = note_listbox.curselection()
            if not idx:
                return
            i = idx[0]
            new_i = i + direction
            if new_i < 0 or new_i >= len(notes):
                return
            result = self.manager.move_note(app_id, i, direction)
            if not result:
                # 移动失败，可能是试图移动受保护的同步触发笔记
                messagebox.showwarning("提示",
                    "无法移动该笔记。\n\n"
                    "第一条云同步触发笔记受到保护，不可移动，\n"
                    "也不允许将其他笔记移动到第一位。",
                    parent=win)
                return
            win.destroy()
            self._refresh_games_list()
            self._open_notes_viewer(app_id, select_index=new_i)

        ttk.Button(btn_row2, text="🔼 上移", command=lambda: do_move(-1)).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(btn_row2, text="🔽 下移", command=lambda: do_move(1)).pack(
            side=tk.LEFT, padx=5)

        # 切换笔记时重置原始文本模式
        def on_select(event=None):
            idx = note_listbox.curselection()
            if not idx:
                return
            _raw_mode['active'] = False
            raw_toggle_btn.config(text="📄 原始文本")
            i = idx[0]
            note = notes[i]
            title_entry.delete(0, tk.END)
            title_entry.insert(0, note.get("title", ""))
            editor.set_content(note.get("content", ""))
            ts = note.get("time_modified", 0)
            if ts:
                ts_label.config(text=f"⏰ {datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')}")
            # 显示 AI 模型信息
            if is_ai_note(note):
                model = extract_ai_model_from_note(note)
                ai_info_label.config(
                    text=f"🤖 AI 生成" + (f" (模型: {model})" if model else ""))
            else:
                ai_info_label.config(text="")

        note_listbox.bind("<<ListboxSelect>>", on_select)
        if notes:
            sel = min(select_index, len(notes) - 1)
            note_listbox.selection_set(sel)
            note_listbox.see(sel)
            note_listbox.event_generate("<<ListboxSelect>>")

        self._center_window(win)

    # ────────────────────── 删除笔记 ──────────────────────

    def _ui_delete_notes(self):
        app_ids = self._get_selected_app_ids()
        if not app_ids:
            # 无选中项时弹出手动输入
            app_id = simpledialog.askstring("删除笔记", "请输入游戏 AppID:",
                                            parent=self.root)
            if app_id and app_id.strip():
                app_ids = [app_id.strip()]
            else:
                return

        if len(app_ids) == 1:
            # 单选：保持原有行为
            app_id = app_ids[0]
            notes = self.manager.read_notes(app_id).get("notes", [])
            if not notes:
                messagebox.showinfo("提示", f"AppID {app_id} 暂无笔记。")
                return
            game_name = self._get_game_name(app_id)
            if messagebox.askyesno("确认删除",
                                   f"确定删除「{game_name}」(AppID {app_id}) 的全部 {len(notes)} 条笔记？\n"
                                   f"此操作不可撤销。"):
                self.manager.delete_all_notes(app_id)
                messagebox.showinfo("✅ 成功", f"已删除「{game_name}」的所有笔记。")
                self._refresh_games_list()
        else:
            # 多选：批量删除
            total_notes = 0
            valid_ids = []
            for aid in app_ids:
                n = len(self.manager.read_notes(aid).get("notes", []))
                if n > 0:
                    total_notes += n
                    valid_ids.append(aid)
            if not valid_ids:
                messagebox.showinfo("提示", "选中的游戏均无笔记。")
                return
            if messagebox.askyesno("确认批量删除",
                                   f"确定删除 {len(valid_ids)} 个游戏的全部 {total_notes} 条笔记？\n"
                                   f"此操作不可撤销。"):
                ok = 0
                for aid in valid_ids:
                    if self.manager.delete_all_notes(aid):
                        ok += 1
                messagebox.showinfo("✅ 成功", f"已删除 {ok} 个游戏的所有笔记。")
                self._refresh_games_list()

    # ────────────────────── API Key 设置 ──────────────────────
