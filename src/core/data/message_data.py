# core/data/message_data.py
from typing import List, Dict

class MessageData:
    """Message container and validator/filter utilities."""
    def __init__(self, data_messages: List[Dict] = None):
        self.raw_messages = data_messages or []

    def filter_valid_messages(self, valid_tasks: list) -> list:
        """Return messages where From and To exist in valid_tasks."""
        return [
            m for m in self.raw_messages
            if m.get("From") in valid_tasks and m.get("To") in valid_tasks
        ]
