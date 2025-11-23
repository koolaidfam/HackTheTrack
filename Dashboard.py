import streamlit as st
import pandas as pd
import numpy as np
import os

def load_data(csv_filename):
    
    script_dir = os.path.dirname(__file__)
    csv_path = os.path.join(script_dir, csv_filename)
    return pd.read_csv(csv_path, sep=";")

st.set_page_config(page_title="Post-Event Analysis", layout="wide")
st.title("🏁 Post-Event Driver Analysis Dashboard")
st.write("Use the filters to explore driver pace, consistency, and performance trends.")

df = load_data("besttenlaps.csv")


def lap_to_seconds(t):
    if isinstance(t, str) and ":" in t:
        m, s = t.split(":")
        return int(m) * 60 + float(s)
    return np.nan


for col in df.columns:
    if "BESTLAP" in col or col == "AVERAGE":
        df[col + "_SEC"] = df[col].apply(lap_to_seconds)

lap_cols = [c for c in df.columns if "BESTLAP_" in c and "_SEC" in c]
df["CONSISTENCY"] = df[lap_cols].std(axis=1)
df["PACE_DROP"] = df["AVERAGE_SEC"] - df["BESTLAP_1_SEC"]

st.sidebar.header("Filter Options")


driver_options = df["NUMBER"].unique()
selected_drivers = st.sidebar.multiselect(
    "Select Drivers",
    options=driver_options,
    default=driver_options
)

df_filtered = df[df["NUMBER"].isin(selected_drivers)]


min_time = float(df["BESTLAP_1_SEC"].min())
max_time = float(df["BESTLAP_1_SEC"].max())

time_range = st.sidebar.slider(
    "Fastest Lap Time Range (seconds)",
    min_value=min_time,
    max_value=max_time,
    value=(min_time, max_time)
)

df_filtered = df_filtered[
    (df_filtered["BESTLAP_1_SEC"] >= time_range[0]) &
    (df_filtered["BESTLAP_1_SEC"] <= time_range[1])
]


consistency_limit = st.sidebar.slider(
    "Maximum Consistency Score ",
    min_value=0.0,
    max_value=float(df["CONSISTENCY"].max()),
    value=float(df["CONSISTENCY"].max())
)

df_filtered = df_filtered[df_filtered["CONSISTENCY"] <= consistency_limit]


pace_limit = st.sidebar.slider(
    "Maximum Pace Drop (seconds)",
    min_value=0.0,
    max_value=float(df["PACE_DROP"].max()),
    value=float(df["PACE_DROP"].max())
)

df_filtered = df_filtered[df_filtered["PACE_DROP"] <= pace_limit]


tab1, tab2, tab3, tab4 = st.tabs([
    "🚗 Fastest Laps",
    "📉 Consistency",
    "⏱ Pace Dropoff",
    "📋 Driver Data Table"
])


with tab1:
    st.subheader("Fastest Lap Comparison")
    st.scatter_chart(
        df_filtered.set_index("NUMBER")["BESTLAP_1_SEC"],
        x_label="Driver Number",
        y_label="Fastest Lap (Seconds)"
    )


with tab2:
    st.subheader("Driver Consistency Rating")
    st.bar_chart(
        df_filtered.set_index("NUMBER")["CONSISTENCY"],
        x_label="Driver Number",
        y_label="Consistency Score"
    )


with tab3:
    st.subheader("Pace Dropoff from Fastest to Average Lap")
    st.area_chart(
        df_filtered.set_index("NUMBER")["PACE_DROP"],
        x_label="Driver Number",
        y_label="Dropoff (Seconds)"
    )


with tab4:
    st.subheader("Driver Detail Breakdown")
    st.dataframe(
        df_filtered[
            ["NUMBER","BESTLAP_1_SEC","AVERAGE_SEC","CONSISTENCY","PACE_DROP"]
        ].sort_values("BESTLAP_1_SEC")
    )
