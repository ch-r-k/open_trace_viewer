import pandas as pd

class TaskData:
    """Represents and processes a collection of task records."""

    def __init__(self, data_tasks=None):
        self.raw_tasks = data_tasks or []
        self.df = None

    def to_dataframe(self) -> pd.DataFrame:
        if not self.raw_tasks:
            raise ValueError("No task data provided.")
        df = pd.DataFrame(self.raw_tasks)
        df["Start_s"] = df["Start"] / 1000.0
        df["Finish_s"] = df["Finish"] / 1000.0
        df["Duration_s"] = df["Finish_s"] - df["Start_s"]
        self.df = df
        return df

    def get_unique_tasks(self) -> list:
        if self.df is None:
            self.to_dataframe()
        return list(dict.fromkeys(self.df["Task"].tolist()))
