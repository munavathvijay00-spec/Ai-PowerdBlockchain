import { useEffect, useState } from 'react';
import { api } from './api/client';
import StatsBar from './components/StatsBar';
import TransactionList from './components/TransactionList';

function App() {
  const [stats, setStats] = useState(null);
  const [transactions, setTransactions] = useState([]);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  async function loadData() {
    try {
      const [statsData, txsData] = await Promise.all([
        api.getStats(),
        api.getTransactions(20),
      ]);
      setStats(statsData);
      setTransactions(txsData.transactions);
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
        <TransactionList transactions={transactions} />
      </main>

      <footer className="text-center text-slate-600 text-xs py-8">
        Built with FastAPI + PostgreSQL + Ollama + React
      </footer>
    </div>
  );
}

export default App;