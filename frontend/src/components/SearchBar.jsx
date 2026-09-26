/**
 * Search bar for filtering transactions by hash or address.
 */
export default function SearchBar({ value, onChange }) {
  return (
    <div className="relative flex-1">
      <span className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500">🔍</span>
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder="Search by hash or address..."
        className="w-full bg-slate-800 border border-slate-700 rounded-lg pl-10 pr-4 py-2.5 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-blue-500 transition-colors"
      />
      {value && (
        <button
          onClick={() => onChange('')}
          className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-500 hover:text-white"
          aria-label="Clear search"
        >
          ×
        </button>
      )}
    </div>
  );
}