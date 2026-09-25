import React from 'react';
import {
  ShieldCheck,
  Activity,
  History,
  Cpu,
  Terminal,
  Radio,
  ChevronRight,
  Sparkles
} from 'lucide-react';

export default function Header({ activeTab, setActiveTab, historyCount = 0 }) {
  const navItems = [
    { id: 'scanner', label: 'Threat Scanner', icon: Terminal },
    { id: 'dashboard', label: 'Dashboard', icon: Activity },
    { id: 'history', label: 'Audit History', icon: History, count: historyCount },
    { id: 'telemetry', label: 'System Specs', icon: Cpu },
  ];

  return (
    <header className="sticky top-0 z-50 border-b border-white/[0.08] bg-[#05080e]/90 backdrop-blur-2xl">
      <div className="absolute inset-x-0 top-0 h-px bg-gradient-to-r from-transparent via-cyan-400/70 to-transparent" />

      <div className="mx-auto flex min-h-[76px] max-w-7xl items-center justify-between gap-6 px-5 lg:px-8">

        {/* Brand */}
        <button
          onClick={() => setActiveTab('scanner')}
          className="group flex min-w-0 items-center gap-3 text-left"
        >
          <div className="relative flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl border border-cyan-400/30 bg-gradient-to-br from-cyan-400/15 via-blue-500/10 to-transparent shadow-[0_0_30px_rgba(0,242,254,0.12)] transition-all duration-300 group-hover:border-cyan-300/60 group-hover:shadow-[0_0_35px_rgba(0,242,254,0.22)]">
            <ShieldCheck className="h-6 w-6 text-cyan-300" />

            <span className="absolute -right-1 -top-1 flex h-3 w-3">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-50" />
              <span className="relative inline-flex h-3 w-3 rounded-full border-2 border-[#05080e] bg-emerald-400" />
            </span>
          </div>

          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="text-lg font-black tracking-[0.16em] text-white">
                SentriX AI AI AI
              </span>

              <span className="hidden rounded-md border border-cyan-400/20 bg-cyan-400/[0.08] px-2 py-0.5 font-mono text-[9px] font-bold tracking-wider text-cyan-300 sm:inline-block">
                AI DEFENSE
              </span>
            </div>

            <div className="mt-0.5 flex items-center gap-1.5 font-mono text-[10px] tracking-wide text-slate-500">
              <Radio className="h-3 w-3 text-emerald-400" />
              <span>NEURAL THREAT INTELLIGENCE</span>
            </div>
          </div>
        </button>

        {/* Navigation */}
        <nav className="hidden items-center rounded-2xl border border-white/[0.08] bg-white/[0.025] p-1 md:flex">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`group relative flex items-center gap-2 rounded-xl px-4 py-2.5 text-xs font-semibold transition-all duration-200 ${
                  active
                    ? 'bg-gradient-to-r from-cyan-400 to-blue-500 text-slate-950 shadow-[0_4px_20px_rgba(0,200,255,0.25)]'
                    : 'text-slate-400 hover:bg-white/[0.05] hover:text-white'
                }`}
              >
                <Icon className={`h-4 w-4 ${active ? 'text-slate-950' : 'text-slate-500 group-hover:text-cyan-300'}`} />

                <span>{item.label}</span>

                {item.count !== undefined && (
                  <span
                    className={`rounded-full px-1.5 py-0.5 font-mono text-[9px] ${
                      active
                        ? 'bg-black/15 text-slate-950'
                        : 'border border-cyan-400/20 bg-cyan-400/10 text-cyan-300'
                    }`}
                  >
                    {item.count}
                  </span>
                )}

                {active && (
                  <ChevronRight className="h-3 w-3 opacity-60" />
                )}
              </button>
            );
          })}
        </nav>

        {/* Security status */}
        <div className="hidden items-center gap-3 lg:flex">
          <div className="flex items-center gap-2 rounded-xl border border-emerald-400/15 bg-emerald-400/[0.05] px-3 py-2">
            <div className="relative">
              <span className="absolute h-2.5 w-2.5 animate-ping rounded-full bg-emerald-400/40" />
              <span className="relative block h-2.5 w-2.5 rounded-full bg-emerald-400" />
            </div>

            <div>
              <div className="flex items-center gap-1.5 font-mono text-[9px] font-bold tracking-widest text-emerald-300">
                <Sparkles className="h-3 w-3" />
                PROTECTED
              </div>
              <div className="font-mono text-[8px] text-slate-500">
                ENGINE ONLINE
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Mobile navigation */}
      <div className="border-t border-white/[0.05] px-4 py-2 md:hidden">
        <div className="flex gap-1 overflow-x-auto">
          {navItems.map((item) => {
            const Icon = item.icon;
            const active = activeTab === item.id;

            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`flex shrink-0 items-center gap-2 rounded-lg px-3 py-2 text-[11px] font-semibold ${
                  active
                    ? 'bg-cyan-400 text-slate-950'
                    : 'bg-white/[0.04] text-slate-400'
                }`}
              >
                <Icon className="h-3.5 w-3.5" />
                {item.label}
              </button>
            );
          })}
        </div>
      </div>
    </header>
  );
}

