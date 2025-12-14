"""Notes panel helper: create annotation-only column for timestamped notes."""

from typing import Dict, List, Any

import plotly.graph_objects as go


class NotesPlot:
    """Creates a vertical notes panel with timestamp-aligned annotations."""

    def __init__(self) -> None:
        self.traces: List[Any] = []  # No traces needed — panel is annotation-based
        self.annotations: List[Dict] = []

    def add_notes(self, notes: List[Dict], notes_col_idx: int) -> None:
        """Convert a list of note dicts into Plotly annotations.

        Each note should contain `Timestamp` and `Text` keys.
        """
        if not notes:
            return

        def axis_ref(axis: str, col_idx: int) -> str:
            return axis if col_idx == 1 else f"{axis}{col_idx}"

        xref = axis_ref("x", notes_col_idx)
        yref = axis_ref("y", notes_col_idx)

        for note in notes:
            ts = note.get("Timestamp")
            text = note.get("Text", "")
            if ts is None:
                continue

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
                text=text,
                standoff=0,
            )

            self.annotations.append(ann)
