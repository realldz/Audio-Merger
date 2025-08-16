import os
import json
import dataclasses
from core.models import Settings, LogSettings

SETTINGS_FILE = 'settings.json'

def load_settings() -> Settings:
    if not os.path.exists(SETTINGS_FILE):
        return Settings() # Return default settings if file doesn't exist

    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
            
            # Handle LogSettings separately
            log_data = data.get('log', {})
            # Filter log_data to only include fields that are in the LogSettings dataclass
            known_log_fields = {f.name for f in dataclasses.fields(LogSettings)}
            filtered_log_data = {k: v for k, v in log_data.items() if k in known_log_fields}
            log_settings = LogSettings(**filtered_log_data)

            # Filter main settings data
            known_settings_fields = {f.name for f in dataclasses.fields(Settings) if f.name != 'log'}
            filtered_settings_data = {k: v for k, v in data.items() if k in known_settings_fields}
            
            # Create Settings object, passing the created LogSettings object
            return Settings(log=log_settings, **filtered_settings_data)

        except (json.JSONDecodeError, TypeError):
            return Settings() # Return default settings if file is corrupted or not a dict

def save_settings(settings: Settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        settings_dict = dataclasses.asdict(settings)
        json.dump(settings_dict, f, ensure_ascii=False, indent=4)
