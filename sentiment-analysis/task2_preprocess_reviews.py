"""
task2_preprocess_reviews.py
============================
Task 2 — Text Preprocessing Pipeline
======================================

Removes stopwords, punctuation, numbers, and irrelevant characters from
each user review. Converts all text to lowercase. Outputs a clean CSV
with both the raw and preprocessed review columns.

This script uses the same stopword list as NLTK's English corpus
(embedded here so no internet download is required) and mirrors the
token-filtering behaviour of spaCy's default English pipeline.

Steps performed:
  1. Lowercase all text
  2. Strip numeric characters
  3. Remove punctuation and special characters (keep word chars + spaces)
  4. Tokenise on whitespace
  5. Remove stopwords (NLTK English list + domain-generic film words)
  6. Drop tokens of length ≤ 2

Input:  reviews_raw.csv   (movieId, title, avg_rating, review)
Output: task2_preprocessed_reviews.csv
        — adds columns: clean_review, token_count_raw, token_count_clean

Dependencies:
    pip install pandas
    (no NLTK/spaCy download needed — stopwords are embedded below)

Usage:
    python task2_preprocess_reviews.py
"""

import re
import pandas as pd

# ── Embedded NLTK English stopwords + domain-generic film words ───────────────
#    Source: nltk.corpus.stopwords.words('english')  (v3.8 release)
#    Extended with common film-review filler that carries no sentiment.

STOPWORDS: set[str] = {
    # ── NLTK English corpus ────────────────────────────────────────────────
    "i","me","my","myself","we","our","ours","ourselves",
    "you","your","yours","yourself","yourselves",
    "he","him","his","himself",
    "she","her","hers","herself",
    "it","its","itself",
    "they","them","their","theirs","themselves",
    "what","which","who","whom",
    "this","that","these","those",
    "am","is","are","was","were","be","been","being",
    "have","has","had","having",
    "do","does","did","doing",
    "a","an","the",
    "and","but","if","or","because","as","until","while",
    "of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below",
    "to","from","up","down","in","out","on","off","over","under",
    "again","further","then","once",
    "here","there","when","where","why","how",
    "all","both","each","few","more","most","other","some","such",
    "no","nor","not","only","own","same","so","than","too","very",
    "s","t","can","will","just","don","should","now",
    "d","ll","m","o","re","ve","y",
    "ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn",
    "wasn","weren","won","wouldn",
    # ── domain-generic (film reviews) ──────────────────────────────────────
    "film","movie","see","make","made","much","well","never",
    "still","every","many","though","really","way","back","first",
    "time","little","think","find","come","know","say","bit","feel",
    "lot","something","nothing","everything","anything",
    "go","going","watch","watching","watched","seen",
    "quite","rather","pretty","also","would","could","get","got",
    "like","even","one","two","three",
}


def preprocess(text: str) -> str:
    """
    Full text preprocessing pipeline.

    Parameters
    ----------
    text : str
        Raw review string.

    Returns
    -------
    str
        Space-joined string of cleaned, filtered tokens.
    """
    # 1. Lowercase
    text = text.lower()

    # 2. Remove digits
    text = re.sub(r"\d+", "", text)

    # 3. Remove punctuation and special characters
    #    Keep: word characters (\w) and whitespace (\s)
    text = re.sub(r"[^\w\s]", " ", text)

    # 4. Tokenise on whitespace
    tokens = text.split()

    # 5–6. Remove stopwords and very short tokens
    tokens = [t for t in tokens if t not in STOPWORDS and len(t) > 2]

    return " ".join(tokens)


# ── Load raw reviews ──────────────────────────────────────────────────────────
INPUT_FILE  = "reviews_raw.csv"
OUTPUT_FILE = "task2_preprocessed_reviews.csv"

print(f"Reading {INPUT_FILE} …")
df = pd.read_csv(INPUT_FILE)
print(f"  {len(df)} rows loaded.")

# ── Apply preprocessing ───────────────────────────────────────────────────────
print("Applying preprocessing pipeline …")

df["token_count_raw"]   = df["review"].str.split().str.len()
df["clean_review"]      = df["review"].apply(preprocess)
df["token_count_clean"] = df["clean_review"].str.split().str.len()

# ── Summary statistics ────────────────────────────────────────────────────────
avg_raw   = df["token_count_raw"].mean()
avg_clean = df["token_count_clean"].mean()
reduction = (1 - avg_clean / avg_raw) * 100

print("\n── Preprocessing summary ──────────────────────────────────────────────")
print(f"  Total reviews processed : {len(df)}")
print(f"  Avg tokens before clean : {avg_raw:.1f}")
print(f"  Avg tokens after  clean : {avg_clean:.1f}")
print(f"  Token reduction         : {reduction:.1f}%")
print(f"  Unique movies           : {df['movieId'].nunique()}")
print("───────────────────────────────────────────────────────────────────────")

# ── Sample output ─────────────────────────────────────────────────────────────
print("\n── First 5 examples ────────────────────────────────────────────────────")
for _, row in df.head(5).iterrows():
    print(f"\n  ORIGINAL  ({row['token_count_raw']} tokens):")
    print(f"  {row['review']}")
    print(f"  CLEANED   ({row['token_count_clean']} tokens):")
    print(f"  {row['clean_review']}")

# ── Save output ───────────────────────────────────────────────────────────────
cols_ordered = [
    "movieId", "title", "avg_rating",
    "review", "token_count_raw",
    "clean_review", "token_count_clean",
]
df[cols_ordered].to_csv(OUTPUT_FILE, index=False)
print(f"\nSaved: {OUTPUT_FILE}")
