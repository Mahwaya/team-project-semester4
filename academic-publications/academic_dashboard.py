import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
from collections import Counter
import re

st.set_page_config(page_title="Academic Publication Trends", layout="wide", page_icon="📚")

# ── Load Data ──────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    import os
    base = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base, "clean_publications.csv"))
    return df

df = load_data()

STOP_WORDS = {
    "a","an","the","of","in","and","for","to","with","on","at","by","from",
    "is","are","was","be","as","its","this","that","using","based","study",
    "analysis","approach","novel","new","towards","via","into","between",
    "within","across","over","under","their","these","through","such","has",
    "have","been","than","also","both","during","after","when","where"
}

def extract_keywords(titles, top_n=20):
    words = []
    for t in titles:
        if isinstance(t, str):
            words += [w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t)
                      if w.lower() not in STOP_WORDS]
    return Counter(words).most_common(top_n)

# ── Sidebar ────────────────────────────────────────────────────────────────────
st.sidebar.title("Filters")
all_fields = sorted(df["field"].unique())
selected_fields = st.sidebar.multiselect("Fields", all_fields, default=all_fields)
year_range = st.sidebar.slider("Year Range", 2015, 2025, (2015, 2025))

df_f = df[df["field"].isin(selected_fields) &
          df["year"].between(year_range[0], year_range[1])]
pivot = (df_f.groupby(["year", "field"])["title"]
         .count().unstack().fillna(0)
         .loc[year_range[0]:year_range[1], selected_fields])

# ── Header ─────────────────────────────────────────────────────────────────────
st.title("Academic Publication Trend Analysis")
st.caption(f"CrossRef API | 3,327 clean records | 5 fields | 2015–2025 | Christian / Shamil")

# ── KPI Cards ──────────────────────────────────────────────────────────────────
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Total Papers", f"{len(df_f):,}")
c2.metric("Fields", str(len(selected_fields)))
c3.metric("Years", f"{year_range[0]}–{year_range[1]}")
c4.metric("Avg Citations", f"{df_f['citations'].mean():.1f}")
top_field = df_f.groupby("field")["title"].count().idxmax() if len(df_f) else "—"
c5.metric("Top by Volume", top_field)

st.divider()

# ── Row 1: Volume Trend + YoY Growth ──────────────────────────────────────────
col_l, col_r = st.columns(2)

with col_l:
    st.subheader("Publication Volume by Field")
    fig1 = px.line(pivot.reset_index().melt(id_vars="year"),
                   x="year", y="value", color="field", markers=True,
                   labels={"value": "Papers", "year": "Year", "field": "Field"})
    fig1.update_layout(height=370, legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig1, use_container_width=True)

with col_r:
    st.subheader("Year-over-Year Growth Rate (%)")
    growth = pivot.pct_change() * 100
    fig2 = px.line(growth.reset_index().melt(id_vars="year"),
                   x="year", y="value", color="field", markers=True,
                   labels={"value": "Growth (%)", "year": "Year", "field": "Field"})
    fig2.add_hline(y=0, line_dash="dash", line_color="gray")
    fig2.update_layout(height=370, legend=dict(orientation="h", y=-0.25))
    st.plotly_chart(fig2, use_container_width=True)

# ── Row 2: Emerging vs Declining + Citations ───────────────────────────────────
col_l2, col_r2 = st.columns(2)

with col_l2:
    st.subheader("Emerging vs Declining Fields")
    trend_rows = []
    for field in selected_fields:
        if field in pivot.columns and len(pivot[field]) > 1:
            y = pivot[field].values
            x = np.arange(len(y))
            slope, _, _, p, _ = stats.linregress(x, y)
            trend_rows.append({
                "Field": field,
                "Slope": round(slope, 2),
                "Direction": "Emerging" if slope > 0 else "Declining",
                "p-value": round(p, 3)
            })
    tdf = pd.DataFrame(trend_rows).sort_values("Slope")
    fig3 = px.bar(tdf, x="Slope", y="Field", orientation="h", color="Direction",
                  color_discrete_map={"Emerging": "#2ecc71", "Declining": "#e74c3c"},
                  text="Slope",
                  hover_data={"p-value": True})
    fig3.add_vline(x=0, line_color="black", line_width=1)
    fig3.update_layout(height=370, showlegend=True)
    st.plotly_chart(fig3, use_container_width=True)

with col_r2:
    st.subheader("Average Citations per Field")
    cit = (df_f.groupby("field")["citations"].mean()
           .round(2).reset_index()
           .sort_values("citations"))
    cit.columns = ["Field", "Avg Citations"]
    fig4 = px.bar(cit, x="Avg Citations", y="Field", orientation="h",
                  color="Avg Citations", color_continuous_scale="Blues",
                  text="Avg Citations")
    fig4.update_traces(texttemplate="%{text:.1f}", textposition="outside")
    fig4.update_layout(height=370, coloraxis_showscale=False)
    st.plotly_chart(fig4, use_container_width=True)

# ── Row 3: Heatmap ─────────────────────────────────────────────────────────────
st.subheader("Publication Volume Heatmap")
fig5 = px.imshow(pivot.T, text_auto=True, aspect="auto",
                 color_continuous_scale="YlOrRd",
                 labels=dict(x="Year", y="Field", color="Papers"))
fig5.update_layout(height=280)
st.plotly_chart(fig5, use_container_width=True)

# ── Row 4: 3-Year Moving Average ───────────────────────────────────────────────
st.subheader("3-Year Moving Average (Smoothed Trends)")
ma = pivot.rolling(window=3, center=True).mean()
fig6 = px.line(ma.reset_index().melt(id_vars="year"),
               x="year", y="value", color="field",
               labels={"value": "Papers (smoothed)", "year": "Year", "field": "Field"})
fig6.update_traces(line=dict(width=2.5))
fig6.update_layout(height=340, legend=dict(orientation="h", y=-0.25))
st.plotly_chart(fig6, use_container_width=True)

st.divider()

# ── Row 5: Keyword Analysis ────────────────────────────────────────────────────
st.subheader("Keyword Frequency Analysis")

col_ka, col_kb = st.columns(2)

with col_ka:
    st.markdown("**Top 15 Keywords — 2015 vs 2025**")
    kw_2015 = extract_keywords(df_f[df_f["year"] == 2015]["title"], 15)
    kw_2025 = extract_keywords(df_f[df_f["year"] == 2025]["title"], 15)

    kw_df = pd.DataFrame({
        "Keyword": [w for w, _ in kw_2015],
        "2015": [c for _, c in kw_2015]
    }).merge(
        pd.DataFrame({"Keyword": [w for w, _ in kw_2025],
                      "2025": [c for _, c in kw_2025]}),
        on="Keyword", how="outer"
    ).fillna(0).sort_values("2015", ascending=False)

    fig7 = go.Figure()
    fig7.add_trace(go.Bar(name="2015", y=kw_df["Keyword"], x=kw_df["2015"],
                          orientation="h", marker_color="#3498db"))
    fig7.add_trace(go.Bar(name="2025", y=kw_df["Keyword"], x=kw_df["2025"],
                          orientation="h", marker_color="#e67e22"))
    fig7.update_layout(barmode="group", height=420,
                       xaxis_title="Frequency",
                       legend=dict(orientation="h", y=1.08),
                       margin=dict(l=130))
    st.plotly_chart(fig7, use_container_width=True)

with col_kb:
    st.markdown("**Keyword Trend Over Time**")
    sel_field = st.selectbox("Filter by field for keyword trend",
                             ["All Fields"] + all_fields)
    src = df_f if sel_field == "All Fields" else df_f[df_f["field"] == sel_field]

    top_words = [w for w, _ in extract_keywords(src["title"], 8)]
    kw_trend = {}
    for year in sorted(src["year"].unique()):
        counts = Counter()
        for t in src[src["year"] == year]["title"]:
            if isinstance(t, str):
                counts.update([w.lower() for w in re.findall(r'\b[a-zA-Z]{4,}\b', t)
                               if w.lower() not in STOP_WORDS])
        total = sum(counts.values()) or 1
        kw_trend[year] = {w: round(counts[w] / total * 100, 2) for w in top_words}

    kw_trend_df = pd.DataFrame(kw_trend).T.reset_index()
    kw_trend_df.columns = ["year"] + top_words
    kw_melt = kw_trend_df.melt(id_vars="year", var_name="Keyword", value_name="Frequency (%)")

    fig8 = px.line(kw_melt, x="year", y="Frequency (%)", color="Keyword", markers=True,
                   labels={"year": "Year"})
    fig8.update_layout(height=420, legend=dict(orientation="h", y=-0.3, font=dict(size=10)))
    st.plotly_chart(fig8, use_container_width=True)

# ── Row 6: Top Cited Papers ────────────────────────────────────────────────────
st.subheader("Top Cited Papers per Field")
top_n = st.slider("Show top N papers per field", 1, 10, 3)
rows = []
for field, group in df_f.groupby("field"):
    rows.append(group.nlargest(top_n, "citations")[["field", "year", "title", "citations"]])
top_df = pd.concat(rows).reset_index(drop=True)
top_df.columns = ["Field", "Year", "Title", "Citations"]
st.dataframe(top_df, use_container_width=True, height=320)

# ── Key Findings ───────────────────────────────────────────────────────────────
st.divider()
st.subheader("Key Findings")
col_f1, col_f2, col_f3 = st.columns(3)
col_f1.info("**Only Growing Field**\nRenewable Energy is the only field with a positive publication trend (+1.41 papers/year), driven by global energy policy and investment.")
col_f2.warning("**Highest Impact**\nRenewable Energy leads citation impact at 59.21 avg citations/paper — nearly 3× Climate Science (23.52) and the rest.")
col_f3.error("**Declining Fields**\nNeuroscience and Bioinformatics are declining fastest (−0.68/year each). Bioinformatics crashed sharply 2018–2020, likely displaced by COVID-related research.")

st.divider()
st.caption("Standalone Task: Academic Publication Mining System | Christian / Shamil | Semester 4 Team Project")
