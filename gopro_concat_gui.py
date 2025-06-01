import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from typing import Optional, List
import shutil
import tempfile
from src.ffmpeg import write_file_list, video_concat, delete_file_list
import threading

class GoProConcatGUI:
    """GoPro動画結合ツールのGUIクラス。フォルダ単位/ファイル単位の選択が可能。"""
    def __init__(self, master: tk.Tk):
        self.master = master
        self.master.title("GoPro動画結合ツール")
        self.master.geometry("1000x700")  # デフォルトウインドウサイズを大きく設定
        self.mode_var: tk.StringVar = tk.StringVar(value="folder")
        self.selected_files: List[Path] = []
        self.selected_folder: Optional[Path] = None
        self.save_dir: Optional[Path] = None
        self._create_widgets()

    def _create_widgets(self) -> None:
        """画面要素の作成"""
        # ラジオボタン
        mode_frame = tk.LabelFrame(self.master, text="結合方法の選択")
        mode_frame.pack(padx=10, pady=5, fill="x")
        tk.Radiobutton(mode_frame, text="フォルダ単位", variable=self.mode_var, value="folder", command=self._update_select_btn).pack(side="left", padx=5)
        tk.Radiobutton(mode_frame, text="ファイル単位", variable=self.mode_var, value="file", command=self._update_select_btn).pack(side="left", padx=5)

        # 選択ボタン
        self.select_btn = tk.Button(self.master, text="動画フォルダを選択", command=self._select)
        self.select_btn.pack(padx=10, pady=5, fill="x")

        # 保存先選択
        self.save_btn = tk.Button(self.master, text="保存先フォルダを選択", command=self._select_save_dir)
        self.save_btn.pack(padx=10, pady=5, fill="x")

        # 実行ボタン
        self.run_btn = tk.Button(self.master, text="結合実行", command=self._run_concat)
        self.run_btn.pack(padx=10, pady=10, fill="x")

        # メッセージ欄
        self.msg_label = tk.Label(self.master, text="", fg="blue")
        self.msg_label.pack(padx=10, pady=5, fill="x")

        # 選択内容表示欄（Frameでまとめる）
        self.selected_info_frame = tk.Frame(self.master)
        self.selected_info_frame.pack(padx=10, pady=2, fill="x")
        self.selected_folder_label = tk.Label(self.selected_info_frame, text="動画フォルダ: 未選択", anchor="w")
        self.selected_folder_label.pack(padx=0, pady=2, fill="x")
        self.selected_files_label = tk.Label(self.selected_info_frame, text="動画ファイル: 未選択", anchor="w")
        # 初期表示ではpackしない（非表示）
        self.save_dir_label = tk.Label(self.selected_info_frame, text="保存先: 未選択", anchor="w")
        self.save_dir_label.pack(padx=0, pady=2, fill="x")
        # 結合プレビュー欄（スクロール・リサイズ対応）
        preview_frame = tk.Frame(self.master)
        preview_frame.pack(padx=10, pady=2, fill="both", expand=True)
        self.preview_label = tk.Label(preview_frame, text="結合プレビュー:", anchor="w", fg="green")
        self.preview_label.pack(anchor="w")
        self.preview_text = tk.Text(preview_frame, height=6, state="disabled", bg="#f0f0f0", wrap="none")
        self.preview_text.pack(side="left", fill="both", expand=True)
        yscroll = tk.Scrollbar(preview_frame, orient="vertical", command=self.preview_text.yview)
        yscroll.pack(side="right", fill="y")
        xscroll = tk.Scrollbar(preview_frame, orient="horizontal", command=self.preview_text.xview)
        xscroll.pack(side="bottom", fill="x")
        self.preview_text.configure(yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)

    def _update_select_btn(self) -> None:
        """ラジオボタンの選択に応じてボタンのラベルを変更"""
        if self.mode_var.get() == "folder":
            self.select_btn.config(text="動画フォルダを選択")
        else:
            self.select_btn.config(text="動画ファイルを選択")
        self._update_selected_labels()
        self._update_preview()

    def _select(self) -> None:
        """フォルダまたはファイル選択ダイアログを表示"""
        if self.mode_var.get() == "folder":
            folder = filedialog.askdirectory(title="動画フォルダを選択")
            if folder:
                self.selected_folder = Path(folder)
                self.selected_files = []
                self.msg_label.config(text=f"選択フォルダ: {folder}")
        else:
            files = filedialog.askopenfilenames(title="動画ファイルを選択", filetypes=[("MP4 files", "*.mp4"), ("All files", "*.*")])
            if files:
                self.selected_files = [Path(f) for f in files]
                self.selected_folder = None
                self.msg_label.config(text=f"選択ファイル数: {len(files)}")
        self._update_selected_labels()
        self._update_preview()

    def _select_save_dir(self) -> None:
        """保存先フォルダ選択ダイアログを表示"""
        folder = filedialog.askdirectory(title="保存先フォルダを選択")
        if folder:
            self.save_dir = Path(folder)
            self.msg_label.config(text=f"保存先: {folder}")
        self._update_selected_labels()
        self._update_preview()

    def _update_selected_labels(self) -> None:
        """選択内容のラベルを更新（ラジオボタンの状態で表示/非表示を切替、再表示も確実に行う）"""
        # まず両方消す（Frame内なので順序崩れない）
        self.selected_folder_label.pack_forget()
        self.selected_files_label.pack_forget()
        self.save_dir_label.pack_forget()  # いったん必ず消す
        if self.mode_var.get() == "folder":
            self.selected_folder_label.pack(padx=0, pady=2, fill="x")
            if self.selected_folder:
                self.selected_folder_label.config(text=f"動画フォルダ: {self.selected_folder}")
            else:
                self.selected_folder_label.config(text="動画フォルダ: 未選択")
        else:
            self.selected_files_label.pack(padx=0, pady=2, fill="x")
            if self.selected_files:
                files_str = ", ".join([f.name for f in self.selected_files])
                self.selected_files_label.config(text=f"動画ファイル: {files_str}")
            else:
                self.selected_files_label.config(text="動画ファイル: 未選択")
        # 保存先ラベルは常に一番下に再pack
        if self.save_dir:
            self.save_dir_label.config(text=f"保存先: {self.save_dir}")
        else:
            self.save_dir_label.config(text="保存先: 未選択")
        self.save_dir_label.pack(padx=0, pady=2, fill="x")

    def _update_preview(self) -> None:
        """結合プレビュー欄を更新（命名規則に従いグループ化して表示）"""
        self.preview_text.config(state="normal")
        self.preview_text.delete("1.0", tk.END)
        groups = {}
        if self.mode_var.get() == "folder" and self.selected_folder:
            files = list(self.selected_folder.iterdir())
            for f in files:
                if f.is_file() and len(f.name) == 12 and f.name.startswith("GX") and f.suffix.lower() == ".mp4":
                    key = f.name[4:8]
                    groups.setdefault(key, []).append(f)
        elif self.mode_var.get() == "file" and self.selected_files:
            for f in self.selected_files:
                if f.is_file() and len(f.name) == 12 and f.name.startswith("GX") and f.suffix.lower() == ".mp4":
                    key = f.name[4:8]
                    groups.setdefault(key, []).append(f)
        if groups:
            for key, group_files in sorted(groups.items()):
                out_name = f"GX{key}.mp4"
                self.preview_text.insert(tk.END, f"結合後ファイル: {out_name}\n")
                self.preview_text.insert(tk.END, "結合対象:\n")
                for f in sorted(group_files):
                    self.preview_text.insert(tk.END, f"  {f.name}\n")
                self.preview_text.insert(tk.END, "\n")
        else:
            self.preview_text.insert(tk.END, "GX????.MP4ファイルが見つかりません\n")
        self.preview_text.config(state="disabled")

    def _run_concat(self) -> None:
        """GUIから実際の結合処理をスレッドで実行し、進捗をプレビューに表示"""
        thread = threading.Thread(target=self._run_concat_worker)
        thread.start()

    def _run_concat_worker(self) -> None:
        if self.mode_var.get() == "folder":
            if not self.selected_folder:
                self._show_error_dialog("動画フォルダを選択してください")
                return
            files = list(self.selected_folder.iterdir())
        else:
            if not self.selected_files:
                self._show_error_dialog("動画ファイルを選択してください")
                return
            files = self.selected_files
        if not self.save_dir:
            self._show_error_dialog("保存先フォルダを選択してください")
            return
        groups = {}
        for f in files:
            if f.is_file() and len(f.name) == 12 and f.name.startswith("GX") and f.suffix.lower() == ".mp4":
                key = f.name[4:8]
                groups.setdefault(key, []).append(f)
        if not groups:
            self._show_error_dialog("結合対象ファイルがありません")
            return
        ffmpeg_logs = ""
        total = len(groups)
        self._update_progress(f"=== 結合処理開始: {total}グループ ===\n", append=True)
        for idx, (key, group_files) in enumerate(sorted(groups.items()), 1):
            self._update_progress(f"[{idx}/{total}] GX{key} 結合中...\n", append=True)
            with tempfile.TemporaryDirectory() as tmpdir:
                tmpdir_path = Path(tmpdir)
                txt_path = tmpdir_path / f"{key}.txt"
                with open(txt_path, "w", encoding="utf-8") as ftxt:
                    ftxt.write("ffconcat version 1.0\n")
                    for f in sorted(group_files):
                        ftxt.write(f"file '{str(f.resolve())}'\n")
                try:
                    log = video_concat(txt_path, self.save_dir, f"GX{key}")
                    ffmpeg_logs += f"[GX{key}]\n" + log + "\n"
                    # --- ここでグループごとにffmpegログを即時表示 ---
                    self._update_progress(f"[GX{key}] ffmpegログ:\n{log}\n", append=True)
                except Exception as e:
                    self._show_error_dialog(f"ffmpeg結合失敗: {e}")
                    return
            self._update_progress(f"[{idx}/{total}] GX{key} 完了\n", append=True)
        self._update_progress(f"=== 全グループの結合が完了しました ===\n", append=True)
        self.msg_label.after(0, lambda: self.msg_label.config(text="結合処理が完了しました"))
        # self._show_ffmpeg_log(ffmpeg_logs)  # 全体まとめ表示は不要
        self.master.after(0, lambda: messagebox.showinfo("完了", "動画の結合が完了しました"))

    def _update_progress(self, msg: str, append: bool = True) -> None:
        def update():
            self.preview_text.config(state="normal")
            if not append:
                self.preview_text.delete("1.0", tk.END)
            self.preview_text.insert(tk.END, msg)
            self.preview_text.see(tk.END)
            self.preview_text.config(state="disabled")
        self.preview_text.after(0, update)

    def _show_error_dialog(self, msg: str) -> None:
        self.master.after(0, lambda: messagebox.showerror("エラー", msg))

    def _show_ffmpeg_log(self, log: str) -> None:
        """ffmpegの出力内容をプレビュー欄に追記表示"""
        self.preview_text.config(state="normal")
        self.preview_text.insert(tk.END, log)
        self.preview_text.see(tk.END)
        self.preview_text.config(state="disabled")


def main() -> None:
    """GUIアプリのエントリポイント"""
    root = tk.Tk()
    app = GoProConcatGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
