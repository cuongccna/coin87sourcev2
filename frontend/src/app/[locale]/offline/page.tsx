'use client'

export default function Offline() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
      <div className="text-center max-w-md">
        <div className="w-24 h-24 mx-auto mb-6 bg-primary rounded-full flex items-center justify-center text-4xl font-bold text-slate-900">
          C87
        </div>
        
        <h1 className="text-2xl font-bold text-slate-100 mb-2">
          You're Offline
        </h1>
        
        <p className="text-slate-400 mb-6">
          No internet connection. Don't worry, you can still browse cached news.
        </p>
        
        <button
          onClick={() => window.location.reload()}
          className="btn btn-primary"
        >
          Try Again
        </button>
      </div>
    </div>
  )
}
