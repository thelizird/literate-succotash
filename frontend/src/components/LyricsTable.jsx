export function LyricsTable({ lyrics, handleRowClick }) {
    return (
      <div className="rounded-md border border-zinc-700 overflow-hidden">
        <table className="w-full">
          <thead className="bg-zinc-800">
            <tr>
              <th className="text-left p-4 text-zinc-100 font-bold">ID</th>
              <th className="text-left p-4 text-zinc-100 font-bold">Artist</th>
              <th className="text-left p-4 text-zinc-100 font-bold">Title</th>
            </tr>
          </thead>
          <tbody>
            {lyrics.map(lyric => (
              <tr 
                key={lyric.id}
                onClick={() => handleRowClick(lyric)}
                className="hover:bg-zinc-800/50 cursor-pointer border-t border-zinc-700"
              >
                <td className="p-4 text-zinc-300">{lyric.id}</td>
                <td className="p-4 text-zinc-300">{lyric.artist}</td>
                <td className="p-4 text-zinc-300">{lyric.title}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }