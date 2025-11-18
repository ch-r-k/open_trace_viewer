# core/visualization/timeline_plot.py
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict

class TimelinePlot:
    """Creates VERTICAL bar traces for task timeline and prepares annotations for messages."""
    def __init__(self):
        self.traces: List[go.Bar] = []
        self.annotations: List[Dict] = []
        self.task_color_map = {}

    def add_tasks(self, df_tasks):
        # Preserve task order
        unique_tasks = list(dict.fromkeys(df_tasks["Task"].tolist()))

        palette = px.colors.qualitative.Plotly
        self.task_color_map = {t: palette[i % len(palette)] for i, t in enumerate(unique_tasks)}

        # Produce VERTICAL bars:
        #   x = task (category)
        #   y = duration
        #   base = start time  ← used to shift the bar up
        added_tasks = set()
        for _, row in df_tasks.iterrows():
            task = row["Task"]
            color = self.task_color_map[task]
            showlegend = task not in added_tasks
            if showlegend:
                added_tasks.add(task)

            trace = go.Bar(
                x=[task],                  # categorical axis
                y=[row["Duration_s"]],     # bar height
                base=[row["Start_s"]],     # start time on Y-axis
                orientation="v",
                name=task,
                marker_color=color,
                showlegend=showlegend,
                hovertemplate=(
                    "%{x}<br>"
                    "start: %{base:.3f}s<br>"
                    "finish: %{y + base:.3f}s<br>"
                    "duration: %{y:.3f}s<extra></extra>"
                )
            )
            self.traces.append(trace)

        return unique_tasks

    def add_messages(self, messages: List[Dict], timeline_col_idx: int):
        """
        Prepare annotations for messages, swapping x/y roles for vertical timeline.
        """

        def axis_ref(axis: str, col_idx: int) -> str:
            return axis if col_idx == 1 else f"{axis}{col_idx}"

        xref = axis_ref("x", timeline_col_idx)
        yref = axis_ref("y", timeline_col_idx)

        # swapped axis logic:
        #   - x = task name (category)
        #   - y = timestamp (seconds)
        for msg in messages:
            ts = msg["Timestamp"]
            x_from = msg["From"]   # category on X axis
            x_to = msg["To"]

            ann = dict(
                x=x_to,
                y=ts,
                ax=x_from,
                ay=ts,
                xref=xref,
                yref=yref,
                axref=xref,
                ayref=yref,
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="blue",
                text=msg.get("Text", ""),
                standoff=0
            )
            self.annotations.append(ann)
