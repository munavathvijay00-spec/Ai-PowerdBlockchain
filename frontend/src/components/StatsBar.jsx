/**
 * Top stats bar showing network summary.
 */
export default function StatsBar({ stats }) {
  if (!stats) {
    return (
      <div className="bg-slate-800 rounded-lg p-6 mb-6 animate-pulse">
        <div className="h-6 bg-slate-700 rounded w-1/4"></div>
      </div>
    );
  }

  const cards = [
    { label: 'Total Transactions', value: stats.total_transactions.toLocaleString(), color: 'text-blue-400' },
    { label: 'Addresses Tracked', value: stats.total_addresses.toLocaleString(), color: 'text-purple-400' },
    { label: 'Flagged', value: stats.flagged_transactions, color: 'text-red-400' },
    { label: 'Avg Risk Score', value: stats.avg_risk_score, color: 'text-yellow-400' },
    { label: 'AI Explained', value: stats.explained_transactions, color: 'text-green-400' },
  ];

  return (
    <div className="grid grid-cols-5 gap-4 mb-6">
      {cards.map((card) => (
        <div key={card.label} className="bg-slate-800 rounded-lg p-4 border border-slate-700">
          <div className="text-slate-400 text-xs uppercase tracking-wide mb-1">
            {card.label}
          </div>
          <div className={`text-2xl font-bold ${card.color}`}>
            {card.value}
          </div>
        </div>
      ))}
    </div>
  );
}