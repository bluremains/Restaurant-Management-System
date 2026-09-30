"""
FileManager — the only class in the project allowed to touch the disk.

Keeping all file handling here means the rest of the application (models,
services, GUI) never has to know whether data is stored as JSON, CSV or
anything else. This is the "Recommended: Create a FileManager class to
keep file handling separate from business logic" pattern from the project
requirements.
"""

from __future__ import annotations
import json
import os
from typing import Any, Dict


class FileManager:
    """Loads and saves the restaurant's data as a single JSON file."""

    def __init__(self, file_path: str) -> None:
        self.file_path: str = file_path
        folder = os.path.dirname(self.file_path)
        if folder and not os.path.exists(folder):
            os.makedirs(folder)

    def load(self) -> Dict[str, Any]:
        """Load and return the saved data, or an empty structure if none exists yet."""
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError) as error:
            print(f"Warning: could not read '{self.file_path}' ({error}). Starting with empty data.")
            return {}

    def save(self, data: Dict[str, Any]) -> None:
        """Save the given data, completely overwriting any previous content."""
        try:
            with open(self.file_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=4)
        except OSError as error:
            print(f"Error: could not save data to '{self.file_path}' ({error}).")
