# core/visualization/timeline_plot.py
import plotly.graph_objects as go
import plotly.express as px
from typing import List, Dict

class TimelinePlot:
    """Creates bar traces for task timeline and prepares annotations for messages."""
    def __init__(self):
        self.traces: List[go.Bar] = []
        self.annotations: List[Dict] = []
        self.task_color_map = {}

    def add_tasks(self, df_tasks):
        unique_tasks = list(dict.fromkeys(df_tasks["Task"].tolist()))
        palette = px.colors.qualitative.Plotly
        self.task_color_map = {t: palette[i % len(palette)] for i, t in enumerate(unique_tasks)}

        # Create one bar trace per row (we still add them as separate traces so they
        # are drawn in overlay mode and can have separate hover info)
        added_tasks = set()
        for _, row in df_tasks.iterrows():
            task = row["Task"]
            color = self.task_color_map[task]
            showlegend = task not in added_tasks
            if showlegend:
                added_tasks.add(task)

            trace = go.Bar(
                x=[row["Duration_s"]],
                y=[task],
                base=[row["Start_s"]],
                orientation="h",
                name=task,
                marker_color=color,
                showlegend=showlegend,
                hovertemplate=(
                    "%{y}<br>"
                    "start: %{base:.3f}s<br>"
                    "finish: %{x + base:.3f}s<br>"
                    "duration: %{x:.3f}s<extra></extra>"
                )
            )
            self.traces.append(trace)

        return unique_tasks

    def add_messages(self, messages: List[Dict], timeline_row_idx: int):
        """
        Prepare annotations for messages. We don't attach annotations to a figure yet,
        but we compute annotation dicts using correct axis refs for the timeline row.
        """
        # helper to produce axis ref string like "x" or "x2"
        def axis_ref(axis: str, row_idx: int) -> str:
            return axis if row_idx == 1 else f"{axis}{row_idx}"

        xref = axis_ref("x", timeline_row_idx)
        yref = axis_ref("y", timeline_row_idx)
        axref = xref
        ayref = yref

        for msg in messages:
            ts = msg["Timestamp"] / 1000.0
            y_from = msg["From"]
            y_to = msg["To"]

            ann = dict(
                x=ts,
                y=y_to,
                ax=ts,
                ay=y_from,
                xref=xref,
                yref=yref,
                axref=axref,
                ayref=ayref,
                showarrow=True,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="blue",
                text=msg.get("Text", ""),
                standoff=0
            )
            self.annotations.append(ann)
