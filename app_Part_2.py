import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit.components.v1 as components

# ---------------- PAGE CONFIG ----------------
st.set_page_config(layout="wide")

# ---------------- LOAD DATA ----------------
@st.cache_data
def load_data():
    df = pd.read_csv("citibike_deploy.csv", low_memory=False)
    return df

df = load_data()

# ---------------- PREP DATA ----------------
df["started_at"] = pd.to_datetime(df["started_at"], errors="coerce")
df["date"] = df["started_at"].dt.date
df["hour"] = df["started_at"].dt.hour

# ---------------- SIDEBAR NAVIGATION ----------------
page = st.sidebar.selectbox(
    "Navigate",
    (
        "Intro",
        "Trips vs Temperature",
        "Popular Stations",
        "Map",
        "Operational Insight",
        "Recommendations",
    ),
)

# ======================================================
# INTRO PAGE
# ======================================================
if page == "Intro":
    st.title("NYC CitiBike 2022 Supply & Demand Dashboard")

    st.markdown("""
This dashboard analyzes CitiBike usage patterns in New York City and their relationship with weather and location.

**Goal:** Help the operations team understand demand behavior and improve bike availability across stations.
    
The analysis focuses on:
- Seasonal usage trends
- Station demand concentration
- Geographic distribution of trips
- Daily operational demand patterns
""")

# ======================================================
# TRIPS VS TEMPERATURE PAGE
# ======================================================
elif page == "Trips vs Temperature":

    st.title("Seasonality: Trips vs Temperature")

    daily = (
        df.dropna(subset=["date"])
        .groupby("date")
        .agg(
            trips=("ride_id", "count"),
            tavg=("tavg", "mean"),
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
        go.Scatter(x=daily["date"], y=daily["tavg"], name="Avg Temperature"),
        secondary_y=True,
    )

    fig_dual.update_yaxes(title_text="Trips", secondary_y=False)
    fig_dual.update_yaxes(title_text="Temperature (°C)", secondary_y=True)

    st.plotly_chart(fig_dual, use_container_width=True)

    st.markdown("""
**Interpretation**

Bike usage strongly follows temperature patterns. During colder months trips drop significantly, while warmer temperatures lead to a sharp increase in ridership.  
This indicates CitiBike demand is highly seasonal and fleet size should be adjusted accordingly.
""")

# ======================================================
# POPULAR STATIONS PAGE
# ======================================================
elif page == "Popular Stations":

    st.title("Station Demand Concentration (Start vs End)")

    col1, col2 = st.columns(2)

    # ---------- TOP START STATIONS ----------
    with col1:
        st.subheader("Top 10 Start Stations")

        top_start = (
            df.dropna(subset=["start_station_name"])
            .groupby("start_station_name")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="trips")
        )

        fig_start = px.bar(
            top_start,
            x="trips",
            y="start_station_name",
            orientation="h",
            labels={"trips": "Trips", "start_station_name": "Station"},
        )
        fig_start.update_layout(height=450, yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_start, use_container_width=True)

    # ---------- TOP END STATIONS ----------
    with col2:
        st.subheader("Top 10 End Stations")

        top_end = (
            df.dropna(subset=["end_station_name"])
            .groupby("end_station_name")
            .size()
            .sort_values(ascending=False)
            .head(10)
            .reset_index(name="trips")
        )

        fig_end = px.bar(
            top_end,
            x="trips",
            y="end_station_name",
            orientation="h",
            labels={"trips": "Trips", "end_station_name": "Station"},
        )
        fig_end.update_layout(height=450, yaxis=dict(categoryorder="total ascending"))
        st.plotly_chart(fig_end, use_container_width=True)

    st.divider()

    # ---------- NET FLOW (IMBALANCE) ----------
    st.subheader("Net Flow (End trips − Start trips) — Rebalancing signal")

    starts = (
        df.dropna(subset=["start_station_name"])
        .groupby("start_station_name")
        .size()
        .rename("start_trips")
    )

    ends = (
        df.dropna(subset=["end_station_name"])
        .groupby("end_station_name")
        .size()
        .rename("end_trips")
    )

    net = (
        pd.concat([starts, ends], axis=1)
        .fillna(0)
        .assign(net_flow=lambda x: x["end_trips"] - x["start_trips"])
        .reset_index()
        .rename(columns={"index": "station"})
    )

    colA, colB = st.columns(2)

    with colA:
        st.markdown("**Stations that likely RUN EMPTY (more starts than ends):**")
        st.dataframe(
            net.sort_values("net_flow", ascending=True).head(10)[
                ["station", "start_trips", "end_trips", "net_flow"]
            ],
            use_container_width=True,
        )

    with colB:
        st.markdown("**Stations that likely FILL UP (more ends than starts):**")
        st.dataframe(
            net.sort_values("net_flow", ascending=False).head(10)[
                ["station", "start_trips", "end_trips", "net_flow"]
            ],
            use_container_width=True,
        )

    st.markdown("""
**Interpretation**

- Stations with strongly **negative net flow** are likely to **run empty** (high departures, fewer arrivals).  
- Stations with strongly **positive net flow** are likely to **fill up** (many arrivals).  
This is a direct operational signal for **truck rebalancing priorities** and where to add capacity or incentives.
""")

# ======================================================
# MAP PAGE
# ======================================================
elif page == "Map":

    st.title("Geographic Distribution of Trips")

    try:
        with open("outputs/task_2_5_kepler_map.html", "r", encoding="utf-8") as f:
            html_data = f.read()
        components.html(html_data, height=700, scrolling=True)
    except FileNotFoundError:
        st.warning("Kepler map file not found. Check file path.")

    st.markdown("""
**Interpretation**

Trips are heavily concentrated in Manhattan and waterfront areas.  
This suggests high commuter usage and indicates potential need for additional stations in dense corridors.
""")

# ======================================================
# OPERATIONAL INSIGHT PAGE (NEW REQUIRED CHART)
# ======================================================
elif page == "Operational Insight":

    st.title("Operational Insight: Hourly Demand")

    hourly = (
        df.groupby("hour")
        .agg(trips=("ride_id", "count"))
        .reset_index()
    )

    fig_hour = px.line(hourly, x="hour", y="trips", markers=True)
    st.plotly_chart(fig_hour, use_container_width=True)

    st.markdown("""
**Interpretation**

Demand peaks during commuting hours (morning and evening).  
This indicates rebalancing trucks should operate before peak commute periods to avoid empty stations.
""")

# ======================================================
# RECOMMENDATIONS PAGE
# ======================================================
elif page == "Recommendations":

    st.title("Operational Recommendations")

    st.markdown("""
### 1. Winter Scaling (November – April)
Reduce active bikes during winter months, as ridership decreases significantly with low temperatures.

### 2. Waterfront Expansion
Add stations in dense waterfront corridors where demand clusters are visible on the map.

### 3. Keeping Stations Stocked
- Perform predictive rebalancing before commuting peaks
- Increase truck redistribution during rush hours
- Prioritize top 10 stations for monitoring
""")
