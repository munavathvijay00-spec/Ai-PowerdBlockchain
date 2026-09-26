/**
 * Donut chart showing risk score distribution.
 */
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from 'recharts';

function categorize(transactions) {
  const buckets = { minimal: 0, low: 0, medium: 0, high: 0 };
  transactions.forEach((tx) => {
    if (tx.risk_score >= 80) buckets.high++;
    else if (tx.risk_score >= 40) buckets.medium++;
    else if (tx.risk_score >= 20) buckets.low++;
    else buckets.minimal++;
  });
  return [
    { name: 'Minimal (0-19)', value: buckets.minimal, color: '#22c55e' },
    { name: 'Low (20-39)', value: buckets.low, color: '#eab308' },
    { name: 'Medium (40-79)', value: buckets.medium, color: '#f97316' },
    { name: 'High (80-100)', value: buckets.high, color: '#ef4444' },
  ].filter((item) => item.value > 0);
}

export default function RiskChart({ transactions }) {
  if (!transactions || transactions.length === 0) return null;

  const data = categorize(transactions);
  const total = transactions.length;

  return (
    <div className="bg-slate-800 rounded-lg border border-slate-700 p-6">
      <h3 className="text-white font-semibold mb-4">Risk Distribution</h3>
      <div className="flex items-center gap-6">
        <div className="w-40 h-40">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                innerRadius={45}
                outerRadius={75}
                paddingAngle={2}
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={index} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip
                contentStyle={{
                  backgroundColor: '#1e293b',
                  border: '1px solid #334155',
                  borderRadius: '8px',
                  color: '#f1f5f9',
                }}
              />
            </PieChart>
          </ResponsiveContainer>
        </div>
        <div className="flex-1 space-y-2">
          {data.map((item) => (
            <div key={item.name} className="flex items-center justify-between text-sm">
              <div className="flex items-center gap-2">
                <span className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                <span className="text-slate-300">{item.name}</span>
              </div>
              <span className="text-slate-400 font-mono">
                {item.value} ({((item.value / total) * 100).toFixed(1)}%)
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}