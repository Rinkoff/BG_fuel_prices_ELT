"""
Streamlit dashboard for the BG fuel-prices star schema (read from DuckDB).
"""
from pathlib import Path

import duckdb
import pandas as pd
import plotly.express as px
import streamlit as st

#Configuration
ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "data" / "warehouse.duckdb"

st.set_page_config(page_title="Цени на горивата в България", page_icon="⛽", layout="wide")


# Data loading
@st.cache_data
def load_data() -> pd.DataFrame:
    """Read the star schema (fact joined to both dimensions) into a DataFrame."""
    # read_only so the dashboard never locks the file for the pipeline.
    con = duckdb.connect(str(DB_PATH), read_only=True)
    try:
        out = con.execute(
            """
            SELECT d.date_day,
                   ft.fuel_label,
                   f.price_eur
            FROM main.fct_fuel_price_weekly f
            JOIN main.dim_fuel_type ft ON f.fuel_key = ft.fuel_key
            JOIN main.dim_date       d ON f.date_key = d.date_key
            ORDER BY d.date_day
            """
        ).df()

        out["date_day"] = pd.to_datetime(out["date_day"]).dt.date
        return out
    finally:
        con.close()


df = load_data()

#Visual elements
st.title("⛽ Цени на горивата в България")

st.sidebar.header("Филтри")

fuels = sorted(df["fuel_label"].unique())
chosen_fuels = st.sidebar.multiselect("Гориво", fuels, default=fuels)

min_d, max_d = df["date_day"].min(), df["date_day"].max()
date_range = st.sidebar.slider(
    "Период", min_value=min_d, max_value=max_d, value=(min_d, max_d)
)

mask = (
    df["fuel_label"].isin(chosen_fuels)
    & (df["date_day"] >= date_range[0])
    & (df["date_day"] <= date_range[1])
)
view = df[mask]

#KPI cards
st.subheader("Последни цени")
cols = st.columns(max(len(fuels), 1))
for col, fuel in zip(cols, fuels):
    series = df[df["fuel_label"] == fuel].sort_values("date_day")
    if len(series) >= 2:
        latest = series["price_eur"].iloc[-1]
        prev = series["price_eur"].iloc[-2]
        col.metric(fuel, f"{latest:.3f} €/л", f"{latest - prev:+.3f} €")
    elif len(series) == 1:
        col.metric(fuel, f"{series['price_eur'].iloc[-1]:.3f} €/л")

#Main trend chart
st.subheader("Тренд на цените през времето")
if view.empty:
    st.info("Няма данни за избраните филтри.")
else:
    fig = px.line(
        view, x="date_day", y="price_eur", color="fuel_label",
        labels={"date_day": "Седмица", "price_eur": "Цена (EUR/л)", "fuel_label": "Гориво"},
    )
    fig.update_layout(legend_title_text="", hovermode="x unified")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Средна цена по година")
if not view.empty:
    yearly = (
        view.assign(year=view["date_day"].map(lambda d: d.year))
        .groupby(["year", "fuel_label"], as_index=False)["price_eur"]
        .mean()
    )
    bar = px.bar(
        yearly, x="year", y="price_eur", color="fuel_label", barmode="group",
        labels={"year": "Година", "price_eur": "Средна цена (EUR/л)", "fuel_label": "Гориво"},
    )
    bar.update_layout(legend_title_text="")
    st.plotly_chart(bar, use_container_width=True)

st.divider()
st.caption("Данни: fuel-prices.eu, CC BY 4.0 (Европейска комисия, Weekly Oil Bulletin).")
