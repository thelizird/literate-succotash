import { useState, useEffect, useCallback } from 'react';
import './App.css';
import { Header } from './components/Header';
import { Hero } from './components/Hero';
import { SearchBar } from './components/SearchBar';
import { LyricsTable } from './components/LyricsTable';
import { Pagination } from './components/Pagination';
import { SongClusters } from './components/SongClusters';
import { LyricDetails } from './components/LyricDetails';

function App() {
  // State declarations
  const [lyrics, setLyrics] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTitle, setSearchTitle] = useState('');
  const [selectedArtist, setSelectedArtist] = useState('');
  const [artists, setArtists] = useState([]);
  const [selectedLyric, setSelectedLyric] = useState(null);
  const [sentimentResults, setSentimentResults] = useState(null);
  const [analyzingLyrics, setAnalyzingLyrics] = useState(false);
  const [similarSongs, setSimilarSongs] = useState([]);
  const [loadingSimilar, setLoadingSimilar] = useState(false);
  const [clusterSongs, setClusterSongs] = useState(null);
  const [clusterStats, setClusterStats] = useState([]);
  const [showRecommender, setShowRecommender] = useState(false);
  const [recommendQuery, setRecommendQuery] = useState('');
  const [recommendations, setRecommendations] = useState([]);
  const [loadingRecommendations, setLoadingRecommendations] = useState(false);

  // Fetch lyrics
  const fetchLyrics = useCallback(async (page) => {
    setLoading(true);
    try {
      const response = await fetch(
        `http://localhost:8000/api/lyrics/?page=${page}&title=${searchTitle}&artist=${selectedArtist}`
      );
      const data = await response.json();
      setLyrics(data.results);
      setTotalPages(Math.ceil(data.count / 10));
    } catch (error) {
      console.error('Error fetching lyrics:', error);
    }
    setLoading(false);
  }, [searchTitle, selectedArtist]);

  // Fetch artists
  useEffect(() => {
    console.log('Fetching artists...');
    fetch('http://localhost:8000/api/lyrics/artists/')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Received artists:', data);
        setArtists(data);
      })
      .catch(error => {
        console.error('Error fetching artists:', error);
      });
  }, []);

  // Fetch cluster stats
  useEffect(() => {
    console.log('Fetching cluster stats...');
    fetch('http://localhost:8000/api/lyrics/cluster_stats/')
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        console.log('Received cluster stats:', data);
        setClusterStats(data);
      })
      .catch(error => {
        console.error('Error fetching cluster stats:', error);
      });
  }, []);

  // Fetch lyrics when page or filters change
  useEffect(() => {
    fetchLyrics(currentPage);
  }, [currentPage, fetchLyrics]);

  // Handlers
  const handleSearchChange = (e) => {
    setSearchTitle(e.target.value);
    setCurrentPage(1);
  };

  const handleArtistChange = (e) => {
    setSelectedArtist(e.target.value);
    setCurrentPage(1);
  };

  const handleRowClick = async (lyric) => {
    try {
      // Fetch complete song details first
      const response = await fetch(`http://localhost:8000/api/lyrics/${lyric.id}/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const completeData = await response.json();
      setSelectedLyric(completeData);  // Now includes the lyric field
      fetchSimilarSongs(lyric.id);
    } catch (error) {
      console.error('Error fetching complete song details:', error);
    }
  };

  const handleClusterClick = async (clusterId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/lyrics/cluster_songs/?cluster=${clusterId}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setClusterSongs({ cluster: clusterId, songs: data.songs });
    } catch (error) {
      console.error('Error fetching cluster songs:', error);
    }
  };

  const analyzeSentiment = async (lyricId) => {
    setAnalyzingLyrics(true);
    try {
      const response = await fetch(`http://localhost:8000/api/lyrics/${lyricId}/sentiment/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSentimentResults({
        scores: data.sentiment_scores,
        truncated: data.truncated
      });
    } catch (error) {
      console.error('Error analyzing sentiment:', error);
    }
    setAnalyzingLyrics(false);
  };

  const fetchSimilarSongs = async (lyricId) => {
    setLoadingSimilar(true);
    try {
      const response = await fetch(`http://localhost:8000/api/lyrics/${lyricId}/similar/`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      const data = await response.json();
      setSimilarSongs(data);
    } catch (error) {
      console.error('Error fetching similar songs:', error);
    }
    setLoadingSimilar(false);
  };

  const handleRecommendations = async (e) => {
    e.preventDefault();
    setLoadingRecommendations(true);
    try {
      const response = await fetch('http://localhost:8000/api/lyrics/recommend/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query: recommendQuery }),
      });
      const data = await response.json();
      setRecommendations(data);
    } catch (error) {
      console.error('Error getting recommendations:', error);
    }
    setLoadingRecommendations(false);
  };

  return (
    <div className="min-h-screen bg-zinc-900 text-zinc-100">
      <Header />
      <Hero />
      <div className="max-w-7xl mx-auto p-8">
        <div className="mb-8">
          <button
            className="bg-zinc-800 text-zinc-100 px-4 py-2 rounded-md hover:bg-zinc-700 mb-3"
            onClick={() => setShowRecommender(!showRecommender)}
          >
            {showRecommender ? 'Hide Recommender' : 'Show Song Recommender'}
          </button>
          
          {showRecommender && (
            <div className="bg-zinc-800 p-4 rounded-lg">
              <form onSubmit={handleRecommendations} className="mb-4">
                <input
                  type="text"
                  value={recommendQuery}
                  onChange={(e) => setRecommendQuery(e.target.value)}
                  placeholder="Describe the type of song you're looking for..."
                  className="w-full p-2 rounded bg-zinc-700 text-zinc-100"
                />
                <button
                  type="submit"
                  className="mt-2 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
                  disabled={loadingRecommendations}
                >
                  {loadingRecommendations ? 'Finding Songs...' : 'Get Recommendations'}
                </button>
              </form>
              
              {recommendations.length > 0 && (
                <div>
                  <h3 className="text-xl font-bold mb-2">Recommended Songs</h3>
                  <table className="w-full">
                    <thead>
                      <tr className="text-left">
                        <th className="p-2">Artist</th>
                        <th className="p-2">Title</th>
                        <th className="p-2">Match Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recommendations.map((song) => (
                        <tr
                          key={song.id}
                          className="hover:bg-zinc-700 cursor-pointer"
                          onClick={() => handleRowClick(song)}
                        >
                          <td className="p-2">{song.artist}</td>
                          <td className="p-2">{song.title}</td>
                          <td className="p-2">{(song.similarity_score * 100).toFixed(1)}%</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          )}
        </div>
        
        {selectedLyric ? (
          <LyricDetails 
            selectedLyric={selectedLyric}
            sentimentResults={sentimentResults}
            analyzingLyrics={analyzingLyrics}
            similarSongs={similarSongs}
            loadingSimilar={loadingSimilar}
            onBack={() => {
              setSelectedLyric(null);
              setSentimentResults(null);
            }}
            onAnalyze={analyzeSentiment}
            onSimilarSongClick={(id) => {
              fetch(`http://localhost:8000/api/lyrics/${id}/`)
                .then(response => response.json())
                .then(data => {
                  setSelectedLyric(data);
                  fetchSimilarSongs(data.id);
                })
                .catch(error => {
                  console.error('Error fetching song details:', error);
                });
            }}
          />
        ) : clusterSongs ? (
          <>
            <button 
              className="bg-zinc-800 text-zinc-100 px-4 py-2 rounded-md hover:bg-zinc-700 mb-3"
              onClick={() => {
                setClusterSongs(null);
                fetchLyrics(currentPage);
              }}
            >
              Back to List
            </button>
            <h2 className="text-2xl font-bold mb-4">Cluster {clusterSongs.cluster} Songs</h2>
            <LyricsTable lyrics={clusterSongs.songs} handleRowClick={handleRowClick} />
          </>
        ) : (
          <>
            <SearchBar 
              searchTitle={searchTitle}
              selectedArtist={selectedArtist}
              artists={artists}
              handleSearchChange={handleSearchChange}
              handleArtistChange={handleArtistChange}
            />
            
            {loading ? (
              <p className="text-zinc-400">Loading...</p>
            ) : (
              <>
                <LyricsTable lyrics={lyrics} handleRowClick={handleRowClick} />
                <Pagination 
                  currentPage={currentPage}
                  totalPages={totalPages}
                  setCurrentPage={setCurrentPage}
                />
              </>
            )}
            
            <SongClusters 
              clusterStats={clusterStats}
              handleClusterClick={handleClusterClick}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;