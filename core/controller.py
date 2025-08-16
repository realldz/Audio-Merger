import os
import random
import music_tag
from datetime import datetime
from PyQt5.QtCore import QTime
from PyQt5.QtWidgets import QMessageBox
from core.models import AudioFile
from services.audio_service import MergeMP3Thread
from services.settings_service import load_settings, save_settings

class Controller:
    def __init__(self, view):
        self.view = view
        self.audio_files = []

    def sort_files(self):
        # Sorts the list to bring pinned items to the top.
        # The key `not af.is_pinned` makes False (pinned) come before True (not pinned).
        self.audio_files.sort(key=lambda af: not af.is_pinned)

    def add_files(self, files):
        for file in files:
            metadata = music_tag.load_file(file)
            title = metadata['title'] if metadata['title'] else None
            display_name = title if title else os.path.basename(file).title()[:-4]
            # New files are not pinned by default
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
        output_folder = self.view.output_path.text() or os.getcwd()
        output_file_name = self.view.output_file_name.text() or datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file_name = self.view.log_file_name.text()
        
        if self.audio_files:
            self.view.start_time = QTime(0, 0, 0)
            file_paths_to_merge = [af.path for af in self.audio_files]
            output_file = os.path.join(output_folder, output_file_name + '.mp3')
            log_file = os.path.join(output_folder, log_file_name + '.txt') if log_file_name else None
            self.view.thread = MergeMP3Thread(file_paths_to_merge, output_file, log_file=log_file)
            self.view.thread.progress.connect(self.view.update_progress)
            self.view.thread.finished.connect(self.view.on_merge_finished)
            self.view.timer.start(1000)
            self.view.thread.start()
            self.view.toggle_ui(False)
        else:
            QMessageBox.warning(self.view, 'Warning', 'Please add at least one audio file.')

    def load_settings(self):
        settings = load_settings()
        self.view.output_path.setText(settings.get('output_folder', ''))
        self.view.output_file_name.setText(settings.get('output_file', ''))
        self.view.log_file_name.setText(settings.get('log_file', ''))

    def save_settings(self):
        settings = {
            'output_folder': self.view.output_path.text(),
            'output_file': self.view.output_file_name.text(),
            'log_file': self.view.log_file_name.text()
        }
        save_settings(settings)