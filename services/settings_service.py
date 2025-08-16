import os
import json
import dataclasses
from core.models import Settings

SETTINGS_FILE = 'settings.json'

def load_settings() -> Settings:
    if not os.path.exists(SETTINGS_FILE):
        return Settings()

    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            # Filter the data to only include fields that are in the Settings dataclass
            known_fields = {f.name for f in dataclasses.fields(Settings)}
            filtered_data = {k: v for k, v in data.items() if k in known_fields}
            return Settings(**filtered_data)
        except (json.JSONDecodeError, TypeError):
            return Settings() # Return default settings if file is corrupted or not a dict

def save_settings(settings: Settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        settings_dict = dataclasses.asdict(settings)
        json.dump(settings_dict, f, ensure_ascii=False, indent=4)