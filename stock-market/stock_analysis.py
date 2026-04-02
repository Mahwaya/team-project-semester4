"""
SHAMIL: Stock Market Data Mining
Companies: AAPL (Apple), TSLA (Tesla), AMZN (Amazon)
Period:    2025-03-01 to 2026-03-27

Tasks covered:
  1. Collect 12 months of historical stock price data
  2. Clean and structure the dataset
  3. Perform volatility analysis (monthly + weekly std dev, top 3 volatile periods per company)
  4. Calculate 7-day and 30-day moving averages
"""

import yfinance as yf
import pandas as pd

# ── Configuration ─────────────────────────────────────────────────────────────
TICKERS    = ["AAPL", "TSLA", "AMZN"]
START_DATE = "2025-03-01"
END_DATE   = "2026-03-28"   # end is exclusive in yfinance

# ── Phase 1: Collect raw data ─────────────────────────────────────────────────
print("=" * 60)
print("Phase 1: Collecting 12 months of stock data...")
print("=" * 60)

raw = yf.download(TICKERS, start=START_DATE, end=END_DATE, auto_adjust=True, progress=False)

# Keep only Close and Volume
close  = raw["Close"].copy()
volume = raw["Volume"].copy()

# Reshape to long format: columns -> date, ticker, close, volume
close_long  = close.stack(future_stack=True).rename("close").reset_index()
volume_long = volume.stack(future_stack=True).rename("volume").reset_index()
close_long.columns  = ["date", "ticker", "close"]
volume_long.columns = ["date", "ticker", "volume"]

df_raw = pd.merge(close_long, volume_long, on=["date", "ticker"])
df_raw["date"] = pd.to_datetime(df_raw["date"]).dt.tz_localize(None)
df_raw = df_raw.sort_values(["ticker", "date"]).reset_index(drop=True)

df_raw.to_csv(
    r"c:\Users\shami\Documents\team project semester 4\stock_data_raw.csv",
    index=False
)
print(f"  Rows collected: {len(df_raw)}")
print(f"  Date range:     {df_raw['date'].min().date()} -> {df_raw['date'].max().date()}")
print(f"  Tickers:        {sorted(df_raw['ticker'].unique())}")
print(f"  Saved -> stock_data_raw.csv\n")

# ── Phase 2: Clean and structure the dataset ───────────────────────────────────
print("=" * 60)
print("Phase 2: Cleaning and structuring the dataset...")
print("=" * 60)

# Build one complete date range per ticker and forward-fill gaps
all_dates  = pd.date_range(start=START_DATE, end="2026-03-27", freq="B")  # business days
tickers_df = pd.DataFrame({"ticker": TICKERS})
date_df    = pd.DataFrame({"date": all_dates})
full_index = tickers_df.merge(date_df, how="cross")

df_clean = full_index.merge(df_raw, on=["date", "ticker"], how="left")
df_clean = df_clean.sort_values(["ticker", "date"]).reset_index(drop=True)

# Forward-fill close and volume within each ticker
df_clean["close"]  = df_clean.groupby("ticker")["close"].ffill()
df_clean["volume"] = df_clean.groupby("ticker")["volume"].ffill().fillna(0).astype(int)

# Drop rows still missing close (e.g. before first trading day)
df_clean = df_clean.dropna(subset=["close"])

# Daily return (pct change per ticker)
df_clean["daily_return"] = (
    df_clean.groupby("ticker")["close"]
    .pct_change()
    .round(6)
)

# Set date as index
df_clean = df_clean.set_index("date")

df_clean.to_csv(
    r"c:\Users\shami\Documents\team project semester 4\stock_data_clean.csv"
)

missing = df_clean["close"].isna().sum()
print(f"  Rows after cleaning: {len(df_clean)}")
print(f"  Missing close values: {missing}")
print(f"  Columns: {list(df_clean.columns)}")
print(f"  Saved -> stock_data_clean.csv\n")

# ── Phase 3: Volatility analysis ──────────────────────────────────────────────
print("=" * 60)
print("Phase 3: Performing volatility analysis...")
print("=" * 60)

df_vol = df_clean.reset_index().copy()
df_vol["year_month"] = df_vol["date"].dt.to_period("M").astype(str)

monthly_vol = (
    df_vol.groupby(["ticker", "year_month"])["daily_return"]
    .std()
    .rename("volatility")
    .reset_index()
)
monthly_vol["volatility"] = monthly_vol["volatility"].round(6)

# Top 3 highest volatility months per company
top3 = (
    monthly_vol.sort_values("volatility", ascending=False)
    .groupby("ticker")
    .head(3)
    .sort_values(["ticker", "volatility"], ascending=[True, False])
    .reset_index(drop=True)
)

monthly_vol.to_csv(
    r"c:\Users\shami\Documents\team project semester 4\volatility_analysis.csv",
    index=False
)

print("  Monthly volatility (std dev of daily returns):")
print(f"  Rows: {len(monthly_vol)}")
print()
print("  Top 3 highest volatility months per company:")
for ticker, group in top3.groupby("ticker"):
    print(f"    {ticker}:")
    for _, row in group.iterrows():
        print(f"      {row['year_month']}  volatility={row['volatility']:.6f}")
print(f"\n  Saved -> volatility_analysis.csv\n")

# ── Weekly volatility (matches Percival's year_week format e.g. 2025-W13) ─────
df_vol["year_week"] = df_vol["date"].dt.strftime("%G-W%V")

weekly_vol = (
    df_vol.groupby(["ticker", "year_week"])["daily_return"]
    .std()
    .rename("volatility")
    .reset_index()
)
weekly_vol["volatility"] = weekly_vol["volatility"].round(6)

# Top 3 highest volatility weeks per company
top3_weeks = (
    weekly_vol.sort_values("volatility", ascending=False)
    .groupby("ticker")
    .head(3)
    .sort_values(["ticker", "volatility"], ascending=[True, False])
    .reset_index(drop=True)
)

weekly_vol.to_csv(
    r"c:\Users\shami\Documents\team project semester 4\weekly_volatility.csv",
    index=False
)

print("  Weekly volatility (std dev of daily returns):")
print(f"  Rows: {len(weekly_vol)}")
print()
print("  Top 3 highest volatility weeks per company:")
for ticker, group in top3_weeks.groupby("ticker"):
    print(f"    {ticker}:")
    for _, row in group.iterrows():
        print(f"      {row['year_week']}  volatility={row['volatility']:.6f}")
print(f"\n  Saved -> weekly_volatility.csv\n")

# ── Phase 4: Moving averages ───────────────────────────────────────────────────
print("=" * 60)
print("Phase 4: Calculating 7-day and 30-day moving averages...")
print("=" * 60)

df_final = df_clean.copy()

df_final["MA7"]  = (
    df_final.groupby("ticker")["close"]
    .transform(lambda x: x.rolling(window=7,  min_periods=1).mean())
    .round(4)
)
df_final["MA30"] = (
    df_final.groupby("ticker")["close"]
    .transform(lambda x: x.rolling(window=30, min_periods=1).mean())
    .round(4)
)

df_final.to_csv(
    r"c:\Users\shami\Documents\team project semester 4\stock_data_final.csv"
)

print(f"  Columns: {list(df_final.columns)}")
print(f"  Rows: {len(df_final)}")
print(f"  Saved -> stock_data_final.csv\n")

# ── Summary ───────────────────────────────────────────────────────────────────
print("=" * 60)
print("DONE. Output files:")
print("  stock_data_raw.csv       - Raw daily close + volume")
print("  stock_data_clean.csv     - Cleaned, with daily_return")
print("  volatility_analysis.csv  - Monthly volatility (std dev)")
print("  weekly_volatility.csv    - Weekly volatility (std dev, matches Percival year_week)")
print("  stock_data_final.csv     - Clean + MA7 + MA30")
print("=" * 60)
