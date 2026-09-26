import { useEffect, useMemo, useState } from 'react';
import { api } from './api/client';
import StatsBar from './components/StatsBar';
import TransactionList from './components/TransactionList';
import TransactionModal from './components/TransactionModal';
import SearchBar from './components/SearchBar';
import FilterTabs from './components/FilterTabs';
import RiskChart from './components/RiskChart';

function App() {
  const [stats, setStats] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [flagged, setFlagged] = useState([]);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [selectedTx, setSelectedTx] = useState(null);
  const [search, setSearch] = useState('');
  const [filter, setFilter] = useState('all');

  async function loadData() {
    try {
      const [statsData, txsData, flaggedData] = await Promise.all([
        api.getStats(),
        api.getTransactions(50),
        api.getFlagged(20),
      ]);
      setStats(statsData);
      setTransactions(txsData.transactions);
      setFlagged(flaggedData.transactions);
      setLastUpdate(new Date());
      setError(null);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5000);
    return () => clearInterval(interval);
  }, []);

  const counts = useMemo(() => ({
    all: transactions.length,
    flagged: flagged.length,
    high: flagged.filter((tx) => tx.risk_score >= 40).length,
  }), [transactions, flagged]);

  const filtered = useMemo(() => {
    let list = transactions;

    // For flagged/high views, use the dedicated flagged list
    if (filter === 'flagged') list = flagged;
    else if (filter === 'high') list = flagged.filter((tx) => tx.risk_score >= 40);

    if (search.trim()) {
      const s = search.toLowerCase();
      list = list.filter((tx) =>
        tx.hash.toLowerCase().includes(s) ||
        tx.from_address.toLowerCase().includes(s) ||
        tx.to_address.toLowerCase().includes(s)
      );
    }

    return list;
  }, [transactions, flagged, filter, search]);

  return (
    <div className="min-h-screen bg-slate-900">
      <header className="bg-slate-800 border-b border-slate-700 mb-6">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-white">
                🔗 Blockchain Intelligence Platform
              </h1>
              <p className="text-slate-400 text-sm mt-1">
                AI-powered Ethereum transaction analysis
              </p>
            </div>
            <div className="text-right">
              <div className="flex items-center gap-2 text-green-400 text-sm">
                <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                Live
              </div>
              <div className="text-slate-500 text-xs mt-1">
                Updated: {lastUpdate.toLocaleTimeString()}
              </div>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 pb-12">
        {error && (
          <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-4 mb-6 text-red-400">
            ⚠️ Error: {error}
          </div>
        )}

        <StatsBar stats={stats} />

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          <div className="lg:col-span-2">
            <div className="flex gap-3 mb-4">
              <SearchBar value={search} onChange={setSearch} />
            </div>
            <FilterTabs active={filter} onChange={setFilter} counts={counts} />
          </div>
          <div className="lg:col-span-1">
            <RiskChart transactions={transactions} />
          </div>
        </div>

        <TransactionList transactions={filtered} onSelect={setSelectedTx} />
      </main>

      <footer className="text-center text-slate-600 text-xs py-8">
        Built with FastAPI + PostgreSQL + Ollama + React
      </footer>

      {selectedTx && (
        <TransactionModal tx={selectedTx} onClose={() => setSelectedTx(null)} />
      )}
    </div>
  );
}

export default App;