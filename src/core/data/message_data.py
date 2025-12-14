"""Message data utilities and validation helpers."""

from typing import Dict, List


class MessageData:
    """Container for message-like records with small validation helpers."""

    def __init__(self, data_messages: List[Dict] | None = None) -> None:
        self.raw_messages: List[Dict] = data_messages or []

    def filter_valid_messages(self, valid_tasks: List[str]) -> List[Dict]:
        """Return messages whose `From` and `To` fields reference known tasks."""
        return [
            m for m in self.raw_messages if m.get("From") in valid_tasks and m.get("To") in valid_tasks
        ]
