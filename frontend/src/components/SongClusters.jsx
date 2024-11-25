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

    return (
      <div className="mt-8">
        <h3 className="text-2xl font-bold mb-4">Song Clusters</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {clusterStats.map((stat) => (
            <div 
              key={stat.cluster_label}
              className="rounded-md border border-zinc-700 bg-zinc-800/50 p-4 cursor-pointer hover:bg-zinc-800"
              onClick={() => handleClusterClick(stat.cluster_label)}
            >
              <h5 className="text-lg font-semibold mb-2">Cluster {stat.cluster_label}</h5>
              <p className="text-zinc-400">{stat.count} songs</p>
            </div>
          ))}
        </div>
      </div>
    );
  }