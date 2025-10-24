import streamlit as st
from core.plotter import TimeSeriesPlotter

st.set_page_config(page_title="Task Timeline", layout="wide")  # Make Streamlit page full width

st.title("Interactive Task Timeline")

# Example task data
default_tasks = [
    {"Task": "Task1", "Start": 0, "Finish": 1000},
    {"Task": "Task2", "Start": 1000, "Finish": 2000},
    {"Task": "Task3", "Start": 2000, "Finish": 10000},
    {"Task": "Task1", "Start": 10000, "Finish": 10100},
]

default_messages = [
    {"Message": "Message1", "Timestamp": 1000, "From": "Task1", "To": "Task2", "Text": "Task1 → Task2"},
    {"Message": "Message2", "Timestamp": 2000, "From": "Task2", "To": "Task3", "Text": "Task2 → Task3"},
]

# Initialize the plotter with default data
plotter = TimeSeriesPlotter(data_tasks=default_tasks, data_messages=default_messages)

# Generate figure
fig = plotter.plot()

# Make the Plotly figure responsive to the container width
fig.update_layout(
    autosize=True,
    margin=dict(l=20, r=20, t=50, b=50),
)

# Display the chart, filling the entire Streamlit page width
st.plotly_chart(fig, use_container_width=True)
