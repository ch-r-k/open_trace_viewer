# core/data/state_data.py
import pandas as pd
from typing import List, Dict

class StateData:
    """Load/validate/transform state groups into a DataFrame per task."""

    def __init__(self, data_states: List[List[Dict]] = None):
        """
        data_states: list of state groups,
        each a list of dicts like [{"Task": "A", "time": 100, "State": "IDLE"}, ...]
        """
        self.raw_states = data_states or []
        self.frames = {}  # task_name -> DataFrame

    def to_dataframes(self) -> Dict[str, pd.DataFrame]:
        """Convert all state groups into tidy DataFrames, indexed by task name."""
        if not self.raw_states:
            raise ValueError("No state data provided.")

        result = {}
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

        if not result:
            raise ValueError("No valid state groups found.")
        self.frames = result
        return result

    def get_unique_tasks(self) -> list:
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
                "Duration": duration
            })
        return pd.DataFrame(stats)
