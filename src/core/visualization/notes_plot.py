# core/visualization/notes_plot.py
import plotly.graph_objects as go
from typing import List, Dict


class NotesPlot:
    """Creates a vertical notes panel with timestamp-aligned annotations."""

    def __init__(self):
        self.traces = []         # No traces needed — panel is annotation-based
        self.annotations = []    # List[Dict]

    def add_notes(self, notes, notes_col_idx: int):
        """
        notes: [{ "Text": "...", "Timestamp": ... }]

        The Notes panel uses annotations only.
        """

        if not notes:
            return

        # annotation axis refs
        def axis_ref(axis: str, col_idx: int) -> str:
            return axis if col_idx == 1 else f"{axis}{col_idx}"

        xref = axis_ref("x", notes_col_idx)
        yref = axis_ref("y", notes_col_idx)

        # Place annotations vertically spaced
        for i, note in enumerate(notes):
            ts = note["Timestamp"]
            text = note["Text"]

            ann = dict(
                x=1,
                y=ts,
                ax=2,
                ay=ts,
                xref=xref,
                yref=yref,
                axref=xref,
                ayref=yref,
                showarrow=False,
                arrowhead=3,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor="blue",
                text=text,
                standoff=0
            )

            self.annotations.append(ann)
