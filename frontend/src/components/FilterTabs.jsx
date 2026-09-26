/**
 * Filter tabs for switching between All / Flagged / High Risk views.
 */
export default function FilterTabs({ active, onChange, counts }) {
  const tabs = [
    { id: 'all', label: 'All', count: counts.all, color: 'text-slate-300' },
    { id: 'flagged', label: 'Flagged', count: counts.flagged, color: 'text-yellow-400' },
    { id: 'high', label: 'High Risk', count: counts.high, color: 'text-red-400' },
  ];

  return (
    <div className="flex gap-2 bg-slate-800 rounded-lg p-1 border border-slate-700">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          onClick={() => onChange(tab.id)}
          className={`px-4 py-2 rounded-md text-sm font-medium transition-colors flex items-center gap-2 ${
            active === tab.id
              ? 'bg-slate-700 text-white'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          <span>{tab.label}</span>
          <span className={`text-xs px-1.5 py-0.5 rounded ${active === tab.id ? 'bg-slate-600' : 'bg-slate-900'} ${tab.color}`}>
            {tab.count}
          </span>
        </button>
      ))}
    </div>
  );
}