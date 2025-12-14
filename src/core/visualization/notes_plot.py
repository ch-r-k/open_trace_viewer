"""Notes panel helper: create annotation-only column for timestamped notes."""

from typing import Dict, List, Any, Optional
import textwrap

import plotly.graph_objects as go


class NotesPlot:
    """Creates a vertical notes panel with timestamp-aligned annotations."""

    def __init__(self) -> None:
        self.traces: List[Any] = []  # No traces needed — panel is annotation-based
        self.annotations: List[Dict] = []
        self.shapes: List[Dict] = []

    def add_notes(self, notes: List[Dict], notes_col_idx: int, search: Optional[str] = None) -> None:
        """Convert a list of note dicts into Plotly annotations.

        Each note should contain `Timestamp` and `Text` keys.
        """
        if not notes:
            return

        def axis_ref(axis: str, col_idx: int) -> str:
            return axis if col_idx == 1 else f"{axis}{col_idx}"

        xref = axis_ref("x", notes_col_idx)
        yref = axis_ref("y", notes_col_idx)

        def wrap(text: str, width: int = 36) -> str:
            if not text:
                return ""
            return "<br>".join(textwrap.fill(text, width=width, break_long_words=False).splitlines())

        for note in notes:
            ts = note.get("Timestamp")
            text = note.get("Text", "")
            if ts is None:
                continue

            ann = dict(
                x=0,
                y=ts,
                ax=2,
                ay=ts,
                xref=xref,
                yref=yref,
                axref=xref,
                ayref=yref,
                showarrow=False,
                text=wrap(text),
                align="left",
                xanchor="left",
                standoff=0,
            )

            self.annotations.append(ann)

            # If a search string is provided and the note text contains it,
            # add a horizontal marker (line) at the note timestamp so the
            # notes subplot visually indicates matches.
            if search:
                try:
                    if search.lower() in (text or "").lower():
                        line = dict(
                            type="line",
                            x0=0,
                            x1=2,
                            y0=ts,
                            y1=ts,
                            xref=xref,
                            yref=yref,
                            line=dict(color="red", width=2, dash="dash"),
                        )
                        self.shapes.append(line)
                except Exception:
                    # Ignore search errors — don't break plotting for malformed notes
                    pass
