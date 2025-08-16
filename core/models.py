from dataclasses import dataclass

@dataclass
class AudioFile:
    path: str
    title: str
    display_name: str
    is_pinned: bool = False
