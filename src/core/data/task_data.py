"""Utilities for loading and validating task records.

This module converts lists of task dicts into a pandas DataFrame with
computed helper columns used by the visualization code.
"""

from typing import Dict, List

import pandas as pd


class TaskData:
    """Load/validate/transform task data into a DataFrame.

    Attributes
    ----------
    raw_tasks:
        The original list of task mapping dictionaries.
    df:
        Cached pandas DataFrame representation (or None).
    """

    def __init__(self, data_tasks: List[Dict] | None = None) -> None:
        self.raw_tasks: List[Dict] = data_tasks or []
        self.df: pd.DataFrame | None = None

    def to_dataframe(self) -> pd.DataFrame:
        """Return a DataFrame view of the tasks with computed time columns.

        The method is defensive: if no tasks are provided an empty DataFrame is
        returned (rather than raising) so callers can continue gracefully.
        """
        if not self.raw_tasks:
            self.df = pd.DataFrame()
            return self.df

        df = pd.DataFrame(self.raw_tasks).copy()

        # Ensure required columns exist
        for col in ("Start", "Finish", "Task"):
            if col not in df.columns:
                raise ValueError(f"Task records must include '{col}'")

        df["Start_s"] = df["Start"]
        df["Finish_s"] = df["Finish"]
        df["Duration_s"] = df["Finish_s"] - df["Start_s"]
        self.df = df
        return df

    def get_unique_tasks(self) -> List[str]:
        """Return ordered list of unique task names (preserve original order)."""
        if self.df is None:
            self.to_dataframe()

        if self.df.empty or "Task" not in self.df.columns:
            return []

        return list(dict.fromkeys(self.df["Task"].tolist()))
