from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QLineEdit, QProgressBar, QMessageBox, QListWidget, QAbstractItemView, QListWidgetItem)
from PyQt5.QtCore import QTimer, QTime
from PyQt5.QtGui import QDragEnterEvent, QDropEvent
from core.controller import Controller
from ui.track_widget import TrackWidget

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()
        self.title = 'Audio Merger'
        self.controller = Controller(self)
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        self.setAcceptDrops(True)
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

        self.time_label = QLabel('Time Elapsed: 00:00:00')
        layout.addWidget(self.time_label)

        self.merge_button = QPushButton('Merge Audio', self)
        self.merge_button.clicked.connect(self.merge_audio)
        layout.addWidget(self.merge_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.start_time = QTime(0, 0, 0)

        self.setLayout(layout)
        self.controller.load_settings()
        self.show()

    def rebuild_file_list(self, audio_files):
        self.files_list.clear()
        for i, audio_file in enumerate(audio_files):
            list_item = QListWidgetItem(self.files_list)
            track_widget = TrackWidget(audio_file.path, audio_file.is_pinned)
            
            # Connect the pin toggle signal to the controller
            track_widget.pin_toggled.connect(partial(self.controller.toggle_pin_status, i))
            
            list_item.setSizeHint(track_widget.sizeHint())
            self.files_list.addItem(list_item)
            self.files_list.setItemWidget(list_item, track_widget)

    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(self, 'Select Audio Files', '', 'Audio Files (*.mp3 *.wav)')
        if files:
            self.controller.add_files(files)

    def remove_files(self):
        self.controller.remove_files()

    def shuffle_files(self):
        self.controller.shuffle_files()

    def update_track_count(self):
        self.track_count_label.setText(f'Number of track: {self.files_list.count()}')

    def browse_output_folder(self):
        folder = QFileDialog.getExistingDirectory(self, 'Select Output Folder')
        if folder:
            self.output_path.setText(folder)
            
    def update_timer(self):
        elapsed_time = self.start_time.addSecs(1)
        self.start_time = elapsed_time
        self.time_label.setText(f'Time Elapsed: {elapsed_time.toString("hh:mm:ss")}')
        
    def merge_audio(self):
        self.controller.merge_audio()

    def update_progress(self, value):
        self.progress_bar.setValue(value)

    def on_merge_finished(self):
        self.timer.stop()
        QMessageBox.information(self, 'Information', 'Audio files have been merged successfully!')
        self.toggle_ui(True)
        self.controller.save_settings()

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

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                file_path = url.toLocalFile()
                if file_path.endswith(('.mp3', '.wav')):
                    files.append(file_path)
        if files:
            self.controller.add_files(files)