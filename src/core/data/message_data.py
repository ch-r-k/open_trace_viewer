class MessageData:
    """Handles message metadata validation and filtering."""

    def __init__(self, data_messages=None):
        self.raw_messages = data_messages or []

    def filter_valid_messages(self, valid_tasks):
        """Keep only messages whose endpoints exist in the valid task list."""
        valid_msgs = [
            m for m in self.raw_messages
            if m.get("From") in valid_tasks and m.get("To") in valid_tasks
        ]
        return valid_msgs
