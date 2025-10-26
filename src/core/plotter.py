import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class TimeSeriesPlotter:
    def __init__(self, data_tasks=None, data_messages=None):
        """
        Initialize the plotter with optional tasks and messages.
        """
        print("TimeSeriesPlotter initialized")
        self.origin = pd.Timestamp("2025-10-11 09:00:00")
        self.data_tasks = data_tasks
        self.data_messages = data_messages
        self.df_tasks = None

        self.fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=("Metric A", "Project Timeline"),
            specs=[[{"type": "xy"}], [{"type": "xy"}]]  # xy needed for Timeline
        )

    def set_tasks(self, data_tasks):
        """Set or update the task data."""
        self.data_tasks = data_tasks

    def set_messages(self, data_messages):
        """Set or update the message data."""
        self.data_messages = data_messages

    def create_task_dataframe(self):
        """Convert raw task data into a DataFrame with proper datetime columns."""
        if self.data_tasks is None:
            raise ValueError("No task data set. Use set_tasks() or provide data_tasks at init.")
        
        df_tasks = pd.DataFrame(self.data_tasks)
        df_tasks["Start"] = self.origin + pd.to_timedelta(df_tasks["Start"], unit="ms")
        df_tasks["Finish"] = self.origin + pd.to_timedelta(df_tasks["Finish"], unit="ms")
        return df_tasks

    def create_timeline_figure(self):
        """Create and store the base timeline figure."""
        if self.data_tasks is None:
            raise ValueError("No task data set. Use set_tasks() first.")
        
        self.df_tasks = self.create_task_dataframe()        
        fig = px.timeline(
                self.df_tasks, 
                x_start="Start", 
                x_end="Finish", 
                y="Task", 
                color="Task"
            )
        
        for trace in fig.data:
            self.fig.add_trace(trace, row=1, col=1)

        self.fig.update_xaxes(type='date')        
        #self.fig.update_yaxes(autorange="reversed")  # Task1 at the top
        self.fig.update_xaxes(tickformat="%S.%L", title="Time (s)")
        self.fig.update_layout(title="Task Activity with Messages")

    def map_tasks_to_y_positions(self):
        """Map each unique task name to a y-axis position for the timeline."""
        if self.df_tasks is None:
            raise ValueError("Timeline must be created first.")
        
        unique_tasks = []
        for task in self.df_tasks["Task"]:
            if task not in unique_tasks:
                unique_tasks.append(task)

        task_map = {task: i for i, task in enumerate(unique_tasks)}
        return task_map

    def add_messages_to_figure(self):
        """Add arrow annotations representing messages between tasks."""
        if self.fig is None:
            raise ValueError("Figure not created. Run create_timeline_figure() first.")

        if self.data_messages is None:
            return  # Nothing to add

        task_map = self.map_tasks_to_y_positions()

        for msg in self.data_messages:
            y_from = task_map[msg["From"]]
            y_to = task_map[msg["To"]]
            ts = self.origin + pd.to_timedelta(msg["Timestamp"], unit="ms")

            self.fig.add_annotation(
                x=ts,
                y=y_to,
                ax=ts,
                ay=y_from,
                xref="x", yref="y",
                axref="x", ayref="y",
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="blue",
                text=msg["Text"],
                standoff=5,
            )

    def plot(self):
        """Convenience method to build and show the full plot."""
        self.create_timeline_figure()
        self.add_messages_to_figure()
        return self.fig
