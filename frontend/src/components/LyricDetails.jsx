export function LyricDetails({ 
    selectedLyric, 
    sentimentResults, 
    analyzingLyrics, 
    similarSongs, 
    loadingSimilar,
    onBack,
    onAnalyze,
    onSimilarSongClick 
  }) {
    return (
      <>
        <button 
          className="bg-zinc-800 text-zinc-100 px-4 py-2 rounded-md hover:bg-zinc-700 mb-3"
          onClick={onBack}
        >
          Back to List
        </button>
        <div className="rounded-md border border-zinc-700 bg-zinc-800/50 p-6">
          <h2 className="text-2xl font-bold mb-2">{selectedLyric.title}</h2>
          <h4 className="text-zinc-400 mb-4">by {selectedLyric.artist}</h4>
          <p className="text-zinc-500">ID: {selectedLyric.id}</p>
          
          <button 
            className="bg-zinc-700 text-zinc-100 px-4 py-2 rounded-md hover:bg-zinc-600 mb-3"
            onClick={() => onAnalyze(selectedLyric.id)}
            disabled={analyzingLyrics}
          >
            {analyzingLyrics ? 'Analyzing...' : 'Analyze Sentiment'}
          </button>
  
          {/* Sentiment Results Section */}
          {sentimentResults && (
            <div className="bg-zinc-800 rounded-md p-4 mb-4">
              <h5 className="font-bold mb-2">Sentiment Analysis Results:</h5>
              {sentimentResults.truncated && (
                <p className="text-yellow-400 mb-2">
                  Note: Lyrics were truncated for analysis due to length
                </p>
              )}
              {sentimentResults.scores.map(score => (
                <div key={score.label} className="text-zinc-300">
                  {score.label}: {(score.score * 100).toFixed(1)}%
                </div>
              ))}
            </div>
          )}
  
          {/* Similar Songs Section */}
          {loadingSimilar ? (
            <div className="text-zinc-400">Loading similar songs...</div>
          ) : similarSongs.length > 0 && (
            <div className="border border-zinc-700 rounded-md p-4 mb-4">
              <h5 className="font-bold mb-2">Similar Songs:</h5>
              <div className="space-y-2">
                {similarSongs.map(song => (
                  <button
                    key={song.similar_song_id}
                    className="w-full text-left p-3 rounded-md bg-zinc-800 hover:bg-zinc-700"
                    onClick={() => onSimilarSongClick(song.similar_song_id)}
                  >
                    <div className="flex justify-between items-center">
                      <div>
                        <strong>{song.title}</strong> by {song.artist}
                      </div>
                      <small>
                        Similarity: {(song.similarity_score * 100).toFixed(1)}%
                      </small>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}
  
          <hr className="border-zinc-700 my-4" />
          <pre className="text-zinc-300 whitespace-pre-wrap">
            {selectedLyric.lyric}
          </pre>
        </div>
      </>
    );
  }