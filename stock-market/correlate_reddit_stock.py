"""
Correlate stock data with Percival's Reddit findings
Join keys: year_week + ticker
Output:    correlation_dataset.csv

Steps:
  1. Aggregate stock_data_final.csv to weekly level (weekly close change, avg volume, avg daily return)
  2. Merge with weekly_volatility.csv (weekly std dev)
  3. Merge with reddit_weekly_sentiment.csv (Percival's Reddit data)
  4. Add lag columns: next-week price change to detect if Reddit activity preceded moves
  5. Flag high-Reddit-activity weeks
  6. Spotlight Percival's flagged week: AMZN 2025-W17
"""

import pandas as pd

BASE = r"c:\Users\shami\Documents\team project semester 4"

# ── Load data ──────────────────────────────────────────────────────────────────
print("=" * 60)
print("Loading data...")
print("=" * 60)

stock_daily  = pd.read_csv(f"{BASE}\\stock_data_final.csv", parse_dates=["date"])
weekly_vol   = pd.read_csv(f"{BASE}\\weekly_volatility.csv")
reddit       = pd.read_csv(f"{BASE}\\reddit_weekly_sentiment.csv")

print(f"  stock_data_final rows : {len(stock_daily)}")
print(f"  weekly_volatility rows: {len(weekly_vol)}")
print(f"  reddit_weekly_sentiment rows: {len(reddit)}\n")

# ── Step 1: Aggregate stock to weekly level ────────────────────────────────────
print("=" * 60)
print("Step 1: Aggregating stock data to weekly level...")
print("=" * 60)

stock_daily["year_week"] = stock_daily["date"].dt.strftime("%G-W%V")

# Per week per ticker: first close, last close, avg volume, avg daily_return
weekly_stock = (
    stock_daily.groupby(["ticker", "year_week"])
    .agg(
        week_open_close  = ("close",        "first"),
        week_close       = ("close",        "last"),
        avg_volume       = ("volume",       "mean"),
        avg_daily_return = ("daily_return", "mean"),
        trading_days     = ("close",        "count"),
    )
    .reset_index()
)

weekly_stock["weekly_price_change_pct"] = (
    (weekly_stock["week_close"] - weekly_stock["week_open_close"])
    / weekly_stock["week_open_close"]
    * 100
).round(4)

weekly_stock["avg_volume"]        = weekly_stock["avg_volume"].round(0).astype(int)
weekly_stock["avg_daily_return"]  = weekly_stock["avg_daily_return"].round(6)
weekly_stock["week_open_close"]   = weekly_stock["week_open_close"].round(4)
weekly_stock["week_close"]        = weekly_stock["week_close"].round(4)

print(f"  Weekly stock rows: {len(weekly_stock)}\n")

# ── Step 2: Merge stock weekly + volatility ────────────────────────────────────
print("=" * 60)
print("Step 2: Merging stock weekly data with weekly volatility...")
print("=" * 60)

df = weekly_stock.merge(weekly_vol, on=["ticker", "year_week"], how="left")
df.rename(columns={"volatility": "weekly_volatility"}, inplace=True)
print(f"  Rows after merge: {len(df)}\n")

# ── Step 3: Merge with Reddit sentiment ───────────────────────────────────────
print("=" * 60)
print("Step 3: Merging with Reddit sentiment data...")
print("=" * 60)

reddit_slim = reddit[[
    "ticker", "year_week", "post_count", "avg_score",
    "avg_upvote_ratio", "avg_comments", "avg_sentiment",
    "positive_posts", "negative_posts", "neutral_posts"
]].copy()

df = df.merge(reddit_slim, on=["ticker", "year_week"], how="left")

reddit_weeks_matched = df["post_count"].notna().sum()
print(f"  Rows with Reddit data matched: {reddit_weeks_matched} / {len(df)}\n")

# ── Step 4: Next-week price change (did stock move the FOLLOWING week?) ────────
print("=" * 60)
print("Step 4: Calculating next-week price change (lag)...")
print("=" * 60)

df = df.sort_values(["ticker", "year_week"]).reset_index(drop=True)

df["next_week_price_change_pct"] = (
    df.groupby("ticker")["weekly_price_change_pct"]
    .shift(-1)
    .round(4)
)

print(f"  Lag column added.\n")

# ── Step 5: Flag high Reddit activity weeks ────────────────────────────────────
print("=" * 60)
print("Step 5: Flagging high Reddit activity weeks...")
print("=" * 60)

# High activity = avg_score in top 25% of all weeks that have Reddit data
reddit_rows = df[df["avg_score"].notna()]
score_threshold = reddit_rows["avg_score"].quantile(0.75)
print(f"  High-activity threshold (75th pct of avg_score): {score_threshold:.0f}")

df["high_reddit_activity"] = (df["avg_score"] >= score_threshold).fillna(False)

high_activity_weeks = df[df["high_reddit_activity"]][["ticker", "year_week", "avg_score", "weekly_price_change_pct", "next_week_price_change_pct"]]
print(f"  High-activity weeks flagged: {len(high_activity_weeks)}")
print()
print(high_activity_weeks.to_string(index=False))
print()

# ── Step 6: Spotlight AMZN 2025-W17 ───────────────────────────────────────────
print("=" * 60)
print("Step 6: Spotlight — AMZN 2025-W17 (flagged by Percival)")
print("=" * 60)

spotlight = df[(df["ticker"] == "AMZN") & (df["year_week"] == "2025-W17")]
if not spotlight.empty:
    row = spotlight.iloc[0]
    print(f"  Week:                    {row['year_week']}")
    print(f"  Reddit avg_score:        {row['avg_score']}")
    print(f"  Reddit avg_sentiment:    {row['avg_sentiment']}")
    print(f"  Reddit post_count:       {row['post_count']}")
    print(f"  AMZN open price (Mon):   {row['week_open_close']}")
    print(f"  AMZN close price (Fri):  {row['week_close']}")
    print(f"  Weekly price change:     {row['weekly_price_change_pct']}%")
    print(f"  Next-week price change:  {row['next_week_price_change_pct']}%")
    print(f"  Weekly volatility:       {row['weekly_volatility']}")
    print(f"  High Reddit activity:    {row['high_reddit_activity']}")
else:
    print("  AMZN 2025-W17 not found in merged dataset (no stock data for that week).")
print()

# ── Save final output ──────────────────────────────────────────────────────────
print("=" * 60)
print("Saving correlation_dataset.csv...")
print("=" * 60)

col_order = [
    "ticker", "year_week",
    "week_open_close", "week_close", "weekly_price_change_pct",
    "next_week_price_change_pct", "avg_volume", "avg_daily_return",
    "weekly_volatility", "trading_days",
    "post_count", "avg_score", "avg_upvote_ratio", "avg_comments",
    "avg_sentiment", "positive_posts", "negative_posts", "neutral_posts",
    "high_reddit_activity"
]
df = df[col_order]

df.to_csv(f"{BASE}\\correlation_dataset.csv", index=False)
print(f"  Rows: {len(df)}")
print(f"  Columns: {list(df.columns)}")
print(f"  Saved -> correlation_dataset.csv\n")
print("=" * 60)
print("DONE. Share correlation_dataset.csv with Percival.")
print("=" * 60)
