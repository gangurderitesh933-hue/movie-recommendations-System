"""
Feature Engineering Pipeline for Movie Recommendation System.

Constructs high-signal features for:
1. Temporal & Era grouping (decade, era, movie_age)
2. Genre Synergy (primary genre, genre combo, rarity score, single/multi-genre flags)
3. Linguistic & Franchise Architecture (franchise root, sequel detection, subtitle & alternate title extraction)
4. Weighted Recommendation Soup for TF-IDF / Cosine Similarity algorithms.
"""

import os
import re
import time
import numpy as np
import pandas as pd

CURRENT_YEAR = 2026

ALL_GENRES = [
    'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

SEQUEL_REGEX = re.compile(
    r'(\b(Part|Episode|Vol|Volume|Chapter)\s+([IVXLCDM\d]+)|(?:\s+|:)(?:2|3|4|5|6|7|8|9|10)\b|\b(Returns|Reloaded|Revolutions|Resurrection|Rebirth|Origins|Forever)\b)',
    re.IGNORECASE
)

def categorize_era(year) -> str:
    """Categorizes release year into cinematic eras."""
    if pd.isna(year):
        return 'Unknown'
    y = int(year)
    if y < 1930:
        return 'Pioneer / Silent Era'
    elif y < 1960:
        return 'Golden Age (1930-1959)'
    elif y < 1980:
        return 'New Hollywood (1960-1979)'
    elif y < 2000:
        return 'Modern Classic (1980-1999)'
    elif y < 2015:
        return 'Contemporary (2000-2014)'
    else:
        return 'Recent (2015+)'

def get_decade(year) -> str:
    """Extracts decade bucket (e.g. 1990s, 2000s)."""
    if pd.isna(year):
        return 'Unknown'
    return f"{(int(year) // 10) * 10}s"

def extract_franchise_info(title: str):
    """
    Identifies if a movie is part of a franchise or sequel,
    and extracts the franchise base root name.
    """
    t = str(title).strip()
    is_seq = bool(SEQUEL_REGEX.search(t))
    
    if ":" in t:
        root = t.split(":")[0].strip()
        is_seq = True
    else:
        root = re.sub(
            r'\s+(Part\s+[IVXLCDM\d]+|Vol\.\s*\d+|Chapter\s+\d+|[2-9]|II|III|IV|V|VI|VII|VIII|IX|X)\s*$',
            '',
            t,
            flags=re.IGNORECASE
        ).strip()
        if root != t:
            is_seq = True
            
    return is_seq, root

def extract_alternate_title(title: str):
    """Extracts alternate or foreign titles enclosed in parentheses."""
    m = re.findall(r'\((.*?)\)', str(title))
    if m:
        return True, m[-1].strip()
    return False, ''

def engineer_features(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Applies comprehensive feature engineering to preprocessed movies dataframe.
    """
    df = df_input.copy()
    
    # ----------------------------------------------------
    # 1. Temporal & Era Features
    # ----------------------------------------------------
    df['decade'] = df['year'].apply(get_decade)
    df['era'] = df['year'].apply(categorize_era)
    df['movie_age'] = (CURRENT_YEAR - df['year']).astype('Int64')
    
    # ----------------------------------------------------
    # 2. Genre Synergy & Structural Metrics
    # ----------------------------------------------------
    # Primary genre is the first listed genre (dominant thematic genre)
    df['primary_genre'] = df['genres_clean'].fillna('').apply(
        lambda x: x.split('|')[0] if x else 'Unknown'
    )
    
    # Alphabetically sorted genre combination tag (e.g. Action_Adventure_Sci-Fi)
    df['genre_combo'] = df['genres_clean'].fillna('').apply(
        lambda x: '_'.join(sorted(x.split('|'))) if x else 'None'
    )
    
    df['is_single_genre'] = (df['genre_count'] == 1)
    df['is_multi_genre'] = (df['genre_count'] >= 3)
    
    # Genre Rarity Score (Inverse Document Frequency weighting)
    # Rare genres (IMAX, Film-Noir, Western) yield a higher rarity score
    n_movies = len(df)
    genre_cols = [c for c in df.columns if c.startswith('genre_') and c not in ['genre_count', 'genre_combo']]
    
    rarity_scores = np.zeros(n_movies)
    for col in genre_cols:
        doc_freq = df[col].sum()
        idf = np.log((n_movies + 1.0) / (doc_freq + 1.0)) + 1.0
        rarity_scores += df[col].values * idf
    df['genre_rarity_score'] = np.round(rarity_scores, 2)
    
    # ----------------------------------------------------
    # 3. Title Linguistic & Franchise Features
    # ----------------------------------------------------
    df['title_word_count'] = df['clean_title'].astype(str).str.split().str.len()
    df['title_char_length'] = df['clean_title'].astype(str).str.len()
    df['has_subtitle'] = df['clean_title'].astype(str).str.contains(':', regex=False)
    
    franchise_results = [extract_franchise_info(t) for t in df['clean_title']]
    df['is_sequel_or_franchise'] = [r[0] for r in franchise_results]
    df['franchise_root'] = [r[1] for r in franchise_results]
    
    alt_results = [extract_alternate_title(df['clean_title'].iloc[i]) for i in range(len(df))]
    df['has_alternate_title'] = [r[0] for r in alt_results]
    df['alternate_title'] = [r[1] for r in alt_results]
    
    # ----------------------------------------------------
    # 4. Weighted Recommendation Metadata Soup
    # ----------------------------------------------------
    # Enhanced feature weighting for NLP & vector similarity:
    # 2x Clean Title, 1x Franchise Root, 2x Primary Genre, 1x All Genres, 1x Decade, 1x Era
    genres_spaced = df['genres_clean'].fillna('').str.replace('|', ' ', regex=False)
    df['weighted_metadata_soup'] = (
        df['clean_title'] + " " +
        df['clean_title'] + " " +
        df['franchise_root'] + " " +
        df['primary_genre'] + " " +
        df['primary_genre'] + " " +
        genres_spaced + " " +
        df['decade'] + " " +
        df['era']
    ).str.replace(r'\s+', ' ', regex=True).str.strip()
    
    return df

def build_recommender(df: pd.DataFrame, max_features: int = 15000):
    """
    Builds a TF-IDF matrix and provides a recommendation function.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    
    tfidf = TfidfVectorizer(stop_words='english', max_features=max_features)
    tfidf_mat = tfidf.fit_transform(df['weighted_metadata_soup'].fillna(''))
    
    def recommend(query_title: str, top_n: int = 6):
        q = query_title.lower().strip()
        match = df[df['search_title'] == q]
        if match.empty:
            match = df[df['search_title'].str.contains(q, regex=False)]
        if match.empty:
            return None
        idx = match.index[0]
        sim = linear_kernel(tfidf_mat[idx], tfidf_mat).flatten()
        best_indices = sim.argsort()[-(top_n + 1):-1][::-1]
        
        cols = ['movieId', 'clean_title', 'year', 'primary_genre', 'franchise_root', 'decade', 'era']
        res = df.iloc[best_indices][cols].copy()
        res['similarity_score'] = sim[best_indices].round(4)
        return res
        
    return recommend

if __name__ == "__main__":
    t0 = time.time()
    input_path = os.path.join(os.path.dirname(__file__), "movies_preprocessed.csv")
    output_path = os.path.join(os.path.dirname(__file__), "movies_featured.csv")
    
    if not os.path.exists(input_path):
        from preprocess import load_data, preprocess_movies
        raw_path = os.path.join(os.path.dirname(__file__), "movies.csv")
        print(f"movies_preprocessed.csv not found, generating from {raw_path}...")
        df_raw = load_data(raw_path)
        df_prep = preprocess_movies(df_raw)
    else:
        print(f"Reading preprocessed dataset from: {input_path}")
        df_prep = pd.read_csv(input_path)
        
    print(f"Running feature engineering on {len(df_prep):,} records...")
    df_featured = engineer_features(df_prep)
    
    print(f"Saving engineered dataset to: {output_path}")
    df_featured.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Saved {df_featured.shape[0]:,} rows and {df_featured.shape[1]} columns in {time.time() - t0:.2f} seconds.")
    
    # Quick demo verification
    print("\n--- Verifying Content-Based Recommender with Engineered Features ---")
    recommender = build_recommender(df_featured)
    demo_rec = recommender("Inception")
    if demo_rec is not None:
        print("\nTop Recommendations for 'Inception':")
        print(demo_rec[['clean_title', 'year', 'primary_genre', 'franchise_root', 'similarity_score']])
