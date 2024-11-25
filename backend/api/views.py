from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers
from rest_framework.decorators import action
from django.db.models import Q
from .models import Lyrics, SongSimilarity
from transformers import pipeline, AutoTokenizer
from django.shortcuts import get_object_or_404
from .serializers import LyricsSerializer
from django.db import connection
from django.db.models import Count
import random

# Create your views here.

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello, World!"})

class LyricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lyrics
        fields = ['id', 'artist', 'title', 'lyric', 'clean_lyrics']

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 15
    page_size_query_param = 'page_size'
    max_page_size = 100

# Initialize both tokenizer and sentiment analyzer
tokenizer = AutoTokenizer.from_pretrained("siebert/sentiment-roberta-large-english")
sentiment_analyzer = pipeline(
    "sentiment-analysis",
    model="siebert/sentiment-roberta-large-english",
    return_all_scores=True
)

class LyricsViewSet(viewsets.ModelViewSet):
    queryset = Lyrics.objects.all().order_by('id')
    serializer_class = LyricsSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        queryset = Lyrics.objects.all().order_by('id')
        search = self.request.query_params.get('search', None)
        artist = self.request.query_params.get('artist', None)

        if search:
            queryset = queryset.filter(title__icontains=search)
        if artist:
            queryset = queryset.filter(artist=artist)

        return queryset

    @action(detail=False, methods=['get'])
    def artists(self, request):
        artists = Lyrics.objects.values_list('artist', flat=True).distinct().order_by('artist')
        return Response(list(artists))

    @action(detail=True, methods=['get'])
    def sentiment(self, request, pk=None):
        lyric = self.get_object()
        if not lyric.clean_lyrics:
            return Response({"error": "No cleaned lyrics available"}, status=400)
        
        try:
            # Tokenize and truncate the text
            tokens = tokenizer(lyric.clean_lyrics, 
                             truncation=True, 
                             max_length=510, 
                             return_tensors="pt")
            
            # Convert truncated tokens back to text
            truncated_text = tokenizer.decode(tokens['input_ids'][0], 
                                            skip_special_tokens=True)
            
            # Analyze sentiment of truncated text
            results = sentiment_analyzer(truncated_text)[0]
            
            return Response({
                "sentiment_scores": results,
                "truncated": len(lyric.clean_lyrics) != len(truncated_text)
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=True, methods=['get'])
    def similar(self, request, pk=None):
        try:
            # Use direct SQL query with cursor for better control
            with connection.cursor() as cursor:
                cursor.execute('''
                    SELECT 
                        CASE 
                            WHEN ss.song_id1 = %s THEN ss.song_id2
                            ELSE ss.song_id1
                        END as similar_song_id,
                        l.title,
                        l.artist,
                        ss.similarity_score
                    FROM song_similarities ss
                    JOIN lyrics l ON (
                        CASE 
                            WHEN ss.song_id1 = %s THEN ss.song_id2
                            ELSE ss.song_id1
                        END = l.id
                    )
                    WHERE (ss.song_id1 = %s OR ss.song_id2 = %s)  -- Check both directions
                    AND ss.similarity_score > 0  -- Ensure non-zero similarity
                    AND ss.song_id1 != ss.song_id2  -- Exclude self-similarity
                    ORDER BY ss.similarity_score DESC
                    LIMIT 5
                ''', [pk, pk, pk, pk])  # Pass pk four times for the different conditions
                
                # Convert the results to dictionaries
                columns = [col[0] for col in cursor.description]
                results = [
                    dict(zip(columns, row))
                    for row in cursor.fetchall()
                ]

                # Convert similarity scores to float
                for result in results:
                    result['similarity_score'] = float(result['similarity_score'])
                    
                # Debug information
                print(f"Found {len(results)} similar songs for song_id {pk}")
                if len(results) < 5:
                    # Check why we got fewer results
                    cursor.execute('''
                        SELECT COUNT(*) 
                        FROM song_similarities 
                        WHERE (song_id1 = %s OR song_id2 = %s)
                        AND similarity_score > 0
                    ''', [pk, pk])
                    total_similarities = cursor.fetchone()[0]
                    print(f"Total similarities found in database: {total_similarities}")
                
                return Response(results)
            
        except Exception as e:
            import traceback
            print(f"Error in similar songs endpoint: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {"error": "Failed to fetch similar songs", "details": str(e)}, 
                status=500
            )

    @action(detail=False, methods=['get'])
    def cluster_songs(self, request):
        cluster_num = request.query_params.get('cluster', None)
        if cluster_num is None:
            return Response({"error": "Cluster number is required"}, status=400)
        
        try:
            # Get 20 random songs from the specified cluster
            songs = list(Lyrics.objects.filter(
                cluster_label=cluster_num
            ).values('id', 'artist', 'title', 'lyric', 'clean_lyrics')[:100])  # Added 'lyric' and 'clean_lyrics'
            
            # Randomly select 20 songs
            selected_songs = random.sample(songs, min(20, len(songs)))
            
            return Response({
                "cluster": cluster_num,
                "songs": selected_songs
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)

    @action(detail=False, methods=['get'])
    def cluster_stats(self, request):
        # Get counts for each cluster
        stats = Lyrics.objects.values('cluster_label').annotate(
            count=Count('id')
        ).order_by('cluster_label')
        
        return Response(list(stats))

    @action(detail=False, methods=['post'])
    def recommend(self, request):
        query = request.data.get('query', '')
        recommendations = self.queryset.model.get_recommendations(query)
        return Response(recommendations)

@api_view(['GET'])
def get_similar_songs(request, pk):
    # Get the top 5 most similar songs
    similar_songs = SongSimilarity.objects.filter(
        song_id1=pk
    ).select_related(
        'song_id2'
    ).order_by(
        '-similarity_score'
    )[:5]
    
    # Format the response
    results = [{
        'song_id2': sim.song_id2.id,
        'title': sim.song_id2.title,
        'artist': sim.song_id2.artist,
        'similarity_score': sim.similarity_score
    } for sim in similar_songs]
    
    return Response(results)

@api_view(['POST'])
def recommend_songs(request):
    query = request.data.get('query', '')
    recommendations = Lyrics.get_recommendations(query)
    return Response(recommendations)
