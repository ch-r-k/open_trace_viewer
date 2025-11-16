# app.py
import streamlit as st
import json
import pandas as pd
from core.plotter import TimeSeriesPlotter
from data.demo_data import default_tasks, default_messages

st.set_page_config(page_title="Task Timeline", layout="wide")
st.title("📊 Interactive Task Timeline Viewer")

# Sidebar upload
uploaded_file = st.sidebar.file_uploader("Upload JSON with 'tasks' and 'messages'", type=["json"])

if uploaded_file:
    try:
        data = json.load(uploaded_file)
        data_tasks = data.get("tasks", [])
        data_messages = data.get("messages", [])
        data_states = data.get("states", [])
        st.sidebar.success(f"Loaded {len(data_tasks)} tasks and {len(data_states)} state groups.")
    except Exception as e:
        st.sidebar.error(f"Failed to read file: {e}")
        data_tasks, data_messages, data_states = [], [], []
else:
    st.sidebar.info("Using demo data (upload JSON to replace).")
    data_tasks, data_messages = default_tasks, default_messages
    data_states = []  # no states in demo

# Optional demo metrics
show_demo_metrics = st.sidebar.checkbox("Show demo metrics", value=True)

# Build plot
plotter = TimeSeriesPlotter(title="System Activity Timeline")

if show_demo_metrics:
    df_idle = pd.DataFrame({"x": [0, 5, 10, 15], "y": [20, 30, 15, 25]})
    df_user = pd.DataFrame({"x": [0, 5, 10, 15], "y": [10, 25, 30, 20]})
    plotter.add_metric("Idle Time (%)", df_idle, x_col="x", y_col="y", plot_type="area")
    plotter.add_metric("User Load", df_user, x_col="x", y_col="y", plot_type="line")

# Add tasks & messages
plotter.add_tasks_and_messages(data_tasks, data_messages)

# ============================
# Add state step diagrams
# ============================
for state_group in data_states:
    if not state_group:
        continue

    df_state = pd.DataFrame(state_group)
    if not {"time", "State", "Task"}.issubset(df_state.columns):
        continue

    df_state = df_state.sort_values("time")
    df_state["StateValue"] = pd.factorize(df_state["State"])[0]
    task_name = df_state["Task"].iloc[0]

    # Add step-style diagram using existing API
    plotter.add_metric(
        title=f"State: {task_name}",
        df=df_state,
        x_col="time",
        y_col="StateValue",
        plot_type="step"
    )


# Generate figure
fig = plotter.plot()
fig.update_layout(autosize=True, margin=dict(l=20, r=20, t=50, b=50))
st.plotly_chart(fig, use_container_width=True)
