import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class TimeSeriesPlotter:
    def __init__(self, data_tasks=None, data_messages=None):
        print("TimeSeriesPlotter initialized")
        self.origin = pd.Timestamp("2025-10-11 09:00:00")
        self.data_tasks = data_tasks or []
        self.data_messages = data_messages or []
        self.df_tasks = None

        self.fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=("Metric A", "Project Timeline"),
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )

    def set_tasks(self, data_tasks):
        self.data_tasks = data_tasks

    def set_messages(self, data_messages):
        self.data_messages = data_messages

    def create_task_dataframe(self):
        """Convert raw task data into DataFrame with Start/Finish in seconds."""
        if not self.data_tasks:
            raise ValueError("No task data set.")
        df = pd.DataFrame(self.data_tasks)
        # Keep original ms columns if present, compute seconds
        df["Start_s"] = df["Start"] / 1000.0
        df["Finish_s"] = df["Finish"] / 1000.0
        df["Duration_s"] = df["Finish_s"] - df["Start_s"]
        return df

    def create_timeline_figure(self):
        if not self.data_tasks:
            raise ValueError("No task data set.")
        self.df_tasks = self.create_task_dataframe()
        df = self.df_tasks

        # Determine task order (preserve first-appearance order)
        unique_tasks = list(dict.fromkeys(df["Task"].tolist()))

        # Create a color map so each task always has the same color
        palette = px.colors.qualitative.Plotly  # or use .D3, .Bold, etc.
        task_color_map = {
            task: palette[i % len(palette)] for i, task in enumerate(unique_tasks)
        }

        # Add one horizontal bar per task-row (use overlay and one legend entry per task)
        added_tasks = set()
        for _, row in df.iterrows():
            show_legend = False
            if row["Task"] not in added_tasks:
                show_legend = True
                added_tasks.add(row["Task"])

            color = task_color_map[row["Task"]]

            self.fig.add_trace(
                go.Bar(
                    x=[row["Duration_s"]],
                    y=[row["Task"]],
                    base=[row["Start_s"]],
                    orientation="h",
                    name=row["Task"],
                    showlegend=show_legend,
                    marker_color=color,
                    hovertemplate=(
                        "%{y}<br>"
                        "start: %{base:.3f}s<br>"
                        "finish: %{x + base:.3f}s<br>"
                        "duration: %{x:.3f}s<extra></extra>"
                    )
                ),
                row=2, col=1
            )

        # Force y-category order so annotations align predictably
        self.fig.update_yaxes(
            title="Tasks",
            categoryorder="array",
            categoryarray=unique_tasks,
            row=2, col=1
        )

        # Numeric x-axis (seconds)
        self.fig.update_xaxes(
            title="Time (s)",
            type="linear",
            row=2, col=1
        )

        # Layout tweaks
        self.fig.update_layout(
            barmode="overlay",
            title="Task Activity with Messages",
            height=600,
            margin=dict(t=60, l=120),
            dragmode="zoom",        # Allow only zoom interactions
            yaxis_fixedrange=True,  # Lock y-axis for first subplot
            yaxis2_fixedrange=True  # Lock y-axis for second subplot
        )

    def add_messages_to_figure(self):
        """Add arrow annotations; use category labels for y/ay so arrows land on correct rows."""
        if self.fig is None:
            raise ValueError("Figure not created. Run create_timeline_figure() first.")
        if not self.data_messages:
            return

        tasks_in_plot = list(dict.fromkeys(self.df_tasks["Task"].tolist()))

        for msg in self.data_messages:
            if msg["From"] not in tasks_in_plot or msg["To"] not in tasks_in_plot:
                continue

            ts = msg["Timestamp"] / 1000.0  # ms → s
            y_from = msg["From"]
            y_to = msg["To"]

            # For subplot row=2, col=1 → use "x2" and "y2"
            self.fig.add_annotation(
                x=ts,
                y=y_to,
                ax=ts,
                ay=y_from,
                xref="x2",
                yref="y2",
                axref="x2",
                ayref="y2",
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="blue",
                text=msg.get("Text", ""),
                standoff=0,
            )


    def plot(self):
        """Build and return the figure."""
        self.create_timeline_figure()
        self.add_messages_to_figure()
        return self.fig
