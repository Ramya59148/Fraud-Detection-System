import React, { useState, useEffect } from 'react';

import Header from './components/Header';
import DashboardStats from './components/DashboardStats';
import ScannerTabs from './components/ScannerTabs';
import ResultCard from './components/ResultCard';
import ScanHistory from './components/ScanHistory';
import TelemetryModal from './components/TelemetryModal';
import { Shield, Activity, Radio, Cpu, Lock } from 'lucide-react';

export default function App() {
  const [activeTab, setActiveTab] = useState('scanner');
  const [stats, setStats] = useState(null);
  const [currentResult, setCurrentResult] = useState(null);
  const [isScanning, setIsScanning] = useState(false);

  const fetchStats = async () => {
    try {
      const res = await fetch('/api/stats');
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (e) {
      console.error('Failed to load stats', e);
    }
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const handleScanComplete = (result) => {
    setCurrentResult(result);
    fetchStats();
  };

  const handleReset = () => {
    setCurrentResult(null);
    setActiveTab('scanner');
  };

  const handleSelectScan = (scan) => {
    setCurrentResult(scan);
  };

  return (
    <div className="min-h-screen flex flex-col bg-[#06090F] text-slate-100 selection:bg-cyan-500/30 selection:text-cyan-200">
      
      {/* Top Header Navigation */}
      <Header
        activeTab={activeTab}
        setActiveTab={(tab) => {
          setActiveTab(tab);
          setCurrentResult(null);
        }}
        historyCount={stats?.total_scans ?? 0}
      />

      {/* Main Content Area */}
      <main className="flex-1 w-full max-w-7xl mx-auto p-4 lg:p-8 space-y-6">
        
        {/* If a scan result is active, show the rich Result Card */}
        {currentResult ? (
          <ResultCard
            result={currentResult}
            onReset={handleReset}
            onViewHistory={() => {
              setCurrentResult(null);
              setActiveTab('history');
            }}
          />
        ) : (
          <>
            {activeTab === 'scanner' && (
              <ScannerTabs
                onScanComplete={handleScanComplete}
                isScanning={isScanning}
                setIsScanning={setIsScanning}
              />
            )}

            {activeTab === 'dashboard' && (
              <DashboardStats
                stats={stats}
                onSelectScan={handleSelectScan}
                onNewScan={() => setActiveTab('scanner')}
              />
            )}

            {activeTab === 'history' && (
              <ScanHistory onSelectScan={handleSelectScan} />
            )}

            {activeTab === 'telemetry' && (
              <TelemetryModal />
            )}
          </>
        )}

      </main>

      {/* Cybersecurity Status Footer */}
      <footer className="border-t border-white/[0.06] bg-[#04070c]/95 px-5 py-3 backdrop-blur-xl">
        <div className="mx-auto flex max-w-7xl flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 rounded-lg border border-emerald-400/15 bg-emerald-400/[0.04] px-3 py-2">
              <span className="relative flex h-2 w-2">
                <span className="absolute h-full w-full animate-ping rounded-full bg-emerald-400/50" />
                <span className="relative h-2 w-2 rounded-full bg-emerald-400" />
              </span>
              <span className="font-mono text-[10px] font-bold tracking-wider text-emerald-300">
                SentriX AI AI AI SHIELD ACTIVE
              </span>
            </div>

            <div className="hidden h-5 w-px bg-white/10 sm:block" />

            <div className="hidden items-center gap-2 font-mono text-[10px] text-slate-500 sm:flex">
              <span className="text-cyan-400">AI</span>
              <span>Multi-Modal Detection Engine</span>
            </div>
          </div>

          <div className="flex flex-wrap items-center gap-x-5 gap-y-2 font-mono text-[9px] text-slate-500">
            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-cyan-400" />
              DISTILBERT
            </span>

            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-blue-400" />
              RANDOM FOREST
            </span>

            <span className="flex items-center gap-1.5">
              <Lock className="h-3 w-3 text-cyan-400" />
              ENCRYPTED PIPELINE
            </span>

            <span className="flex items-center gap-1.5">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
              AUDIT LOG ACTIVE
            </span>
          </div>

        </div>
      </footer>

    </div>
  );
}



