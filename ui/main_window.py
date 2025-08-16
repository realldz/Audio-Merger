from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QLineEdit, QProgressBar, QMessageBox, QListWidget, QAbstractItemView, QListWidgetItem,
                             QDoubleSpinBox, QSpinBox, QFrame)
from PyQt5.QtCore import QTimer, QTime, Qt
from PyQt5.QtGui import QDragEnterEvent, QDropEvent, QFont
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
        main_layout = QVBoxLayout()

        # --- File List Section ---
        files_layout = QVBoxLayout()
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
        files_layout.addWidget(self.files_label)
        files_layout.addWidget(self.files_list)
        files_button_layout = QHBoxLayout()
        files_button_layout.addWidget(self.add_files_button)
        files_button_layout.addWidget(self.remove_files_button)
        files_button_layout.addWidget(self.shuffle_files_button)
        files_layout.addLayout(files_button_layout)
        main_layout.addLayout(files_layout)

        self.track_count_label = QLabel(f'Number of track: {self.files_list.count()}')
        main_layout.addWidget(self.track_count_label)

        # --- Output Section ---
        output_group_layout = QVBoxLayout()
        output_folder_layout = QHBoxLayout()
        self.output_label = QLabel('Output Folder:')
        self.output_path = QLineEdit(self)
        self.output_button = QPushButton('Browse', self)
        self.output_button.clicked.connect(self.browse_output_folder)
        output_folder_layout.addWidget(self.output_label)
        output_folder_layout.addWidget(self.output_path)
        output_folder_layout.addWidget(self.output_button)
        output_group_layout.addLayout(output_folder_layout)

        output_file_layout = QHBoxLayout()
        self.output_file_label = QLabel('Output File Name:')
        self.output_file_name = QLineEdit(self)
        output_file_layout.addWidget(self.output_file_label)
        output_file_layout.addWidget(self.output_file_name)
        output_group_layout.addLayout(output_file_layout)

        log_file_layout = QHBoxLayout()
        self.log_file_label = QLabel('Log File Name (optional):')
        self.log_file_name = QLineEdit(self)
        log_file_layout.addWidget(self.log_file_label)
        log_file_layout.addWidget(self.log_file_name)
        output_group_layout.addLayout(log_file_layout)
        main_layout.addLayout(output_group_layout)

        # --- Line Separator ---
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        main_layout.addWidget(line)

        # --- Silence Removal Section ---
        settings_layout = QHBoxLayout()
        # Silence Threshold
        thresh_layout = QVBoxLayout()
        self.silence_thresh_label = QLabel("Silence Threshold (dBFS):")
        self.silence_thresh_input = QDoubleSpinBox()
        self.silence_thresh_input.setRange(-100.0, 0.0)
        self.silence_thresh_input.setSingleStep(1.0)
        thresh_desc = QLabel("Max volume to be considered silent.")
        thresh_desc.setStyleSheet("color: gray;")
        thresh_layout.addWidget(self.silence_thresh_label)
        thresh_layout.addWidget(self.silence_thresh_input)
        thresh_layout.addWidget(thresh_desc)
        thresh_layout.addStretch()

        # Chunk Size
        chunk_layout = QVBoxLayout()
        self.chunk_size_label = QLabel("Chunk Size (ms):")
        self.chunk_size_input = QSpinBox()
        self.chunk_size_input.setRange(1, 1000)
        chunk_desc = QLabel("Step size for silence detection. Smaller is more precise.")
        chunk_desc.setStyleSheet("color: gray;")
        chunk_layout.addWidget(self.chunk_size_label)
        chunk_layout.addWidget(self.chunk_size_input)
        chunk_layout.addWidget(chunk_desc)
        chunk_layout.addStretch()

        settings_layout.addLayout(thresh_layout)
        settings_layout.addLayout(chunk_layout)
        main_layout.addLayout(settings_layout)

        # --- Progress and Merge Section ---
        main_layout.addStretch()
        self.progress_bar = QProgressBar(self)
        main_layout.addWidget(self.progress_bar)

        self.time_label = QLabel('Time Elapsed: 00:00:00')
        main_layout.addWidget(self.time_label)

        self.merge_button = QPushButton('Merge Audio', self)
        self.merge_button.clicked.connect(self.merge_audio)
        main_layout.addWidget(self.merge_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.start_time = QTime(0, 0, 0)

        self.setLayout(main_layout)
        self.controller.load_settings()
        self.show()

    def rebuild_file_list(self, audio_files):
        self.files_list.clear()
        for i, audio_file in enumerate(audio_files):
            list_item = QListWidgetItem(self.files_list)
            track_widget = TrackWidget(audio_file.path, audio_file.is_pinned)
            
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