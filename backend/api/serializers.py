from rest_framework import serializers
from .models import Lyrics

class LyricsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Lyrics
        fields = ['id', 'title', 'artist', 'lyric', 'clean_lyrics']
