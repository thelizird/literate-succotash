export function SongClusters({ clusterStats, handleClusterClick }) {
    console.log('SongClusters render:', clusterStats);
    
    if (!clusterStats || clusterStats.length === 0) {
      return (
        <div className="mt-8">
          <h3 className="text-2xl font-bold mb-4">Song Clusters</h3>
          <p className="text-zinc-400">Loading clusters...</p>
        </div>
      );
    }

    // Add array of distinct colors for the playlists
    const playlistColors = [
        '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEEAD',
        '#D4A5A5', '#9B59B6', '#3498DB', '#E67E22', '#27AE60',
        '#E74C3C', '#F1C40F', '#1ABC9C'
    ];

    return (
      <div className="mt-8">
        <h3 className="text-2xl font-bold mb-4">Song Clusters</h3>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-2 justify-items-center">
          {clusterStats.map((stat, index) => (
            <div 
              key={stat.cluster_label}
              className="rounded-md border border-zinc-700 bg-zinc-800/50 p-4 cursor-pointer hover:bg-zinc-800 w-48 h-48 flex flex-col items-center justify-center text-center"
              onClick={() => handleClusterClick(stat.cluster_label)}
            >
              <svg 
                width="64" 
                height="64" 
                viewBox="0 0 32 32" 
                className="mb-4"
                style={{ fill: playlistColors[index % playlistColors.length] }}
              >
                <path d="M27.985,21.015l-0,-14c-0,-0.796 -0.316,-1.559 -0.879,-2.121c-0.562,-0.563 -1.325,-0.879 -2.121,-0.879c-3.463,0 -10.537,0 -14,0c-0.552,0 -1,0.448 -1,1c-0,0.552 0.448,1 1,1l14,0c0.265,0 0.519,0.105 0.707,0.293c0.188,0.188 0.293,0.442 0.293,0.707l-0,14c-0,0.552 0.448,1 1,1c0.552,0 1,-0.448 1,-1Z"/>
                <path d="M24,11c0,-0.796 -0.316,-1.559 -0.879,-2.121c-0.562,-0.563 -1.325,-0.879 -2.121,-0.879c-3.463,0 -10.537,0 -14,0c-0.796,-0 -1.559,0.316 -2.121,0.879c-0.563,0.562 -0.879,1.325 -0.879,2.121c-0,3.463 -0,10.537 -0,14c-0,0.796 0.316,1.559 0.879,2.121c0.562,0.563 1.325,0.879 2.121,0.879c3.463,0 10.537,0 14,0c0.796,0 1.559,-0.316 2.121,-0.879c0.563,-0.562 0.879,-1.325 0.879,-2.121l-0,-14Zm-14.005,9.003l-0.002,0c-1.105,0 -2.002,0.897 -2.002,2.002c0,1.105 0.897,2.002 2.002,2.002c1.105,-0 2.002,-0.897 2.002,-2.002l-0,-7.122c-0,-0 6.001,-0.75 6.001,-0.75l0.002,3.867c-1.104,0 -2.001,0.897 -2.001,2.002c-0,1.105 0.897,2.001 2.001,2.001c1.105,0 2.002,-0.896 2.002,-2.001l-0.005,-7.003c-0,-0.286 -0.124,-0.559 -0.339,-0.749c-0.215,-0.19 -0.501,-0.278 -0.785,-0.242l-8,1c-0.501,0.062 -0.876,0.488 -0.876,0.992l-0,6.003Z"/>
              </svg>
              <h5 className="text-lg font-semibold mb-2">Playlist {stat.cluster_label}</h5>
              <p className="text-zinc-400">{stat.count} songs</p>
            </div>
          ))}
        </div>
      </div>
    );
  }