import customtkinter
from tkinter import filedialog
from pathlib import Path
import threading
import sys # For redirecting stdout
import io # For redirecting stdout

from src.fileListing import video_key_listing
from src.ffmpeg import write_file_list, video_concat, delete_file_list

# Ensure this directory exists for temporary ffmpeg files
TEMP_FFMPEG_DIR_GUI = Path("./tmp_ffmpeg_gui")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        self.title("GoPro動画結合ツール")
        self.geometry("700x550")

        # --- UI Elements ---
        # Raw Video Path
        self.raw_video_label = customtkinter.CTkLabel(self, text="元の動画フォルダ:")
        self.raw_video_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.raw_video_path_entry = customtkinter.CTkEntry(self, width=400)
        self.raw_video_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.raw_video_button = customtkinter.CTkButton(self, text="フォルダ選択", command=self.select_raw_video_dir)
        self.raw_video_button.grid(row=0, column=2, padx=10, pady=5)

        # Output Path
        self.output_dir_label = customtkinter.CTkLabel(self, text="出力先フォルダ:")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.output_dir_path_entry = customtkinter.CTkEntry(self, width=400)
        self.output_dir_path_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.output_dir_button = customtkinter.CTkButton(self, text="フォルダ選択", command=self.select_output_dir)
        self.output_dir_button.grid(row=1, column=2, padx=10, pady=5)

        # Delete temp files checkbox
        self.delete_temp_checkbox = customtkinter.CTkCheckBox(self, text="結合後に一時ファイルを削除する")
        self.delete_temp_checkbox.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        self.delete_temp_checkbox.select() # Default to checked

        # Start button
        self.start_button = customtkinter.CTkButton(self, text="結合開始", command=self.start_concatenation_thread)
        self.start_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # Log Textbox
        self.log_textbox = customtkinter.CTkTextbox(self, width=660, height=300)
        self.log_textbox.grid(row=4, column=0, columnspan=3, padx=10, pady=10, sticky="nsew")
        self.log_textbox.configure(state="disabled") # Make read-only initially

        self.grid_columnconfigure(1, weight=1) # Allow path entry to expand

    def log_message(self, message):
        self.log_textbox.configure(state="normal")
        self.log_textbox.insert("end", message + "\n")
        self.log_textbox.configure(state="disabled")
        self.log_textbox.see("end")
        self.update_idletasks() # Ensure UI updates

    def select_raw_video_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.raw_video_path_entry.delete(0, "end")
            self.raw_video_path_entry.insert(0, path)
            self.log_message(f"元の動画フォルダを選択しました: {path}")

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir_path_entry.delete(0, "end")
            self.output_dir_path_entry.insert(0, path)
            self.log_message(f"出力先フォルダを選択しました: {path}")

    def start_concatenation_thread(self):
        self.start_button.configure(state="disabled")
        self.log_message("結合処理を開始します...")
        thread = threading.Thread(target=self.run_concatenation)
        thread.start()

    def run_concatenation(self):
        raw_video_dir_str = self.raw_video_path_entry.get()
        output_dir_str = self.output_dir_path_entry.get()
        delete_temp_files = self.delete_temp_checkbox.get() == 1

        if not raw_video_dir_str or not output_dir_str:
            self.log_message("エラー: 元の動画フォルダと出力先フォルダを選択してください。")
            self.start_button.configure(state="normal")
            return

        raw_video_path = Path(raw_video_dir_str)
        output_dir_for_concat = Path(output_dir_str)

        TEMP_FFMPEG_DIR_GUI.mkdir(parents=True, exist_ok=True)
        self.log_message(f"一時ディレクトリを使用します: {TEMP_FFMPEG_DIR_GUI.resolve()}")

        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()
        any_error_occurred = False
        video_set_processed = False # To track if we actually had videos to process

        try:
            self.log_message(f"動画元フォルダをスキャン中: {raw_video_path}")
            if not raw_video_path.is_dir():
                self.log_message(f"エラー: 動画元フォルダ '{raw_video_path}' が見つからないか、ディレクトリではありません。")
                any_error_occurred = True
                return # Critical error, stop processing

            video_set = video_key_listing(raw_video_path)
            video_set_processed = True # Mark that we attempted to get videos

            stdout_content = captured_output.getvalue(); captured_output.seek(0); captured_output.truncate(0)
            if stdout_content.strip(): self.log_message(f"[内部ログ - video_key_listing]:\n{stdout_content.strip()}")

            if not video_set:
                self.log_message("結合する動画セットが見つかりませんでした。")
                # No error flag here as it's a valid case, but processing stops.
                return

            self.log_message(f"検出された動画セット: {', '.join(video_set.keys())}")

            self.log_message(f"ffmpeg指示書を一時フォルダに書き込み中: {TEMP_FFMPEG_DIR_GUI}")
            write_file_list(video_set, TEMP_FFMPEG_DIR_GUI)
            stdout_content = captured_output.getvalue(); captured_output.seek(0); captured_output.truncate(0)
            if stdout_content.strip(): self.log_message(f"[内部ログ - write_file_list]:\n{stdout_content.strip()}")

            if not list(TEMP_FFMPEG_DIR_GUI.glob("*.txt")): # Check if any txt files were actually created
                self.log_message("ffmpeg指示書の作成に失敗したか、対象ファイルがありませんでした。処理を中断します。")
                any_error_occurred = True
                return # Critical error if files were expected

            self.log_message("動画の結合を開始します...")

            for ffmpeg_file_name_path in TEMP_FFMPEG_DIR_GUI.glob("*.txt"):
                video_key = ffmpeg_file_name_path.stem
                self.log_message(f"動画セットを処理中: GX{video_key} ({ffmpeg_file_name_path.name})")

                ffmpeg_stdout, ffmpeg_stderr, retcode = video_concat(
                    ffmpeg_file_name_path,
                    output_dir_for_concat,
                    f"GX{video_key}"
                )

                if ffmpeg_stdout and ffmpeg_stdout.strip():
                    self.log_message(f"[FFMPEG stdout - GX{video_key}]:\n{ffmpeg_stdout.strip()}")

                if ffmpeg_stderr and ffmpeg_stderr.strip():
                    if retcode == 0:
                        self.log_message(f"[FFMPEG 情報 - GX{video_key}]:\n{ffmpeg_stderr.strip()}")
                    else:
                        self.log_message(f"[FFMPEG エラー - GX{video_key}]:\n{ffmpeg_stderr.strip()}")

                if retcode == 0:
                    self.log_message(f"GX{video_key} の結合に成功しました。出力先: {output_dir_for_concat.joinpath(f'GX{video_key}.mp4')}")
                elif retcode == -1:
                    self.log_message("エラー: ffmpegコマンドが見つかりません。インストールとPATH設定を確認してください。")
                    any_error_occurred = True
                    break
                elif retcode == -2:
                    self.log_message(f"エラー: GX{video_key} の処理中にffmpeg実行エラーが発生しました。詳細は上記のffmpegエラー出力を確認してください。")
                    any_error_occurred = True
                elif retcode == -3:
                     self.log_message(f"エラー: GX{video_key} の処理中に出力ディレクトリ作成エラーが発生しました。パス: {output_dir_for_concat}")
                     any_error_occurred = True
                else:
                    self.log_message(f"エラー: GX{video_key} の結合に失敗しました。ffmpegリターンコード: {retcode}。詳細は上記のffmpegエラー出力を確認してください。")
                    any_error_occurred = True

            if not any_error_occurred and list(TEMP_FFMPEG_DIR_GUI.glob("*.txt")): # Ensure txt files existed for processing
                 self.log_message("全ての動画セットの結合処理が完了しました。")
            elif any_error_occurred and list(TEMP_FFMPEG_DIR_GUI.glob("*.txt")):
                 self.log_message("いくつかのエラーが発生したため、結合処理が中断または部分的に失敗しました。")

            if delete_temp_files:
                self.log_message(f"一時指示書を削除中: {TEMP_FFMPEG_DIR_GUI}")
                delete_file_list(TEMP_FFMPEG_DIR_GUI)
                stdout_content = captured_output.getvalue(); captured_output.seek(0); captured_output.truncate(0)
                if stdout_content.strip(): self.log_message(f"[内部ログ - delete_file_list]:\n{stdout_content.strip()}")
                self.log_message("一時指示書を削除しました。")
            else:
                self.log_message(f"一時指示書は保存されています: {TEMP_FFMPEG_DIR_GUI}")

        except ValueError as ve:
            self.log_message(f"処理エラー: {ve}")
            any_error_occurred = True
        except Exception as e:
            self.log_message(f"予期せぬエラーが発生しました: {e}")
            any_error_occurred = True
            import traceback
            self.log_message(f"トレースバック:\n{traceback.format_exc()}")
        finally:
            sys.stdout = old_stdout
            self.start_button.configure(state="normal")
            if any_error_occurred:
                self.log_message("処理がエラーで終了しました。ログを確認してください。")
            elif not video_set_processed:
                 self.log_message("処理が開始されませんでした（動画元フォルダの問題等）。")
            elif not video_set and video_set_processed : # No videos found initially
                 self.log_message("処理が終了しました (対象動画なし)。")
            elif video_set and not list(TEMP_FFMPEG_DIR_GUI.glob("*.txt")) and video_set_processed : # Videos found but no txt files made
                 self.log_message("処理が終了しました (指示書作成失敗または対象ファイルなし)。")
            else: # Normal successful completion
                 self.log_message("処理が正常に終了しました。")

if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

    app = App()
    app.mainloop()
