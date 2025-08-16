import os
import random
import music_tag
import sys
import subprocess
from datetime import datetime
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QMessageBox
from core.models import AudioFile, Settings
from services.audio_service import MergeMP3Thread
from services import settings_service
from services.ai_service import FetchModelsThread, StandardizeLogThread

class Controller:
    def __init__(self, view):
        self.view = view
        self.audio_files = []
        self.fetch_models_thread = None
        self.standardize_thread = None

    # ... (file handling methods are unchanged) ...
    def sort_files(self):
        self.audio_files.sort(key=lambda af: not af.is_pinned)

    def add_files(self, files):
        for file in files:
            metadata = music_tag.load_file(file)
            title = metadata['title'] if metadata['title'] else None
            display_name = title if title else os.path.basename(file).title()[:-4]
            audio_file = AudioFile(file, title, display_name, is_pinned=False)
            self.audio_files.append(audio_file)
        self.sort_files()
        self.refresh_view()

    def remove_files(self):
        selected_rows = sorted([self.view.files_list.row(item) for item in self.view.files_list.selectedItems()], reverse=True)
        for row in selected_rows:
            del self.audio_files[row]
        self.refresh_view()

    def shuffle_files(self):
        pinned_items = [af for af in self.audio_files if af.is_pinned]
        unpinned_items = [af for af in self.audio_files if not af.is_pinned]
        random.shuffle(unpinned_items)
        self.audio_files = pinned_items + unpinned_items
        self.refresh_view()

    def toggle_pin_status(self, index):
        if 0 <= index < len(self.audio_files):
            self.audio_files[index].is_pinned = not self.audio_files[index].is_pinned
            self.sort_files()
            self.refresh_view()

    def refresh_view(self):
        self.view.rebuild_file_list(self.audio_files)
        self.view.update_track_count()

    def merge_audio(self):
        # ... (merge_audio logic is unchanged)
        output_folder = self.view.output_path.text() or os.getcwd()
        output_file_name = self.view.output_file_name.text() or datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file_name = self.view.log_file_name.text()
        silence_thresh = self.view.silence_thresh_input.value()
        chunk_size = self.view.chunk_size_input.value()
        if self.audio_files:
            self.view.start_time = QTime(0, 0, 0)
            output_file = os.path.join(output_folder, output_file_name + '.mp3')
            log_file = os.path.join(output_folder, log_file_name + '.txt') if log_file_name else None
            self.view.thread = MergeMP3Thread(self.audio_files, output_file, silence_thresh=silence_thresh, chunk_size=chunk_size, log_file=log_file)
            self.view.thread.progress.connect(self.view.update_progress)
            self.view.thread.finished.connect(self.view.on_merge_finished)
            self.view.timer.start(1000)
            self.view.thread.start()
            self.view.toggle_ui(False)
        else:
            QMessageBox.warning(self.view, 'Warning', 'Please add at least one audio file.')

    def handle_fetch_models(self):
        # ... (handle_fetch_models logic is unchanged) ...
        api_key = self.view.api_key_input.text()
        if not api_key:
            QMessageBox.warning(self.view, 'Warning', 'Please enter your Gemini API Key first.')
            return
        self.view.refresh_models_button.setText("Fetching...")
        self.view.refresh_models_button.setEnabled(False)
        self.fetch_models_thread = FetchModelsThread(api_key)
        self.fetch_models_thread.finished.connect(self.on_fetch_models_finished)
        self.fetch_models_thread.start()

    def on_fetch_models_finished(self, result):
        # ... (on_fetch_models_finished logic is unchanged) ...
        success, data = result
        if success:
            current_model = self.view.model_name_input.currentText()
            self.view.model_name_input.clear()
            self.view.model_name_input.addItems(data)
            if current_model in data:
                self.view.model_name_input.setCurrentText(current_model)
            else:
                if data:
                    self.view.model_name_input.setCurrentIndex(0)
            QMessageBox.information(self.view, 'Success', 'Model list has been updated.')
        else:
            QMessageBox.critical(self.view, 'Error', data)
        self.view.refresh_models_button.setText("Refresh List")
        self.view.refresh_models_button.setEnabled(True)

    def handle_standardize_log(self):
        log_file_name = self.view.log_file_name.text()
        if not log_file_name:
            QMessageBox.warning(self.view, 'Warning', 'No log file name specified.')
            return
        output_folder = self.view.output_path.text() or os.getcwd()
        self.log_path = os.path.join(output_folder, log_file_name + '.txt')
        if not os.path.exists(self.log_path):
            QMessageBox.warning(self.view, 'Warning', f'Log file not found at: {self.log_path}')
            return
        with open(self.log_path, 'r', encoding='utf-8') as f:
            log_content = f.read()
        
        self.view.standardize_button.setEnabled(False)
        self.view.standardize_button.setText("Standardizing...")

        api_key = self.view.api_key_input.text()
        model_name = self.view.model_name_input.currentText()
        is_advanced = self.view.advanced_mode_checkbox.isChecked()
        custom_prompt = self.view.custom_prompt_input.toPlainText()
        custom_keywords = self.view.custom_keywords_input.text()

        self.standardize_thread = StandardizeLogThread(api_key, model_name, log_content, is_advanced, custom_prompt, custom_keywords)
        self.standardize_thread.finished.connect(self.on_standardize_log_finished)
        self.standardize_thread.start()

    def on_standardize_log_finished(self, result):
        success, data = result
        if success:
            with open(self.log_path, 'w', encoding='utf-8') as f:
                f.write(data)
            QMessageBox.information(self.view, 'Success', 'Log file has been standardized successfully!')
            self.open_file_with_default_app(self.log_path)
        else:
            QMessageBox.critical(self.view, 'Error', data)
        
        self.view.standardize_button.setText("Standardize Log with AI 💎")
        self.view.standardize_button.setEnabled(True)

    def open_file_with_default_app(self, file_path):
        # ... (open_file_with_default_app logic is unchanged) ...
        try:
            if sys.platform == "win32":
                os.startfile(file_path)
            elif sys.platform == "darwin":
                subprocess.run(["open", file_path], check=True)
            else:
                subprocess.run(["xdg-open", file_path], check=True)
        except Exception as e:
            QMessageBox.warning(self.view, 'Error', f"Could not open file: {e}")

    def load_settings(self):
        # ... (load_settings logic is unchanged) ...
        settings = settings_service.load_settings()
        self.view.output_path.setText(settings.output_folder)
        self.view.output_file_name.setText(settings.output_file)
        self.view.log_file_name.setText(settings.log_file)
        self.view.silence_thresh_input.setValue(settings.silence_thresh)
        self.view.chunk_size_input.setValue(settings.chunk_size)
        self.view.api_key_input.setText(settings.gemini_api_key)
        self.view.model_name_input.setCurrentText(settings.gemini_model_name)
        self.view.custom_keywords_input.setText(settings.custom_keywords)
        self.view.advanced_mode_checkbox.setChecked(settings.is_advanced_prompt_mode)
        self.view.custom_prompt_input.setPlainText(settings.custom_prompt)

    def save_settings(self):
        # ... (save_settings logic is unchanged) ...
        settings = Settings(
            output_folder=self.view.output_path.text(),
            output_file=self.view.output_file_name.text(),
            log_file=self.view.log_file_name.text(),
            silence_thresh=self.view.silence_thresh_input.value(),
            chunk_size=self.view.chunk_size_input.value(),
            gemini_api_key=self.view.api_key_input.text(),
            gemini_model_name=self.view.model_name_input.currentText(),
            custom_keywords=self.view.custom_keywords_input.text(),
            is_advanced_prompt_mode=self.view.advanced_mode_checkbox.isChecked(),
            custom_prompt=self.view.custom_prompt_input.toPlainText()
        )
        settings_service.save_settings(settings)
