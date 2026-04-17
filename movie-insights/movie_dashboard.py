import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Movie Insights & Sentiment", layout="wide", page_icon="🎬")

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    repo = os.path.dirname(base)
    movies   = pd.read_csv(os.path.join(base, "movies_cleaned.csv"))
    ratings  = pd.read_csv(os.path.join(base, "ratings.csv"))
    sent_agg = pd.read_csv(os.path.join(repo, "sentiment-analysis", "movie_sentiment_agg.csv"))
    reviews  = pd.read_csv(os.path.join(repo, "sentiment-analysis", "reviews_with_sentiment.csv"))
    return movies, ratings, sent_agg, reviews

movies, ratings, sent_agg, reviews = load_data()

movies_exploded = movies.copy()
movies_exploded["genres"] = movies_exploded["genres"].str.split("|")
movies_exploded = movies_exploded.explode("genres")
movies_exploded = movies_exploded[movies_exploded["genres"] != "(no genres listed)"]

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
all_genres = sorted(movies_exploded["genres"].unique())
selected_genres = st.sidebar.multiselect("Genre", all_genres, default=all_genres[:8])
min_ratings = st.sidebar.slider("Min ratings per movie", 1, 200, 50)
year_range = st.sidebar.slider("Release Year", 1900, 2018, (1990, 2018))

movies_f = movies[
    (movies["rating_count"] >= min_ratings) &
    (movies["release_year"].between(year_range[0], year_range[1]))
]

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Movie Insights & Sentiment Analysis")
st.caption("MovieLens Dataset (100K ratings) + VADER Sentiment Analysis | Peris & Nihat")

# ── KPI Cards ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Movies", f"{len(movies_f):,}")
c2.metric("Total Ratings", f"{len(ratings):,}")
c3.metric("Avg Rating", f"{movies_f['avg_rating'].mean():.2f} / 5.0")
c4.metric("Genres", str(len(all_genres)))
c5.metric("Sentiment Analysed", f"{len(sent_agg)} movies")

st.divider()

# ── Row 1: Rating Distributions ───────────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Individual Rating Distribution")
    fig1 = px.histogram(ratings, x="rating", nbins=10,
                        color_discrete_sequence=["#3498db"],
                        labels={"rating": "Star Rating", "count": "Number of Ratings"})
    fig1.update_layout(height=360, bargap=0.1)
    fig1.add_vline(x=ratings["rating"].mean(), line_dash="dash", line_color="red",
                   annotation_text=f"Mean: {ratings['rating'].mean():.2f}")
    st.plotly_chart(fig1, use_container_width=True)

with col_r:
    st.subheader("Average Rating per Movie")
    fig2 = px.histogram(movies_f, x="avg_rating", nbins=30,
                        color_discrete_sequence=["#2ecc71"],
                        labels={"avg_rating": "Average Rating", "count": "Movies"})
    fig2.update_layout(height=360, bargap=0.05)
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Genre Analysis ──────────────────────────────────────────────────────
st.subheader("Genre Analysis")
col_l2, col_r2 = st.columns(2)

genre_stats = (movies_exploded[movies_exploded["genres"].isin(selected_genres)]
               .groupby("genres")
               .agg(avg_rating=("avg_rating", "mean"),
                    movie_count=("movieId", "count"),
                    total_ratings=("rating_count", "sum"))
               .reset_index()
               .sort_values("avg_rating", ascending=True))

with col_l2:
    st.markdown("**Average Rating by Genre**")
    fig3 = px.bar(genre_stats, x="avg_rating", y="genres", orientation="h",
                  color="avg_rating", color_continuous_scale="RdYlGn",
                  text=genre_stats["avg_rating"].round(2),
                  labels={"avg_rating": "Avg Rating", "genres": "Genre"})
    fig3.update_layout(height=420, coloraxis_showscale=False)
    fig3.update_traces(textposition="outside")
    st.plotly_chart(fig3, use_container_width=True)

with col_r2:
    st.markdown("**Movie Count by Genre**")
    fig4 = px.bar(genre_stats.sort_values("movie_count", ascending=True),
                  x="movie_count", y="genres", orientation="h",
                  color="movie_count", color_continuous_scale="Blues",
                  labels={"movie_count": "Number of Movies", "genres": "Genre"})
    fig4.update_layout(height=420, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Ratings Over Release Year ──────────────────────────────────────────
st.subheader("Average Rating by Release Year")
year_trend = (movies_f.groupby("release_year")
              .agg(avg_rating=("avg_rating", "mean"),
                   movie_count=("movieId", "count"))
              .reset_index())

fig5 = px.scatter(year_trend, x="release_year", y="avg_rating",
                  size="movie_count", color="avg_rating",
                  color_continuous_scale="RdYlGn",
                  labels={"release_year": "Release Year", "avg_rating": "Avg Rating",
                          "movie_count": "Number of Movies"})
fig5.update_layout(height=350, coloraxis_showscale=False)
st.plotly_chart(fig5, use_container_width=True)

st.divider()

# ── Row 4: Sentiment vs Rating ─────────────────────────────────────────────────
st.subheader("Sentiment Score vs Numerical Rating (Top 30 Movies)")
st.caption("VADER compound score: -1 = most negative, +1 = most positive. Size = number of reviews analysed.")

col_l3, col_r3 = st.columns([2, 1])

with col_l3:
    fig6 = px.scatter(sent_agg, x="avg_rating", y="avg_compound",
                      text="title", size="total_reviews",
                      color="discrepancy", color_continuous_scale="RdYlGn_r",
                      labels={"avg_rating": "Avg Star Rating",
                              "avg_compound": "VADER Sentiment Score",
                              "discrepancy": "Discrepancy",
                              "total_reviews": "Reviews Analysed"},
                      hover_data={"title": True, "avg_rating": ":.2f",
                                  "avg_compound": ":.3f", "discrepancy": ":.3f"})
    fig6.update_traces(textposition="top center", textfont_size=7)
    fig6.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5,
                   annotation_text="Neutral sentiment")
    fig6.update_layout(height=500)
    st.plotly_chart(fig6, use_container_width=True)

with col_r3:
    st.markdown("**Biggest Discrepancies**")
    st.caption("Movies where sentiment and star ratings diverge most")
    top_disc = (sent_agg.nlargest(10, "discrepancy")
                [["title", "avg_rating", "avg_compound", "discrepancy"]]
                .copy())
    top_disc.columns = ["Movie", "Rating", "Sentiment", "Gap"]
    top_disc["Rating"] = top_disc["Rating"].round(2)
    top_disc["Sentiment"] = top_disc["Sentiment"].round(3)
    top_disc["Gap"] = top_disc["Gap"].round(3)
    st.dataframe(top_disc.reset_index(drop=True), use_container_width=True, height=480)

# ── Row 5: Sentiment Breakdown per Movie ──────────────────────────────────────
st.subheader("Positive vs Negative Review Breakdown per Movie")
sent_sorted = sent_agg.sort_values("avg_compound", ascending=True)

fig7 = go.Figure()
fig7.add_trace(go.Bar(
    name="Positive", y=sent_sorted["title"], x=sent_sorted["pos_pct"],
    orientation="h", marker_color="#2ecc71"))
fig7.add_trace(go.Bar(
    name="Negative", y=sent_sorted["title"], x=sent_sorted["neg_pct"],
    orientation="h", marker_color="#e74c3c"))
fig7.update_layout(barmode="stack", height=620,
                   xaxis_title="Proportion of Reviews",
                   legend=dict(orientation="h", y=1.02),
                   margin=dict(l=260))
st.plotly_chart(fig7, use_container_width=True)

# ── Row 6: Top & Bottom Rated Movies ──────────────────────────────────────────
st.subheader("Top & Bottom Rated Movies")
col_t, col_b = st.columns(2)

top_movies = (movies[movies["rating_count"] >= 50]
              .nlargest(10, "avg_rating")
              [["title", "genres", "release_year", "avg_rating", "rating_count"]])
bot_movies = (movies[movies["rating_count"] >= 50]
              .nsmallest(10, "avg_rating")
              [["title", "genres", "release_year", "avg_rating", "rating_count"]])

with col_t:
    st.markdown("**Top 10 Highest Rated**")
    st.dataframe(top_movies.reset_index(drop=True), use_container_width=True)

with col_b:
    st.markdown("**Bottom 10 Lowest Rated**")
    st.dataframe(bot_movies.reset_index(drop=True), use_container_width=True)

# ── Row 7: Review Explorer ─────────────────────────────────────────────────────
st.divider()
st.subheader("Individual Review Explorer")
selected_movie = st.selectbox("Select a movie to read its reviews", sorted(reviews["title"].unique()))
movie_reviews = reviews[reviews["title"] == selected_movie]

ca, cb, cc = st.columns(3)
ca.metric("Avg Sentiment Score", f"{movie_reviews['compound'].mean():.3f}")
cb.metric("Positive Reviews",
          f"{(movie_reviews['sentiment_label'] == 'positive').sum()} / {len(movie_reviews)}")
cc.metric("Star Rating", f"{movie_reviews['avg_rating'].iloc[0]:.2f} / 5.0")

for _, row in movie_reviews.iterrows():
    if row["sentiment_label"] == "positive":
        bg, label = "#1a3d2b", "POS"
    elif row["sentiment_label"] == "negative":
        bg, label = "#3d1a1a", "NEG"
    else:
        bg, label = "#2a2a2a", "NEU"
    st.markdown(
        f'<div style="background:{bg};padding:10px 14px;border-radius:6px;margin:4px 0;">'
        f'<b>[{label} {row["compound"]:+.3f}]</b>&nbsp; {row["review"]}</div>',
        unsafe_allow_html=True)

# ── Footer ─────────────────────────────────────────────────────────────────────
st.divider()
st.caption("Integration 1: Peris (Movie Recommendation Insights) + Nihat (Sentiment Analysis) | Semester 4 Team Project")
