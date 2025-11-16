import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neighbors import NearestNeighbors

# ---------- Load dataset ----------
books = pd.read_csv("data/Books.csv", low_memory=False)

# Make safe columns
books['Book-Title'] = books.get('Book-Title', books.columns[0]).astype(str)
books['Book-Author'] = books.get('Book-Author', '').astype(str)
books['ISBN'] = books.get('ISBN', '').astype(str)

# Combined text for recommendation
books['combined'] = (books['Book-Title'].fillna('') + " " +
                     books['Book-Author'].fillna('')).astype(str)

# TF-IDF
tfidf = TfidfVectorizer(stop_words='english', max_features=40000)
tfidf_matrix = tfidf.fit_transform(books['combined'])

# ✅ ✅ MEMORY SAFE KNN MODEL
knn = NearestNeighbors(metric='cosine', algorithm='brute')
knn.fit(tfidf_matrix)

# Autocomplete list
titles_list = books['Book-Title'].astype(str).tolist()

# ---------- CATEGORY CLUSTERING ----------
from sklearn.cluster import KMeans

N_CLUSTERS = 6
kmeans = KMeans(n_clusters=N_CLUSTERS, random_state=42, n_init=10)
kmeans.fit(tfidf_matrix)

books['cluster'] = kmeans.labels_

def get_cluster_names(vectorizer=tfidf, model=kmeans, n_terms=3):
    terms = vectorizer.get_feature_names_out()
    names = {}
    centroids = model.cluster_centers_
    for i, c in enumerate(centroids):
        top_idx = c.argsort()[-n_terms:][::-1]
        names[i] = " / ".join([terms[j] for j in top_idx])
    return names

cluster_names = get_cluster_names()

# ---------- RECOMMENDATION ----------
def recommend_by_title(title, k=6):
    title = str(title).strip().lower()
    books['search_title'] = books['Book-Title'].str.lower()

    # exact match
    if title in books['search_title'].values:
        index = int(books[books['search_title'] == title].index[0])
    else:
        # partial match fallback
        matches = books[books['search_title'].str.contains(title, na=False)]
        if matches.empty:
            return []
        index = int(matches.index[0])

    # ✅ Use KNN instead of full cosine_similarity
    distances, indices = knn.kneighbors(tfidf_matrix[index], n_neighbors=k)

    results = []
    for idx in indices[0][1:]:  # skip itself
        results.append({
            "Book-Title": books.iloc[idx]["Book-Title"],
            "Book-Author": books.iloc[idx]["Book-Author"],
            "ISBN": books.iloc[idx]["ISBN"],
            "cluster": int(books.iloc[idx]["cluster"]),
            "cluster_name": cluster_names[int(books.iloc[idx]["cluster"])]
        })
    return results

# ---------- Similar Authors ----------
def similar_authors(author, top_n=6):
    grouped = books.groupby('Book-Author')['Book-Title'] \
                   .apply(lambda s: ' '.join(s.astype(str))).reset_index()
    grouped.columns = ['author', 'titles']

    # TF-IDF for authors
    vectorizer = TfidfVectorizer(stop_words='english')
    mat = vectorizer.fit_transform(grouped['titles'])

    # find author index
    mask = grouped['author'].str.lower().str.contains(author.lower())
    if mask.sum() == 0:
        return []

    author_index = mask.idxmax()

    # KNN again (memory safe)
    knn_auth = NearestNeighbors(metric='cosine', algorithm='brute')
    knn_auth.fit(mat)

    dist, idxs = knn_auth.kneighbors(mat[author_index], n_neighbors=top_n)
    result = []
    for i in idxs[0][1:]:
        result.append({
            "author": grouped.iloc[i]['author'],
            "score": float(1 - dist[0][1])  # optional similarity
        })
    return result

# ---------- Autocomplete ----------
def autocomplete_titles(q, limit=10):
    q = q.lower().strip()
    if q == "":
        return []
    return [t for t in titles_list if q in t.lower()][:limit]

# ---------- AI Categories ----------
def get_categories_summary():
    summary = []
    for c in range(N_CLUSTERS):
        sample = books[books['cluster'] == c]['Book-Title'].head(6).tolist()
        summary.append({
            "cluster": c,
            "name": cluster_names[c],
            "count": int((books['cluster'] == c).sum()),
            "sample": sample
        })
    return summary

# ---------- Trending ----------
def trending_books(n=10):
    return books.sample(n)[["Book-Title", "Book-Author"]].to_dict(orient="records")
