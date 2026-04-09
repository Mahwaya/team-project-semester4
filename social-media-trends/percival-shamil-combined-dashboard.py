"""
Combined Dashboard — Stock Market + Reddit Sentiment
Shamil (stock) + Percival (Reddit) integration
Run with: streamlit run dashboard.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Market & Reddit Sentiment Dashboard",
    page_icon="📈",
    layout="wide"
)

BASE = r"C:\Users\Percival Mahwaya\Desktop\MSc DS\Sem 4\SIPDiDS Team Project\stock-market"

# ── Load data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    stock_daily  = pd.read_csv(f"{BASE}\\stock_data_final.csv", parse_dates=["date"])
    corr_df      = pd.read_csv(f"{BASE}\\correlation_dataset.csv")
    weekly_vol   = pd.read_csv(f"{BASE}\\weekly_volatility.csv")
    return stock_daily, corr_df, weekly_vol

stock_daily, corr_df, weekly_vol = load_data()

TICKER_NAMES = {"AAPL": "Apple", "TSLA": "Tesla", "AMZN": "Amazon"}
COLORS       = {"AAPL": "#1f77b4", "TSLA": "#d62728", "AMZN": "#ff7f0e"}

# ── Sidebar controls ───────────────────────────────────────────────────────────
st.sidebar.title("🔧 Controls")

selected_tickers = st.sidebar.multiselect(
    "Select Companies",
    options=["AAPL", "TSLA", "AMZN"],
    default=["AAPL", "TSLA", "AMZN"],
    format_func=lambda x: f"{TICKER_NAMES[x]} ({x})"
)

show_ma7  = st.sidebar.checkbox("Show 7-day MA",  value=True)
show_ma30 = st.sidebar.checkbox("Show 30-day MA", value=True)

st.sidebar.markdown("---")
st.sidebar.markdown("**Data sources**")
st.sidebar.markdown("📊 Stock: Shamil via yfinance")
st.sidebar.markdown("💬 Reddit: Percival via PRAW")
st.sidebar.markdown("📅 Period: Mar 2025 – Mar 2026")

# ── Title ─────────────────────────────────────────────────────────────────────
st.title("📈 Stock Market & Reddit Sentiment Dashboard")
st.markdown("*AAPL · TSLA · AMZN — March 2025 to March 2026*")
st.markdown("---")

if not selected_tickers:
    st.warning("Please select at least one company from the sidebar.")
    st.stop()

# ── KPI summary row ────────────────────────────────────────────────────────────
st.subheader("📌 Key Metrics")
kpi_cols = st.columns(len(selected_tickers))

for col, ticker in zip(kpi_cols, selected_tickers):
    data     = stock_daily[stock_daily["ticker"] == ticker].sort_values("date")
    first_c  = data["close"].iloc[0]
    last_c   = data["close"].iloc[-1]
    change   = ((last_c - first_c) / first_c) * 100

    reddit_data  = corr_df[(corr_df["ticker"] == ticker) & corr_df["avg_score"].notna()]
    high_weeks   = reddit_data["high_reddit_activity"].sum() if not reddit_data.empty else 0
    max_score    = reddit_data["avg_score"].max() if not reddit_data.empty else 0

    col.metric(f"{TICKER_NAMES[ticker]} ({ticker})", f"${last_c:.2f}", f"{change:+.1f}% (12mo)")
    col.caption(f"High Reddit weeks: {int(high_weeks)} | Peak score: {int(max_score):,}")

st.markdown("---")

# ── Section 1: Price + MA + Reddit sentiment volume ────────────────────────────
st.subheader("📊 Stock Price Trends with Reddit Sentiment Volume")
st.caption("Top: daily close + moving averages. Bottom: Reddit average score per week (bars). Weeks with high Reddit activity are marked.")

for ticker in selected_tickers:
    s_data = stock_daily[stock_daily["ticker"] == ticker].sort_values("date")
    r_data = corr_df[(corr_df["ticker"] == ticker) & corr_df["avg_score"].notna()].sort_values("year_week")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=False,
        row_heights=[0.65, 0.35],
        vertical_spacing=0.08,
        subplot_titles=(
            f"{TICKER_NAMES[ticker]} ({ticker}) — Daily Close Price",
            "Reddit Average Score per Week"
        )
    )

    # Close price
    fig.add_trace(go.Scatter(
        x=s_data["date"], y=s_data["close"],
        name="Close", line=dict(color=COLORS[ticker], width=1.5),
        hovertemplate="%{x|%b %d, %Y}<br>Close: $%{y:.2f}<extra></extra>"
    ), row=1, col=1)

    # MA7
    if show_ma7:
        fig.add_trace(go.Scatter(
            x=s_data["date"], y=s_data["MA7"],
            name="MA7", line=dict(color="black", width=1, dash="dash"),
            hovertemplate="%{x|%b %d}<br>MA7: $%{y:.2f}<extra></extra>"
        ), row=1, col=1)

    # MA30
    if show_ma30:
        fig.add_trace(go.Scatter(
            x=s_data["date"], y=s_data["MA30"],
            name="MA30", line=dict(color="gold", width=2),
            hovertemplate="%{x|%b %d}<br>MA30: $%{y:.2f}<extra></extra>"
        ), row=1, col=1)

    # Reddit score bars
    bar_colors = [
        "#e74c3c" if row["high_reddit_activity"] else COLORS[ticker]
        for _, row in r_data.iterrows()
    ]
    fig.add_trace(go.Bar(
        x=r_data["year_week"], y=r_data["avg_score"],
        name="Reddit Avg Score",
        marker_color=bar_colors,
        hovertemplate=(
            "%{x}<br>Reddit Score: %{y:,.0f}"
            "<br>Sentiment: %{customdata[0]:.3f}"
            "<br>High Activity: %{customdata[1]}<extra></extra>"
        ),
        customdata=r_data[["avg_sentiment", "high_reddit_activity"]].values
    ), row=2, col=1)

    # Highlight high-activity weeks on price chart
    high_weeks = r_data[r_data["high_reddit_activity"] == True]
    for _, hw in high_weeks.iterrows():
        fig.add_vrect(
            x0=hw["year_week"], x1=hw["year_week"],
            row=1, col=1,
            annotation_text="🔴", annotation_position="top left",
            fillcolor="red", opacity=0.08, line_width=0
        )

    fig.update_layout(
        height=520,
        showlegend=True,
        legend=dict(orientation="h", y=1.02, x=0),
        margin=dict(t=60, b=20),
        hovermode="x unified"
    )
    fig.update_yaxes(title_text="Price (USD)", tickprefix="$", row=1, col=1)
    fig.update_yaxes(title_text="Avg Reddit Score", row=2, col=1)

    st.plotly_chart(fig, width='stretch')

st.markdown("---")

# ── Section 2: Weekly volatility + Reddit activity side by side ────────────────
st.subheader("📉 Weekly Volatility vs Reddit Activity")
st.caption("Compare the volatility of stock returns with Reddit engagement for the same week.")

vol_cols = st.columns(len(selected_tickers))
for col, ticker in zip(vol_cols, selected_tickers):
    v_data = weekly_vol[weekly_vol["ticker"] == ticker].sort_values("year_week")
    r_data = corr_df[(corr_df["ticker"] == ticker) & corr_df["avg_score"].notna()].sort_values("year_week")

    merged = v_data.merge(r_data[["year_week", "avg_score", "avg_sentiment"]], on="year_week", how="left")

    fig = make_subplots(specs=[[{"secondary_y": True}]])
    fig.add_trace(go.Bar(
        x=merged["year_week"], y=merged["volatility"],
        name="Weekly Volatility", marker_color=COLORS[ticker], opacity=0.6,
        hovertemplate="%{x}<br>Volatility: %{y:.4f}<extra></extra>"
    ), secondary_y=False)
    fig.add_trace(go.Scatter(
        x=merged["year_week"], y=merged["avg_score"],
        name="Reddit Score", line=dict(color="black", width=2), mode="lines+markers",
        hovertemplate="%{x}<br>Reddit Score: %{y:,.0f}<extra></extra>"
    ), secondary_y=True)

    fig.update_layout(
        title=f"{TICKER_NAMES[ticker]} ({ticker})",
        height=320, showlegend=True,
        legend=dict(orientation="h", y=1.1),
        margin=dict(t=50, b=20)
    )
    fig.update_yaxes(title_text="Volatility (std dev)", secondary_y=False)
    fig.update_yaxes(title_text="Reddit Avg Score", secondary_y=True)
    col.plotly_chart(fig, width='stretch')

st.markdown("---")

# ── Section 3: Correlation heatmap ────────────────────────────────────────────
st.subheader("🔗 Reddit vs Stock — Correlation Heatmap")
st.caption("Pearson correlation between Reddit features and stock metrics (weeks with Reddit data only).")

from scipy import stats

sentiment_features = [
    "post_count", "avg_score", "avg_upvote_ratio",
    "avg_comments", "avg_sentiment"
]
stock_metrics = [
    "weekly_price_change_pct", "next_week_price_change_pct",
    "weekly_volatility", "avg_daily_return"
]

reddit_only = corr_df[corr_df["avg_score"].notna()][sentiment_features + stock_metrics].copy()

pearson_vals = {}
for sf in sentiment_features:
    for sm in stock_metrics:
        valid = reddit_only[[sf, sm]].dropna()
        if len(valid) > 4:
            r, _ = stats.pearsonr(valid[sf], valid[sm])
            pearson_vals[(sf, sm)] = round(r, 3)

heatmap_df = pd.DataFrame(index=sentiment_features, columns=stock_metrics, dtype=float)
for (sf, sm), v in pearson_vals.items():
    heatmap_df.loc[sf, sm] = v

fig_heat = px.imshow(
    heatmap_df.astype(float),
    color_continuous_scale="RdYlGn",
    zmin=-1, zmax=1,
    text_auto=".3f",
    labels=dict(x="Stock Metrics", y="Reddit Features", color="Pearson r"),
    title="Pearson Correlation — Reddit Sentiment vs. Stock Metrics"
)
fig_heat.update_layout(height=380, margin=dict(t=50, b=20))
st.plotly_chart(fig_heat, width='stretch')

st.markdown("---")

# ── Section 4: AMZN 2025-W17 Spotlight ────────────────────────────────────────
st.subheader("🔍 Spotlight: AMZN 2025-W17")
st.caption("Week flagged by Percival — extreme Reddit engagement spike (avg score 43,237).")

spotlight = corr_df[(corr_df["ticker"] == "AMZN") & (corr_df["year_week"] == "2025-W17")]
if not spotlight.empty:
    row = spotlight.iloc[0]
    s1, s2, s3, s4 = st.columns(4)
    s1.metric("Reddit Avg Score",    f"{int(row['avg_score']):,}")
    s2.metric("Reddit Sentiment",    f"{row['avg_sentiment']:.3f}", delta="Negative" if row['avg_sentiment'] < 0 else "Positive")
    s3.metric("AMZN Weekly Return",  f"{row['weekly_price_change_pct']:+.2f}%")
    s4.metric("Next-Week Return",    f"{row['next_week_price_change_pct']:+.2f}%")

    st.info(
        "Despite **negative** Reddit sentiment (-0.40), AMZN stock rose **+12.95%** that week. "
        "This suggests the Reddit post was reacting to a price event, not predicting one. "
        "Next-week return was only +1.21%, confirming no sustained follow-through."
    )
else:
    st.warning("AMZN 2025-W17 not found — check correlation_dataset.csv.")

st.markdown("---")
st.caption("Dashboard built by Percival Mahwaya | Data: yfinance (stock) + PRAW/Percival (Reddit) | March 2025 – March 2026")
