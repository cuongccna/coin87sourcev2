'use client'

export default function Error({
  error,
  reset,
}: {
  error: Error & { digest?: string }
  reset: () => void
}) {
  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 p-4">
      <div className="text-center max-w-md">
        <h2 className="text-2xl font-bold text-red-500 mb-4">Something went wrong!</h2>
        <pre className="text-left bg-slate-900 p-4 rounded text-sm text-slate-300 mb-4 overflow-auto">
          {error.message}
          {error.stack && (
            <div className="mt-2 text-xs text-slate-500">{error.stack}</div>
          )}
        </pre>
        <button
          onClick={() => reset()}
          className="px-4 py-2 bg-primary text-slate-900 rounded font-medium hover:bg-amber-500"
        >
          Try again
        </button>
      </div>
    </div>
  )
}
