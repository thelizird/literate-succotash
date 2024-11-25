export function SearchBar({ searchTitle, selectedArtist, artists, handleSearchChange, handleArtistChange }) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
        <input
          type="text"
          className="bg-zinc-800 text-zinc-100 rounded-md border border-zinc-700 p-2 w-full placeholder-zinc-400"
          placeholder="Search song titles..."
          value={searchTitle}
          onChange={handleSearchChange}
        />
        <select
          className="bg-zinc-800 text-zinc-100 rounded-md border border-zinc-700 p-2 w-full"
          value={selectedArtist}
          onChange={handleArtistChange}
        >
          <option value="">Filter by artist</option>
          {artists.map(artist => (
            <option key={artist} value={artist}>
              {artist}
            </option>
          ))}
        </select>
      </div>
    );
  }