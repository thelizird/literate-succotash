import sqlite3
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer

# Connect to your SQLite database
db_path = 'backend/db.sqlite3'
conn = sqlite3.connect(db_path)

# First, drop the existing table if it exists
conn.execute("DROP TABLE IF EXISTS song_similarities")
conn.commit()

# Read lyrics data
query = "SELECT CAST(id AS INTEGER) as id, clean_lyrics FROM lyrics"
df = pd.read_sql_query(query, conn, index_col='id')

# Create TF-IDF matrix (recomputing it here, but you could also load from tfidf_features if needed)
vectorizer = TfidfVectorizer(max_df=0.8, min_df=3, ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(df['clean_lyrics'].fillna(''))

# Compute cosine similarity
doc_sim = cosine_similarity(tfidf_matrix)

# Create the similarities table
create_table_query = """
CREATE TABLE IF NOT EXISTS song_similarities (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    song_id1 INTEGER NOT NULL,
    song_id2 INTEGER NOT NULL,
    similarity_score REAL NOT NULL,
    FOREIGN KEY (song_id1) REFERENCES lyrics (id),
    FOREIGN KEY (song_id2) REFERENCES lyrics (id)
)
"""
conn.execute(create_table_query)

# Prepare data for insertion
data_to_insert = []
threshold = 0.0  # Adjust this to filter out low similarities if desired

# Get original song IDs
song_ids = df.index.tolist()

# Iterate through the similarity matrix
for i in range(len(doc_sim)):
    for j in range(i + 1):  # Only store lower triangle including diagonal
        similarity = doc_sim[i, j]
        if similarity > threshold:
            data_to_insert.append((
                int(song_ids[i]),  # song_id1
                int(song_ids[j]),  # song_id2
                float(similarity)   # similarity_score
            ))

# Insert data in batches
batch_size = 1000
for i in range(0, len(data_to_insert), batch_size):
    batch = data_to_insert[i:i + batch_size]
    conn.executemany(
        "INSERT INTO song_similarities (song_id1, song_id2, similarity_score) VALUES (?, ?, ?)",
        batch
    )
    conn.commit()

# Create indices for better query performance
conn.execute("CREATE INDEX IF NOT EXISTS idx_song_id1 ON song_similarities (song_id1)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_song_id2 ON song_similarities (song_id2)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_similarity ON song_similarities (similarity_score)")

# Verify some data
cursor = conn.cursor()
cursor.execute("""
SELECT s.*, l1.title as song1_title, l2.title as song2_title 
FROM song_similarities s
JOIN lyrics l1 ON s.song_id1 = l1.id
JOIN lyrics l2 ON s.song_id2 = l2.id
LIMIT 5
""")
print("\nVerifying first 5 rows:")
for row in cursor.fetchall():
    print(row)

conn.close()

print("Song similarities have been successfully stored in the database.")