"""State group helpers: convert lists of state dicts into pandas DataFrames.

Each element of `data_states` is expected to be a list of mappings containing at
least the keys `Task`, `time` and `State`.
"""

from typing import Dict, List

import pandas as pd


class StateData:
    """Load/validate/transform state groups into a DataFrame per task."""

    def __init__(self, data_states: List[List[Dict]] | None = None) -> None:
        """Initialize with raw state groups.

        Parameters
        ----------
        data_states:
            List of state groups; each group is a list of dicts describing a
            task's state transitions.
        """
        self.raw_states: List[List[Dict]] = data_states or []
        self.frames: Dict[str, pd.DataFrame] = {}

    def to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert all state groups into tidy DataFrames, keyed by task name.

        Returns an empty dict if no valid groups are found (no exception).
        """
        result: Dict[str, pd.DataFrame] = {}
        for state_group in self.raw_states:
            if not state_group:
                continue
            df = pd.DataFrame(state_group)
            if not {"Task", "time", "State"}.issubset(df.columns):
                continue

            df = df.sort_values("time").reset_index(drop=True)
            df["StateValue"] = pd.factorize(df["State"])[0]
            task_name = df["Task"].iloc[0]
            result[task_name] = df

        self.frames = result
        return result

    def get_unique_tasks(self) -> List[str]:
        """Return a list of task names that have state data."""
        if not self.frames:
            self.to_dataframes()
        return list(self.frames.keys())

    def summary_stats(self) -> pd.DataFrame:
        """Compute basic statistics per task: number of states, unique states, total duration."""
        if not self.frames:
            self.to_dataframes()

        stats = []
        for task, df in self.frames.items():
            duration = df["time"].max() - df["time"].min() if not df.empty else 0
            stats.append({
                "Task": task,
                "NumStates": len(df),
                "UniqueStates": df["State"].nunique(),
                "Duration": duration,
            })
        return pd.DataFrame(stats)
