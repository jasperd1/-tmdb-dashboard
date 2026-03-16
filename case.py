import streamlit as st
import pandas as pd
import numpy as np

# Titel dashboard
st.title("TMDB Dashboard")
st.write("Analyse van films met Kaggle-data en TMDB API-data")

# Data inlezen
kaggle_df = pd.read_csv("tmdb_5000_movies.csv")
api_df = pd.read_csv("tmdb_api_data.csv")

# Merge op id
merged_df = pd.merge(kaggle_df, api_df, on="id", how="inner")

# Nieuwe kolommen maken
merged_df["Profit"] = merged_df["revenue_api"] - merged_df["budget_api"]
merged_df["ROI"] = merged_df["Profit"] / merged_df["budget_api"]
merged_df["Year"] = pd.to_datetime(merged_df["release_date_api"], errors="coerce").dt.year

# Oneindige waarden weghalen
merged_df["ROI"] = merged_df["ROI"].replace([np.inf, -np.inf], np.nan)

# Alleen rijen met bruikbare waarden
merged_df = merged_df.dropna(subset=["Year", "vote_average_api", "budget_api", "revenue_api"])

# Filters
year_min = int(merged_df["Year"].min())
year_max = int(merged_df["Year"].max())

years = st.slider("Kies jaarbereik", year_min, year_max, (2000, 2015))
min_rating = st.slider("Minimale rating", 0.0, 10.0, 7.0, 0.1)
top_n = st.slider("Aantal films", 0, 2000, 100)

sort_col = st.selectbox(
    "Sorteer op",
    ["budget_api", "revenue_api", "popularity_api", "vote_average_api", "ROI"]
)

only_profitable = st.checkbox("Toon alleen winstgevende films")

# Filteren
filtered = merged_df[
    (merged_df["Year"].between(years[0], years[1])) &
    (merged_df["vote_average_api"] >= min_rating)
]

if only_profitable:
    filtered = filtered[filtered["Profit"] > 0]

filtered = filtered.sort_values(sort_col, ascending=False).head(top_n)

# Samenvatting
st.subheader("Samenvatting")
st.write("Aantal films in selectie:", len(filtered))
st.write("Gemiddelde rating:", round(filtered["vote_average_api"].mean(), 2))
st.write("Gemiddelde ROI:", round(filtered["ROI"].dropna().mean(), 2))
st.write("Gemiddelde revenue:", round(filtered["revenue_api"].mean(), 2))

# Tabel
st.subheader("Gefilterde films")
st.dataframe(filtered[[
    "title",
    "title_api",
    "Year",
    "vote_average_api",
    "popularity_api",
    "budget_api",
    "revenue_api",
    "Profit",
    "ROI"
]])

# Scatterplot
st.subheader("Budget vs rating")
chart_df = filtered[["budget_api", "vote_average_api", "revenue_api", "ROI", "title_api"]].dropna()

st.vega_lite_chart(
    chart_df,
    {
        "mark": "point",
        "encoding": {
            "x": {"field": "budget_api", "type": "quantitative", "title": "Budget"},
            "y": {"field": "vote_average_api", "type": "quantitative", "title": "Rating"},
            "size": {"field": "revenue_api", "type": "quantitative", "title": "Revenue"},
            "color": {"field": "ROI", "type": "quantitative", "title": "ROI"},
            "tooltip": [
                {"field": "title_api", "type": "nominal", "title": "Titel"},
                {"field": "budget_api", "type": "quantitative", "title": "Budget"},
                {"field": "revenue_api", "type": "quantitative", "title": "Revenue"},
                {"field": "vote_average_api", "type": "quantitative", "title": "Rating"},
                {"field": "ROI", "type": "quantitative", "title": "ROI"}
            ]
        }
    },
    use_container_width=True
)