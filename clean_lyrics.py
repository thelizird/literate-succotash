import sqlite3
import sys
import os
import re
import contractions
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

# Download all required NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('punkt_tab')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')

def clean_lyrics(text):
    # Convert to lowercase
    text = text.lower()

    # Expand contractions
    text = contractions.fix(text)

    # Remove all special characters (including apostrophes)
    text = re.sub(r'[^a-z\s]', ' ', text)

    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)

    # Custom stopwords for lyrics
    custom_stopwords = set(stopwords.words('english')) - {'i', 'me', 'my', 'myself',
                                                         'you', 'your', 'yours',
                                                         'he', 'she', 'it',
                                                         'no', 'not', 'never'}
    additional_stopwords = {'la', 'oh', 'ooh', 'yeah', 'na', 'uh', 'woah', 'ah', 'hey', 'baby', 'whoa'}
    custom_stopwords.update(additional_stopwords)

    # Tokenize and remove stopwords
    tokens = word_tokenize(text)
    tokens = [word for word in tokens if word not in custom_stopwords]

    # Join tokens back into text
    text = ' '.join(tokens)

    # Final cleanup of any remaining whitespace
    text = text.strip()

    return text

def main():
    # Path to your SQLite database
    db_path = 'backend/db.sqlite3'
    
    # First, alter the table to add the new column if it doesn't exist
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(lyrics)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'clean_lyrics' not in columns:
            cursor.execute("ALTER TABLE lyrics ADD COLUMN clean_lyrics TEXT")
            print("Added clean_lyrics column to the table")
        
        # Get all lyrics
        cursor.execute("SELECT id, lyric FROM lyrics")
        lyrics_data = cursor.fetchall()
        
        # Update each record with cleaned lyrics
        for lyric_id, lyric in lyrics_data:
            if lyric:
                clean_lyric = clean_lyrics(lyric)
                cursor.execute(
                    "UPDATE lyrics SET clean_lyrics = ? WHERE id = ?",
                    (clean_lyric, lyric_id)
                )
                print(f"Updated lyrics ID: {lyric_id}")
        
        conn.commit()
        print("All lyrics have been cleaned and updated")
        
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    main()