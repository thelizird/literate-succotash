import sqlite3
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

# Connect to your SQLite database
db_path = 'backend/db.sqlite3'
conn = sqlite3.connect(db_path)

# First, drop the existing table if it exists
conn.execute("DROP TABLE IF EXISTS tfidf_features")
conn.commit()

# Read lyrics data - explicitly convert id to integer
query = "SELECT CAST(id AS INTEGER) as id, clean_lyrics FROM lyrics"
df = pd.read_sql_query(query, conn, index_col='id')

# Fill NaN values and create TF-IDF matrix
vectorizer = TfidfVectorizer(max_df=0.8, min_df=3, ngram_range=(1, 2))
tfidf_matrix = vectorizer.fit_transform(df['clean_lyrics'].fillna(''))

# Get feature names
feature_names = vectorizer.get_feature_names_out()

# Create the tfidf_features table with explicit INTEGER type
create_table_query = """
CREATE TABLE IF NOT EXISTS tfidf_features (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lyric_id INTEGER NOT NULL,
    feature_name TEXT NOT NULL,
    tfidf_value REAL NOT NULL,
    FOREIGN KEY (lyric_id) REFERENCES lyrics (id)
)
"""
conn.execute(create_table_query)

# Convert sparse matrix to coordinate format
coo = tfidf_matrix.tocoo()

# Prepare data for insertion
data_to_insert = []
for i, j, v in zip(coo.row, coo.col, coo.data):
    # Only store non-zero values
    if v > 0:
        original_id = int(df.index[i])  # Explicitly cast to int
        data_to_insert.append((
            original_id,      # lyric_id
            feature_names[j], # feature_name
            float(v)         # tfidf_value
        ))

# Insert data in batches
batch_size = 1000
for i in range(0, len(data_to_insert), batch_size):
    batch = data_to_insert[i:i + batch_size]
    conn.executemany(
        "INSERT INTO tfidf_features (lyric_id, feature_name, tfidf_value) VALUES (?, ?, ?)",
        batch
    )
    conn.commit()

# Create indices for better query performance
conn.execute("CREATE INDEX IF NOT EXISTS idx_lyric_id ON tfidf_features (lyric_id)")
conn.execute("CREATE INDEX IF NOT EXISTS idx_feature_name ON tfidf_features (feature_name)")

# Verify some data
cursor = conn.cursor()
cursor.execute("SELECT * FROM tfidf_features LIMIT 5")
print("\nVerifying first 5 rows:")
for row in cursor.fetchall():
    print(row)

conn.close()

print("TF-IDF features have been successfully stored in the database.")