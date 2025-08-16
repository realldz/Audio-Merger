# Audio Merger

A simple yet powerful desktop application for merging audio files, with advanced features like silence removal and AI-powered log standardization. Built with Python, PyQt5, and Pydub.

## Features

*   **Merge Audio Files:** Combine multiple MP3 and WAV audio files into a single output file.
*   **Intuitive File Management:**
    *   Drag-and-drop support for easily adding files.
    *   Reorder tracks by dragging them within the list.
    *   Shuffle tracks randomly.
    *   Pin specific tracks to keep them in their position during shuffling.
*   **Configurable Silence Removal:** Automatically detect and remove silent segments from audio tracks during the merging process, with adjustable silence threshold and chunk size.
*   **AI-Powered Log Standardization:**
    *   Utilize the Google Gemini API to standardize and clean up track lists or log files.
    *   Supports custom keywords for removal and an advanced mode for custom AI prompts.

## Installation

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)
*   `venv` (Python virtual environment module)

### Steps

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/realldz/Audio-Merger.git
    cd Audio-Merger
    ```
2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv .venv
    # On Windows:
    .venv\Scripts\activate
    # On macOS/Linux:
    source .venv/bin/activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python main.py
    ```
2.  **Add Audio Files:** Drag and drop MP3/WAV files onto the application window, or use the "Add Files" button.
3.  **Manage Tracks:** Reorder, remove, shuffle, or pin tracks as needed.
4.  **Configure Output:** Specify the output folder and desired output file name.
5.  **Silence Removal:** Adjust "Silence Threshold" and "Chunk Size" in the settings section if you want to remove silence.
6.  **AI Standardization (Optional):**
    *   Enter your Google Gemini API Key in the "AI Standardization Settings" section.
    *   Select a Gemini model or refresh the list.
    *   Provide a log file name (from the "Output" section).
    *   Use "Custom keywords to remove" for simple cleaning or enable "Advanced prompt editing mode" for a custom AI prompt.
    *   Click "Standardize Log with AI 💎" to process the log file. The standardized log will open automatically.
7.  **Merge Audio:** Click the "Merge Audio" button to start the merging process.

### Logging Configuration

Logging settings are managed via the `settings.json` file in the application's root directory. If the file doesn't exist, default settings will be used.

Example `settings.json` for logging to a file:

```json
{
    "log": {
        "level": "INFO",
        "handler": "file",
        "file_name": "audio_merger.log",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}
```

Example `settings.json` for logging to console (stdout):

```json
{
    "log": {
        "level": "DEBUG",
        "handler": "stdout",
        "format": "%(asctime)s - %(levelname)s - %(message)s"
    }
}
```

Set `"level": "NONE"` to disable logging.

## Building Executable (Windows)

You can create a standalone executable using PyInstaller.

1.  **Install PyInstaller:**
    ```bash
    pip install pyinstaller
    ```
2.  **Build the executable:**
    ```bash
    pyinstaller --noconfirm --onefile --windowed --name "AudioMerger" main.py
    ```
    *   `--noconfirm`: Overwrite existing `dist` and `build` folders without asking.
    *   `--onefile`: Create a single executable file.
    *   `--windowed`: Create a windowed application (no console window).
    *   `--name "AudioMerger"`: Name the executable `AudioMerger.exe`.
3.  **Find the executable:** The executable will be located in the `dist/` folder.

## Credits

This project utilizes the following open-source libraries:

*   **Pydub**
*   **PyQt5**
*   **music-tag**
*   **google-generativeai**

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.