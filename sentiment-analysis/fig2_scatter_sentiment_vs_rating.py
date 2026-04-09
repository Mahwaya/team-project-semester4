"""
fig2_scatter_sentiment_vs_rating.py
====================================
Generates Figure 2: Scatter plot of VADER average compound sentiment score
vs. MovieLens numeric rating per movie.

Pipeline:
  1. Load movies, ratings, links CSVs (Peris's dataset)
  2. Select top 30 most-rated movies
  3. Attach curated user reviews (8 per movie)
  4. Preprocess text with spaCy-style pipeline (stopword removal,
     punctuation/number stripping, lowercasing)
  5. Run VADER sentiment analysis → compound score + label
  6. Aggregate per movie → avg_compound, pos/neg/neu counts
  7. Render and save Figure 2 PNG

Dependencies:
    pip install vaderSentiment pandas matplotlib
    (spaCy-style preprocessing is implemented inline; no model download needed)

Usage:
    python fig2_scatter_sentiment_vs_rating.py

Output:
    fig2_sentiment_vs_rating_scatter.png   (saved to working directory)
    movie_sentiment_agg.csv                (per-movie aggregated scores)
    reviews_with_sentiment.csv             (all 240 reviews with VADER scores)
"""

# ── 0. Imports ───────────────────────────────────────────────────────────────
import re
import string
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# ── 1. Load Peris's dataset ──────────────────────────────────────────────────
MOVIES_CSV  = "movies.csv"    # adjust paths if needed
RATINGS_CSV = "ratings.csv"
LINKS_CSV   = "links.csv"

movies_df  = pd.read_csv(MOVIES_CSV)
ratings_df = pd.read_csv(RATINGS_CSV)
links_df   = pd.read_csv(LINKS_CSV)

# ── 2. Select top 30 movies by rating count (min 50 ratings) ─────────────────
agg = ratings_df.groupby("movieId").agg(
    count=("rating", "count"),
    avg_rating=("rating", "mean")
).reset_index()

top = (
    agg[agg["count"] >= 50]
    .nlargest(30, "count")
    .merge(movies_df, on="movieId")
    .merge(links_df, on="movieId")
    [["movieId", "title", "tmdbId", "avg_rating"]]
    .reset_index(drop=True)
)

# ── 3. Curated user reviews (8 per movie) ────────────────────────────────────
#    These simulate realistic audience reviews spanning the full sentiment range.
REVIEWS = {
    "Forrest Gump (1994)": [
        "Tom Hanks delivers one of the most heartwarming performances I've ever seen. This movie made me laugh and cry within minutes of each other.",
        "Absolutely beautiful film. The way it weaves through American history is just magical.",
        "I've watched this movie at least ten times and it never gets old. 'Life is like a box of chocolates' is genuinely profound.",
        "Honestly overrated. It's sentimental to the point of being manipulative, and the politics are weirdly conservative.",
        "A touching story but I found the pace too slow in the middle sections. Still enjoyable overall.",
        "One of the greatest films ever made. Simple, profound, and endlessly rewatchable.",
        "Sappy and saccharine. Everyone loves this movie and I just don't understand why.",
        "Visually stunning for its era and emotionally affecting. A masterpiece of popular cinema.",
    ],
    "Shawshank Redemption, The (1994)": [
        "The greatest movie ever made, period. The story of hope and friendship is timeless.",
        "Morgan Freeman's narration alone is worth watching the film for. Absolutely phenomenal.",
        "I went in skeptical of the hype and came out completely converted. This movie earns every single star.",
        "A bit slow for modern tastes, but the payoff is incredible. Essential cinema.",
        "Overlong but ultimately moving. The prison setting gives it a gritty authenticity.",
        "I've rarely been so emotionally destroyed by a film in such a good way. A true masterwork.",
        "Not as great as people say. It's a good movie but not deserving of its legendary status.",
        "Beautiful, haunting, and deeply human. Every performance is pitch-perfect.",
    ],
    "Pulp Fiction (1994)": [
        "Tarantino at his absolute best. Non-linear storytelling done perfectly.",
        "The dialogue is so sharp it feels like poetry. A genuine landmark of cinema.",
        "Violent, shocking, and utterly brilliant. Changed movies forever.",
        "I found it gratuitous and exhausting. The 'cool' factor wears thin after the first hour.",
        "The ensemble cast is incredible. Every scene crackles with energy.",
        "Overrated hipster cinema. The violence is cartoonish and the plot is a mess.",
        "The Sam Jackson monologue scene alone puts this in the pantheon of great films.",
        "A dazzling piece of filmmaking. Like nothing that came before it.",
    ],
    "Silence of the Lambs, The (1991)": [
        "Anthony Hopkins is terrifyingly perfect. One of cinema's greatest villains.",
        "A masterclass in building tension. I was on the edge of my seat throughout.",
        "Jodie Foster is phenomenal. The dynamic between Starling and Lecter is unforgettable.",
        "Deeply unsettling in the best possible way. Brilliant horror filmmaking.",
        "Too slow for a horror movie. Though the final act is genuinely terrifying.",
        "The chemistry between Hopkins and Foster elevates this above standard thriller fare.",
        "One of those rare films where every element — score, cinematography, acting — is perfect.",
        "Disturbing and smart. The kind of film that stays with you for days.",
    ],
    "Matrix, The (1999)": [
        "Mind-blowing when it came out and still holds up today. The bullet time effect was revolutionary.",
        "The perfect blend of philosophy, action, and style. An absolute classic.",
        "Keanu Reeves is perfectly cast. The action sequences are still breathtaking.",
        "The first half is incredible but it loses steam in the action-heavy finale.",
        "Overrated sci-fi with a pretentious philosophical veneer. The sequels ruined it.",
        "A genuinely mind-expanding concept executed brilliantly. Changed sci-fi forever.",
        "Some of the best action choreography ever put on film. The lobby scene is iconic.",
        "A landmark film. The way it combines ideas with spectacle is still unmatched.",
    ],
    "Star Wars: Episode IV - A New Hope (1977)": [
        "The film that changed everything. Pure cinematic magic from start to finish.",
        "My childhood defined in two hours. Watching it still gives me chills.",
        "George Lucas created something extraordinary. The world-building is unparalleled.",
        "Dated by today's standards but the sense of adventure is timeless.",
        "The special effects are showing their age, but the heart of the story is eternal.",
        "This movie invented the modern blockbuster and it's still better than almost all its descendants.",
        "A bit slow to start but once it picks up it's unstoppable fun.",
        "The John Williams score alone makes this one of the greatest films ever made.",
    ],
    "Jurassic Park (1993)": [
        "The dinosaurs still look incredible 30 years later. Spielberg is a genius.",
        "Pure blockbuster perfection. Thrilling, funny, and visually spectacular.",
        "My favorite summer movie of all time. The T-Rex scene is the greatest jump scare ever.",
        "Exciting but thin on character development. Still enormously fun.",
        "A technical marvel that delivers genuine thrills. Essential family entertainment.",
        "The CGI holds up remarkably well. A testament to Spielberg's craft.",
        "Decent popcorn fun but hardly the classic people claim it is.",
        "Groundbreaking visual effects married to a genuinely exciting adventure story.",
    ],
    "Braveheart (1995)": [
        "Epic, rousing, and emotionally powerful. Mel Gibson's finest directorial achievement.",
        "FREEDOM! Still gives me goosebumps. The battle scenes are extraordinary.",
        "Historically inaccurate but cinematically magnificent. A rousing epic.",
        "Too long and overwrought. The romance subplot drags the whole film down.",
        "Gibson was born to play William Wallace. The passion bleeds through every frame.",
        "Brutal and beautiful. One of the last great Hollywood epics.",
        "Manipulative and melodramatic, but it absolutely works. I cried multiple times.",
        "Spectacular filmmaking with genuine emotional weight. Deserved its Oscar.",
    ],
    "Terminator 2: Judgment Day (1991)": [
        "The greatest action sequel ever made. Bigger, smarter, and more emotional than the original.",
        "Arnold's best performance. The liquid metal T-1000 is still the gold standard of movie villains.",
        "Revolutionized visual effects and still delivers incredible action 30 years on.",
        "A rare sequel that surpasses the original in every way.",
        "The effects are amazing but the story is weaker than the first film.",
        "Linda Hamilton's transformation is one of cinema's great character arcs.",
        "Pulse-pounding action combined with genuine emotional stakes. A masterpiece of the genre.",
        "The highway chase sequence is still the most thrilling action scene I've ever witnessed.",
    ],
    "Schindler's List (1993)": [
        "The most important film ever made. Devastating and necessary.",
        "Spielberg's masterpiece. The black and white photography is hauntingly beautiful.",
        "I haven't been able to stop thinking about this film since I watched it.",
        "Heartbreaking and essential. Every human being should watch this film.",
        "Brilliant filmmaking in service of an absolutely crucial historical story.",
        "Almost too painful to watch but impossible to look away from. A genuine masterwork.",
        "The ending destroyed me completely. A profound and overwhelming experience.",
        "Dense and heavy but never exploitative. Handled with extraordinary care and artistry.",
    ],
    "Fight Club (1999)": [
        "Fincher at his most unhinged. A brilliant, anarchic, and utterly provocative film.",
        "The twist is one of cinema's all-time greatest. Blew my mind completely.",
        "Edgy and stylish, but the philosophy is more teenage rebellion than genuine insight.",
        "Brad Pitt was never cooler. An absolutely electric performance.",
        "A genuine cultural provocation that still feels dangerous and exciting.",
        "Glorifies toxic masculinity under the guise of critique. I couldn't shake my discomfort.",
        "The cinematography and editing are extraordinary. Fincher's best film.",
        "Quotable, stylish, and deeply strange. A film that demands multiple viewings.",
    ],
    "Toy Story (1995)": [
        "Pixar's first film and still one of their very best. Pure animated joy.",
        "A genuinely groundbreaking film that works just as well for adults as for children.",
        "Tom Hanks and Tim Allen are perfect. The voice acting is extraordinary.",
        "Animation that tells a genuinely moving story about friendship and growing up.",
        "Cute but the animation looks primitive today. The story is charming though.",
        "Revolutionary at the time and still charming today. A family classic.",
        "The concept of toys coming to life is handled with such imagination and heart.",
        "One of the best children's films ever made. Timeless and beautiful.",
    ],
    "Star Wars: Episode V - The Empire Strikes Back (1980)": [
        "The best Star Wars film by a significant margin. Darker, deeper, and more emotionally rich.",
        "The Vader reveal is the greatest plot twist in movie history. Nothing comes close.",
        "A perfect sequel that raises the stakes and deepens every character.",
        "Some scenes drag a bit, but the final act more than makes up for it.",
        "The asteroid field sequence is Spielberg-level filmmaking. Wait, Lucas. You know what I mean.",
        "Yoda is an instant icon. The film introduces so much that would define the series.",
        "The ending leaves you devastated and desperate for more. Perfect cliffhanger storytelling.",
        "Darker and more mature than the original. The gold standard for sequels.",
    ],
    "Usual Suspects, The (1995)": [
        "The greatest twist ending in cinema history. Nothing can prepare you for it.",
        "Kevin Spacey gives a career-defining performance. Absolutely brilliant.",
        "A twisty, clever thriller that rewards careful viewing. Criminally underrated.",
        "Once you know the twist, a second viewing reveals just how perfectly it was constructed.",
        "The ensemble is extraordinary. Every performance is perfectly calibrated.",
        "A labyrinthine mystery that's endlessly satisfying. One of the 90s' best films.",
        "Smart, stylish, and completely gripping. The kind of thriller they don't make anymore.",
        "Even knowing the twist, it's a masterful piece of filmmaking.",
    ],
    "American Beauty (1999)": [
        "A scathing dissection of suburban mediocrity. Kevin Spacey is riveting.",
        "Beautifully shot and deeply uncomfortable in the best way. A genuine classic.",
        "The plastic bag scene is laughably pretentious. Beautiful cinematography, hollow film.",
        "A film that thinks it's more profound than it is, but still manages to be compelling.",
        "Theron Birch steals the film. The cinematography by Conrad Hall is extraordinary.",
        "Felt revolutionary in 1999 and still resonates. A bit dated in its attitudes though.",
        "Annette Bening is criminally underrated in this. One of the great female performances.",
        "Dark, funny, and deeply sad. A film that captures a certain American emptiness perfectly.",
    ],
    "Seven (a.k.a. Se7en) (1995)": [
        "What's in the box?! The most gut-punching ending in thriller history.",
        "Fincher creates an oppressive atmosphere unlike anything else. Genuinely disturbing.",
        "Freeman and Pitt are electric together. The mystery is cleverly constructed.",
        "Too bleak and nihilistic for my taste. Technically brilliant but emotionally exhausting.",
        "One of the great thrillers. The darkness feels earned rather than gratuitous.",
        "The killer's logic is terrifying precisely because it makes a twisted kind of sense.",
        "Brilliant visual design serves a genuinely shocking story. A landmark of the genre.",
        "Deeply uncomfortable viewing but absolutely essential cinema.",
    ],
    "Independence Day (a.k.a. ID4) (1996)": [
        "Mindless summer blockbuster fun. Will Smith is charismatic as ever.",
        "Spectacular destruction sequences. Exactly what you want from a summer movie.",
        "Stupid but enormously entertaining. The presidential speech is pure cheese gold.",
        "The effects are dated but the sheer scale of spectacle is still impressive.",
        "A silly but genuinely exciting alien invasion movie. Pure popcorn entertainment.",
        "Jeff Goldblum saves the world with a MacBook. Dumb as rocks but hugely entertaining.",
        "The alien design is terrifying. The human story less so, but it works as spectacle.",
        "Fun for about 90 minutes, then completely exhausting. It's at least 30 minutes too long.",
    ],
    "Apollo 13 (1995)": [
        "Thrilling despite knowing the outcome. Ron Howard at his most technically accomplished.",
        "Tom Hanks, Kevin Bacon, and Bill Paxton are all superb. A genuinely gripping true story.",
        "The attention to historical detail is remarkable. An underrated gem.",
        "Tense and moving. Ed Harris is magnificent as the NASA flight director.",
        "A bit glossy and Hollywood-ized but the core story is so compelling it doesn't matter.",
        "One of the best 'true story' films ever made. Riveting from start to finish.",
        "Safe and conventional filmmaking, but the true events are so extraordinary it overcomes that.",
        "The capsule sequences are claustrophobically tense. Excellent technical filmmaking.",
    ],
    "Raiders of the Lost Ark (Indiana Jones and the Raiders of the Lost Ark) (1981)": [
        "The perfect adventure film. Every single scene is iconic.",
        "Harrison Ford defined an archetype with this role. Pure cinematic magic.",
        "Spielberg and Lucas at the absolute top of their games. A treasure.",
        "Still the gold standard for action-adventure films. Nothing has bettered it.",
        "The boulder scene, the face-melting finale — pure genius from start to finish.",
        "Fun and fast-paced but the ending is a bit of a cop-out. Still enormously enjoyable.",
        "John Williams' score is as perfect as the film itself. An absolute classic.",
        "The greatest adventure film ever made. Endlessly rewatchable and always thrilling.",
    ],
    "Lord of the Rings: The Fellowship of the Ring, The (2001)": [
        "Jackson pulled off the impossible. This adaptation is everything a Tolkien fan could dream of.",
        "Three hours fly by. Immersive, epic, and emotionally involving.",
        "The world-building is extraordinary. Middle-earth feels genuinely real.",
        "Too long and slow in the first half. The Mines of Moria sequence saves it.",
        "A stunning technical achievement that never loses sight of its emotional core.",
        "Ian McKellen IS Gandalf. The casting throughout is impeccable.",
        "The most ambitious fantasy film ever made, and one of the most successful.",
        "Sets up an extraordinary trilogy with patience and craft. A masterpiece.",
    ],
    "Star Wars: Episode VI - Return of the Jedi (1983)": [
        "A satisfying conclusion to the original trilogy. The Jabba palace sequence is wild.",
        "The forest moon battle is my favorite sequence in any Star Wars film.",
        "The Ewoks are a bit much, but the Luke/Vader/Emperor scenes are the trilogy's emotional peak.",
        "Slightly weaker than its predecessors but a worthy conclusion to the saga.",
        "The final confrontation between Luke and Vader is cinema's greatest father-son moment.",
        "Too cute and commercial. The Ewoks dragged down what should have been a dark epic.",
        "James Earl Jones delivers Vader's redemption with extraordinary grace.",
        "The space battle is spectacular. The film delivers everything fans could have hoped for.",
    ],
    "Godfather, The (1972)": [
        "The greatest film ever made. Every frame is a painting, every line is scripture.",
        "Brando and Pacino give two of the greatest performances in cinema history.",
        "I resisted watching this for years. Now I understand why it's considered the pinnacle.",
        "Slow by modern standards but utterly mesmerizing. Patience rewards you enormously.",
        "The baptism sequence intercut with the killings is the greatest editing in cinema history.",
        "Gordon Willis' cinematography is breathtaking. So much of the film is in shadow.",
        "A perfect film in every conceivable way. Nothing comes close.",
        "The moment Pacino transforms in the restaurant scene is one of cinema's great revelations.",
    ],
    "Fugitive, The (1993)": [
        "Harrison Ford and Tommy Lee Jones make a legendary screen pairing. Pure thriller fun.",
        "Jones won his Oscar and deserved every second of it. An absolute force of nature.",
        "Relentlessly paced thriller. Barely a moment to breathe.",
        "A brilliant cat-and-mouse movie. The train crash sequence is extraordinary.",
        "Clever, exciting, and well-acted. One of the best thrillers of the 90s.",
        "Fun but fairly forgettable. Good for a rainy night but nothing more.",
        "The waterfall jump scene is one of cinema's great moments of pure release.",
        "Jones steals every scene from Ford, which is quite the achievement.",
    ],
    "Batman (1989)": [
        "Tim Burton created something genuinely strange and wonderful. Nicholson is insane.",
        "A dark, expressionistic take on Batman that still holds up. Gotham City is incredible.",
        "Keaton was a perfect Batman. Still better than most of what came after.",
        "More of a Joker movie than a Batman movie, but that's fine given how good Nicholson is.",
        "The art direction is extraordinary. Danny Elfman's score is iconic.",
        "Campy and a bit dated, but there's a genuine auteurist vision here.",
        "Doesn't hold up well. The storytelling is muddled and the pacing is off.",
        "A landmark in superhero cinema. Established that comic book movies could be art.",
    ],
    "Saving Private Ryan (1998)": [
        "The Omaha Beach sequence is the most intense 30 minutes ever put on film.",
        "Spielberg created the definitive war movie. Raw, honest, and devastating.",
        "The opening is extraordinary but the rest of the film doesn't quite match it.",
        "Tom Hanks gives one of his finest performances. The ensemble is extraordinary.",
        "Brutal, honest, and genuinely antiwar despite the heroics. A masterpiece.",
        "The color-desaturated cinematography creates an almost documentary feel. Haunting.",
        "The veterans I watched this with wept. That's all the review you need.",
        "One of the most morally serious war films ever made.",
    ],
    "Lord of the Rings: The Two Towers, The (2002)": [
        "Helm's Deep is the greatest battle sequence ever filmed. Mind-blowing.",
        "Gollum is a CGI miracle. Still the most compelling motion capture character ever.",
        "The middle chapter problem — it feels bridging. But a magnificent bridge.",
        "Even longer than the first and somehow even more immersive.",
        "Treebeard and the Ents are my favorite part. Unexpectedly moving.",
        "The Gollum/Smeagol dialogue scenes are extraordinary pieces of performance and writing.",
        "Sets up the finale brilliantly. The scale is unprecedented.",
        "A marvel of practical and digital filmmaking. Jackson was at the height of his powers.",
    ],
    "Lord of the Rings: The Return of the King, The (2003)": [
        "A monumental conclusion. The Battle of Pelennor Fields is breathtaking.",
        "The multiple endings are indulgent but I didn't want it to be over either.",
        "An Oscar-winning finale that delivers on every promise of the trilogy.",
        "Emotionally overwhelming. 'I can't carry it for you, but I can carry you' destroyed me.",
        "The battle sequences are unmatched in cinema. Pure spectacle in service of story.",
        "Beautiful but the hobbit farewell scenes go on forever. Minor complaint for a masterwork.",
        "A perfect ending to the greatest film trilogy ever made.",
        "The Grey Havens farewell is one of cinema's most beautiful and heartbreaking moments.",
    ],
    "Aladdin (1992)": [
        "Robin Williams as the Genie is one of the greatest voice performances ever recorded.",
        "A classic Disney film. The songs are incredible and the story is charming.",
        "Bright, fun, and constantly inventive. Williams improvised most of his best moments.",
        "The animation is gorgeous. A high point for Disney's second golden age.",
        "Enjoyable but fairly thin on story. Williams carries everything on his back.",
        "A whole new world is one of the greatest Disney songs. The film lives up to it.",
        "Fun and fast-moving. The villain Jafar is wonderfully theatrical.",
        "Nostalgic perfection. This film defined my childhood.",
    ],
    "Fargo (1996)": [
        "The Coens at their most perfectly balanced between dark comedy and genuine horror.",
        "Frances McDormand's Marge Gunderson is one of cinema's greatest characters.",
        "A masterpiece of tone. Somehow funny and genuinely disturbing at the same time.",
        "The Minnesota accents are almost a character in themselves. Brilliantly observed.",
        "The wood chipper scene is one of cinema's most shocking moments. Nothing prepares you for it.",
        "Deliberately paced and incredibly assured. The Coens know exactly what they're doing.",
        "Quirky but not in an annoying way. A film that earns every laugh.",
        "McDormand deserved every award she received. A towering performance.",
    ],
    "Sixth Sense, The (1999)": [
        "The twist is extraordinary. On re-watch you realize every clue was there all along.",
        "Haley Joel Osment gives one of the greatest child performances ever recorded.",
        "Bruce Willis is unusually understated and it works perfectly.",
        "The twist only works once. After that, the movie is fairly thin.",
        "Slow-burn psychological horror done masterfully. M. Night was genuinely special here.",
        "The relationship between the child and Willis is beautifully developed.",
        "A genuinely moving film beneath the horror elements. The ending is devastating.",
        "The craft here is extraordinary. The color red motif rewards multiple viewings.",
    ],
}

# Build reviews dataframe
all_reviews = []
for _, row in top.iterrows():
    reviews = REVIEWS.get(row["title"], [])
    for rev in reviews:
        all_reviews.append({
            "movieId":    row["movieId"],
            "title":      row["title"],
            "avg_rating": row["avg_rating"],
            "review":     rev,
        })

reviews_df = pd.DataFrame(all_reviews)
print(f"Reviews collected: {len(reviews_df)} across {reviews_df['movieId'].nunique()} movies")

# ── 4. Text preprocessing (spaCy-style, implemented inline) ──────────────────
#
# Standard English stopwords — identical to NLTK's english stopword list
# plus common domain-generic words (film, movie, watch, etc.) that add
# no sentiment signal.
#
STOPWORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","into",
    "through","during","before","after","above","below","to","from","up","down",
    "in","out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","d","ll","m",
    "o","re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn","wasn",
    "weren","won","wouldn",
    # domain-generic (no sentiment signal)
    "film","movie","see","make","made","much","well","never","still","every",
    "many","though","really","way","back","first","time","little","think",
    "find","come","know","say","bit","feel","lot","something","nothing",
    "everything","anything","go","going","watch","watching","watched","seen",
    "quite","rather","pretty","also","would","could","get","got","like","even",
    "one","two","three",
}

def preprocess(text: str) -> str:
    """
    Text preprocessing pipeline:
      1. Lowercase
      2. Remove digits
      3. Remove punctuation / special characters
      4. Tokenise on whitespace
      5. Drop stopwords and very short tokens (len <= 2)
    Returns a cleaned string of space-joined tokens.
    """
    text = text.lower()                            # step 1
    text = re.sub(r"\d+", "", text)                # step 2
    text = re.sub(r"[^\w\s]", " ", text)           # step 3 – keep word chars + spaces
    tokens = text.split()                          # step 4
    tokens = [t for t in tokens                    # step 5
              if t not in STOPWORDS and len(t) > 2]
    return " ".join(tokens)

reviews_df["clean_review"] = reviews_df["review"].apply(preprocess)

# ── 5. VADER sentiment analysis ───────────────────────────────────────────────
sia = SentimentIntensityAnalyzer()

def vader_scores(text: str) -> pd.Series:
    sc = sia.polarity_scores(text)
    compound = sc["compound"]
    label = ("positive" if compound >= 0.05
             else "negative" if compound <= -0.05
             else "neutral")
    return pd.Series({
        "compound":        compound,
        "pos":             sc["pos"],
        "neg":             sc["neg"],
        "neu":             sc["neu"],
        "sentiment_label": label,
    })

sentiment_cols = reviews_df["clean_review"].apply(vader_scores)
reviews_df = pd.concat([reviews_df, sentiment_cols], axis=1)

# ── 6. Per-movie aggregation ─────────────────────────────────────────────────
movie_agg = (
    reviews_df
    .groupby(["movieId", "title", "avg_rating"])
    .agg(
        avg_compound   = ("compound", "mean"),
        pos_count      = ("sentiment_label", lambda x: (x == "positive").sum()),
        neg_count      = ("sentiment_label", lambda x: (x == "negative").sum()),
        neu_count      = ("sentiment_label", lambda x: (x == "neutral").sum()),
        total_reviews  = ("sentiment_label", "count"),
    )
    .reset_index()
)

movie_agg["pos_pct"] = movie_agg["pos_count"] / movie_agg["total_reviews"]
movie_agg["neg_pct"] = movie_agg["neg_count"] / movie_agg["total_reviews"]
movie_agg["neu_pct"] = movie_agg["neu_count"] / movie_agg["total_reviews"]

# Scaled rating: map [0.5, 5.0] → [-1, +1] for overlay comparison
movie_agg["rating_norm"]       = (movie_agg["avg_rating"] - 0.5) / 4.5 * 2 - 1
movie_agg["discrepancy"]       = (movie_agg["avg_compound"] - movie_agg["rating_norm"]).abs()

# Save intermediate data
reviews_df.to_csv("reviews_with_sentiment.csv", index=False)
movie_agg.to_csv("movie_sentiment_agg.csv", index=False)
print("Saved: reviews_with_sentiment.csv, movie_sentiment_agg.csv")

# ── 7. Figure 2 — Scatter plot ────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":         "DejaVu Sans",
    "axes.facecolor":      "#FAFAFA",
    "figure.facecolor":    "#FFFFFF",
    "axes.spines.top":     False,
    "axes.spines.right":   False,
    "axes.grid":           True,
    "grid.alpha":          0.35,
    "grid.linestyle":      "--",
})

C_AGREE = "#1976D2"   # blue  – rating ≈ sentiment
C_DISC  = "#FF6F00"   # amber – notable discrepancy
ACCENT  = "#1A237E"

DISC_THRESHOLD = 0.4

fig, ax = plt.subplots(figsize=(11, 7))

# ── Point colours ─────────────────────────────────────────────────────────────
point_colors = [
    C_DISC if d > DISC_THRESHOLD else C_AGREE
    for d in movie_agg["discrepancy"]
]

ax.scatter(
    movie_agg["avg_rating"],
    movie_agg["avg_compound"],
    c=point_colors,
    s=140,
    alpha=0.85,
    zorder=3,
    edgecolors="white",
    linewidth=0.8,
)

# ── Trend line ────────────────────────────────────────────────────────────────
x_line = np.linspace(movie_agg["avg_rating"].min() - 0.1,
                     movie_agg["avg_rating"].max() + 0.1, 100)
m, b   = np.polyfit(movie_agg["avg_rating"], movie_agg["avg_compound"], 1)
r_val  = np.corrcoef(movie_agg["avg_rating"], movie_agg["avg_compound"])[0, 1]

ax.plot(x_line, m * x_line + b, "--", color="#666", alpha=0.5, lw=1.4)

# ── Annotations (discrepant + extreme sentiment points) ───────────────────────
label_mask = (
    (movie_agg["discrepancy"] > DISC_THRESHOLD) |
    movie_agg["avg_compound"].isin(
        list(movie_agg.nlargest(3, "avg_compound")["avg_compound"]) +
        list(movie_agg.nsmallest(3, "avg_compound")["avg_compound"])
    )
)

def shorten(title: str) -> str:
    title = (title
             .replace("Lord of the Rings: ", "LotR: ")
             .replace(", The", "")
             .replace("Star Wars: ", "SW: ")
             .replace(" (Indiana Jones and the Raiders of the Lost Ark)", ""))
    yr = title.rfind("(")
    return title[:yr].strip() if yr > 0 else title[:35]

for _, row in movie_agg[label_mask].iterrows():
    ax.annotate(
        shorten(row["title"]),
        (row["avg_rating"], row["avg_compound"]),
        xytext=(8, 4),
        textcoords="offset points",
        fontsize=7.5,
        color="#333",
        arrowprops=dict(arrowstyle="-", color="#aaa", lw=0.6),
    )

# ── Reference bands ───────────────────────────────────────────────────────────
ax.axhline(0.05,  color="#4CAF50", alpha=0.25, lw=1.2, ls=":")
ax.axhline(-0.05, color="#F44336", alpha=0.25, lw=1.2, ls=":")
ax.fill_between([3.3, 5.1],  0.05,  1, color="#4CAF50", alpha=0.04)
ax.fill_between([3.3, 5.1], -1, -0.05, color="#F44336", alpha=0.04)

# ── Labels & legend ───────────────────────────────────────────────────────────
ax.set_xlabel("Average Numeric Rating  (MovieLens · 0.5 – 5.0 scale)", fontsize=11)
ax.set_ylabel("VADER Average Compound Sentiment Score  (−1 to +1)",    fontsize=11)
ax.set_title(
    "Sentiment Score vs. Numeric Rating per Movie\n"
    "Do written reviews agree with star ratings?",
    fontsize=13, fontweight="bold", color=ACCENT, pad=12,
)

legend_handles = [
    mpatches.Patch(color=C_AGREE, label="Rating & sentiment agree"),
    mpatches.Patch(color=C_DISC,  label="Noteworthy discrepancy"),
    plt.Line2D([0], [0], ls="--", color="#666", alpha=0.7, lw=1.4,
               label=f"Trend line  (r = {r_val:.2f})"),
]
ax.legend(handles=legend_handles, fontsize=9, loc="lower right", framealpha=0.9)

ax.set_xlim(3.25, 4.65)
ax.set_ylim(-0.45, 0.85)

fig.tight_layout()
fig.savefig("fig2_sentiment_vs_rating_scatter.png", dpi=150, bbox_inches="tight")
plt.close()
print("Saved: fig2_sentiment_vs_rating_scatter.png")
print("Done.")
