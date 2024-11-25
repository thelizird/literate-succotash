import sys
import os

# Add the backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.append(backend_dir)

import django
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from collections import Counter

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import after Django setup
from api.models import Lyrics

def apply_clustering():
    # Fetch data from database
    lyrics_data = list(Lyrics.objects.all().values('id', 'clean_lyrics'))
    df = pd.DataFrame(lyrics_data)
    
    print(f"Processing {len(df)} lyrics records...")
    
    # Perform TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_df=0.8, min_df=3, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(df['clean_lyrics'].fillna(''))
    
    # Perform KMeans clustering
    km = KMeans(
        n_clusters=13,
        max_iter=10000,
        n_init=50,
        random_state=42
    ).fit(tfidf_matrix)
    
    # Create a dictionary mapping id to cluster label
    cluster_assignments = dict(zip(df['id'], km.labels_))
    
    # Print cluster distribution
    print("Cluster distribution:", Counter(km.labels_))
    
    # Update database records
    print("Updating database records...")
    
    # First, add cluster column if it doesn't exist
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE lyrics 
                ADD COLUMN cluster_label INTEGER DEFAULT NULL
            """)
    except Exception as e:
        print("Column might already exist or other error:", e)
    
    # Update records with cluster labels
    for lyric_id, cluster_label in cluster_assignments.items():
        Lyrics.objects.filter(id=lyric_id).update(cluster_label=cluster_label)
    
    print("Clustering complete and labels saved to database!")

if __name__ == "__main__":
    apply_clustering()