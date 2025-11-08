from core.data.task_data import TaskData
from core.data.message_data import MessageData
from core.visualization.timeline_figure import TimelineFigure

class TimeSeriesPlotter:
    """High-level API for creating time series and message timeline plots."""

    def __init__(self, data_tasks=None, data_messages=None):
        print("TimeSeriesPlotter initialized")
        self.tasks = TaskData(data_tasks)
        self.messages = MessageData(data_messages)
        self.timeline = TimelineFigure()

    def plot(self):
        """Build and return the Plotly figure."""
        df = self.tasks.to_dataframe()
        unique_tasks = self.tasks.get_unique_tasks()
        valid_messages = self.messages.filter_valid_messages(unique_tasks)

        self.timeline.add_tasks(df, unique_tasks)
        self.timeline.add_messages(valid_messages)
        return self.timeline.finalize_layout()
