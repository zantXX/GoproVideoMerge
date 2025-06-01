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
        self.title("GoPro Video Concatenator")
        self.geometry("700x550")

        # --- UI Elements ---
        # Raw Video Path
        self.raw_video_label = customtkinter.CTkLabel(self, text="Raw Video Folder:")
        self.raw_video_label.grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.raw_video_path_entry = customtkinter.CTkEntry(self, width=400)
        self.raw_video_path_entry.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        self.raw_video_button = customtkinter.CTkButton(self, text="Select Folder", command=self.select_raw_video_dir)
        self.raw_video_button.grid(row=0, column=2, padx=10, pady=5)

        # Output Path
        self.output_dir_label = customtkinter.CTkLabel(self, text="Output Folder:")
        self.output_dir_label.grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.output_dir_path_entry = customtkinter.CTkEntry(self, width=400)
        self.output_dir_path_entry.grid(row=1, column=1, padx=10, pady=5, sticky="ew")
        self.output_dir_button = customtkinter.CTkButton(self, text="Select Folder", command=self.select_output_dir)
        self.output_dir_button.grid(row=1, column=2, padx=10, pady=5)

        # Delete temp files checkbox
        self.delete_temp_checkbox = customtkinter.CTkCheckBox(self, text="Delete temporary ffmpeg files after concatenation")
        self.delete_temp_checkbox.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        self.delete_temp_checkbox.select() # Default to checked

        # Start button
        self.start_button = customtkinter.CTkButton(self, text="Start Concatenation", command=self.start_concatenation_thread)
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
            self.log_message(f"Selected Raw Video Folder: {path}")

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir_path_entry.delete(0, "end")
            self.output_dir_path_entry.insert(0, path)
            self.log_message(f"Selected Output Folder: {path}")

    def start_concatenation_thread(self):
        self.start_button.configure(state="disabled")
        self.log_message("Starting concatenation process...")
        thread = threading.Thread(target=self.run_concatenation)
        thread.start()

    def run_concatenation(self):
        raw_video_dir_str = self.raw_video_path_entry.get()
        output_dir_str = self.output_dir_path_entry.get()
        delete_temp_files = self.delete_temp_checkbox.get() == 1

        if not raw_video_dir_str or not output_dir_str:
            self.log_message("Error: Raw video folder and Output folder must be selected.")
            self.start_button.configure(state="normal")
            return

        raw_video_path = Path(raw_video_dir_str)
        output_path = Path(output_dir_str)

        # Use a specific temp directory for the GUI to avoid conflicts
        TEMP_FFMPEG_DIR_GUI.mkdir(parents=True, exist_ok=True)
        self.log_message(f"Using temporary directory: {TEMP_FFMPEG_DIR_GUI.resolve()}")


        # Redirect stdout to log_textbox for messages from imported modules
        old_stdout = sys.stdout
        sys.stdout = captured_output = io.StringIO()

        try:
            self.log_message(f"Scanning for videos in: {raw_video_path}")
            video_set = video_key_listing(raw_video_path)

            # Log captured stdout from video_key_listing if any
            stdout_content = captured_output.getvalue()
            if stdout_content: self.log_message(f"[video_key_listing output]:\n{stdout_content}")
            captured_output.seek(0); captured_output.truncate(0) # Reset StringIO

            if not video_set:
                self.log_message("No video sets found to concatenate.")
                self.start_button.configure(state="normal")
                sys.stdout = old_stdout # Restore stdout
                return

            self.log_message(f"Found video sets: {', '.join(video_set.keys())}")

            self.log_message(f"Writing ffmpeg file lists to: {TEMP_FFMPEG_DIR_GUI}")
            write_file_list(video_set, TEMP_FFMPEG_DIR_GUI)
            stdout_content = captured_output.getvalue()
            if stdout_content: self.log_message(f"[write_file_list output]:\n{stdout_content}")
            captured_output.seek(0); captured_output.truncate(0)


            self.log_message("Starting video concatenation...")
            for ffmpeg_file_name in TEMP_FFMPEG_DIR_GUI.glob("*.txt"):
                video_key = ffmpeg_file_name.stem
                self.log_message(f"Processing video set: GX{video_key}")
                video_concat(ffmpeg_file_name, output_path, f"GX{video_key}")
                stdout_content = captured_output.getvalue() # Capture subprocess output if it prints
                if stdout_content: self.log_message(f"[ffmpeg output for GX{video_key}]:\n{stdout_content}")
                captured_output.seek(0); captured_output.truncate(0)
                self.log_message(f"Finished processing GX{video_key}")

            self.log_message("Video concatenation complete.")

            if delete_temp_files:
                self.log_message(f"Deleting temporary ffmpeg files from: {TEMP_FFMPEG_DIR_GUI}")
                delete_file_list(TEMP_FFMPEG_DIR_GUI)
                stdout_content = captured_output.getvalue()
                if stdout_content: self.log_message(f"[delete_file_list output]:\n{stdout_content}")
                captured_output.seek(0); captured_output.truncate(0)
                self.log_message("Temporary files deleted.")
            else:
                self.log_message(f"Temporary ffmpeg files kept in: {TEMP_FFMPEG_DIR_GUI}")

        except ValueError as ve:
            self.log_message(f"Error: {ve}")
        except Exception as e:
            self.log_message(f"An unexpected error occurred: {e}")
        finally:
            sys.stdout = old_stdout # Restore stdout
            self.start_button.configure(state="normal")
            self.log_message("Process finished.")

if __name__ == "__main__":
    customtkinter.set_appearance_mode("System")  # Modes: "System" (default), "Dark", "Light"
    customtkinter.set_default_color_theme("blue")  # Themes: "blue" (default), "green", "dark-blue"

    app = App()
    app.mainloop()
