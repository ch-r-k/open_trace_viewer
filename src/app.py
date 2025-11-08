import streamlit as st
import json
from core.plotter import TimeSeriesPlotter

st.set_page_config(page_title="Task Timeline", layout="wide")

st.title("📊 Interactive Task Timeline Viewer")

# --- File Upload ---
st.sidebar.header("Data Input")

uploaded_file = st.sidebar.file_uploader(
    "Upload JSON file with 'tasks' and 'messages'",
    type=["json"]
)

# --- Load Data ---
if uploaded_file:
    try:
        data = json.load(uploaded_file)
        data_tasks = data.get("tasks", [])
        data_messages = data.get("messages", [])
        st.sidebar.success(f"Loaded {len(data_tasks)} tasks and {len(data_messages)} messages.")
    except Exception as e:
        st.sidebar.error(f"❌ Failed to read file: {e}")
        data_tasks, data_messages = [], []
else:
    st.sidebar.info("No file uploaded — using default demo data.")
    from data.demo_data import default_tasks, default_messages  # move your big arrays to demo_data.py
    data_tasks, data_messages = default_tasks, default_messages

# --- Create Plot ---
plotter = TimeSeriesPlotter(data_tasks=data_tasks, data_messages=data_messages)
fig = plotter.plot()
fig.update_layout(
    autosize=True,
    margin=dict(l=20, r=20, t=50, b=50)
)

st.plotly_chart(fig, use_container_width=True)
