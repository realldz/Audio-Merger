from dataclasses import dataclass, field
from typing import Optional

@dataclass
class AudioFile:
    path: str
    title: str
    display_name: str
    is_pinned: bool = False

@dataclass
class Settings:
    output_folder: str = ''
    output_file: str = ''
    log_file: str = ''
    silence_thresh: float = -50.0
    chunk_size: int = 10