from django.db import models
from django.db.models import Sum
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import numpy as np

class Lyrics(models.Model):
    id = models.AutoField(primary_key=True)
    artist = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    lyric = models.TextField()
    clean_lyrics = models.TextField(null=True, blank=True)
    cluster_label = models.IntegerField(null=True, blank=True)

    class Meta:
        db_table = 'lyrics'
        managed = False

    def __str__(self):
        return f"{self.artist} - {self.title}"

    @classmethod
    def get_recommendations(cls, query_text):
        # Get all unique feature names
        feature_names = TfidfFeature.objects.values_list(
            'feature_name', flat=True).distinct()
        
        # Create vectorizer with known vocabulary
        vectorizer = TfidfVectorizer(vocabulary=set(feature_names))
        
        # Transform query text
        query_vector = vectorizer.fit_transform([query_text])
        
        # Get all songs with their TF-IDF features
        songs = list(cls.objects.all())
        song_vectors = []
        
        for song in songs:
            features = dict(song.tfidffeature_set.values_list('feature_name', 'tfidf_value'))
            vector = [features.get(feature, 0) for feature in feature_names]
            song_vectors.append(vector)
        
        # Convert to numpy array
        song_vectors = np.array(song_vectors)
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, song_vectors)[0]
        
        # Get top 5 most similar songs
        top_indices = np.argsort(similarities)[-5:][::-1]
        
        results = []
        for idx in top_indices:
            song = songs[int(idx)]
            results.append({
                'id': song.id,
                'artist': song.artist,
                'title': song.title,
                'similarity_score': float(similarities[idx])
            })
        
        return results


class TfidfFeature(models.Model):
    lyric = models.ForeignKey(Lyrics, on_delete=models.CASCADE)
    feature_name = models.CharField(max_length=255)
    tfidf_value = models.FloatField()

    class Meta:
        db_table = 'tfidf_features'
        managed = False


class SongSimilarity(models.Model):
    song_id1 = models.ForeignKey(
        'Lyrics',
        on_delete=models.CASCADE,
        db_column='song_id1',
        related_name='similarities_as_song1'
    )
    song_id2 = models.ForeignKey(
        'Lyrics',
        on_delete=models.CASCADE,
        db_column='song_id2',
        related_name='similarities_as_song2'
    )
    similarity_score = models.FloatField()

    class Meta:
        db_table = 'song_similarities'
        managed = False

    def __str__(self):
        return f"{self.song_id1.title} - {self.song_id2.title}: {self.similarity_score}"

