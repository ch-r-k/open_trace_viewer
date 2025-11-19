# core/plotter.py
from core.data.task_data import TaskData
from core.data.message_data import MessageData
from core.visualization.timeline_plot import TimelinePlot
from core.visualization.multiplot_figure import MultiPlotFigure
from core.visualization.notes_plot import NotesPlot

class TimeSeriesPlotter:
    """High-level plotting API for metrics + timeline."""
    def __init__(self, title="System Activity Timeline"):
        self.figure_builder = MultiPlotFigure(title=title)
        self.timeline_plot = TimelinePlot()
        self.notes_plot = NotesPlot()
        self._timeline_added = False

    def add_metric(self, title: str, df, x_col="x", y_col="y", plot_type="line"):
        self.figure_builder.add_metric_subplot(title=title, df=df, x_col=x_col, y_col=y_col, plot_type=plot_type)

    def add_notes(self, notes):
        if not notes:
            return

        # index of notes subplot (horizontal layout)
        notes_col_idx = len(self.figure_builder._registered) + 1



        self.notes_plot.add_notes(notes, notes_col_idx)

        self.figure_builder.add_notes_subplot(
            "Notes",
            traces=self.notes_plot.traces,
            annotations=self.notes_plot.annotations
        )

    def add_tasks_and_messages(self, data_tasks, data_messages):
        task_data = TaskData(data_tasks)
        df_tasks = task_data.to_dataframe()
        unique_tasks = task_data.get_unique_tasks()

        message_data = MessageData(data_messages)
        valid_messages = message_data.filter_valid_messages(unique_tasks)

        # populate timeline structure
        self.timeline_plot = TimelinePlot()
        self.timeline_plot.add_tasks(df_tasks)
        # timeline subplot will be the next row index (we'll compute row idx when building)
        # But we need to pass the timeline row index to compute correct annotation refs.
        # We'll assume timeline is added after any metric subplots; compute its row index now:
        timeline_row_idx = len(self.figure_builder._registered) + 1
        self.timeline_plot.add_messages(valid_messages, timeline_row_idx)

        # register timeline traces+annotations into figure builder
        self.figure_builder.add_timeline_subplot("Task Timeline", traces=self.timeline_plot.traces, annotations=self.timeline_plot.annotations)
        self._timeline_added = True

    def plot(self):
        return self.figure_builder.build_figure()
