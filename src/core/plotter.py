"""High-level plotting API for combining metrics, notes and a task timeline.

This module provides a small, well-typed facade used by the Streamlit app
to compose subplots and timeline annotations.
"""

from typing import Any, List

from core.data.task_data import TaskData
from core.data.message_data import MessageData
from core.visualization.timeline_plot import TimelinePlot
from core.visualization.multiplot_figure import MultiPlotFigure
from core.visualization.notes_plot import NotesPlot


class TimeSeriesPlotter:
    """High-level plotting API for metrics + timeline.

    The plotter coordinates the figure builder and the lower-level plot
    components (`TimelinePlot`, `NotesPlot`) so callers don't need to
    manage trace indices or annotation references.
    """

    def __init__(self, title: str = "System Activity Timeline") -> None:
        self.figure_builder: MultiPlotFigure = MultiPlotFigure(title=title)
        self.timeline_plot: TimelinePlot = TimelinePlot()
        self.notes_plot: NotesPlot = NotesPlot()
        self._timeline_added: bool = False

    def add_metric(self, title: str, df: Any, x_col: str = "x", y_col: str = "y", plot_type: str = "line") -> None:
        """Register a metric subplot backed by `df` (pandas DataFrame-like)."""
        self.figure_builder.add_metric_subplot(title=title, df=df, x_col=x_col, y_col=y_col, plot_type=plot_type)

    def add_notes(self, notes: List[dict]) -> None:
        """Add a notes column (annotation-only) to the figure.

        Notes are placed in a column after any already-registered subplots.
        """
        if not notes:
            return

        notes_col_idx = len(self.figure_builder._registered) + 1

        self.notes_plot.add_notes(notes, notes_col_idx)

        self.figure_builder.add_notes_subplot(
            "Notes",
            traces=self.notes_plot.traces,
            annotations=self.notes_plot.annotations,
        )

    def add_tasks_and_messages(self, data_tasks: List[dict], data_messages: List[dict]) -> None:
        """Convert raw task/message records into timeline traces and annotations."""
        task_data = TaskData(data_tasks)
        df_tasks = task_data.to_dataframe()
        unique_tasks = task_data.get_unique_tasks()

        message_data = MessageData(data_messages)
        valid_messages = message_data.filter_valid_messages(unique_tasks)

        # populate timeline structure
        self.timeline_plot = TimelinePlot()
        self.timeline_plot.add_tasks(df_tasks)

        timeline_row_idx = len(self.figure_builder._registered) + 1
        self.timeline_plot.add_messages(valid_messages, timeline_row_idx)

        self.figure_builder.add_timeline_subplot(
            "Task Timeline",
            traces=self.timeline_plot.traces,
            annotations=self.timeline_plot.annotations,
        )
        self._timeline_added = True

    def plot(self):
        """Build and return the composed Plotly figure."""
        return self.figure_builder.build_figure()
