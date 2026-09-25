import React, { useState, useEffect } from 'react';
import { 
  History, 
  Search, 
  Trash2, 
  ShieldCheck, 
  ShieldAlert, 
  AlertTriangle, 
  RefreshCw, 
  ArrowUpRight, 
  Filter 
} from 'lucide-react';

export default function ScanHistory({ onSelectScan }) {
  const [historyItems, setHistoryItems] = useState([]);
  const [totalCount, setTotalCount] = useState(0);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [selectedVerdict, setSelectedVerdict] = useState('ALL');
  const [selectedType, setSelectedType] = useState('ALL');

  const fetchHistory = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.append('limit', '100');
      if (search.trim()) params.append('search', search.trim());
      if (selectedVerdict !== 'ALL') params.append('verdict', selectedVerdict);
      if (selectedType !== 'ALL') params.append('input_type', selectedType);

      const res = await fetch(`/api/history?${params.toString()}`);
      if (res.ok) {
        const data = await res.json();
        setHistoryItems(data.items || []);
        setTotalCount(data.total || 0);
      }
    } catch (e) {
      console.error('Failed to fetch history', e);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, [selectedVerdict, selectedType]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchHistory();
  };

  const handleClearHistory = async () => {
    if (window.confirm('Are you sure you want to purge all scan records from the database?')) {
      try {
        await fetch('/api/history', { method: 'DELETE' });
        fetchHistory();
      } catch (e) {
        console.error('Failed to clear history', e);
      }
    }
  };

  const handleDeleteItem = async (e, scanId) => {
    e.stopPropagation();
    try {
      await fetch(`/api/history/${scanId}`, { method: 'DELETE' });
      fetchHistory();
    } catch (e) {
      console.error('Failed to delete scan record', e);
    }
  };

  return (
    <div className="glass-panel p-6 lg:p-8 space-y-6">
      
      {/* Header & Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-4">
        <div>
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <History className="w-5 h-5 text-cyan-400" />
            <span>Audit & Threat Telemetry Log</span>
          </h2>
          <p className="text-xs text-slate-400 font-mono mt-0.5">
            Database Archive: {totalCount} events logged in SQLite storage
          </p>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={fetchHistory}
            className="p-2 rounded-lg bg-white/5 hover:bg-white/10 border border-white/10 text-slate-300 hover:text-white transition-colors"
            title="Refresh Log"
          >
            <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          </button>

          {historyItems.length > 0 && (
            <button
              onClick={handleClearHistory}
              className="px-3 py-1.5 rounded-lg bg-red-500/10 hover:bg-red-500/20 text-red-400 border border-red-500/30 text-xs font-mono flex items-center gap-1.5 transition-colors"
            >
              <Trash2 className="w-3.5 h-3.5" />
              <span>Purge History</span>
            </button>
          )}
        </div>
      </div>

      {/* Filters & Search */}
      <div className="flex flex-col md:flex-row items-center gap-3">
        
        {/* Search Input */}
        <form onSubmit={handleSearchSubmit} className="relative flex-1 w-full">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by Scan ID, content summary, or explanation..."
            className="cyber-input pl-10 text-xs"
          />
        </form>

        {/* Verdict Filter */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto">
          {['ALL', 'SAFE', 'SUSPICIOUS', 'FRAUDULENT'].map((verdict) => (
            <button
              key={verdict}
              onClick={() => setSelectedVerdict(verdict)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all whitespace-nowrap ${
                selectedVerdict === verdict
                  ? 'bg-cyan-500/20 text-cyan-300 border border-cyan-400/40 shadow-sm'
                  : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-white/5'
              }`}
            >
              {verdict}
            </button>
          ))}
        </div>

        {/* Type Filter */}
        <div className="flex items-center gap-1.5 overflow-x-auto w-full md:w-auto">
          {['ALL', 'text', 'email', 'url', 'file', 'audio'].map((type) => (
            <button
              key={type}
              onClick={() => setSelectedType(type)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono font-semibold transition-all uppercase whitespace-nowrap ${
                selectedType === type
                  ? 'bg-blue-500/20 text-blue-300 border border-blue-400/40 shadow-sm'
                  : 'bg-white/5 text-slate-400 hover:bg-white/10 border border-white/5'
              }`}
            >
              {type}
            </button>
          ))}
        </div>

      </div>

      {/* History Table */}
      {loading ? (
        <div className="text-center py-16 text-cyan-400 font-mono text-sm flex items-center justify-center gap-2">
          <RefreshCw className="w-5 h-5 animate-spin" />
          <span>Querying SQLite Database Records...</span>
        </div>
      ) : historyItems.length > 0 ? (
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-white/10 text-slate-400 font-mono">
                <th className="pb-3 font-semibold">SCAN ID</th>
                <th className="pb-3 font-semibold">TIMESTAMP</th>
                <th className="pb-3 font-semibold">TYPE</th>
                <th className="pb-3 font-semibold">PAYLOAD SUMMARY</th>
                <th className="pb-3 font-semibold">VERDICT</th>
                <th className="pb-3 font-semibold">CONFIDENCE</th>
                <th className="pb-3 font-semibold text-right">ACTIONS</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-white/5 font-mono">
              {historyItems.map((item) => (
                <tr
                  key={item.scan_id}
                  onClick={() => onSelectScan(item)}
                  className="hover:bg-white/[0.03] cursor-pointer transition-colors"
                >
                  <td className="py-3 text-cyan-400 font-bold">{item.scan_id}</td>
                  <td className="py-3 text-slate-400 text-[11px]">
                    {item.created_at ? new Date(item.created_at).toLocaleString() : 'N/A'}
                  </td>
                  <td className="py-3 uppercase text-slate-300">{item.input_type}</td>
                  <td className="py-3 text-slate-200 max-w-sm truncate">{item.input_summary}</td>
                  <td className="py-3">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      item.verdict === 'SAFE' ? 'badge-safe' :
                      item.verdict === 'SUSPICIOUS' ? 'badge-suspicious' : 'badge-fraud'
                    }`}>
                      {item.verdict}
                    </span>
                  </td>
                  <td className="py-3 text-white font-bold">{item.confidence}%</td>
                  <td className="py-3 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectScan(item);
                        }}
                        className="text-cyan-400 hover:text-cyan-300 p-1 hover:bg-cyan-500/10 rounded transition-colors"
                        title="View Full Report"
                      >
                        <ArrowUpRight className="w-4 h-4" />
                      </button>
                      <button
                        onClick={(e) => handleDeleteItem(e, item.scan_id)}
                        className="text-red-400 hover:text-red-300 p-1 hover:bg-red-500/10 rounded transition-colors"
                        title="Delete Record"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : (
        <div className="text-center py-16 text-slate-500 font-mono text-xs space-y-2">
          <p>No matching scan records found.</p>
          <p className="text-slate-600">Run a scan using the Threat Scanner to populate the telemetry database.</p>
        </div>
      )}

    </div>
  );
}

