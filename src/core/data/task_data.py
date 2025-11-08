# core/data/task_data.py
import pandas as pd
from typing import List, Dict

class TaskData:
    """Load/validate/transform task data into a DataFrame."""
    def __init__(self, data_tasks: List[Dict] = None):
        self.raw_tasks = data_tasks or []
        self.df = None

    def to_dataframe(self) -> pd.DataFrame:
        if not self.raw_tasks:
            raise ValueError("No task data provided.")
        df = pd.DataFrame(self.raw_tasks).copy()
        # Ensure required columns exist
        for col in ("Start", "Finish", "Task"):
            if col not in df.columns:
                raise ValueError(f"Task records must include '{col}'")
        df["Start_s"] = df["Start"] / 1000.0
        df["Finish_s"] = df["Finish"] / 1000.0
        df["Duration_s"] = df["Finish_s"] - df["Start_s"]
        self.df = df
        return df

    def get_unique_tasks(self) -> list:
        if self.df is None:
            self.to_dataframe()
        return list(dict.fromkeys(self.df["Task"].tolist()))
