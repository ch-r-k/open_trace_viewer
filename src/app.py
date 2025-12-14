"""Streamlit app entry for Open Trace Viewer.

This module contains a small, well-structured main() function and helpers so the
app is easier to read and test.
"""

from typing import Any, Dict, List, Optional

import json
import pandas as pd
import streamlit as st

from core.plotter import TimeSeriesPlotter
from data.demo_data import default_tasks, default_messages, default_notes


def load_input_data(uploaded_file: Optional[Any]) -> Dict[str, List[Dict]]:
    """Load JSON input from uploaded file or fallback to demo data.

    Returns a dict with keys: tasks, messages, states, notes.
    """
    if not uploaded_file:
        st.sidebar.info("Using demo data (upload JSON to replace).")
        return {
            "tasks": default_tasks,
            "messages": default_messages,
            "states": [],
            "notes": default_notes,
        }

    try:
        data = json.load(uploaded_file)
    except Exception as exc:  # keep UI-friendly message
        st.sidebar.error(f"Failed to read file: {exc}")
        return {"tasks": [], "messages": [], "states": [], "notes": []}

    st.sidebar.success(f"Loaded {len(data.get('tasks', []))} tasks and {len(data.get('states', []))} state groups.")
    return {
        "tasks": data.get("tasks", []),
        "messages": data.get("messages", []),
        "states": data.get("states", []),
        "notes": data.get("notes", []),
    }


def build_plotter(title: str = "System Activity Timeline") -> TimeSeriesPlotter:
    """Create and return a configured TimeSeriesPlotter instance."""
    return TimeSeriesPlotter(title=title)


def add_state_groups_to_plotter(plotter: TimeSeriesPlotter, data_states: List[List[Dict]]):
    """Convert state groups to dataframes and add them as step metrics to the plotter."""
    for state_group in data_states:
        if not state_group:
            continue

        df_state = pd.DataFrame(state_group)
        if not {"time", "State", "Task"}.issubset(df_state.columns):
            continue

        df_state = df_state.sort_values("time")
        df_state["StateValue"] = pd.factorize(df_state["State"])[0]
        task_name = df_state["Task"].iloc[0]

        plotter.add_metric(
            title=f"State: {task_name}",
            df=df_state,
            x_col="time",
            y_col="StateValue",
            plot_type="step",
        )


def main() -> None:
    """Streamlit main entrypoint."""
    st.set_page_config(page_title="Task Timeline", layout="wide")
    st.title("📊 Interactive Task Timeline Viewer")

    uploaded_file = st.sidebar.file_uploader("Upload JSON with 'tasks' and 'messages'", type=["json"])
    data = load_input_data(uploaded_file)

    plotter = build_plotter()
    plotter.add_tasks_and_messages(data["tasks"], data["messages"])
    plotter.add_notes(data.get("notes", []))

    add_state_groups_to_plotter(plotter, data.get("states", []))

    # --- Subplot selection UI ---
    try:
        titles = plotter.figure_builder.get_subplot_titles()
    except Exception:
        titles = []

    selected = []
    if titles:
        st.sidebar.markdown("### Subplots")
        for t in titles:
            if st.sidebar.checkbox(t, value=True):
                selected.append(t)

        if not selected:
            st.sidebar.warning("Select at least one subplot to display.")
            return

        # keep only the selected subplot registrations
        plotter.figure_builder.select_subplots(selected)

    fig = plotter.plot()
    # Ensure the rendered figure doesn't allow x-axis zoom/pan interactions.
    fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=50, b=50), dragmode=False)
    fig.update_xaxes(fixedrange=True)
    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
