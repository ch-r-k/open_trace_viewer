import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

class TimelineFigure:
    """Responsible for constructing and decorating the Plotly figure."""

    def __init__(self, title="Task Activity with Messages"):
        self.fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            subplot_titles=("Metric A", "Project Timeline"),
            specs=[[{"type": "xy"}], [{"type": "xy"}]]
        )
        self.title = title

    def add_tasks(self, df_tasks, unique_tasks):
        """Add horizontal task bars to the figure."""
        palette = px.colors.qualitative.Plotly
        task_color_map = {task: palette[i % len(palette)] for i, task in enumerate(unique_tasks)}
        added_tasks = set()

        for _, row in df_tasks.iterrows():
            task = row["Task"]
            color = task_color_map[task]
            show_legend = task not in added_tasks
            added_tasks.add(task)

            self.fig.add_trace(
                go.Bar(
                    x=[row["Duration_s"]],
                    y=[task],
                    base=[row["Start_s"]],
                    orientation="h",
                    name=task,
                    marker_color=color,
                    showlegend=show_legend,
                    hovertemplate=(
                        f"{task}<br>"
                        "start: %{base:.3f}s<br>"
                        "finish: %{x + base:.3f}s<br>"
                        "duration: %{x:.3f}s<extra></extra>"
                    )
                ),
                row=2, col=1
            )

        self.fig.update_yaxes(
            title="Tasks",
            categoryorder="array",
            categoryarray=unique_tasks,
            row=2, col=1
        )

        self.fig.update_xaxes(title="Time (s)", type="linear", row=2, col=1)

    def add_messages(self, messages):
        """Draw arrows connecting tasks based on message flow."""
        for msg in messages:
            ts = msg["Timestamp"] / 1000.0
            y_from = msg["From"]
            y_to = msg["To"]
            self.fig.add_annotation(
                x=ts, y=y_to, ax=ts, ay=y_from,
                xref="x2", yref="y2", axref="x2", ayref="y2",
                showarrow=True, arrowhead=3, arrowsize=1,
                arrowwidth=2, arrowcolor="blue", text=msg.get("Text", "")
            )

    def finalize_layout(self):
        """Apply global layout settings."""
        self.fig.update_layout(
            barmode="overlay",
            title=self.title,
            height=600,
            margin=dict(t=60, l=120),
            dragmode="zoom",
            yaxis_fixedrange=True,
            yaxis2_fixedrange=True
        )
        return self.fig
