import html
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics.pairwise import linear_kernel

from feature_engineering import build_tfidf_matrix


st.set_page_config(
    page_title="CineSuggest | Movie Discovery",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp {
  background: radial-gradient(ellipse at 12% 0%, rgba(116,70,255,.14), transparent 30%),
    radial-gradient(ellipse at 88% 18%, rgba(20,184,166,.08), transparent 26%),
    linear-gradient(180deg, #090a0f 0%, #0b0c13 55%, #090a0f 100%);
  color: #f5f3ff;
}
.block-container { max-width: 1420px; padding-top: 1.2rem; padding-bottom: 4rem; }
#MainMenu, footer, [data-testid="stSidebar"], [data-testid="stHeader"] { visibility: hidden; height: 0; }
h1,h2,h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -.035em; }
p, label, .stMarkdown { color: #d8d6e2; }
h1,h2,h3 { color: #f8f7fc; }
div[data-testid="stMetric"] {
  background: linear-gradient(145deg, rgba(22,23,34,.96), rgba(14,15,23,.96));
  border: 1px solid rgba(255,255,255,.075); padding: 17px 20px; border-radius: 17px;
  box-shadow: 0 12px 36px rgba(0,0,0,.16);
}
div[data-testid="stMetricLabel"] { color: #9694a5; }
div[data-testid="stMetricValue"] { color: #fff; font-family: 'Manrope', sans-serif; }
.stButton > button, .stDownloadButton > button {
  border-radius: 11px; border: 1px solid rgba(187,164,255,.25);
  background: linear-gradient(135deg, #8b5cf6, #6d4aff);
  color: white; font-weight: 700; padding: .58rem 1rem;
  transition: transform .18s ease, filter .18s ease, box-shadow .18s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover {
  transform: translateY(-2px); filter: brightness(1.1);
  box-shadow: 0 9px 24px rgba(124,88,255,.25);
}
.stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input {
  background: #11121a !important; border-color: #2a2b38 !important; border-radius: 11px !important;
}
.stSlider [data-baseweb="slider"] { padding-top: .5rem; }
.stRadio [role="radiogroup"] { gap: .45rem; }
.stRadio [role="radiogroup"] label {
  background: #11121a; border: 1px solid #252633; border-radius: 999px;
  padding: .42rem .9rem; transition: all .18s ease;
}
.stRadio [role="radiogroup"] label:has(input:checked) {
  background: rgba(139,92,246,.18); border-color: rgba(167,139,250,.55);
}
.brandbar {
  position:sticky; top:.35rem; z-index:20;
  display:flex; align-items:center; justify-content:space-between; gap:1rem;
  padding:.65rem .8rem; border:1px solid rgba(255,255,255,.08); border-radius:18px;
  margin-bottom:1rem; background:rgba(10,11,17,.82); backdrop-filter:blur(18px);
  box-shadow:0 12px 35px rgba(0,0,0,.18);
}
.brand-lockup { display:flex; align-items:center; gap:.75rem; color:#fff; }
.brand-mark {
  display:grid; place-items:center; width:42px; height:42px; border-radius:14px;
  background:linear-gradient(145deg,#a78bfa,#6d4aff); box-shadow:0 8px 24px rgba(109,74,255,.3);
  font-size:1.3rem; transform-style:preserve-3d; animation:brand-bob 4s ease-in-out infinite;
}
.brand-name { font:800 1.1rem 'Manrope',sans-serif; letter-spacing:-.04em; }
.brand-caption { color:#8d8b9d; font-size:.72rem; letter-spacing:.14em; text-transform:uppercase; }
.brand-status {
  border:1px solid rgba(255,255,255,.09); border-radius:999px; padding:.45rem .75rem;
  color:#aaa8b6; font-size:.78rem; background:rgba(255,255,255,.025);
}
.hero {
  position:relative; overflow:hidden; min-height:300px; padding:clamp(28px,5vw,58px);
  border-radius:28px; margin:1.1rem 0 1.4rem;
  background:linear-gradient(108deg,rgba(23,22,39,.98) 0%,rgba(25,21,43,.94) 52%,rgba(29,20,49,.86) 100%);
  border:1px solid rgba(199,180,255,.16); box-shadow:0 26px 70px rgba(0,0,0,.32);
}
.hero:before {
  content:""; position:absolute; width:440px; height:440px; right:8%; top:-48%;
  border-radius:50%; background:radial-gradient(circle,rgba(139,92,246,.31),rgba(110,70,250,.04) 62%,transparent 72%);
  filter:blur(5px); animation:ambient 8s ease-in-out infinite alternate;
}
.hero:after {
  content:""; position:absolute; inset:0; pointer-events:none; opacity:.13;
  background-image:linear-gradient(rgba(255,255,255,.07) 1px,transparent 1px),linear-gradient(90deg,rgba(255,255,255,.07) 1px,transparent 1px);
  background-size:38px 38px; mask-image:linear-gradient(90deg,transparent,#000 60%,#000);
}
.hero-content { position:relative; z-index:2; max-width:56%; }
.hero-kicker { text-transform:uppercase; letter-spacing:.2em; font-size:.7rem; color:#c4b5fd; font-weight:800; }
.hero-title { font:800 clamp(2.2rem,5vw,4rem)/1.02 'Manrope',sans-serif; letter-spacing:-.065em; color:white; margin:1.1rem 0 .8rem; }
.hero-sub { color:#b9b6c7; max-width:550px; font-size:1rem; line-height:1.7; }
.hero-art {
  position:absolute; z-index:1; right:7%; top:50%; width:260px; height:310px;
  transform:translateY(-47%) perspective(900px) rotateY(-14deg) rotateZ(4deg);
  transform-style:preserve-3d; animation:art-drift 7s ease-in-out infinite;
}
.hero-art:before {
  content:""; position:absolute; inset:-16px -35px 12px -35px; border-radius:50%;
  border:1px solid rgba(196,181,253,.18); transform:rotateX(68deg) rotateZ(-16deg);
  box-shadow:0 0 0 16px rgba(196,181,253,.025),0 0 0 34px rgba(196,181,253,.018);
  animation:orbit-roll 18s linear infinite;
}
.hero-art:after {
  content:"✦"; position:absolute; z-index:4; top:2px; left:9px; color:#e9d5ff;
  font-size:1.5rem; text-shadow:0 0 18px #b99bff; animation:twinkle 2.4s ease-in-out infinite;
}
.hero-disc {
  position:absolute; width:230px; height:230px; right:5px; top:25px; border-radius:50%;
  border:1px solid rgba(221,214,254,.18);
  background:repeating-radial-gradient(circle,rgba(255,255,255,.018) 0 2px,transparent 3px 11px),radial-gradient(circle at 45% 38%,#8065e8 0,#382a69 36%,#171626 68%);
  box-shadow:0 15px 70px rgba(91,67,195,.35),inset 0 0 45px rgba(0,0,0,.45),
    0 16px 0 -5px #231d3b,0 23px 24px -8px rgba(0,0,0,.7);
  transform-style:preserve-3d; animation:record-float 5.5s ease-in-out infinite,record-spin 36s linear infinite;
}
.hero-disc:after {
  content:""; position:absolute; width:40px; height:40px; left:50%; top:50%; transform:translate(-50%,-50%);
  border-radius:50%; background:#11121a; border:7px solid rgba(210,196,255,.6); box-shadow:0 0 25px rgba(196,181,253,.45);
}
.hero-ticket {
  position:absolute; right:0; bottom:22px; width:165px; padding:15px; border-radius:15px;
  background:linear-gradient(145deg,rgba(36,32,55,.96),rgba(17,17,26,.98));
  border:1px solid rgba(255,255,255,.14); box-shadow:0 18px 40px rgba(0,0,0,.35),inset 0 1px rgba(255,255,255,.12);
  transform:translateZ(60px) rotate(5deg); color:#fff; font-weight:800; letter-spacing:.05em;
  animation:ticket-wiggle 5s ease-in-out infinite;
}
.hero-ticket span { display:block; color:#a7a2b7; font-size:.65rem; font-weight:600; letter-spacing:.15em; margin-bottom:7px; }
.section-heading { margin:2rem 0 .3rem; font:750 1.45rem 'Manrope',sans-serif; letter-spacing:-.04em; color:#f5f3ff; }
.section-copy { color:#9391a2; margin-bottom:1rem; font-size:.9rem; }
.hero { color:#f7f5ff; }
@keyframes card-arrive { from { opacity:0; translate:0 20px; } to { opacity:1; translate:0 0; } }
@keyframes record-float { 0%,100% { translate:0 0; } 50% { translate:0 -11px; } }
@keyframes record-spin { from { rotate:0deg; } to { rotate:360deg; } }
@keyframes orbit-roll { from { rotate:0deg; } to { rotate:360deg; } }
@keyframes art-drift { 0%,100% { translate:0 0; } 50% { translate:0 -8px; } }
@keyframes ticket-wiggle { 0%,100% { rotate:5deg; } 50% { rotate:1deg; } }
@keyframes brand-bob { 0%,100% { transform:translateY(0) rotateX(0); } 50% { transform:translateY(-3px) rotateX(12deg); } }
@keyframes twinkle { 0%,100% { opacity:.55; transform:scale(.8) rotate(0); } 50% { opacity:1; transform:scale(1.2) rotate(18deg); } }
.movie-card {
  min-height:350px; padding:11px; border-radius:19px; margin-bottom:.3rem;
  background:linear-gradient(155deg,rgba(22,23,34,.96),rgba(13,14,21,.98));
  border:1px solid rgba(255,255,255,.075); box-shadow:0 12px 28px rgba(0,0,0,.18);
  transform-style:preserve-3d; transition:transform .32s cubic-bezier(.2,.8,.2,1),border-color .24s ease,box-shadow .24s ease;
  animation:card-arrive .65s both; animation-delay:calc(var(--card-order, 0) * 45ms);
}
.movie-card:hover {
  transform:perspective(950px) rotateX(4deg) rotateY(-4deg) translateY(-9px) scale(1.015);
  border-color:rgba(167,139,250,.36); box-shadow:0 22px 44px rgba(0,0,0,.32);
}
.poster {
  position:relative; overflow:hidden; height:215px; border-radius:13px; margin-bottom:13px;
  padding:14px; display:flex; flex-direction:column; justify-content:space-between;
  background:radial-gradient(ellipse at 75% 15%,rgba(255,255,255,.21),transparent 28%),
    radial-gradient(ellipse at 20% 90%,var(--poster-b),transparent 50%),
    linear-gradient(150deg,var(--poster-a),#11121a 78%);
  box-shadow:inset 0 0 35px rgba(0,0,0,.23),0 7px 0 -2px rgba(0,0,0,.28);
  transform:translateZ(18px); transition:transform .35s ease,filter .35s ease;
}
.poster:before {
  content:""; position:absolute; width:180px; height:180px; right:-45px; top:20px; border-radius:50%;
  border:1px solid rgba(255,255,255,.2); box-shadow:0 0 0 18px rgba(255,255,255,.025),0 0 0 38px rgba(255,255,255,.018),0 0 0 58px rgba(255,255,255,.012);
  transition:transform .65s cubic-bezier(.2,.8,.2,1);
}
.poster:after {
  content:""; position:absolute; inset:-80% auto -80% -45%; width:36%;
  transform:rotate(24deg) translateX(-220%);
  background:linear-gradient(90deg,transparent,rgba(255,255,255,.2),transparent);
  transition:transform .7s ease; pointer-events:none;
}
.movie-card:hover .poster { transform:translateZ(28px) rotateX(-2deg); filter:saturate(1.2) brightness(1.08); }
.movie-card:hover .poster:before { transform:scale(1.22) rotate(28deg); }
.movie-card:hover .poster:after { transform:rotate(24deg) translateX(600%); }
.movie-card:hover .card-title { color:#d8c8ff; }
.stButton > button:active, .stDownloadButton > button:active { transform:translateY(1px) scale(.98); }
.stButton > button:focus-visible, .stDownloadButton > button:focus-visible { outline:2px solid #c4b5fd; outline-offset:3px; }
@supports (animation-timeline: view()) {
  .movie-card { animation:card-scroll-reveal linear both; animation-timeline:view(); animation-range:entry 0% entry 75%; }
}
@keyframes card-scroll-reveal {
  from { opacity:.35; translate:0 70px; }
  to { opacity:1; translate:0 0; }
}
.poster-type { z-index:1; color:rgba(255,255,255,.72); font-size:.62rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
.poster-title { z-index:1; max-width:90%; color:white; font:800 clamp(1.08rem,1.55vw,1.4rem)/1.08 'Manrope',sans-serif; letter-spacing:-.04em; text-shadow:0 2px 12px rgba(0,0,0,.45); transform:translateZ(34px); }
.poster-foot { z-index:1; display:flex; justify-content:space-between; color:rgba(255,255,255,.68); font-size:.7rem; }
.card-info { padding:0 5px 3px; }
.card-title { font:750 1rem 'Manrope',sans-serif; color:#f6f4fb; margin-bottom:5px; }
.card-meta { color:#9694a5; font-size:.78rem; min-height:1.3rem; }
.card-score { color:#c4b5fd; font-size:.76rem; font-weight:700; }
.genre-mosaic {
  padding:1rem; border:1px solid rgba(255,255,255,.07); border-radius:18px;
  background:linear-gradient(145deg,rgba(21,22,32,.9),rgba(13,14,20,.9));
}
.pill { display:inline-block; padding:4px 9px; margin: 3px 4px 2px 0; border-radius:999px; font-size:.72rem; color:#e9d5ff; background:rgba(139,92,246,.16); border:1px solid rgba(196,181,253,.17); }
.score { color:#fcd34d; font-weight:800; }
.footer { color:#827b98; text-align:center; font-size:.8rem; padding: 25px 0 5px; }
@keyframes float { 0%,100% { transform:translateY(0) rotate(-3deg); } 50% { transform:translateY(-12px) rotate(2deg); } }
@keyframes ambient { from { transform:translateY(-8px) scale(.96); opacity:.75; } to { transform:translateY(14px) scale(1.05); opacity:1; } }
@media (max-width:760px) {
  .hero { min-height:260px; padding:26px; }
  .hero-art { opacity:.28; right:-30px; transform:translateY(-45%) scale(.75) perspective(900px) rotateY(-14deg) rotateZ(4deg); }
  .hero-content { max-width:100%; }
  .movie-card { min-height:320px; }
  .poster { height:190px; }
  .brand-status { display:none; }
}
@media (prefers-reduced-motion: reduce) {
  *, *:before, *:after { scroll-behavior:auto !important; animation-duration:.01ms !important; animation-iteration-count:1 !important; transition-duration:.01ms !important; }
}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_movies():
    dataset_path = Path(__file__).with_name("movies_featured.csv")
    if not dataset_path.is_file():
        raise FileNotFoundError(
            f"Movie dataset not found: {dataset_path}. "
            "Run feature_engineering.py to generate it."
        )

    movies = pd.read_csv(dataset_path)
    required_columns = {"movieId", "title", "genres_clean", "year"}
    missing_columns = required_columns.difference(movies.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"{dataset_path.name} is missing required columns: {missing}")
    if movies.empty:
        raise ValueError(f"{dataset_path.name} contains no movie records.")
    if movies["movieId"].isna().any() or movies["movieId"].duplicated().any():
        raise ValueError(f"{dataset_path.name} must have a unique movieId for each record.")

    movies["movieId"] = pd.to_numeric(movies["movieId"], errors="raise").astype("int64")
    movies["year"] = pd.to_numeric(movies["year"], errors="coerce").astype("Int64")
    for column in ("genres_clean", "primary_genre", "decade", "era", "franchise_root"):
        if column not in movies:
            movies[column] = ""
        movies[column] = movies[column].fillna("").astype(str)
    return movies


df = load_movies()
GENRES = sorted({
    genre
    for value in df["genres_clean"]
    for genre in value.split("|")
    if genre and genre != "(no genres listed)"
})
ERAS = sorted(value for value in df["era"].unique() if value)
MIN_YEAR = int(df["year"].min())
MAX_YEAR = int(df["year"].max())
DISPLAY_COLUMNS = [
    column for column in (
        "movieId", "title", "genres_clean", "year", "decade", "era",
        "primary_genre", "franchise_root",
    )
    if column in df.columns
]
TITLE_BY_ID = df.drop_duplicates("movieId").set_index("movieId")["title"].to_dict()


def safe(value):
    return html.escape(str(value))


def filter_movies(genre="Any", era="Any", year_range=None, query=""):
    filtered = df
    if genre != "Any":
        genre_pattern = rf"(?:^|\|){re.escape(genre)}(?:\||$)"
        filtered = filtered[
            filtered["genres_clean"].str.contains(genre_pattern, regex=True, na=False)
        ]
    if era != "Any":
        filtered = filtered[filtered["era"] == era]
    if year_range is not None:
        filtered = filtered[
            filtered["year"].between(year_range[0], year_range[1]).fillna(False)
        ]
    query = query.strip()
    if query:
        searchable = (
            filtered["title"].fillna("").astype(str)
            + " "
            + filtered["genres_clean"]
            + " "
            + filtered["decade"]
            + " "
            + filtered["era"]
            + " "
            + filtered["franchise_root"]
        )
        filtered = filtered[
            searchable.str.contains(re.escape(query), case=False, na=False)
        ]
    return filtered


def recommend_movies(genre="Any", era="Any", year_range=None, query="", limit=18):
    results = filter_movies(genre, era, year_range, query).copy()
    if results.empty:
        return results

    results["match_score"] = 0
    if genre != "Any":
        results["match_score"] = (
            results["primary_genre"].eq(genre).astype(int) * 3
            + results["genres_clean"].str.count(r"\|").fillna(0).astype(int)
        )
    if "genre_rarity_score" in results:
        results["_rarity"] = pd.to_numeric(
            results["genre_rarity_score"], errors="coerce"
        ).fillna(0)
    else:
        results["_rarity"] = 0
    results = results.sort_values(
        ["match_score", "_rarity", "year", "title"],
        ascending=[False, False, False, True],
        na_position="last",
    )
    return results.head(limit).drop(columns=["_rarity"])


@st.cache_resource
def build_similarity_index(metadata):
    return build_tfidf_matrix(pd.Series(metadata), max_features=15000)


def recommend_similar_movies(movie_id, limit=8):
    movie_positions = pd.Series(df.index.to_numpy(), index=df["movieId"])
    if movie_id not in movie_positions.index:
        return df.iloc[0:0].assign(similarity_score=pd.Series(dtype=float))

    tfidf_matrix = build_similarity_index(
        tuple(df["weighted_metadata_soup"].fillna("").astype(str).tolist())
        if "weighted_metadata_soup" in df
        else tuple(
            (
                df["title"].fillna("").astype(str)
                + " "
                + df["genres_clean"]
                + " "
                + df["decade"]
                + " "
                + df["era"]
            ).tolist()
        ),
    )
    target_position = int(movie_positions.loc[movie_id])
    similarities = linear_kernel(
        tfidf_matrix[target_position], tfidf_matrix
    ).ravel()
    similarities[target_position] = -1
    candidate_count = min(limit, len(df) - 1)
    if candidate_count <= 0:
        return df.iloc[0:0].assign(similarity_score=pd.Series(dtype=float))
    candidate_positions = np.argpartition(
        similarities, -candidate_count
    )[-candidate_count:]
    candidate_positions = candidate_positions[
        np.argsort(similarities[candidate_positions])[::-1]
    ]
    results = df.iloc[candidate_positions].copy()
    results["similarity_score"] = similarities[candidate_positions]
    results["match_score"] = results["similarity_score"]
    return results


def add_to_watchlist(movie_id):
    movie_id = int(movie_id)
    if movie_id not in st.session_state.watchlist:
        st.session_state.watchlist.append(movie_id)


def poster_palette(genre):
    palettes = {
        "Action": ("#8c264b", "#ee5b5b"),
        "Adventure": ("#195b5b", "#6ec5a1"),
        "Animation": ("#57318c", "#ef83cb"),
        "Children": ("#684a16", "#f5b94c"),
        "Comedy": ("#754213", "#f1a64b"),
        "Crime": ("#29354f", "#7d9bdd"),
        "Documentary": ("#285b67", "#71cbd4"),
        "Drama": ("#543154", "#bb79bd"),
        "Fantasy": ("#3a347c", "#8f88ff"),
        "Film-Noir": ("#34343b", "#888995"),
        "Horror": ("#5c1f35", "#dd4260"),
        "Musical": ("#77345f", "#ed72bd"),
        "Mystery": ("#344362", "#769fe2"),
        "Romance": ("#783b5b", "#eb86ae"),
        "Sci-Fi": ("#174d68", "#59b9ed"),
        "Thriller": ("#3c2c5b", "#ab79ed"),
        "War": ("#4f4533", "#b5a06c"),
        "Western": ("#70452c", "#d59a5a"),
    }
    return palettes.get(genre, ("#3e3366", "#9b84ef"))


def movie_card(movie, key_prefix):
    movie_id = int(movie["movieId"])
    year = "Year unknown" if pd.isna(movie["year"]) else str(int(movie["year"]))
    genres = movie["genres_clean"].replace("|", " · ") or "No genre listed"
    genre = movie["primary_genre"] or "Cinema"
    palette_start, palette_end = poster_palette(genre)
    title = movie.get("clean_title", movie["title"])
    if "similarity_score" in movie:
        rank_label = f"{float(movie['similarity_score']):.0%} match"
    else:
        rank_label = f"Top pick · {genre}"
    st.markdown(f"""
    <div class="movie-card">
      <div class="poster" style="--poster-a:{palette_start};--poster-b:{palette_end}">
        <div class="poster-type">{safe(genre)} · CINEMA</div>
        <div class="poster-title">{safe(title)}</div>
        <div class="poster-foot"><span>{safe(year)}</span><span>#{movie_id}</span></div>
      </div>
      <div class="card-info">
        <div class="card-title">{safe(title)}</div>
        <div class="card-meta">{safe(genres)}</div>
        <div class="card-score">{safe(rank_label)}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    saved = movie_id in st.session_state.watchlist
    if st.button(
        "✓ Saved to Watchlist" if saved else "＋ Add to Watchlist",
        key=f"{key_prefix}_{movie_id}",
        use_container_width=True,
        disabled=saved,
    ):
        add_to_watchlist(movie_id)
        st.toast(f"Added {movie['title']} to your watchlist")
        st.rerun()


def show_movie_grid(movies, columns=3, prefix="grid"):
    if movies.empty:
        st.info("No movies match these filters. Try a different genre, year range, or search.")
        return
    records = movies.to_dict("records")
    for start in range(0, len(records), columns):
        row = st.columns(columns, gap="medium")
        for col, movie in zip(row, records[start:start + columns]):
            with col:
                movie_card(movie, f"{prefix}_{start}")


def hero(title, subtitle, kicker="YOUR PERSONAL MOVIE COMPANION"):
    st.markdown(f"""
    <div class="hero">
      <div class="hero-content">
        <div class="hero-kicker">{safe(kicker)}</div>
        <div class="hero-title">{title}</div>
        <div class="hero-sub">{subtitle}</div>
      </div>
      <div class="hero-art" aria-hidden="true">
        <div class="hero-disc"></div>
        <div class="hero-ticket"><span>YOUR NEXT MOVIE NIGHT</span>STARTS HERE ✦</div>
      </div>
    </div>
    """, unsafe_allow_html=True)


def discover_hero_movies(limit=18):
    """Choose recognizable titles present in the real catalogue for the film reel."""
    featured_titles = [
        "Toy Story", "Jumanji", "Heat", "GoldenEye", "Casino", "Apollo 13",
        "Braveheart", "Jurassic Park", "Forrest Gump", "Pulp Fiction",
        "The Matrix", "Star Wars", "The Godfather", "Titanic",
        "The Shawshank Redemption", "The Lion King", "Back to the Future",
        "Terminator 2: Judgment Day",
    ]
    title_keys = df["clean_title"].fillna("").str.casefold()
    unique_titles = ~title_keys.duplicated()
    by_title = df.loc[unique_titles].copy()
    by_title.index = title_keys.loc[unique_titles].to_numpy()
    selected = []
    for title in featured_titles:
        key = title.casefold()
        if key in by_title.index:
            selected.append(by_title.loc[key])
    if len(selected) < limit:
        selected_ids = {int(movie["movieId"]) for movie in selected}
        for _, movie in df.iterrows():
            movie_id = int(movie["movieId"])
            if movie_id not in selected_ids:
                selected.append(movie)
                selected_ids.add(movie_id)
            if len(selected) >= limit:
                break

    result = []
    for movie in selected[:limit]:
        year = None if pd.isna(movie["year"]) else int(movie["year"])
        poster_url = movie.get("poster_url", movie.get("posterUrl", ""))
        result.append({
            "movieId": int(movie["movieId"]),
            "title": str(movie["title"]),
            "cleanTitle": str(movie.get("clean_title", movie["title"])),
            "year": year,
            "genres": str(movie["genres_clean"]),
            "primaryGenre": str(movie.get("primary_genre", "Cinema")),
            "posterUrl": "" if pd.isna(poster_url) else str(poster_url),
        })
    return result


def show_discover_hero():
    stylesheet = Path(__file__).with_name("static").joinpath("hero.css").read_text(
        encoding="utf-8"
    )
    model_path = Path(__file__).with_name("static").joinpath("assets", "reel.glb")
    model_url = "/app/static/assets/reel.glb" if model_path.is_file() else ""
    movie_json = json.dumps(discover_hero_movies(), ensure_ascii=False).replace(
        "</", "<\\/"
    )
    st.html(f"""
    <style>{stylesheet}</style>
    <section class="cine-journey" aria-label="The Film Reel Journey" data-reel-model="{model_url}">
      <div class="cine-journey__sticky">
        <div class="cine-journey__canvas" aria-hidden="true"></div>
        <div class="cine-journey__veil" aria-hidden="true"></div>
        <div class="cine-journey__grain" aria-hidden="true"></div>
        <div class="cine-journey__copy">
          <p class="cine-journey__eyebrow">The art of finding your next film</p>
          <h1 class="cine-journey__title">
            <span class="cine-journey__title-line">Make tonight</span>
            <span class="cine-journey__title-line"><span class="cine-journey__title-accent">a little more cinematic.</span></span>
          </h1>
          <p class="cine-journey__subtitle">Explore a universe of films. Find your next favourite by genre, era, or a movie you already love.</p>
        </div>
        <div class="cine-journey__callout cine-journey__callout--one"><strong>{len(df):,}</strong><span>films to wander through</span></div>
        <div class="cine-journey__callout cine-journey__callout--two"><strong>{len(GENRES)}</strong><span>genres, endless moods</span></div>
        <div class="cine-journey__callout cine-journey__callout--three"><strong>AI-powered</strong><span>TF-IDF film matching</span></div>
        <div class="cine-journey__progress-label">Scroll to follow the reel</div>
        <div class="cine-journey__progress" aria-hidden="true"><span class="cine-journey__progress-fill"></span></div>
        <a class="cine-journey__cta" href="#discover-stats">Start Discovering <span aria-hidden="true">↓</span></a>
        <div class="cine-journey__loading" role="status" aria-live="polite">
          <span class="cine-journey__loading-copy">Preparing the projector</span>
          <span class="cine-journey__loading-track"><span class="cine-journey__loading-bar"></span></span>
        </div>
        <dialog class="cine-journey__modal" aria-labelledby="cine-detail-title">
          <button class="cine-journey__modal-close" type="button" aria-label="Close movie details">×</button>
          <div class="cine-journey__modal-content">
            <div class="cine-journey__modal-kicker">From the MovieLens collection</div>
            <h2 id="cine-detail-title" data-detail-title></h2>
            <p data-detail-meta></p>
            <a class="cine-journey__modal-cta" href="#discover-controls">Explore the catalogue ↓</a>
          </div>
        </dialog>
        <div class="cine-journey__sr-only" data-accessible-movies aria-label="Featured movies"></div>
        <script type="application/json" data-movies-json>{movie_json}</script>
      </div>
    </section>
    <script type="module" src="/app/static/heroScroll.js"></script>
    <script>
      window.setTimeout(() => {{
        document.querySelectorAll(".cine-journey").forEach((root) => {{
          if (root.isConnected && root.dataset.ready !== "true") {{
            root.classList.add("cine-journey__webgl-fallback");
            root.querySelector(".cine-journey__loading")?.classList.add("is-done");
            root.dataset.ready = "true";
          }}
        }});
      }}, 8000);
    </script>
    """, unsafe_allow_javascript=True)


defaults = {
    "watchlist": [],
    "page": "Discover",
    "catalog_page": 1,
    "similar_movie_id": None,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# Convert watchlist titles from an earlier version of the app to dataset IDs.
title_to_id = df.drop_duplicates("title").set_index("title")["movieId"].to_dict()
converted_watchlist = []
for saved_movie in st.session_state.watchlist:
    try:
        movie_id = int(saved_movie)
    except (TypeError, ValueError):
        movie_id = title_to_id.get(saved_movie)
    if movie_id in TITLE_BY_ID and movie_id not in converted_watchlist:
        converted_watchlist.append(movie_id)
st.session_state.watchlist = converted_watchlist

pages = ["Discover", "Movie Library", "My Watchlist", "AI Lab", "About"]
if st.session_state.page == "About Project":
    st.session_state.page = "About"
if st.session_state.page not in pages:
    st.session_state.page = "Discover"
st.markdown(f"""
<div class="brandbar">
  <div class="brand-lockup">
    <div class="brand-mark">✦</div>
    <div><div class="brand-name">CineSuggest</div><div class="brand-caption">Your personal cinema</div></div>
  </div>
  <div class="brand-status">◉ &nbsp; {len(df):,} films · MovieLens collection</div>
</div>
""", unsafe_allow_html=True)
st.session_state.page = st.radio(
    "Main navigation",
    pages,
    index=pages.index(st.session_state.page),
    horizontal=True,
    label_visibility="collapsed",
    key="main_navigation",
)


if st.session_state.page == "Discover":
    show_discover_hero()
    st.markdown('<div id="discover-stats"></div>', unsafe_allow_html=True)
    metric_columns = st.columns(3)
    metric_columns[0].metric("Movies in dataset", f"{len(df):,}")
    metric_columns[1].metric("Genres", len(GENRES))
    metric_columns[2].metric("Saved titles", len(st.session_state.watchlist))
    st.markdown('<div id="discover-controls"></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-heading">Explore by feeling</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Filter the collection to find something worth watching.</div>', unsafe_allow_html=True)
    genre_col, era_col = st.columns(2)
    with genre_col:
        selected_genre = st.selectbox("Genre", ["Any"] + GENRES, key="discover_genre")
    with era_col:
        selected_era = st.selectbox("Era", ["Any"] + ERAS, key="discover_era")
    discover_years = st.slider(
        "Release year",
        MIN_YEAR,
        MAX_YEAR,
        (MIN_YEAR, MAX_YEAR),
        key="discover_years",
    )
    discover_search = st.text_input(
        "Search titles, genres, era, decade, or franchise",
        placeholder="Try a movie title, a genre, or a decade...",
    )
    recommendations = recommend_movies(
        selected_genre,
        selected_era,
        discover_years,
        discover_search,
    )
    st.markdown(f'<div class="section-heading">Curated for you <span style="color:#9a8bbd;font-size:.9rem">· {len(recommendations)} films</span></div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">A thoughtful shortlist ranked from the real MovieLens catalogue.</div>', unsafe_allow_html=True)
    show_movie_grid(recommendations, 3, "discover")

    st.markdown('<div class="section-heading">Because you loved it</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-copy">Choose a film. The AI will find titles with similar metadata and genres.</div>', unsafe_allow_html=True)
    similar_query = st.text_input(
        "Search for a movie to use as a reference",
        placeholder="Type a movie title, for example Toy Story...",
        key="similar_movie_search",
    )
    if similar_query.strip():
        matching_movies = df[
            df["title"].str.contains(
                re.escape(similar_query.strip()), case=False, regex=True, na=False
            )
        ].head(100)
        if matching_movies.empty:
            st.info("No title matched that search. Try another title.")
        else:
            matching_ids = matching_movies["movieId"].astype(int).tolist()
            selected_movie_id = st.selectbox(
                "Select the reference movie",
                matching_ids,
                format_func=lambda movie_id: (
                    f"{TITLE_BY_ID[movie_id]} (ID {movie_id})"
                ),
                key="similar_movie_selection",
            )
            if st.button("Find similar movies", key="find_similar_movies"):
                st.session_state.similar_movie_id = selected_movie_id

    reference_movie_id = st.session_state.similar_movie_id
    if reference_movie_id in TITLE_BY_ID:
        st.markdown(f"#### Movies similar to {safe(TITLE_BY_ID[reference_movie_id])}")
        similar_movies = recommend_similar_movies(reference_movie_id)
        show_movie_grid(similar_movies, 3, "similar")

elif st.session_state.page == "My Watchlist":
    hero(
        "Your personal <span style='color:#f0abfc'>watchlist.</span>",
        "Saved MovieLens catalogue entries for this browser session.",
        "YOUR COLLECTION",
    )
    watchlist_movies = df[df["movieId"].isin(st.session_state.watchlist)].copy()
    if watchlist_movies.empty:
        st.info("Your watchlist is empty. Add movies from Discover or Movie Library.")
    else:
        st.write(f"**{len(watchlist_movies):,} saved movies**")
        show_movie_grid(watchlist_movies, 3, "watchlist")
        remove_id = st.selectbox(
            "Remove a movie",
            watchlist_movies["movieId"].tolist(),
            format_func=lambda movie_id: (
                f"{TITLE_BY_ID[movie_id]} (ID {movie_id})"
            ),
        )
        if st.button("Remove selected movie"):
            st.session_state.watchlist.remove(remove_id)
            st.rerun()
        if st.button("Clear watchlist"):
            st.session_state.watchlist = []
            st.rerun()

elif st.session_state.page == "Movie Library":
    hero(
        "Explore the full <span style='color:#f0abfc'>catalogue.</span>",
        "Search and filter the real MovieLens-derived dataset. Each table row is a record from movies_featured.csv.",
        "THE MOVIE LIBRARY",
    )
    genre_col, era_col = st.columns(2)
    with genre_col:
        library_genre = st.selectbox("Genre", ["Any"] + GENRES, key="library_genre")
    with era_col:
        library_era = st.selectbox("Era", ["Any"] + ERAS, key="library_era")
    year_range = st.slider(
        "Release year",
        MIN_YEAR,
        MAX_YEAR,
        (MIN_YEAR, MAX_YEAR),
        key="library_years",
    )
    library_search = st.text_input(
        "Search catalogue",
        placeholder="Movie title, genre, decade, era, or franchise...",
    )
    library = filter_movies(library_genre, library_era, year_range, library_search)
    st.caption(f"Showing {len(library):,} of {len(df):,} dataset records")
    if not library.empty:
        library_ids = library["movieId"].astype(int).tolist()
        add_id = st.selectbox(
            "Add a movie to your watchlist",
            library_ids,
            format_func=lambda movie_id: (
                f"{TITLE_BY_ID[movie_id]} (ID {movie_id})"
            ),
        )
        if st.button("＋ Add selected movie to Watchlist"):
            add_to_watchlist(add_id)
            st.toast(f"Added {TITLE_BY_ID[add_id]} to your watchlist")
            st.rerun()

        page_size = 100
        page_count = max(1, (len(library) + page_size - 1) // page_size)
        current_page = min(
            max(int(st.session_state.catalog_page), 1),
            page_count,
        )
        st.session_state.catalog_page = current_page
        page_col, previous_col, next_col = st.columns([2, 1, 1])
        with page_col:
            st.caption(f"Page {current_page} of {page_count} · {page_size} records per page")
        with previous_col:
            if st.button("Previous", disabled=current_page <= 1):
                st.session_state.catalog_page = current_page - 1
                st.rerun()
        with next_col:
            if st.button("Next", disabled=current_page >= page_count):
                st.session_state.catalog_page = current_page + 1
                st.rerun()
        start = (current_page - 1) * page_size
        st.dataframe(
            library[DISPLAY_COLUMNS].iloc[start:start + page_size],
            width="stretch",
            hide_index=True,
        )
        st.download_button(
            "⬇ Download filtered catalogue as CSV",
            data=library.to_csv(index=False).encode("utf-8"),
            file_name="movie_catalogue_filtered.csv",
            mime="text/csv",
        )
    else:
        st.info("No movies match these filters. Try changing your search or filters.")

elif st.session_state.page == "AI Lab":
    hero(
        "Inside the <span style='color:#f0abfc'>recommendation engine.</span>",
        "Recommendations use dataset genre and engineered metadata; no ratings or external movie API are assumed.",
        "DATA-DRIVEN RECOMMENDATIONS",
    )
    st.markdown("### How recommendations are ranked")
    st.markdown(
        "- Genre filters match the dataset's full genre labels.\n"
        "- Primary-genre matches rank higher when a genre is selected.\n"
        "- Engineered genre-rarity score, release year, and title break ties.\n"
        "- An era, year range, and search term can further narrow results.\n"
        "- Similar-movie search uses TF-IDF vectors and cosine similarity over the engineered metadata."
    )
    st.info(
        "The app combines rule-based catalogue filtering with a content-based TF-IDF/cosine similarity model. "
        "It does not learn user preferences or use a generative AI model. "
        "The source CSV has no ratings, language, director, or mood fields."
    )
    st.markdown("### Loaded dataset")
    st.write(f"**{len(df):,} records · {df.shape[1]} columns**")
    st.dataframe(df[DISPLAY_COLUMNS].head(100), width="stretch", hide_index=True)
    st.caption("Previewing the first 100 records. Use Movie Library to search the full dataset.")
    st.download_button(
        "⬇ Download complete featured dataset",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name="movies_featured.csv",
        mime="text/csv",
    )

elif st.session_state.page == "About":
    hero(
        "A movie project with a <span style='color:#f0abfc'>cinematic finish.</span>",
        "CineSuggest uses the processed MovieLens catalogue to make explainable, metadata-based recommendations.",
        "ABOUT THE PROJECT",
    )
    st.markdown("### Project overview")
    st.write(
        "The app loads movies_featured.csv from the project folder. The catalogue, "
        "recommendations, movie counts, and watchlist are based on that dataset."
    )
    st.markdown("### Current data limitations")
    st.write(
        "The available CSV provides movie IDs, titles, genres, years, and engineered metadata. "
        "It does not provide ratings, language, director, runtime, plot descriptions, or mood. "
        "Those details are not shown or used as filters."
    )
    st.info("No account is needed. Your watchlist remains in this browser session and is not saved permanently.")
    st.markdown("### Run locally")
    st.code(
        "pip install pandas scikit-learn streamlit\n"
        "python -m streamlit run app.py",
        language="powershell",
    )

st.markdown(
    '<div class="footer">CineSuggest AI · Dataset-backed discovery · Built with Python + Streamlit</div>',
    unsafe_allow_html=True,
)
