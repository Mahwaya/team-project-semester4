"""
Master Dashboard — Semester 4 Team Data Science Project
Run with: streamlit run master_dashboard.py
"""

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats
from collections import Counter
import re

st.set_page_config(
    page_title="SIPDiDS Team Project",
    page_icon="📊",
    layout="wide"
)

ROOT = os.path.dirname(os.path.abspath(__file__))

# ── WSB Brand Theme ────────────────────────────────────────────────────────────
WSB_PINK   = "#E2007A"
WSB_ORANGE = "#E84813"
WSB_DARK   = "#1C0A12"
WSB_LIGHT  = "#FDEEF6"

st.markdown(f"""
<style>
  /* Sidebar background */
  [data-testid="stSidebar"] {{
      background-color: {WSB_DARK};
  }}
  [data-testid="stSidebar"] * {{
      color: #FFFFFF !important;
  }}
  /* Radio selected item */
  [data-testid="stSidebar"] .stRadio label:has(input:checked) {{
      background-color: {WSB_PINK} !important;
      border-radius: 6px;
      padding: 4px 8px;
  }}
  /* Top header bar */
  [data-testid="stHeader"] {{
      background-color: {WSB_PINK};
  }}
  /* Main page background */
  .stApp {{
      background-color: #FAFAFA;
  }}
  /* Page titles */
  h1 {{
      color: {WSB_PINK} !important;
      border-bottom: 3px solid {WSB_PINK};
      padding-bottom: 8px;
  }}
  h2, h3 {{
      color: {WSB_DARK} !important;
  }}
  /* Metric labels */
  [data-testid="stMetricLabel"] {{
      color: {WSB_PINK} !important;
      font-weight: 600;
  }}
  /* Metric values */
  [data-testid="stMetricValue"] {{
      color: {WSB_DARK} !important;
  }}
  /* Divider */
  hr {{
      border-color: {WSB_PINK} !important;
      opacity: 0.3;
  }}
  /* Info/warning/error boxes */
  .stAlert {{
      border-left: 4px solid {WSB_PINK} !important;
  }}
  /* Dataframe header */
  .dataframe thead th {{
      background-color: {WSB_PINK} !important;
      color: white !important;
  }}
  /* Sidebar section labels */
  [data-testid="stSidebar"] .stMarkdown p {{
      color: #CCCCCC !important;
  }}
  /* WSB logo bar at top of sidebar */
  .wsb-logo {{
      background: {WSB_PINK};
      color: white;
      padding: 14px 16px;
      border-radius: 8px;
      font-size: 1.1rem;
      font-weight: 700;
      letter-spacing: 0.5px;
      margin-bottom: 12px;
      text-align: center;
  }}
  .wsb-sub {{
      color: #FFAAD8 !important;
      font-size: 0.78rem;
      text-align: center;
      margin-top: -8px;
      margin-bottom: 12px;
  }}
</style>
""", unsafe_allow_html=True)

# ── Sidebar navigation ─────────────────────────────────────────────────────────
st.sidebar.markdown('<div class="wsb-logo">WSB University</div>', unsafe_allow_html=True)
st.sidebar.markdown('<div class="wsb-sub">Akademia WSB · Dabrowa Gornicza</div>', unsafe_allow_html=True)
st.sidebar.markdown("**SIPDiDS Team Project**")
st.sidebar.caption("Semester 4 | MSc Data Scientist")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Dashboard",
    [
        "Home",
        "Social Media & Stock Markets",
        "Movie Insights & Sentiment",
        "Academic Publication Trends",
    ]
)

st.sidebar.markdown("---")
st.sidebar.markdown("**Team Members**")
st.sidebar.markdown("Percival · Shamil · Peris · Nihat · Christian")
st.sidebar.markdown("**Presentation:** April 21, 2026")


# ══════════════════════════════════════════════════════════════════════════════
# HOME
# ══════════════════════════════════════════════════════════════════════════════
if page == "Home":
    st.markdown(f"""
    <div style="background:{WSB_PINK};padding:24px 32px;border-radius:10px;margin-bottom:20px;">
        <h1 style="color:white !important;border:none;padding:0;margin:0;font-size:2rem;">
            SIPDiDS Team Data Science Project
        </h1>
        <p style="color:#FDEEF6;margin:6px 0 0 0;font-size:1rem;">
            Semester 4 · MSc Data Scientist · WSB University Dabrowa Gornicza
        </p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    card_style = (
        "border-left:5px solid {color};background:{bg};"
        "padding:20px;border-radius:8px;height:100%;"
    )

    with col1:
        st.markdown(f"""
        <div style="{card_style.format(color=WSB_PINK, bg='#FFF0F8')}">
            <h3 style="color:{WSB_PINK};margin-top:0;">Integration 1</h3>
            <b>Social Media &amp; Stock Markets</b>
            <ul style="margin-top:8px;padding-left:18px;">
                <li>Reddit sentiment (AAPL, TSLA, AMZN)</li>
                <li>Stock price + volatility via yfinance</li>
                <li>Pearson &amp; Spearman correlation</li>
                <li><b>Finding:</b> Reddit is a lagging indicator</li>
            </ul>
            <p style="color:#888;margin:0;"><i>Percival + Shamil</i></p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div style="{card_style.format(color=WSB_ORANGE, bg='#FFF5F0')}">
            <h3 style="color:{WSB_ORANGE};margin-top:0;">Integration 2</h3>
            <b>Movie Insights &amp; Sentiment</b>
            <ul style="margin-top:8px;padding-left:18px;">
                <li>MovieLens 100K ratings analysis</li>
                <li>VADER sentiment on movie reviews</li>
                <li>Genre &amp; user behaviour analysis</li>
                <li><b>Finding:</b> Sentiment ≠ star rating</li>
            </ul>
            <p style="color:#888;margin:0;"><i>Peris + Nihat</i></p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div style="{card_style.format(color='#2ecc71', bg='#F0FFF5')}">
            <h3 style="color:#27ae60;margin-top:0;">Standalone Task</h3>
            <b>Academic Publication Trends</b>
            <ul style="margin-top:8px;padding-left:18px;">
                <li>3,327 papers · 5 fields · 2015–2025</li>
                <li>Publication volume &amp; keyword trends</li>
                <li>Emerging vs declining research areas</li>
                <li><b>Finding:</b> Renewable Energy only growing</li>
            </ul>
            <p style="color:#888;margin:0;"><i>Christian / Shamil</i></p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    m1, m2, m3, m4, m5 = st.columns(5)
    m1.metric("Reddit Posts", "277")
    m2.metric("Stock Records", "840")
    m3.metric("Movie Ratings", "100,836")
    m4.metric("Sentiment Reviews", "240")
    m5.metric("Academic Papers", "3,327")

    st.markdown("---")
    st.info("Use the sidebar to navigate between the three dashboards.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — SOCIAL MEDIA & STOCK MARKETS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Social Media & Stock Markets":

    @st.cache_data
    def load_stock():
        sm = os.path.join(ROOT, "stock-market")
        stock = pd.read_csv(os.path.join(sm, "stock_data_final.csv"), parse_dates=["date"])
        corr  = pd.read_csv(os.path.join(sm, "correlation_dataset.csv"))
        vol   = pd.read_csv(os.path.join(sm, "weekly_volatility.csv"))
        return stock, corr, vol

    stock_daily, corr_df, weekly_vol = load_stock()

    TICKER_NAMES = {"AAPL": "Apple", "TSLA": "Tesla", "AMZN": "Amazon"}
    COLORS = {"AAPL": "#1f77b4", "TSLA": "#d62728", "AMZN": "#ff7f0e"}

    st.title("Social Media & Stock Market Analysis")
    st.caption("Reddit sentiment (PRAW) + Stock prices (yfinance) | AAPL · TSLA · AMZN | Mar 2025 – Mar 2026")

    st.sidebar.markdown("---")
    selected_tickers = st.sidebar.multiselect(
        "Companies", ["AAPL", "TSLA", "AMZN"], default=["AAPL", "TSLA", "AMZN"],
        format_func=lambda x: f"{TICKER_NAMES[x]} ({x})"
    )
    show_ma7  = st.sidebar.checkbox("Show 7-day MA",  value=True)
    show_ma30 = st.sidebar.checkbox("Show 30-day MA", value=True)

    if not selected_tickers:
        st.warning("Select at least one company.")
        st.stop()

    kpi_cols = st.columns(len(selected_tickers))
    for col, ticker in zip(kpi_cols, selected_tickers):
        data   = stock_daily[stock_daily["ticker"] == ticker].sort_values("date")
        change = ((data["close"].iloc[-1] - data["close"].iloc[0]) / data["close"].iloc[0]) * 100
        r_data = corr_df[(corr_df["ticker"] == ticker) & corr_df["avg_score"].notna()]
        col.metric(f"{TICKER_NAMES[ticker]} ({ticker})",
                   f"${data['close'].iloc[-1]:.2f}", f"{change:+.1f}% (12mo)")
        col.caption(f"High Reddit weeks: {int(r_data['high_reddit_activity'].sum())} | "
                    f"Peak score: {int(r_data['avg_score'].max()):,}")

    st.divider()

    st.subheader("Stock Price with Reddit Sentiment Volume")
    for ticker in selected_tickers:
        s_data = stock_daily[stock_daily["ticker"] == ticker].sort_values("date")
        r_data = corr_df[(corr_df["ticker"] == ticker) & corr_df["avg_score"].notna()].sort_values("year_week")
        fig = make_subplots(rows=2, cols=1, shared_xaxes=False,
                            row_heights=[0.65, 0.35], vertical_spacing=0.08,
                            subplot_titles=(f"{TICKER_NAMES[ticker]} — Daily Close",
                                            "Reddit Avg Score per Week"))
        fig.add_trace(go.Scatter(x=s_data["date"], y=s_data["close"], name="Close",
                                 line=dict(color=COLORS[ticker], width=1.5)), row=1, col=1)
        if show_ma7:
            fig.add_trace(go.Scatter(x=s_data["date"], y=s_data["MA7"], name="MA7",
                                     line=dict(color="black", width=1, dash="dash")), row=1, col=1)
        if show_ma30:
            fig.add_trace(go.Scatter(x=s_data["date"], y=s_data["MA30"], name="MA30",
                                     line=dict(color="gold", width=2)), row=1, col=1)
        bar_colors = ["#e74c3c" if row["high_reddit_activity"] else COLORS[ticker]
                      for _, row in r_data.iterrows()]
        fig.add_trace(go.Bar(x=r_data["year_week"], y=r_data["avg_score"],
                             name="Reddit Score", marker_color=bar_colors), row=2, col=1)
        fig.update_layout(height=500, legend=dict(orientation="h", y=1.02), hovermode="x unified")
        fig.update_yaxes(title_text="Price (USD)", tickprefix="$", row=1, col=1)
        fig.update_yaxes(title_text="Reddit Score", row=2, col=1)
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Weekly Volatility vs Reddit Activity")
    vcols = st.columns(len(selected_tickers))
    for col, ticker in zip(vcols, selected_tickers):
        v = weekly_vol[weekly_vol["ticker"] == ticker].sort_values("year_week")
        r = corr_df[(corr_df["ticker"] == ticker) & corr_df["avg_score"].notna()].sort_values("year_week")
        merged = v.merge(r[["year_week", "avg_score"]], on="year_week", how="left")
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=merged["year_week"], y=merged["volatility"],
                             name="Volatility", marker_color=COLORS[ticker], opacity=0.6), secondary_y=False)
        fig.add_trace(go.Scatter(x=merged["year_week"], y=merged["avg_score"],
                                 name="Reddit Score", line=dict(color="black", width=2),
                                 mode="lines+markers"), secondary_y=True)
        fig.update_layout(title=f"{TICKER_NAMES[ticker]}", height=320,
                          legend=dict(orientation="h", y=1.1))
        fig.update_yaxes(title_text="Volatility", secondary_y=False)
        fig.update_yaxes(title_text="Reddit Score", secondary_y=True)
        col.plotly_chart(fig, use_container_width=True)

    st.divider()

    st.subheader("Reddit vs Stock — Correlation Heatmap (Pearson)")
    s_feats = ["post_count", "avg_score", "avg_upvote_ratio", "avg_comments", "avg_sentiment"]
    s_metrics = ["weekly_price_change_pct", "next_week_price_change_pct", "weekly_volatility", "avg_daily_return"]
    r_only = corr_df[corr_df["avg_score"].notna()][s_feats + s_metrics].copy()
    heat = pd.DataFrame(index=s_feats, columns=s_metrics, dtype=float)
    for sf in s_feats:
        for sm in s_metrics:
            valid = r_only[[sf, sm]].dropna()
            if len(valid) > 4:
                r, _ = stats.pearsonr(valid[sf], valid[sm])
                heat.loc[sf, sm] = round(r, 3)
    fig_h = px.imshow(heat.astype(float), color_continuous_scale="RdYlGn", zmin=-1, zmax=1,
                      text_auto=".3f", labels=dict(x="Stock Metrics", y="Reddit Features"))
    fig_h.update_layout(height=360)
    st.plotly_chart(fig_h, use_container_width=True)

    st.divider()

    st.subheader("Spotlight: AMZN 2025-W17 — Extreme Reddit Spike")
    row = corr_df[(corr_df["ticker"] == "AMZN") & (corr_df["year_week"] == "2025-W17")]
    if not row.empty:
        r = row.iloc[0]
        s1, s2, s3, s4 = st.columns(4)
        s1.metric("Reddit Avg Score", f"{int(r['avg_score']):,}")
        s2.metric("Sentiment Score",  f"{r['avg_sentiment']:.3f}")
        s3.metric("AMZN Weekly Return",  f"{r['weekly_price_change_pct']:+.2f}%")
        s4.metric("Next-Week Return", f"{r['next_week_price_change_pct']:+.2f}%")
        st.info("Despite negative sentiment (−0.40), AMZN rose +12.95% that week. "
                "Reddit reacted to the price event — it did not predict it. "
                "**Reddit is a lagging indicator, not a predictive one.**")

    st.caption("Percival Mahwaya (Reddit) + Shamil (Stock) | Integration 1")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — MOVIE INSIGHTS & SENTIMENT
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Movie Insights & Sentiment":

    @st.cache_data
    def load_movies():
        mi = os.path.join(ROOT, "movie-insights")
        sa = os.path.join(ROOT, "sentiment-analysis")
        return (pd.read_csv(os.path.join(mi, "movies_cleaned.csv")),
                pd.read_csv(os.path.join(mi, "ratings.csv")),
                pd.read_csv(os.path.join(sa, "movie_sentiment_agg.csv")),
                pd.read_csv(os.path.join(sa, "reviews_with_sentiment.csv")))

    movies, ratings, sent_agg, reviews = load_movies()
    movies_exp = movies.copy()
    movies_exp["genres"] = movies_exp["genres"].str.split("|")
    movies_exp = movies_exp.explode("genres")
    movies_exp = movies_exp[movies_exp["genres"] != "(no genres listed)"]

    st.title("Movie Insights & Sentiment Analysis")
    st.caption("MovieLens 100K Dataset + VADER Sentiment | Peris & Nihat")

    st.sidebar.markdown("---")
    all_genres = sorted(movies_exp["genres"].unique())
    sel_genres = st.sidebar.multiselect("Genre", all_genres, default=all_genres[:8])
    min_r = st.sidebar.slider("Min ratings per movie", 1, 200, 50)
    yr = st.sidebar.slider("Release Year", 1900, 2018, (1990, 2018))

    movies_f = movies[(movies["rating_count"] >= min_r) &
                      (movies["release_year"].between(yr[0], yr[1]))]

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Movies",    f"{len(movies_f):,}")
    c2.metric("Ratings",   f"{len(ratings):,}")
    c3.metric("Avg Rating", f"{movies_f['avg_rating'].mean():.2f}")
    c4.metric("Genres",    str(len(all_genres)))
    c5.metric("Sentiment Analysed", f"{len(sent_agg)} movies")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Rating Distribution")
        fig1 = px.histogram(ratings, x="rating", nbins=10,
                            color_discrete_sequence=["#3498db"])
        fig1.add_vline(x=ratings["rating"].mean(), line_dash="dash", line_color="red",
                       annotation_text=f"Mean: {ratings['rating'].mean():.2f}")
        fig1.update_layout(height=340, bargap=0.1)
        st.plotly_chart(fig1, use_container_width=True)

    with col_r:
        st.subheader("Avg Rating per Movie")
        fig2 = px.histogram(movies_f, x="avg_rating", nbins=30,
                            color_discrete_sequence=["#2ecc71"])
        fig2.update_layout(height=340, bargap=0.05)
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Genre Analysis")
    genre_stats = (movies_exp[movies_exp["genres"].isin(sel_genres)]
                   .groupby("genres")
                   .agg(avg_rating=("avg_rating","mean"), movie_count=("movieId","count"))
                   .reset_index().sort_values("avg_rating", ascending=True))

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        fig3 = px.bar(genre_stats, x="avg_rating", y="genres", orientation="h",
                      color="avg_rating", color_continuous_scale="RdYlGn",
                      text=genre_stats["avg_rating"].round(2), title="Avg Rating by Genre")
        fig3.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig3, use_container_width=True)
    with col_r2:
        fig4 = px.bar(genre_stats.sort_values("movie_count", ascending=True),
                      x="movie_count", y="genres", orientation="h",
                      color="movie_count", color_continuous_scale="Blues",
                      title="Movie Count by Genre")
        fig4.update_layout(height=400, coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.divider()

    st.subheader("Sentiment Score vs Numerical Rating (Top 30 Movies)")
    st.caption("VADER compound score: −1 most negative → +1 most positive. Colour = size of discrepancy.")
    col_l3, col_r3 = st.columns([2, 1])
    with col_l3:
        fig6 = px.scatter(sent_agg, x="avg_rating", y="avg_compound",
                          text="title", size="total_reviews",
                          color="discrepancy", color_continuous_scale="RdYlGn_r",
                          labels={"avg_rating": "Avg Star Rating",
                                  "avg_compound": "VADER Sentiment Score"})
        fig6.update_traces(textposition="top center", textfont_size=7)
        fig6.add_hline(y=0, line_dash="dash", line_color="gray",
                       annotation_text="Neutral sentiment")
        fig6.update_layout(height=480)
        st.plotly_chart(fig6, use_container_width=True)
    with col_r3:
        st.markdown("**Biggest Discrepancies**")
        top_disc = sent_agg.nlargest(10, "discrepancy")[["title","avg_rating","avg_compound","discrepancy"]].copy()
        top_disc.columns = ["Movie", "Rating", "Sentiment", "Gap"]
        st.dataframe(top_disc.round(3).reset_index(drop=True), use_container_width=True, height=460)

    st.subheader("Positive vs Negative Breakdown per Movie")
    sent_s = sent_agg.sort_values("avg_compound", ascending=True)
    fig7 = go.Figure()
    fig7.add_trace(go.Bar(name="Positive", y=sent_s["title"], x=sent_s["pos_pct"],
                          orientation="h", marker_color="#2ecc71"))
    fig7.add_trace(go.Bar(name="Negative", y=sent_s["title"], x=sent_s["neg_pct"],
                          orientation="h", marker_color="#e74c3c"))
    fig7.update_layout(barmode="stack", height=600, xaxis_title="Proportion",
                       legend=dict(orientation="h", y=1.02), margin=dict(l=260))
    st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Review Explorer")
    sel_movie = st.selectbox("Select a movie", sorted(reviews["title"].unique()))
    mr = reviews[reviews["title"] == sel_movie]
    ca, cb, cc = st.columns(3)
    ca.metric("Avg Sentiment", f"{mr['compound'].mean():.3f}")
    cb.metric("Positive", f"{(mr['sentiment_label']=='positive').sum()} / {len(mr)}")
    cc.metric("Star Rating", f"{mr['avg_rating'].iloc[0]:.2f}")
    for _, row in mr.iterrows():
        bg  = "#1a3d2b" if row["sentiment_label"] == "positive" else (
              "#3d1a1a" if row["sentiment_label"] == "negative" else "#2a2a2a")
        lbl = row["sentiment_label"].upper()[:3]
        st.markdown(
            f'<div style="background:{bg};padding:10px 14px;border-radius:6px;margin:4px 0;">'
            f'<b>[{lbl} {row["compound"]:+.3f}]</b>&nbsp; {row["review"]}</div>',
            unsafe_allow_html=True)

    st.caption("Peris (Movie Insights) + Nihat (Sentiment Analysis) | Integration 2")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — ACADEMIC PUBLICATION TRENDS
# ══════════════════════════════════════════════════════════════════════════════
elif page == "Academic Publication Trends":

    STOP = {
        "a","an","the","of","in","and","for","to","with","on","at","by","from",
        "is","are","was","be","as","its","this","that","using","based","study",
        "analysis","approach","novel","new","towards","via","into","between",
        "within","across","over","under","their","these","through","such"
    }

    def keywords(titles, n=15):
        words = []
        for t in titles:
            if isinstance(t, str):
                words += [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t)
                          if w.lower() not in STOP]
        return Counter(words).most_common(n)

    @st.cache_data
    def load_pubs():
        return pd.read_csv(os.path.join(ROOT, "academic-publications", "clean_publications.csv"))

    df = load_pubs()

    st.title("Academic Publication Trend Analysis")
    st.caption("CrossRef API | 3,327 clean records | 5 fields | 2015–2025 | Christian / Shamil")

    st.sidebar.markdown("---")
    all_fields = sorted(df["field"].unique())
    sel_fields = st.sidebar.multiselect("Fields", all_fields, default=all_fields)
    yr2 = st.sidebar.slider("Year Range ", 2015, 2025, (2015, 2025))

    df_f = df[df["field"].isin(sel_fields) & df["year"].between(yr2[0], yr2[1])]
    pivot = (df_f.groupby(["year","field"])["title"]
             .count().unstack().fillna(0)
             .loc[yr2[0]:yr2[1], sel_fields])

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Papers",       f"{len(df_f):,}")
    c2.metric("Fields",       str(len(sel_fields)))
    c3.metric("Years",        f"{yr2[0]}–{yr2[1]}")
    c4.metric("Avg Citations", f"{df_f['citations'].mean():.1f}")
    c5.metric("Top by Volume", df_f.groupby("field")["title"].count().idxmax() if len(df_f) else "—")

    st.divider()

    col_l, col_r = st.columns(2)
    with col_l:
        st.subheader("Publication Volume by Field")
        fig1 = px.line(pivot.reset_index().melt(id_vars="year"),
                       x="year", y="value", color="field", markers=True,
                       labels={"value": "Papers", "year": "Year"})
        fig1.update_layout(height=360, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig1, use_container_width=True)

    with col_r:
        st.subheader("Year-over-Year Growth Rate (%)")
        growth = pivot.pct_change() * 100
        fig2 = px.line(growth.reset_index().melt(id_vars="year"),
                       x="year", y="value", color="field", markers=True,
                       labels={"value": "Growth (%)", "year": "Year"})
        fig2.add_hline(y=0, line_dash="dash", line_color="gray")
        fig2.update_layout(height=360, legend=dict(orientation="h", y=-0.25))
        st.plotly_chart(fig2, use_container_width=True)

    col_l2, col_r2 = st.columns(2)
    with col_l2:
        st.subheader("Emerging vs Declining Fields")
        trows = []
        for field in sel_fields:
            if field in pivot.columns and len(pivot[field]) > 1:
                s, _, _, p, _ = stats.linregress(np.arange(len(pivot[field])), pivot[field].values)
                trows.append({"Field": field, "Slope": round(s, 2),
                              "Direction": "Emerging" if s > 0 else "Declining"})
        tdf = pd.DataFrame(trows).sort_values("Slope")
        fig3 = px.bar(tdf, x="Slope", y="Field", orientation="h", color="Direction",
                      color_discrete_map={"Emerging": "#2ecc71", "Declining": "#e74c3c"},
                      text="Slope")
        fig3.add_vline(x=0, line_color="black", line_width=1)
        fig3.update_layout(height=360)
        st.plotly_chart(fig3, use_container_width=True)

    with col_r2:
        st.subheader("Average Citations per Field")
        cit = df_f.groupby("field")["citations"].mean().round(2).reset_index().sort_values("citations")
        cit.columns = ["Field", "Avg Citations"]
        fig4 = px.bar(cit, x="Avg Citations", y="Field", orientation="h",
                      color="Avg Citations", color_continuous_scale="Blues", text="Avg Citations")
        fig4.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        fig4.update_layout(height=360, coloraxis_showscale=False)
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Publication Volume Heatmap")
    fig5 = px.imshow(pivot.T, text_auto=True, aspect="auto", color_continuous_scale="YlOrRd",
                     labels=dict(x="Year", y="Field", color="Papers"))
    fig5.update_layout(height=260)
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()

    st.subheader("Keyword Analysis")
    col_ka, col_kb = st.columns(2)

    with col_ka:
        st.markdown("**Top 15 Keywords: 2015 vs 2025**")
        kw15 = keywords(df_f[df_f["year"] == 2015]["title"])
        kw25 = keywords(df_f[df_f["year"] == 2025]["title"])
        kdf = (pd.DataFrame({"Keyword": [w for w,_ in kw15], "2015": [c for _,c in kw15]})
               .merge(pd.DataFrame({"Keyword": [w for w,_ in kw25], "2025": [c for _,c in kw25]}),
                      on="Keyword", how="outer").fillna(0).sort_values("2015", ascending=False))
        fig6 = go.Figure()
        fig6.add_trace(go.Bar(name="2015", y=kdf["Keyword"], x=kdf["2015"],
                              orientation="h", marker_color="#3498db"))
        fig6.add_trace(go.Bar(name="2025", y=kdf["Keyword"], x=kdf["2025"],
                              orientation="h", marker_color="#e67e22"))
        fig6.update_layout(barmode="group", height=420, margin=dict(l=120),
                           legend=dict(orientation="h", y=1.08))
        st.plotly_chart(fig6, use_container_width=True)

    with col_kb:
        st.markdown("**Keyword Trend Over Time**")
        kw_field = st.selectbox("Field", ["All Fields"] + all_fields)
        src = df_f if kw_field == "All Fields" else df_f[df_f["field"] == kw_field]
        top_w = [w for w, _ in keywords(src["title"], 8)]
        ktrend = {}
        for yr_val in sorted(src["year"].unique()):
            c = Counter()
            for t in src[src["year"] == yr_val]["title"]:
                if isinstance(t, str):
                    c.update([w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t)
                              if w.lower() not in STOP])
            total = sum(c.values()) or 1
            ktrend[yr_val] = {w: round(c[w]/total*100, 2) for w in top_w}
        kt_df = pd.DataFrame(ktrend).T.reset_index()
        kt_df.columns = ["year"] + top_w
        fig7 = px.line(kt_df.melt(id_vars="year", var_name="Keyword", value_name="Freq (%)"),
                       x="year", y="Freq (%)", color="Keyword", markers=True)
        fig7.update_layout(height=420, legend=dict(orientation="h", y=-0.3, font=dict(size=10)))
        st.plotly_chart(fig7, use_container_width=True)

    st.subheader("Top Cited Papers")
    top_n = st.slider("Top N per field", 1, 10, 3)
    rows = []
    for field, grp in df_f.groupby("field"):
        rows.append(grp.nlargest(top_n, "citations")[["field","year","title","citations"]])
    top_df = pd.concat(rows).reset_index(drop=True)
    top_df.columns = ["Field", "Year", "Title", "Citations"]
    st.dataframe(top_df, use_container_width=True, height=300)

    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.info("**Only Growing Field**\nRenewable Energy +1.41 papers/year. All others declining.")
    c2.warning("**Highest Citation Impact**\nRenewable Energy 59.21 avg citations — nearly 3× Climate Science.")
    c3.error("**Fastest Declining**\nNeuroscience & Bioinformatics both −0.68/year.")

    st.caption("Standalone: Academic Publication Mining | Christian / Shamil | Semester 4 Team Project")
