"""Utilities for building a task timeline (vertical bars + message arrows)."""

from typing import Dict, List

import plotly.express as px
import plotly.graph_objects as go


class TimelinePlot:
    """Create vertical bar traces for a task timeline and message annotations."""

    def __init__(self) -> None:
        self.traces: List[go.Bar] = []
        self.annotations: List[Dict] = []
        self.task_color_map: Dict[str, str] = {}

    def add_tasks(self, df_tasks) -> List[str]:
        """Convert a DataFrame of tasks into vertical bar traces.

        Returns the ordered list of unique task names.
        """
        if df_tasks is None or df_tasks.empty:
            return []

        unique_tasks = list(dict.fromkeys(df_tasks["Task"].tolist()))

        palette = px.colors.qualitative.Plotly
        self.task_color_map = {t: palette[i % len(palette)] for i, t in enumerate(unique_tasks)}

        added_tasks = set()
        for _, row in df_tasks.iterrows():
            task = row["Task"]
            color = self.task_color_map[task]
            showlegend = task not in added_tasks
            if showlegend:
                added_tasks.add(task)

            trace = go.Bar(
                x=[task],
                y=[row["Duration_s"]],
                base=[row["Start_s"]],
                orientation="v",
                name=task,
                marker_color=color,
                showlegend=showlegend,
                hovertemplate=(
                    "%{x}<br>"
                    "start: %{base:.3f}s<br>"
                    "finish: %{y + base:.3f}s<br>"
                    "duration: %{y:.3f}s<extra></extra>"
                ),
            )
            self.traces.append(trace)

        return unique_tasks

    def add_messages(self, messages: List[Dict], timeline_col_idx: int) -> None:
        """Prepare arrow annotations for messages on the vertical timeline.

        The timeline visualization uses swapped axes (tasks on x, time on y), so
        annotations reference the axis by column index.
        """

        def axis_ref(axis: str, col_idx: int) -> str:
            return axis if col_idx == 1 else f"{axis}{col_idx}"

        xref = axis_ref("x", timeline_col_idx)
        yref = axis_ref("y", timeline_col_idx)

        for msg in messages:
            ts = msg.get("Timestamp")
            x_from = msg.get("From")
            x_to = msg.get("To")

            if ts is None or x_from is None or x_to is None:
                continue

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
                standoff=0,
            )
            self.annotations.append(ann)
