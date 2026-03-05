"""Configuration management for CurseForge CLI."""
import json
import os
from pathlib import Path


class Config:
    """Manages CLI configuration (API key, mods path, etc.)."""

    def __init__(self, config_path: str = None):
        if config_path:
            self.config_path = Path(config_path)
        else:
            # Default to ~/.config/hytale-cf/config.json
            config_dir = Path.home() / ".config" / "hytale-cf"
            config_dir.mkdir(parents=True, exist_ok=True)
            self.config_path = config_dir / "config.json"

        self._data = self._load()

    def _load(self) -> dict:
        """Load config from file."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def save(self):
        """Save config to file."""
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w') as f:
            json.dump(self._data, f, indent=2)

    @property
    def api_key(self) -> str:
        return self._data.get('api_key', '')

    @api_key.setter
    def api_key(self, value: str):
        self._data['api_key'] = value
        self.save()

    @property
    def mods_path(self) -> str:
        """Path to mods directory. For backwards compat, also checks 'game_path'."""
        return self._data.get('mods_path', self._data.get('game_path', ''))

    @mods_path.setter
    def mods_path(self, value: str):
        self._data['mods_path'] = os.path.normpath(os.path.abspath(value))
        # Remove old game_path key if present
        self._data.pop('game_path', None)
        self.save()

    # Alias for backwards compatibility
    @property
    def game_path(self) -> str:
        return self.mods_path

    @game_path.setter
    def game_path(self, value: str):
        self.mods_path = value

    @property
    def installed_mods(self) -> dict:
        """Returns dict of installed mods: {mod_id: {name, file, version, ...}}"""
        return self._data.get('installed', {})

    def add_installed(self, mod_id: int, mod_info: dict):
        """Track an installed mod."""
        if 'installed' not in self._data:
            self._data['installed'] = {}
        self._data['installed'][str(mod_id)] = mod_info
        self.save()

    def add_conflict(self, mod_id:int, conflict_mod_id:int , conflict_mod_name:str):
        """Track a conflict"""
        if 'conflicts' not in self._data:
            self._data['conflicts'] = {}
        conflict = {
            'mod_id':mod_id,
            'conflict_mod_id':conflict_mod_id,
            'conflict_mod_name':conflict_mod_name
        }
        self._data['conflicts'][str(conflict_mod_id)] = conflict
        self.save()
    
    def is_conflict(self, mod_id:int):
        """Check if a mod is a conflict"""
        return str(mod_id) in self._data.get('conflicts' , {})
    
    def get_conflict(self, mod_id:int): 
        """Get information about the mod conflict"""
        return self._data.get('conflicts', {}).get(str(mod_id), {})

    def remove_installed(self, mod_id: int):
        """Remove a mod from tracking."""
        if 'installed' in self._data:
            self._data['installed'].pop(str(mod_id), None)
            self.save()

    def is_installed(self, mod_id: int) -> bool:
        """Check if a mod is installed."""
        return str(mod_id) in self._data.get('installed', {})
