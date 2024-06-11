import sys
import os
import json
import random
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QLineEdit, QProgressBar, QMessageBox, QListWidget, QListWidgetItem, QAbstractItemView)
from PyQt5.QtCore import QThread, pyqtSignal
from pydub import AudioSegment
from pydub.silence import detect_nonsilent

def remove_silence(audio_segment, silence_thresh=-50.0, chunk_size=10):
    nonsilent_parts = detect_nonsilent(audio_segment, min_silence_len=chunk_size, silence_thresh=silence_thresh)
    if nonsilent_parts:
        start_trim = nonsilent_parts[0][0]
        end_trim = nonsilent_parts[-1][1]
        return audio_segment[start_trim:end_trim]
    return audio_segment

class MergeMP3Thread(QThread):
    progress = pyqtSignal(int)
    log = pyqtSignal(str)

    def __init__(self, audio_files, output_file, silence_thresh=-50.0, chunk_size=10, log_file=None):
        super().__init__()
        self.audio_files = audio_files
        self.output_file = output_file
        self.silence_thresh = silence_thresh
        self.chunk_size = chunk_size
        self.log_file = log_file

    def run(self):
        combined = AudioSegment.empty()
        total_files = len(self.audio_files)
        current_time = 0

        log_entries = []

        for i, audio_file in enumerate(self.audio_files):
            audio = AudioSegment.from_file(audio_file)
            audio = remove_silence(audio, silence_thresh=self.silence_thresh, chunk_size=self.chunk_size)
            combined += audio

            metadata = audio.tags
            title = metadata.get('title') if metadata else None
            display_name = title if title else os.path.basename(audio_file)

            log_entries.append(f"{self.format_time(current_time)} {display_name}")
            current_time += len(audio) // 1000

            self.progress.emit(int((i + 1) / total_files * 99))

        combined.export(self.output_file, format='mp3')

        if self.log_file:
            with open(self.log_file, 'w', encoding='utf-8') as f:
                for entry in log_entries:
                    f.write(entry + '\n')
        
        self.progress.emit(100)

    @staticmethod
    def format_time(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"
        else:
            return f"{int(minutes):02}:{int(seconds):02}"


class App(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Audio Merger'
        self.settings_file = 'settings.json'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)

        layout = QVBoxLayout()

        self.files_label = QLabel('Audio Files:')
        self.files_list = QListWidget(self)
        self.files_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.files_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.add_files_button = QPushButton('Add Files', self)
        self.add_files_button.clicked.connect(self.add_files)
        self.remove_files_button = QPushButton('Remove Selected Files', self)
        self.remove_files_button.clicked.connect(self.remove_files)
        self.shuffle_files_button = QPushButton('Shuffle', self)
        self.shuffle_files_button.clicked.connect(self.shuffle_files)

        files_layout = QVBoxLayout()
        files_layout.addWidget(self.files_label)
        files_layout.addWidget(self.files_list)
        files_layout.addWidget(self.add_files_button)
        files_layout.addWidget(self.remove_files_button)
        files_layout.addWidget(self.shuffle_files_button)
        layout.addLayout(files_layout)

        self.track_count_label = QLabel(f'Number of track: {self.files_list.count()}')
        layout.addWidget(self.track_count_label)

        self.output_label = QLabel('Output Folder:')
        self.output_path = QLineEdit(self)
        self.output_button = QPushButton('Browse', self)
        self.output_button.clicked.connect(self.browse_output_folder)

        output_layout = QHBoxLayout()
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(self.output_path)
        output_layout.addWidget(self.output_button)
        layout.addLayout(output_layout)

        self.output_file_label = QLabel('Output File Name:')
        self.output_file_name = QLineEdit(self)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.output_file_label)
        file_layout.addWidget(self.output_file_name)
        layout.addLayout(file_layout)

        self.log_file_label = QLabel('Log File Name (optional):')
        self.log_file_name = QLineEdit(self)

        log_layout = QHBoxLayout()
        log_layout.addWidget(self.log_file_label)
        log_layout.addWidget(self.log_file_name)
        layout.addLayout(log_layout)

        self.progress_bar = QProgressBar(self)
        layout.addWidget(self.progress_bar)

        self.merge_button = QPushButton('Merge Audio', self)
        self.merge_button.clicked.connect(self.merge_audio)

        layout.addWidget(self.merge_button)

        self.setLayout(layout)
        self.load_settings()
        self.show()

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Audio Files', '', 'Audio Files (*.mp3 *.wav)')
        for file in files:
            self.files_list.addItem(QListWidgetItem(file))
        self.update_track_count()

    def remove_files(self):
        for item in self.files_list.selectedItems():
            self.files_list.takeItem(self.files_list.row(item))
        self.update_track_count()

    def shuffle_files(self):
        items = [self.files_list.takeItem(0) for _ in range(self.files_list.count())]
        random.shuffle(items)
        for item in items:
            self.files_list.addItem(item)
        self.update_track_count()

    def update_track_count(self):
        self.track_count_label.setText(f'Number of track: {self.files_list.count()}')

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if folder:
            self.output_path.setText(folder)

    def merge_audio(self):
        audio_files = [self.files_list.item(i).text() for i in range(self.files_list.count())]
        output_folder = self.output_path.text() or os.getcwd()
        output_file_name = self.output_file_name.text() or datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        log_file_name = self.log_file_name.text()

        if audio_files:
            output_file = os.path.join(output_folder, output_file_name + '.mp3')
            log_file = os.path.join(output_folder, log_file_name + '.txt') if log_file_name else None
            self.thread = MergeMP3Thread(audio_files, output_file, log_file=log_file)
            self.thread.progress.connect(self.update_progress)
            self.thread.finished.connect(self.on_merge_finished)
            self.thread.start()
            self.toggle_ui(False)
        else:
            QMessageBox.warning(self, 'Warning', 'Please add at least one audio file.')

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_merge_finished(self):
        QMessageBox.information(self, 'Information', 'Audio files have been merged successfully!')
        self.toggle_ui(True)
        self.save_settings()

    def toggle_ui(self, enabled):
        self.add_files_button.setEnabled(enabled)
        self.remove_files_button.setEnabled(enabled)
        self.shuffle_files_button.setEnabled(enabled)
        self.output_button.setEnabled(enabled)
        self.merge_button.setEnabled(enabled)
        self.files_list.setEnabled(enabled)
        self.output_path.setEnabled(enabled)
        self.output_file_name.setEnabled(enabled)
        self.log_file_name.setEnabled(enabled)

    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                self.output_path.setText(settings.get('output_folder', ''))
                self.output_file_name.setText(settings.get('output_file', ''))
                self.log_file_name.setText(settings.get('log_file', ''))

    def save_settings(self):
        settings = {
            'output_folder': self.output_path.text(),
            'output_file': self.output_file_name.text(),
            'log_file': self.log_file_name.text()
        }
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, ensure_ascii=False, indent=4)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
