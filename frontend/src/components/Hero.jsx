export function Hero() {
    return (
      <div className="bg-zinc-900 py-12">
        <div className="container mx-auto px-4 flex justify-center">
          <img 
            src="/lyrify.jpeg" 
            alt="Lyrify Logo" 
            className="max-w-md w-full h-auto"  // adjust max-w-md to control image size
          />
        </div>
      </div>
    );
  }