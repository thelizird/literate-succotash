import sqlite3
import csv
import os

def import_lyrics(csv_file_path, db_path):
    # Connect to SQLite database using the full path
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS lyrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            artist TEXT,
            title TEXT,
            lyric TEXT
        )
    ''')
    
    # Clear existing data (optional)
    cursor.execute('DELETE FROM lyrics')
    
    # Read and import CSV
    with open(csv_file_path, 'r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        
        batch = []
        count = 0
        
        for row in csv_reader:
            batch.append((
                row['Artist'],
                row['Title'],
                row['Lyric']
            ))
            
            # Insert in batches of 1000
            if len(batch) >= 1000:
                cursor.executemany('INSERT INTO lyrics (artist, title, lyric) VALUES (?, ?, ?)', batch)
                conn.commit()
                batch = []
                count += 1000
                print(f'Imported {count} records...')
        
        # Insert any remaining records
        if batch:
            cursor.executemany('INSERT INTO lyrics (artist, title, lyric) VALUES (?, ?, ?)', batch)
            conn.commit()
            count += len(batch)
    
    print('Successfully imported lyrics data')
    print(f'Total records imported: {count}')
    
    conn.close()

# Define exact file paths
csv_file_path = '/Users/owenmendiola/Desktop/2Brain/Projects/DATA_5420/mvpapp/clean_consolidated_lyrics.csv'
db_path = '/Users/owenmendiola/Desktop/2Brain/Projects/DATA_5420/mvpapp/backend/db.sqlite3'

# Run the import
if __name__ == '__main__':
    import_lyrics(csv_file_path, db_path)