"""
Dataset Preprocessing and Feature Engineering Pipeline
for Movie Recommendation System.
"""

import os
import re
import time
import pandas as pd
import numpy as np

ALL_GENRES = [
    'Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime',
    'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'IMAX',
    'Musical', 'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western'
]

def load_data(filepath="movies.csv"):
    """Load raw movie dataset with safe UTF-8 decoding."""
    return pd.read_csv(filepath, encoding='utf-8', encoding_errors='replace')

def clean_articles(title: str, article_pattern=None) -> str:
    """Normalize inverted articles like 'Matrix, The' -> 'The Matrix'."""
    if article_pattern is None:
        article_pattern = re.compile(
            r'^(.*),\s*(The|A|An|Der|Die|Das|Le|La|Les|El|Il|L\')(\s*\(.*\))?$', 
            re.IGNORECASE
        )
    m = article_pattern.match(title)
    if m:
        base = m.group(1).strip()
        art = m.group(2).strip()
        extra = m.group(3) if m.group(3) else ""
        return f"{art} {base}{extra}".strip()
    return title

def preprocess_movies(df_raw: pd.DataFrame) -> pd.DataFrame:
    """
    Executes end-to-end preprocessing:
    - Text trimming and whitespace cleanup
    - Precise extraction of 4-digit release year
    - Title normalization (stripping year, fixing inverted articles)
    - Normalized lowercase alphanumeric search title
    - Genre parsing, genre counting, and handling '(no genres listed)'
    - One-hot / binary encoding for all 19 unique genres
    - Construction of metadata soup for content-based recommendation / TF-IDF
    """
    df = df_raw.copy()
    
    # 1. Clean whitespace
    df['title'] = df['title'].astype(str).str.strip()
    df['genres'] = df['genres'].astype(str).str.strip()
    
    # 2. Extract Year
    # Primary: 4 digits in parentheses at/near end
    year_pattern = r'\((\d{4})\)\s*\)?$'
    df['year'] = df['title'].str.extract(year_pattern)[0]
    
    # Secondary fallback: 4 digits anywhere inside parentheses
    missing_mask = df['year'].isna()
    if missing_mask.any():
        fallback_years = df.loc[missing_mask, 'title'].str.extract(r'\((\d{4})\)')[0]
        df.loc[missing_mask, 'year'] = fallback_years
        
    df['year'] = pd.to_numeric(df['year'], errors='coerce').astype('Int64')
    
    # 3. Clean Title
    article_pat = re.compile(
        r'^(.*),\s*(The|A|An|Der|Die|Das|Le|La|Les|El|Il|L\')(\s*\(.*\))?$', 
        re.IGNORECASE
    )
    
    # Extract titles stripped of year
    clean_titles = []
    for title, yr in zip(df['title'], df['year']):
        t = title
        if pd.notna(yr):
            # Strip (year) at the end
            t = re.sub(rf'\({int(yr)}\)\s*\)?$', '', t).strip()
            # If still has (year) inside
            if f"({int(yr)})" in t:
                idx = t.rfind(f"({int(yr)})")
                t = (t[:idx] + t[idx + len(f"({int(yr)})"):]).strip()
        
        # Clean inverted articles
        t = clean_articles(t, article_pat)
        clean_titles.append(t)
        
    df['clean_title'] = clean_titles
    
    # 4. Search Title (lowercase, alphanumeric only)
    df['search_title'] = (
        df['clean_title']
        .str.lower()
        .str.replace(r'[^\w\s]', ' ', regex=True)
        .str.replace(r'\s+', ' ', regex=True)
        .str.strip()
    )
    
    # 5. Genre List & Flags
    df['is_genre_listed'] = df['genres'] != '(no genres listed)'
    df['genres_clean'] = df['genres'].replace('(no genres listed)', '')
    df['genres_list'] = df['genres_clean'].apply(lambda x: x.split('|') if x else [])
    df['genre_count'] = df['genres_list'].apply(len)
    
    # 6. Recommendation Metadata Soup
    # Joins clean_title + space-separated genres + year
    genres_joined = df['genres_list'].apply(lambda g: ' '.join(g))
    years_str = df['year'].apply(lambda y: str(int(y)) if pd.notna(y) else '')
    df['metadata_soup'] = (
        df['clean_title'] + ' ' + genres_joined + ' ' + years_str
    ).str.replace(r'\s+', ' ', regex=True).str.strip()
    
    # 7. One-hot / binary encoding for genres
    for g in ALL_GENRES:
        col = f"genre_{g.lower().replace('-', '_')}"
        df[col] = df['genres_clean'].apply(lambda s: 1 if g in s.split('|') else 0)
        
    return df

def generate_eda_report(df_raw: pd.DataFrame, df_clean: pd.DataFrame) -> dict:
    """Computes key statistics and insights on raw and cleaned data."""
    raw_shape = df_raw.shape
    missing_genres = (df_raw['genres'] == '(no genres listed)').sum()
    year_stats = df_clean['year'].describe().to_dict()
    missing_years = int(df_clean['year'].isna().sum())
    duplicate_titles = int(df_raw['title'].duplicated().sum())
    
    # Genre frequency
    genre_freq = {}
    for g in ALL_GENRES:
        col = f"genre_{g.lower().replace('-', '_')}"
        genre_freq[g] = int(df_clean[col].sum())
        
    # Sort genres descending
    genre_freq = dict(sorted(genre_freq.items(), key=lambda x: x[1], reverse=True))
    
    return {
        "total_movies": raw_shape[0],
        "total_columns_raw": raw_shape[1],
        "total_columns_processed": df_clean.shape[1],
        "missing_genres_count": int(missing_genres),
        "missing_genres_pct": round(missing_genres / raw_shape[0] * 100, 2),
        "missing_years_count": missing_years,
        "missing_years_pct": round(missing_years / raw_shape[0] * 100, 2),
        "min_year": int(year_stats.get('min', 0)) if pd.notna(year_stats.get('min')) else None,
        "max_year": int(year_stats.get('max', 0)) if pd.notna(year_stats.get('max')) else None,
        "median_year": int(year_stats.get('50%', 0)) if pd.notna(year_stats.get('50%')) else None,
        "duplicate_raw_titles": duplicate_titles,
        "genre_distribution": genre_freq
    }

def get_content_recommendations(query_title: str, df: pd.DataFrame = None, top_n: int = 5):
    """
    Computes top-N content-based recommendations using TF-IDF on metadata_soup.
    """
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import linear_kernel
    
    if df is None:
        csv_path = os.path.join(os.path.dirname(__file__), "movies_preprocessed.csv")
        df = pd.read_csv(csv_path)
        
    query_clean = query_title.lower().strip()
    match = df[df['search_title'] == query_clean]
    if match.empty:
        match = df[df['search_title'].str.contains(query_clean, regex=False)]
    if match.empty:
        return None
        
    idx = match.index[0]
    tfidf = TfidfVectorizer(stop_words='english', max_features=10000)
    tfidf_matrix = tfidf.fit_transform(df['metadata_soup'].fillna(''))
    
    target_vec = tfidf_matrix[idx]
    cosine_sim = linear_kernel(target_vec, tfidf_matrix).flatten()
    top_indices = cosine_sim.argsort()[-(top_n + 1):-1][::-1]
    
    results = df.iloc[top_indices][['movieId', 'clean_title', 'year', 'genres_clean']].copy()
    results['similarity_score'] = cosine_sim[top_indices].round(4)
    return results

if __name__ == "__main__":
    t0 = time.time()
    input_path = os.path.join(os.path.dirname(__file__), "movies.csv")
    output_path = os.path.join(os.path.dirname(__file__), "movies_preprocessed.csv")
    
    print(f"Reading dataset from: {input_path}")
    df_raw = load_data(input_path)
    
    print(f"Running preprocessing on {len(df_raw):,} records...")
    df_clean = preprocess_movies(df_raw)
    
    print("Generating EDA report...")
    report = generate_eda_report(df_raw, df_clean)
    
    print(f"Saving preprocessed dataset to: {output_path}")
    # Export preprocessed CSV (excluding list column which can be recreated from genres_clean)
    export_df = df_clean.drop(columns=['genres_list'])
    export_df.to_csv(output_path, index=False, encoding='utf-8')
    
    print(f"Done in {time.time() - t0:.2f} seconds.")
    print("\n--- Summary Report ---")
    for k, v in report.items():
        if k != "genre_distribution":
            print(f"  {k}: {v}")
    print("\nTop 5 Genres:")
    for g, count in list(report["genre_distribution"].items())[:5]:
        print(f"  {g}: {count:,}")
