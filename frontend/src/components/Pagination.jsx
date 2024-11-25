export function Pagination({ currentPage, totalPages, setCurrentPage }) {
    return (
      <div className="flex items-center justify-center gap-4 mt-6">
        <button 
          onClick={() => setCurrentPage(prev => prev - 1)}
          disabled={currentPage === 1}
          className="bg-zinc-800 text-zinc-100 px-4 py-2 rounded-md hover:bg-zinc-700 disabled:opacity-50"
        >
          Previous
        </button>
        <span className="text-zinc-400">
          Page {currentPage} of {totalPages}
        </span>
        <button 
          onClick={() => setCurrentPage(prev => prev + 1)}
          disabled={currentPage === totalPages}
          className="bg-zinc-800 text-zinc-100 px-4 py-2 rounded-md hover:bg-zinc-700 disabled:opacity-50"
        >
          Next
        </button>
      </div>
    );
  }