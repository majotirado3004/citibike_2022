import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

# ---------- PAGE ----------
st.set_page_config(layout="wide")
st.title("NYC CitiBike 2022 Dashboard")
st.write("This dashboard explores bike usage patterns and their relationship with weather conditions.")

# ---------- LOAD DATA ----------
@st.cache_data
def load_data():
    df = pd.read_csv("data/processed/citibike_weather_2022.csv", low_memory=False)
    return df

df = load_data()

# ---------- CREATE AVERAGE TEMPERATURE ----------
# (many NOAA datasets don't have tavg)
if "tavg" not in df.columns:
    if "tmax" in df.columns and "tmin" in df.columns:
        df["tavg"] = (df["tmax"] + df["tmin"]) / 2
    elif "TMAX" in df.columns and "TMIN" in df.columns:
        df["tavg"] = (df["TMAX"] + df["TMIN"]) / 2

# ---------- DATE PROCESSING ----------
df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
df["date"] = df["started_at"].dt.date

# ---------- TOP START STATIONS ----------
st.subheader("Most Popular Start Stations")

top_stations = (
    df.dropna(subset=["start_station_name"])
      .groupby("start_station_name")
      .size()
      .sort_values(ascending=False)
      .head(10)
      .reset_index(name="trips")
)

fig_bar = px.bar(
    top_stations,
    x="trips",
    y="start_station_name",
    orientation="h",
    labels={"trips": "Trips", "start_station_name": "Station"},
)

fig_bar.update_layout(height=500, yaxis=dict(categoryorder="total ascending"))
st.plotly_chart(fig_bar, use_container_width=True)

# ---------- DAILY TRIPS VS TEMPERATURE ----------
st.subheader("Trips vs Temperature Over Time")

daily = (
    df.dropna(subset=["date"])
      .groupby("date")
      .agg(
          trips=("ride_id", "count"),
          tavg=("tavg", "mean")
      )
      .reset_index()
)

daily["date"] = pd.to_datetime(daily["date"])

fig_dual = make_subplots(specs=[[{"secondary_y": True}]])

fig_dual.add_trace(
    go.Scatter(x=daily["date"], y=daily["trips"], name="Trips"),
    secondary_y=False,
)

fig_dual.add_trace(
    go.Scatter(x=daily["date"], y=daily["tavg"], name="Avg Temp"),
    secondary_y=True,
)

fig_dual.update_yaxes(title_text="Trips", secondary_y=False)
fig_dual.update_yaxes(title_text="Temperature", secondary_y=True)

st.plotly_chart(fig_dual, use_container_width=True)

# ---------- KEPLER MAP ----------
st.subheader("Spatial Distribution of CitiBike Trips in New York City")

try:
    with open("outputs/task_2_5_kepler_map.html", "r", encoding="utf-8") as f:
        html_data = f.read()
    components.html(html_data, height=700, scrolling=True)
except FileNotFoundError:
    st.warning("Kepler map file not found yet — path will be fixed next.")
