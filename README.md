# NYC CitiBike 2022 - Supply & Demand Dashboard

## Live Dashboard

🔗 https://nyc-citibike-dashboard-mtirado.streamlit.app/

This interactive dashboard analyzes CitiBike usage patterns in New York City using 2022 trip data combined with weather information.

The application is publicly hosted on Streamlit Cloud and updates automatically from this repository.

---

## Project Goal

The objective of this project is to understand how bike usage changes depending on:

* seasonality
* temperature
* station popularity
* trip patterns across the city

The dashboard allows users to explore patterns instead of looking at static charts.

---

## Main Analyses

### Station Popularity

* Top 10 start stations
* Top 10 end stations
* Geographic visualization of bike activity

### Seasonality

* Monthly ridership trends
* Weekly usage patterns
* Demand fluctuations throughout the year

### Weather Relationship

* Daily trips vs average temperature
* Seasonal demand changes based on weather

---

## Technologies Used

* Python
* Pandas
* Plotly
* Streamlit
* Kepler.gl

---

## How to Run Locally

1. Clone the repository
2. Install dependencies:

```
pip install -r requirements.txt
```

3. Run the app:

```
streamlit run app_Part_2.py
```

---

## Data Notes

The original CitiBike dataset is very large and is not stored in the repository.

A processed sample dataset is used for deployment.
Large raw datasets are excluded using `.gitignore`.

---

## Author

Maria Tirado
