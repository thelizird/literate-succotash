import sys
import os

# Add the backend directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_dir = os.path.join(current_dir, 'backend')
sys.path.append(backend_dir)

import django
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
import matplotlib
matplotlib.use('Agg')  # Set the backend to non-interactive
import matplotlib.pyplot as plt

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

# Import after Django setup
from api.models import Lyrics

def calculate_elbow_score(inertias):
    """Calculate the rate of change in inertia to help identify the elbow point"""
    inertia_changes = np.diff(inertias)
    change_in_changes = np.diff(inertia_changes)
    return change_in_changes

def perform_elbow_test():
    # Fetch data from database
    lyrics_data = list(Lyrics.objects.all().values('id', 'clean_lyrics'))
    df = pd.DataFrame(lyrics_data)
    
    print(f"Processing {len(df)} lyrics records...")
    
    # Perform TF-IDF vectorization
    vectorizer = TfidfVectorizer(max_df=0.8, min_df=3, ngram_range=(1, 2))
    tfidf_matrix = vectorizer.fit_transform(df['clean_lyrics'].fillna(''))
    
    # Perform elbow test
    inertias = []
    K = range(2, 21)  # Test from 2 to 20 clusters
    
    print("Performing elbow test...")
    for k in K:
        print(f"Testing k={k}")
        km = KMeans(
            n_clusters=k,
            max_iter=10000,
            n_init=10,
            random_state=42
        )
        km.fit(tfidf_matrix)
        inertias.append(km.inertia_)
    
    # Plot the elbow curve
    plt.figure(figsize=(10, 6))
    plt.plot(K, inertias, 'bx-')
    plt.xlabel('Number of Clusters (k)')
    plt.ylabel('Inertia')
    plt.title('Elbow Method For Optimal k')
    plt.grid(True)
    
    # Save the plot with high DPI for better quality
    plot_path = os.path.join(current_dir, 'elbow_test.png')
    plt.savefig(plot_path, dpi=300, bbox_inches='tight')
    print(f"\nElbow curve has been saved as: {plot_path}")
    
    # Calculate and print the analysis
    print("\nAnalysis:")
    print("----------")
    print("Inertia values:")
    for k, inertia in zip(K, inertias):
        print(f"k={k}: {inertia:,.2f}")
    
    # Calculate percentage decrease
    print("\nPercentage decrease in inertia:")
    for i in range(1, len(inertias)):
        decrease = ((inertias[i-1] - inertias[i]) / inertias[i-1]) * 100
        print(f"From k={K[i-1]} to k={K[i]}: {decrease:.2f}%")
    
    # Suggest optimal k based on rate of change
    changes = calculate_elbow_score(inertias)
    suggested_k = K[np.argmin(changes) + 1]
    print(f"\nBased on the rate of change analysis, the suggested number of clusters is: {suggested_k}")
    print("\nNote: Please review the elbow_test.png plot to confirm this suggestion visually.")

if __name__ == "__main__":
    perform_elbow_test()