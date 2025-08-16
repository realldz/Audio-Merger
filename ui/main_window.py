from functools import partial
from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, 
                             QLineEdit, QProgressBar, QMessageBox, QListWidget, QAbstractItemView, QListWidgetItem,
                             QDoubleSpinBox, QSpinBox, QFrame, QTextEdit, QCheckBox, QComboBox, QSizePolicy)
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
        self.files_list.setProperty("disableOnMerge", True)
        self.files_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.files_list.setDragDropMode(QAbstractItemView.InternalMove)
        self.add_files_button = QPushButton('Add Files', self)
        self.add_files_button.setProperty("disableOnMerge", True)
        self.add_files_button.clicked.connect(self.add_files)
        self.remove_files_button = QPushButton('Remove Selected Files', self)
        self.remove_files_button.setProperty("disableOnMerge", True)
        self.remove_files_button.clicked.connect(self.remove_files)
        self.shuffle_files_button = QPushButton('Shuffle', self)
        self.shuffle_files_button.setProperty("disableOnMerge", True)
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
        self.output_path.setProperty("disableOnMerge", True)
        self.output_button = QPushButton('Browse', self)
        self.output_button.setProperty("disableOnMerge", True)
        self.output_button.clicked.connect(self.browse_output_folder)
        output_folder_layout.addWidget(self.output_label)
        output_folder_layout.addWidget(self.output_path)
        output_folder_layout.addWidget(self.output_button)
        output_group_layout.addLayout(output_folder_layout)
        output_file_layout = QHBoxLayout()
        self.output_file_label = QLabel('Output File Name:')
        self.output_file_name = QLineEdit(self)
        self.output_file_name.setProperty("disableOnMerge", True)
        output_file_layout.addWidget(self.output_file_label)
        output_file_layout.addWidget(self.output_file_name)
        output_group_layout.addLayout(output_file_layout)
        log_file_layout = QHBoxLayout()
        self.log_file_label = QLabel('Log File Name (optional):')
        self.log_file_name = QLineEdit(self)
        self.log_file_name.setProperty("disableOnMerge", True)
        self.log_file_name.textChanged.connect(self.update_ai_button_states)
        log_file_layout.addWidget(self.log_file_label)
        log_file_layout.addWidget(self.log_file_name)
        output_group_layout.addLayout(log_file_layout)
        main_layout.addLayout(output_group_layout)

        main_layout.addWidget(self.create_separator())

        # --- Silence Removal Section ---
        settings_layout = QHBoxLayout()
        thresh_layout = QVBoxLayout()
        self.silence_thresh_label = QLabel("Silence Threshold (dBFS):")
        self.silence_thresh_input = QDoubleSpinBox()
        self.silence_thresh_input.setProperty("disableOnMerge", True)
        self.silence_thresh_input.setRange(-100.0, 0.0)
        self.silence_thresh_input.setSingleStep(1.0)
        thresh_desc = QLabel("Max volume to be considered silent.")
        thresh_desc.setStyleSheet("color: gray;")
        thresh_layout.addWidget(self.silence_thresh_label)
        thresh_layout.addWidget(self.silence_thresh_input)
        thresh_layout.addWidget(thresh_desc)
        thresh_layout.addStretch()
        chunk_layout = QVBoxLayout()
        self.chunk_size_label = QLabel("Chunk Size (ms):")
        self.chunk_size_input = QSpinBox()
        self.chunk_size_input.setProperty("disableOnMerge", True)
        self.chunk_size_input.setRange(1, 1000)
        chunk_desc = QLabel("Step size for silence detection.")
        chunk_desc.setStyleSheet("color: gray;")
        chunk_layout.addWidget(self.chunk_size_label)
        chunk_layout.addWidget(self.chunk_size_input)
        chunk_layout.addWidget(chunk_desc)
        chunk_layout.addStretch()
        settings_layout.addLayout(thresh_layout)
        settings_layout.addLayout(chunk_layout)
        main_layout.addLayout(settings_layout)

        main_layout.addWidget(self.create_separator())

        # --- AI Standardization Section ---
        ai_layout = QVBoxLayout()
        ai_title_label = QLabel("AI Standardization Settings")
        font = ai_title_label.font()
        font.setBold(True)
        ai_title_label.setFont(font)
        ai_layout.addWidget(ai_title_label)

        self.api_key_label = QLabel("Gemini API Key:")
        self.api_key_input = QLineEdit()
        self.api_key_input.setProperty("disableOnMerge", True)
        self.api_key_input.setEchoMode(QLineEdit.Password)
        self.api_key_input.textChanged.connect(self.update_ai_button_states)
        ai_layout.addWidget(self.api_key_label)
        ai_layout.addWidget(self.api_key_input)

        model_layout = QHBoxLayout()
        self.model_name_label = QLabel("Gemini Model Name:")
        self.model_name_input = QComboBox()
        self.model_name_input.setProperty("disableOnMerge", True)
        self.model_name_input.setEditable(True)
        self.model_name_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.refresh_models_button = QPushButton("Refresh List")
        self.refresh_models_button.setProperty("disableOnMerge", True)
        self.refresh_models_button.clicked.connect(self.fetch_models)
        model_layout.addWidget(self.model_name_label)
        model_layout.addWidget(self.model_name_input)
        model_layout.addWidget(self.refresh_models_button)
        ai_layout.addLayout(model_layout)

        self.simple_ai_group = QWidget()
        simple_ai_layout = QVBoxLayout(self.simple_ai_group)
        simple_ai_layout.setContentsMargins(0,0,0,0)
        self.custom_keywords_label = QLabel("Custom keywords to remove (comma-separated):")
        self.custom_keywords_input = QLineEdit()
        self.custom_keywords_input.setProperty("disableOnMerge", True)
        simple_ai_layout.addWidget(self.custom_keywords_label)
        simple_ai_layout.addWidget(self.custom_keywords_input)
        ai_layout.addWidget(self.simple_ai_group)

        self.advanced_ai_group = QWidget()
        advanced_ai_layout = QVBoxLayout(self.advanced_ai_group)
        advanced_ai_layout.setContentsMargins(0,0,0,0)
        self.custom_prompt_label = QLabel("Advanced: Custom Prompt")
        self.custom_prompt_input = QTextEdit()
        self.custom_prompt_input.setProperty("disableOnMerge", True)
        self.custom_prompt_input.setAcceptRichText(False)
        advanced_ai_layout.addWidget(self.custom_prompt_label)
        advanced_ai_layout.addWidget(self.custom_prompt_input)
        ai_layout.addWidget(self.advanced_ai_group)

        self.advanced_mode_checkbox = QCheckBox("Enable advanced prompt editing mode")
        self.advanced_mode_checkbox.setProperty("disableOnMerge", True)
        self.advanced_mode_checkbox.toggled.connect(self.toggle_advanced_mode)
        ai_layout.addWidget(self.advanced_mode_checkbox)
        
        self.standardize_button = QPushButton("Standardize Log with AI 💎")
        self.standardize_button.setProperty("disableOnMerge", True)
        self.standardize_button.clicked.connect(self.standardize_log)
        ai_layout.addWidget(self.standardize_button)

        main_layout.addLayout(ai_layout)

        main_layout.addStretch()
        self.progress_bar = QProgressBar(self)
        self.time_label = QLabel('Time Elapsed: 00:00:00')
        self.merge_button = QPushButton('Merge Audio', self)
        self.merge_button.setProperty("disableOnMerge", True)
        self.merge_button.clicked.connect(self.merge_audio)
        main_layout.addWidget(self.progress_bar)
        main_layout.addWidget(self.time_label)
        main_layout.addWidget(self.merge_button)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.start_time = QTime(0, 0, 0)

        self.setLayout(main_layout)
        self.controller.load_settings()
        self.toggle_advanced_mode(self.advanced_mode_checkbox.isChecked())
        self.update_ai_button_states()
        self.show()

    def create_separator(self):
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        return line

    def toggle_advanced_mode(self, checked):
        self.simple_ai_group.setVisible(not checked)
        self.advanced_ai_group.setVisible(checked)

    def update_ai_button_states(self):
        api_key_present = bool(self.api_key_input.text())
        log_file_present = bool(self.log_file_name.text())
        self.refresh_models_button.setEnabled(api_key_present)
        self.standardize_button.setEnabled(api_key_present and log_file_present)

    def toggle_ui(self, enabled):
        # Automatically find and toggle all widgets marked with 'disableOnMerge'
        for widget in self.findChildren(QWidget):
            if widget.property("disableOnMerge"):
                widget.setEnabled(enabled)
        
        # Post-merge, re-evaluate the state of AI buttons
        if enabled:
            self.update_ai_button_states()

    def fetch_models(self):
        self.controller.handle_fetch_models()

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

    def standardize_log(self):
        self.controller.handle_standardize_log()

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
