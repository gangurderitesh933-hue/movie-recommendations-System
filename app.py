import streamlit as st
import pandas as pd
import random
import html
from datetime import datetime

# ============================================================
# CineSuggest AI | Rule-Based Movie Discovery
# Run: python -m streamlit run app.py
# Demo login: demo / movie123
# ============================================================

st.set_page_config(
    page_title="CineSuggest AI",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------- Theme ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
:root { color-scheme: dark; }
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp {
  background:
    radial-gradient(ellipse at 8% 0%, rgba(124,58,237,.20), transparent 34%),
    radial-gradient(ellipse at 92% 10%, rgba(236,72,153,.12), transparent 30%),
    #09090f;
  color: #f7f5ff;
}
.block-container { max-width: 1450px; padding-top: 1.4rem; padding-bottom: 3rem; }
[data-testid="stSidebar"] { background: #101019; border-right: 1px solid rgba(255,255,255,.08); }
[data-testid="stSidebar"] * { color: #efebff; }
h1,h2,h3 { font-family: 'Manrope', sans-serif !important; letter-spacing: -.035em; }
h1 { font-weight: 800 !important; }
p, label, .stMarkdown { color: #ded9ed; }
div[data-testid="stMetric"] {
  background: linear-gradient(145deg, rgba(30,25,47,.95), rgba(17,17,27,.95));
  border: 1px solid rgba(196,181,253,.15); padding: 18px 20px; border-radius: 18px;
}
div[data-testid="stMetricLabel"] { color: #aaa2c2; }
div[data-testid="stMetricValue"] { color: #fff; font-family: 'Manrope', sans-serif; }
.stButton > button, .stDownloadButton > button {
  border-radius: 12px; border: 1px solid rgba(196,181,253,.22);
  background: linear-gradient(135deg, #7c3aed, #a21caf);
  color: white; font-weight: 700; padding: .55rem 1rem;
  transition: transform .15s ease, filter .15s ease;
}
.stButton > button:hover, .stDownloadButton > button:hover { filter: brightness(1.12); transform: translateY(-1px); border-color: #c4b5fd; }
.stTextInput input, .stSelectbox div[data-baseweb="select"], .stNumberInput input,
.stTextArea textarea, .stMultiSelect div[data-baseweb="select"] {
  background: #171522 !important; border-color: #38314b !important; border-radius: 11px !important;
}
.stTabs [data-baseweb="tab-list"] { gap: 8px; border-bottom: 1px solid #282336; }
.stTabs [data-baseweb="tab"] { border-radius: 10px 10px 0 0; padding: 10px 15px; }
.stTabs [aria-selected="true"] { color: #e9d5ff !important; border-bottom-color: #c084fc !important; }
hr { border-color: rgba(255,255,255,.09); }
.hero {
  padding: 30px 32px; border-radius: 24px; margin-bottom: 22px;
  background: linear-gradient(115deg, rgba(91,33,182,.78), rgba(30,27,52,.94) 54%, rgba(131,24,67,.52));
  border: 1px solid rgba(216,180,254,.25); box-shadow: 0 20px 60px rgba(0,0,0,.25);
}
.hero-kicker { text-transform: uppercase; letter-spacing: .18em; font-size: .74rem; color: #e9d5ff; font-weight: 800; }
.hero-title { font-family: 'Manrope',sans-serif; font-size: clamp(2rem,4vw,3.2rem); line-height: 1.08; font-weight: 800; color: white; margin: 10px 0; }
.hero-sub { color: #e6ddfa; max-width: 720px; font-size: 1.02rem; }
.movie-card {
  height: 100%; padding: 18px; border-radius: 19px;
  background: linear-gradient(155deg, rgba(32,27,47,.98), rgba(17,17,27,.98));
  border: 1px solid rgba(196,181,253,.15); box-shadow: 0 12px 28px rgba(0,0,0,.16);
}
.movie-poster {
  min-height: 135px; display:flex; align-items:center; justify-content:center;
  font-size: 4.1rem; border-radius: 14px; margin-bottom: 14px;
  background: radial-gradient(circle at 50% 25%, rgba(192,132,252,.3), rgba(76,29,149,.13) 60%, rgba(255,255,255,.02));
  border: 1px solid rgba(255,255,255,.07);
}
.movie-title { font-family: 'Manrope',sans-serif; font-weight: 800; color: #fff; font-size: 1.12rem; line-height: 1.25; }
.movie-meta { color: #aaa2c2; font-size: .82rem; margin: 5px 0 9px; }
.movie-desc { color: #d4cde4; font-size: .9rem; min-height: 58px; }
.pill { display:inline-block; padding:4px 9px; margin: 3px 4px 2px 0; border-radius:999px; font-size:.72rem; color:#e9d5ff; background:rgba(139,92,246,.16); border:1px solid rgba(196,181,253,.17); }
.score { color:#fcd34d; font-weight:800; }
.section-eyebrow { color:#c4b5fd; text-transform:uppercase; font-size:.72rem; letter-spacing:.16em; font-weight:800; }
.small-muted { color:#9f97b7; font-size:.84rem; }
.login-wrap { max-width: 560px; margin: 6vh auto 0; }
.footer { color:#827b98; text-align:center; font-size:.8rem; padding: 25px 0 5px; }
</style>
""", unsafe_allow_html=True)

# ---------- Movie data ----------
MOVIES = [
    {"title":"Interstellar","genre":"Sci-Fi","language":"English","mood":"Mind-blowing","year":2014,"rating":8.7,"emoji":"🚀","runtime":169,"director":"Christopher Nolan","description":"A team travels beyond this galaxy to discover whether mankind has a future among the stars.","tags":["Space","Emotional","Epic"]},
    {"title":"Inception","genre":"Sci-Fi","language":"English","mood":"Mind-blowing","year":2010,"rating":8.8,"emoji":"🌀","runtime":148,"director":"Christopher Nolan","description":"A skilled thief enters dreams to plant an idea inside a target's mind.","tags":["Dreams","Thriller","Twisty"]},
    {"title":"The Dark Knight","genre":"Action","language":"English","mood":"Intense","year":2008,"rating":9.0,"emoji":"🦇","runtime":152,"director":"Christopher Nolan","description":"Batman faces a criminal mastermind who pushes Gotham into chaos.","tags":["Superhero","Crime","Iconic"]},
    {"title":"The Shawshank Redemption","genre":"Drama","language":"English","mood":"Inspirational","year":1994,"rating":9.3,"emoji":"🕊️","runtime":142,"director":"Frank Darabont","description":"A banker forms an unlikely friendship while holding on to hope in prison.","tags":["Hope","Friendship","Classic"]},
    {"title":"The Prestige","genre":"Mystery","language":"English","mood":"Mind-blowing","year":2006,"rating":8.5,"emoji":"🎩","runtime":130,"director":"Christopher Nolan","description":"Two rival magicians become consumed by their competition and its secrets.","tags":["Mystery","Rivalry","Twisty"]},
    {"title":"Dune: Part Two","genre":"Sci-Fi","language":"English","mood":"Epic","year":2024,"rating":8.5,"emoji":"🏜️","runtime":166,"director":"Denis Villeneuve","description":"Paul Atreides unites with the Fremen while pursuing a path of destiny and revenge.","tags":["Desert","War","Epic"]},
    {"title":"Spider-Man: Into the Spider-Verse","genre":"Animation","language":"English","mood":"Feel-good","year":2018,"rating":8.4,"emoji":"🕸️","runtime":117,"director":"Bob Persichetti, Peter Ramsey, Rodney Rothman","description":"Miles Morales discovers what it means to be Spider-Man across multiple dimensions.","tags":["Superhero","Colorful","Coming-of-age"]},
    {"title":"Coco","genre":"Animation","language":"English","mood":"Emotional","year":2017,"rating":8.4,"emoji":"🎸","runtime":105,"director":"Lee Unkrich","description":"A music-loving boy journeys to the Land of the Dead to uncover his family history.","tags":["Family","Music","Heartwarming"]},
    {"title":"The Grand Budapest Hotel","genre":"Comedy","language":"English","mood":"Feel-good","year":2014,"rating":8.1,"emoji":"🏨","runtime":99,"director":"Wes Anderson","description":"A legendary concierge and his lobby boy become tangled in a priceless painting mystery.","tags":["Quirky","Adventure","Stylish"]},
    {"title":"Knives Out","genre":"Mystery","language":"English","mood":"Funny","year":2019,"rating":7.9,"emoji":"🔎","runtime":130,"director":"Rian Johnson","description":"A detective investigates a wealthy family's secrets after a novelist's death.","tags":["Whodunit","Comedy","Clues"]},
    {"title":"La La Land","genre":"Romance","language":"English","mood":"Romantic","year":2016,"rating":8.0,"emoji":"🎹","runtime":128,"director":"Damien Chazelle","description":"An aspiring actress and a jazz musician fall in love while chasing their dreams.","tags":["Music","Dreams","Bittersweet"]},
    {"title":"The Notebook","genre":"Romance","language":"English","mood":"Emotional","year":2004,"rating":7.8,"emoji":"💌","runtime":123,"director":"Nick Cassavetes","description":"A decades-spanning love story tests the strength of a couple's bond.","tags":["Love","Classic","Tearjerker"]},
    {"title":"The Conjuring","genre":"Horror","language":"English","mood":"Scary","year":2013,"rating":7.5,"emoji":"👻","runtime":112,"director":"James Wan","description":"Paranormal investigators help a family facing a terrifying presence in their farmhouse.","tags":["Supernatural","Suspense","Haunted"]},
    {"title":"Get Out","genre":"Horror","language":"English","mood":"Intense","year":2017,"rating":7.8,"emoji":"🪞","runtime":104,"director":"Jordan Peele","description":"A weekend visit to meet a girlfriend's family turns into a disturbing mystery.","tags":["Social Thriller","Mystery","Psychological"]},
    {"title":"The Martian","genre":"Adventure","language":"English","mood":"Inspirational","year":2015,"rating":8.0,"emoji":"🪐","runtime":144,"director":"Ridley Scott","description":"An astronaut stranded on Mars uses science and ingenuity to survive.","tags":["Space","Survival","Science"]},
    {"title":"Top Gun: Maverick","genre":"Action","language":"English","mood":"Epic","year":2022,"rating":8.2,"emoji":"✈️","runtime":130,"director":"Joseph Kosinski","description":"A veteran pilot trains an elite team for a dangerous mission.","tags":["Aviation","Teamwork","Adrenaline"]},
    {"title":"Everything Everywhere All at Once","genre":"Sci-Fi","language":"English","mood":"Mind-blowing","year":2022,"rating":7.8,"emoji":"🌌","runtime":139,"director":"Daniel Kwan, Daniel Scheinert","description":"An exhausted laundromat owner becomes the unlikely hero of a multiverse-spanning adventure.","tags":["Multiverse","Family","Absurdist"]},
    {"title":"The Social Network","genre":"Drama","language":"English","mood":"Intense","year":2010,"rating":7.8,"emoji":"💻","runtime":120,"director":"David Fincher","description":"The creation of a social network reshapes friendships, ambition and business.","tags":["Technology","Ambition","Biography"]},
    {"title":"3 Idiots","genre":"Comedy","language":"Hindi","mood":"Feel-good","year":2009,"rating":8.4,"emoji":"🎓","runtime":170,"director":"Rajkumar Hirani","description":"Three engineering students challenge pressure, expectations and the meaning of success.","tags":["College","Friendship","Life Lessons"]},
    {"title":"Dangal","genre":"Drama","language":"Hindi","mood":"Inspirational","year":2016,"rating":8.3,"emoji":"🤼","runtime":161,"director":"Nitesh Tiwari","description":"A former wrestler trains his daughters to compete at the highest level.","tags":["Sports","Family","Determination"]},
    {"title":"Zindagi Na Milegi Dobara","genre":"Adventure","language":"Hindi","mood":"Feel-good","year":2011,"rating":8.2,"emoji":"🌊","runtime":155,"director":"Zoya Akhtar","description":"Three friends take a road trip that changes how they see life and one another.","tags":["Travel","Friendship","Self-discovery"]},
    {"title":"Andhadhun","genre":"Thriller","language":"Hindi","mood":"Mind-blowing","year":2018,"rating":8.2,"emoji":"🎹","runtime":139,"director":"Sriram Raghavan","description":"A pianist becomes entangled in a murder mystery full of deception and surprises.","tags":["Crime","Twists","Dark Comedy"]},
    {"title":"Drishyam","genre":"Thriller","language":"Hindi","mood":"Intense","year":2015,"rating":8.2,"emoji":"🧩","runtime":163,"director":"Nishikant Kamat","description":"A family man uses clever planning to protect his family from a criminal investigation.","tags":["Crime","Family","Suspense"]},
    {"title":"Taare Zameen Par","genre":"Drama","language":"Hindi","mood":"Emotional","year":2007,"rating":8.3,"emoji":"🎨","runtime":165,"director":"Aamir Khan","description":"An art teacher helps a child whose learning difficulties have gone misunderstood.","tags":["Education","Family","Heartwarming"]},
    {"title":"Kantara","genre":"Action","language":"Kannada","mood":"Intense","year":2022,"rating":8.2,"emoji":"🌿","runtime":148,"director":"Rishab Shetty","description":"A village's traditions and land become the center of a powerful local conflict.","tags":["Folklore","Culture","Mystery"]},
    {"title":"777 Charlie","genre":"Adventure","language":"Kannada","mood":"Emotional","year":2022,"rating":8.7,"emoji":"🐕","runtime":164,"director":"Kiranraj K","description":"A lonely man finds a new reason to live through an unexpected bond with a dog.","tags":["Animals","Journey","Heartwarming"]},
    {"title":"Vikram","genre":"Action","language":"Tamil","mood":"Intense","year":2022,"rating":8.3,"emoji":"🕶️","runtime":174,"director":"Lokesh Kanagaraj","description":"A covert investigation uncovers a dangerous network of crime and corruption.","tags":["Crime","Action","Undercover"]},
    {"title":"Jai Bhim","genre":"Drama","language":"Tamil","mood":"Inspirational","year":2021,"rating":8.7,"emoji":"⚖️","runtime":164,"director":"T. J. Gnanavel","description":"A lawyer fights for justice for a marginalized family after a custodial disappearance.","tags":["Justice","Courtroom","Social"]},
    {"title":"Parasite","genre":"Thriller","language":"Korean","mood":"Mind-blowing","year":2019,"rating":8.5,"emoji":"🏠","runtime":132,"director":"Bong Joon-ho","description":"Two families' lives intersect in a story of class, secrets and escalating tension.","tags":["Social Thriller","Dark Comedy","Twists"]},
    {"title":"Train to Busan","genre":"Horror","language":"Korean","mood":"Intense","year":2016,"rating":7.6,"emoji":"🚆","runtime":118,"director":"Yeon Sang-ho","description":"Passengers struggle to survive a sudden outbreak aboard a high-speed train.","tags":["Zombies","Survival","Thriller"]},
    {"title":"Spirited Away","genre":"Animation","language":"Japanese","mood":"Magical","year":2001,"rating":8.6,"emoji":"🐉","runtime":125,"director":"Hayao Miyazaki","description":"A young girl enters a strange spirit world and must find courage to rescue her parents.","tags":["Fantasy","Coming-of-age","Classic"]},
    {"title":"Your Name","genre":"Romance","language":"Japanese","mood":"Emotional","year":2016,"rating":8.4,"emoji":"☄️","runtime":106,"director":"Makoto Shinkai","description":"Two teenagers mysteriously begin switching bodies and search for each other across time.","tags":["Anime","Fantasy","Love"]},
    {"title":"The Lion King","genre":"Animation","language":"English","mood":"Epic","year":1994,"rating":8.5,"emoji":"🦁","runtime":88,"director":"Roger Allers, Rob Minkoff","description":"A young lion prince learns responsibility and courage after tragedy changes his life.","tags":["Family","Adventure","Classic"]},
    {"title":"The Truman Show","genre":"Drama","language":"English","mood":"Mind-blowing","year":1998,"rating":8.2,"emoji":"📺","runtime":103,"director":"Peter Weir","description":"A man begins to suspect that his seemingly ordinary life is actually a constructed reality.","tags":["Reality","Satire","Philosophical"]},
    {"title":"Mad Max: Fury Road","genre":"Action","language":"English","mood":"Intense","year":2015,"rating":8.1,"emoji":"🏎️","runtime":120,"director":"George Miller","description":"A high-octane escape across a brutal wasteland becomes a fight for freedom.","tags":["Dystopian","Chase","Adrenaline"]},
    {"title":"The Imitation Game","genre":"Drama","language":"English","mood":"Inspirational","year":2014,"rating":8.0,"emoji":"🔐","runtime":114,"director":"Morten Tyldum","description":"A mathematician and his team race to crack a wartime code.","tags":["History","Technology","Biography"]},
    {"title":"Paddington 2","genre":"Comedy","language":"English","mood":"Feel-good","year":2017,"rating":7.8,"emoji":"🧸","runtime":103,"director":"Paul King","description":"A kind bear's search for a special gift leads to an unexpected adventure.","tags":["Family","Warm","Funny"]},
    {"title":"The Secret Life of Walter Mitty","genre":"Adventure","language":"English","mood":"Inspirational","year":2013,"rating":7.3,"emoji":"📷","runtime":114,"director":"Ben Stiller","description":"A quiet dreamer embarks on a real-world journey beyond his comfort zone.","tags":["Travel","Dreams","Self-discovery"]},
    {"title":"Queen","genre":"Comedy","language":"Hindi","mood":"Inspirational","year":2013,"rating":8.1,"emoji":"👑","runtime":146,"director":"Vikas Bahl","description":"A young woman takes her planned honeymoon alone and discovers her independence.","tags":["Travel","Self-discovery","Comedy"]},
    {"title":"Article 15","genre":"Thriller","language":"Hindi","mood":"Intense","year":2019,"rating":8.1,"emoji":"📜","runtime":130,"director":"Anubhav Sinha","description":"A police officer investigates a case that exposes deep-rooted social injustice.","tags":["Crime","Investigation","Social"]},
    {"title":"Super Deluxe","genre":"Drama","language":"Tamil","mood":"Mind-blowing","year":2019,"rating":8.2,"emoji":"🎭","runtime":176,"director":"Thiagarajan Kumararaja","description":"Several unusual lives collide in a darkly comic, interconnected story.","tags":["Ensemble","Dark Comedy","Unusual"]},
    {"title":"The Boy and the Heron","genre":"Animation","language":"Japanese","mood":"Magical","year":2023,"rating":7.4,"emoji":"🪶","runtime":124,"director":"Hayao Miyazaki","description":"A grieving boy enters a mysterious world guided by a strange grey heron.","tags":["Fantasy","Adventure","Anime"]},
]

df = pd.DataFrame(MOVIES)
GENRES = ["Any"] + sorted(df["genre"].unique().tolist())
LANGUAGES = ["Any"] + sorted(df["language"].unique().tolist())
MOODS = ["Any"] + sorted(df["mood"].unique().tolist())

# ---------- Session state ----------
defaults = {
    "authenticated": False,
    "username": "",
    "accounts": {"demo": "movie123"},
    "watchlist": [],
    "seen": [],
    "page": "Discover",
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

def safe(text):
    return html.escape(str(text))

def score_movie(movie, genre, language, mood, min_rating):
    score, reasons = 0, []
    if genre != "Any" and movie["genre"] == genre:
        score += 3
        reasons.append(f"Matches your {genre} genre")
    if language != "Any" and movie["language"] == language:
        score += 2
        reasons.append(f"Available in your selected language ({language})")
    if mood != "Any" and movie["mood"] == mood:
        score += 2
        reasons.append(f"Fits your {mood.lower()} mood")
    if float(movie["rating"]) >= 8.0:
        score += 1
        reasons.append("Highly rated (8.0+)")
    if not reasons:
        reasons.append("A strong general pick based on rating")
    return score, reasons

def recommend_movies(genre="Any", language="Any", mood="Any", min_rating=7.0, query="", limit=12):
    results = []
    query_lower = query.strip().lower()
    for movie in MOVIES:
        if float(movie["rating"]) < min_rating:
            continue
        if genre != "Any" and movie["genre"] != genre:
            continue
        if language != "Any" and movie["language"] != language:
            continue
        if mood != "Any" and movie["mood"] != mood:
            continue
        haystack = " ".join([movie["title"], movie["genre"], movie["language"], movie["mood"], movie["director"], movie["description"], " ".join(movie["tags"])]).lower()
        if query_lower and query_lower not in haystack:
            continue
        score, reasons = score_movie(movie, genre, language, mood, min_rating)
        results.append({**movie, "score": score, "reasons": reasons})
    results.sort(key=lambda x: (x["score"], x["rating"], x["year"]), reverse=True)
    return results[:limit]

def movie_card(movie, key_prefix="movie"):
    title = safe(movie["title"])
    st.markdown(f"""
    <div class="movie-card">
      <div class="movie-poster">{safe(movie['emoji'])}</div>
      <div class="movie-title">{title}</div>
      <div class="movie-meta">{safe(movie['year'])} &nbsp;·&nbsp; {safe(movie['language'])} &nbsp;·&nbsp; {safe(movie['runtime'])} min</div>
      <div style="margin-bottom:9px"><span class="pill">{safe(movie['genre'])}</span><span class="pill">{safe(movie['mood'])}</span></div>
      <div class="movie-desc">{safe(movie['description'])}</div>
      <div style="margin-top:13px;display:flex;justify-content:space-between;align-items:center">
        <span class="score">★ {float(movie['rating']):.1f}/10</span>
        <span class="small-muted">{'Match ' + str(movie.get('score', 0)) if 'score' in movie else 'CineSuggest pick'}</span>
      </div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("＋ Add to Watchlist" if movie["title"] not in st.session_state.watchlist else "✓ Saved to Watchlist",
                 key=f"{key_prefix}_{movie['title']}", use_container_width=True,
                 disabled=movie["title"] in st.session_state.watchlist):
        st.session_state.watchlist.append(movie["title"])
        st.toast(f"Added {movie['title']} to your watchlist")
        st.rerun()
    with st.expander("Why this movie? / Details", expanded=False):
        st.write(movie["description"])
        st.caption(f"Director: {movie['director']} · Runtime: {movie['runtime']} min")
        st.write("**Tags:** " + " · ".join(movie["tags"]))
        if "reasons" in movie:
            for reason in movie["reasons"]:
                st.write(f"✓ {reason}")

def show_movie_grid(movies, columns=3, prefix="grid"):
    if not movies:
        st.info("No movies match these filters. Try lowering the minimum rating or changing a filter.")
        return
    for start in range(0, len(movies), columns):
        row = st.columns(columns, gap="medium")
        for col, movie in zip(row, movies[start:start+columns]):
            with col:
                movie_card(movie, f"{prefix}_{start}")

def hero(title, subtitle, kicker="YOUR PERSONAL MOVIE COMPANION"):
    st.markdown(f"""
    <div class="hero">
      <div class="hero-kicker">{safe(kicker)}</div>
      <div class="hero-title">{title}</div>
      <div class="hero-sub">{subtitle}</div>
    </div>
    """, unsafe_allow_html=True)

# ---------- Login screen ----------
if not st.session_state.authenticated:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    st.markdown("""
    <div class="hero">
      <div class="hero-kicker">CINEMA, CURATED FOR YOU</div>
      <div class="hero-title">Find your next<br>favourite film. 🎬</div>
      <div class="hero-sub">A personal movie discovery studio powered by transparent, rule-based recommendations.</div>
    </div>
    """, unsafe_allow_html=True)
    login_tab, signup_tab = st.tabs(["Sign in", "Create account"])
    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            submitted = st.form_submit_button("Enter CineSuggest →", use_container_width=True)
        if submitted:
            if username in st.session_state.accounts and st.session_state.accounts[username] == password:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.rerun()
            else:
                st.error("Incorrect username or password.")
        st.caption("Demo access: username `demo` · password `movie123`")
    with signup_tab:
        with st.form("signup_form"):
            new_user = st.text_input("Choose username")
            new_pass = st.text_input("Choose password", type="password")
            confirm_pass = st.text_input("Confirm password", type="password")
            signup = st.form_submit_button("Create account", use_container_width=True)
        if signup:
            if len(new_user.strip()) < 3:
                st.error("Username must contain at least 3 characters.")
            elif len(new_pass) < 4:
                st.error("Password must contain at least 4 characters.")
            elif new_pass != confirm_pass:
                st.error("Passwords do not match.")
            elif new_user in st.session_state.accounts:
                st.error("That username already exists.")
            else:
                st.session_state.accounts[new_user] = new_pass
                st.session_state.username = new_user
                st.session_state.authenticated = True
                st.success("Account created.")
                st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('<div class="footer">CineSuggest AI · A student project built with Python and Streamlit</div>', unsafe_allow_html=True)
    st.stop()

# ---------- Sidebar navigation ----------
with st.sidebar:
    st.markdown("## 🎬 CineSuggest")
    st.caption("MOVIE DISCOVERY STUDIO")
    st.divider()
    pages = ["Discover", "Mood Match", "My Watchlist", "Movie Library", "AI Lab", "About Project"]
    selected_page = st.radio("NAVIGATION", pages, index=pages.index(st.session_state.page) if st.session_state.page in pages else 0)
    st.session_state.page = selected_page
    st.divider()
    st.markdown(f"Signed in as **{safe(st.session_state.username)}**")
    st.caption(f"{len(MOVIES)} movies in your local catalogue")
    if st.button("Log out", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.username = ""
        st.rerun()
    st.markdown("---")
    st.caption("Recommendations are generated locally using transparent rules. No external API required.")

# ---------- Discover ----------
if st.session_state.page == "Discover":
    hero("A better way to <span style='color:#f0abfc'>pick a movie.</span>", "Tell us what you feel like watching. CineSuggest ranks movies using genre, language, mood and rating preferences.", "CINESUGGEST AI · PERSONAL DISCOVERY")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Movies in library", len(MOVIES))
    m2.metric("Genres", df["genre"].nunique())
    m3.metric("Languages", df["language"].nunique())
    m4.metric("Saved titles", len(st.session_state.watchlist))
    st.markdown("### ✨ Tune your recommendations")
    with st.container(border=True):
        f1, f2, f3 = st.columns(3)
        with f1:
            genre = st.selectbox("Genre", GENRES, key="discover_genre")
        with f2:
            language = st.selectbox("Language", LANGUAGES, key="discover_language")
        with f3:
            mood = st.selectbox("Mood", MOODS, key="discover_mood")
        f4, f5 = st.columns([2, 1])
        with f4:
            search = st.text_input("Search titles, directors, themes", placeholder="Try: space, friendship, Nolan...")
        with f5:
            min_rating = st.slider("Minimum rating", 5.0, 9.0, 7.0, 0.1)
    recommendations = recommend_movies(genre, language, mood, min_rating, search, limit=18)
    st.markdown(f"### Your matches <span class='small-muted'>· {len(recommendations)} results</span>", unsafe_allow_html=True)
    show_movie_grid(recommendations, 3, "discover")

# ---------- Mood match ----------
elif st.session_state.page == "Mood Match":
    hero("What’s your <span style='color:#f0abfc'>mood tonight?</span>", "Choose the feeling you want from a movie and discover a curated set of options.", "MOOD-BASED DISCOVERY")
    mood_options = ["Feel-good", "Mind-blowing", "Emotional", "Inspirational", "Intense", "Funny", "Romantic", "Scary", "Magical", "Epic"]
    mood_choice = st.selectbox("Pick a mood", mood_options)
    mood_language = st.selectbox("Preferred language", LANGUAGES, key="mood_lang")
    min_mood_rating = st.slider("Minimum IMDb-style rating", 5.0, 9.0, 7.0, 0.1, key="mood_rating")
    picks = recommend_movies("Any", mood_language, mood_choice, min_mood_rating, limit=15)
    st.markdown(f"### Picks for a {mood_choice.lower()} mood")
    show_movie_grid(picks, 3, "mood")

# ---------- Watchlist ----------
elif st.session_state.page == "My Watchlist":
    hero("Your personal <span style='color:#f0abfc'>watchlist.</span>", "Keep the films you want to watch next in one place. Your list is stored for this session.", "YOUR COLLECTION")
    watchlist_movies = [m for m in MOVIES if m["title"] in st.session_state.watchlist]
    if not watchlist_movies:
        st.info("Your watchlist is empty. Head to Discover and add movies you want to watch.")
        if st.button("Explore movies"):
            st.session_state.page = "Discover"
            st.rerun()
    else:
        st.write(f"**{len(watchlist_movies)} saved movies**")
        show_movie_grid(watchlist_movies, 3, "watchlist")
        if st.button("Clear entire watchlist", type="secondary"):
            st.session_state.watchlist = []
            st.rerun()

# ---------- Movie library ----------
elif st.session_state.page == "Movie Library":
    hero("Explore the full <span style='color:#f0abfc'>catalogue.</span>", "Browse the movie database and narrow it down by genre, language, release year and rating.", "THE MOVIE LIBRARY")
    a, b, c, d = st.columns(4)
    with a:
        lib_genre = st.selectbox("Genre", GENRES, key="lib_genre")
    with b:
        lib_language = st.selectbox("Language", LANGUAGES, key="lib_language")
    with c:
        year_range = st.slider("Release year", int(df.year.min()), int(df.year.max()), (int(df.year.min()), int(df.year.max())))
    with d:
        lib_rating = st.slider("Minimum rating", 5.0, 9.0, 7.0, 0.1, key="lib_rating")
    lib_search = st.text_input("Search catalogue", placeholder="Movie title, genre, director or tag...")
    library = []
    for movie in MOVIES:
        if lib_genre != "Any" and movie["genre"] != lib_genre: continue
        if lib_language != "Any" and movie["language"] != lib_language: continue
        if not (year_range[0] <= movie["year"] <= year_range[1]): continue
        if movie["rating"] < lib_rating: continue
        if lib_search:
            haystack = (movie["title"] + " " + movie["genre"] + " " + movie["director"] + " " + movie["description"] + " " + " ".join(movie["tags"])).lower()
            if lib_search.lower() not in haystack: continue
        library.append(movie)
    st.caption(f"Showing {len(library)} of {len(MOVIES)} movies")
    show_movie_grid(sorted(library, key=lambda m: (m["rating"], m["year"]), reverse=True), 3, "library")
    with st.expander("View catalogue as a table"):
        st.dataframe(pd.DataFrame([{k: m[k] for k in ["title","genre","language","mood","year","rating","runtime","director"]} for m in library]), use_container_width=True, hide_index=True)

# ---------- AI Lab ----------
elif st.session_state.page == "AI Lab":
    hero("Inside the <span style='color:#f0abfc'>recommendation engine.</span>", "Explore the local movie knowledge base and understand exactly how each recommendation is scored.", "TRANSPARENT RULE-BASED AI")
    st.markdown("### How the scoring works")
    rule_cols = st.columns(4)
    rule_cols[0].metric("Genre match", "+3 points")
    rule_cols[1].metric("Language match", "+2 points")
    rule_cols[2].metric("Mood match", "+2 points")
    rule_cols[3].metric("Rating ≥ 8.0", "+1 point")
    st.info("The app applies these rules to each movie that passes the filters, then sorts results by match score, rating and release year. This is a rule-based recommender, not a trained machine-learning model.")
    st.markdown("### Knowledge base")
    st.dataframe(pd.DataFrame([{k: m[k] for k in ["title","genre","language","mood","year","rating","runtime","director"]} for m in MOVIES]), use_container_width=True, hide_index=True)
    csv_data = df.drop(columns=["tags"]).to_csv(index=False).encode("utf-8")
    st.download_button("⬇ Export movie database as CSV", data=csv_data, file_name="cinesuggest_movie_database.csv", mime="text/csv")
    st.markdown("### Try the scoring rules")
    x, y, z = st.columns(3)
    with x: test_genre = st.selectbox("Test genre", GENRES, key="test_genre")
    with y: test_language = st.selectbox("Test language", LANGUAGES, key="test_language")
    with z: test_mood = st.selectbox("Test mood", MOODS, key="test_mood")
    test_results = recommend_movies(test_genre, test_language, test_mood, 5.0, limit=8)
    if test_results:
        st.dataframe(pd.DataFrame([{"Movie": m["title"], "Score": m["score"], "Rating": m["rating"], "Explanation": "; ".join(m["reasons"])} for m in test_results]), use_container_width=True, hide_index=True)
    else:
        st.warning("No results for this combination. Change one of the selections.")

# ---------- About ----------
elif st.session_state.page == "About Project":
    hero("A student project with a <span style='color:#f0abfc'>cinematic finish.</span>", "CineSuggest AI demonstrates how a recommendation system can use structured movie data and explainable rules to help users discover films.", "ABOUT THE PROJECT")
    st.markdown("### Project overview")
    st.write("CineSuggest AI is a rule-based movie recommendation web application developed with Python and Streamlit. It matches user preferences with a curated local movie catalogue and explains why each result appears.")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("#### Key features")
        st.markdown("- Sign in and demo account flow\n- Account creation for the current session\n- Genre, language, mood and rating filters\n- Search across titles, directors and themes\n- Match score with a plain-language explanation\n- Personal watchlist\n- Movie library and CSV export\n- AI Lab showing the rules and data")
    with c2:
        st.markdown("#### Technology stack")
        st.markdown("- **Python** — application logic\n- **Streamlit** — interactive web interface\n- **Pandas** — movie catalogue and tabular views\n- **Rule-based scoring** — transparent recommendations\n- **Session state** — temporary account and watchlist storage")
    st.warning("Project limitations: accounts and watchlists are stored in Streamlit session state, not a permanent database. This demo login is not production-grade security. Movie data is bundled locally; the app does not call a live movie API.")
    st.markdown("### Run locally")
    st.code("pip install streamlit pandas\npython -m streamlit run app.py", language="powershell")

st.markdown('<div class="footer">CineSuggest AI · Discover something worth watching · Built with Python + Streamlit</div>', unsafe_allow_html=True)
