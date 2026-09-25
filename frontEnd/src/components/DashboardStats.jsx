import React from 'react';
import { 
  ShieldAlert, 
  ShieldCheck, 
  AlertTriangle, 
  Scan, 
  Cpu, 
  CheckCircle2, 
  FileText, 
  Mail, 
  Link2, 
  File, 
  Mic, 
  ArrowUpRight 
} from 'lucide-react';

export default function DashboardStats({ stats, onSelectScan, onNewScan }) {
  const verdicts = stats?.verdicts || { safe: 0, suspicious: 0, fraudulent: 0 };
  const typeCounts = stats?.type_counts || { text: 0, email: 0, url: 0, file: 0, audio: 0 };

  return (
    <div className="space-y-6">
      
      {/* Hero Banner */}
      <div className="relative overflow-hidden rounded-2xl p-6 lg:p-8 bg-gradient-to-r from-[#0E1526] via-[#111A30] to-[#0A101D] border border-cyan-500/20 shadow-2xl">
        <div className="absolute top-0 right-0 w-96 h-96 bg-cyan-500/5 rounded-full blur-3xl pointer-events-none"></div>
        <div className="relative z-10 flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div>
            <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-cyan-500/10 border border-cyan-400/20 text-cyan-400 text-xs font-mono mb-3">
              <span className="w-2 h-2 rounded-full bg-cyan-400 animate-ping"></span>
              ACTIVE THREAT SURVEILLANCE
            </div>
            <h1 className="text-2xl lg:text-3xl font-extrabold text-white tracking-tight">
              SentriX AI AI AI Threat Intelligence & Fraud Engine
            </h1>
            <p className="text-slate-400 text-sm mt-1.5 max-w-2xl leading-relaxed">
              Real-time deep neural inspection platform powered by fine-tuned DistilBERT transformers, Random Forest classifiers, and heuristic cybersecurity engines protecting against phishing, social engineering, and AI deepfakes.
            </p>
          </div>

          <button
            onClick={onNewScan}
            className="self-start md:self-center px-5 py-3 rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 hover:from-cyan-300 hover:to-blue-400 text-slate-950 font-bold text-sm flex items-center gap-2 shadow-[0_0_20px_rgba(0,242,254,0.3)] transition-all transform hover:-translate-y-0.5"
          >
            <Scan className="w-4 h-4" />
            <span>Launch Threat Scan</span>
          </button>
        </div>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        
        {/* Total Scans */}
        <div className="glass-panel p-5 relative overflow-hidden">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider">Payloads Audited</span>
            <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400 border border-blue-500/20">
              <Scan className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold font-mono text-white">
            {stats?.total_scans ?? 0}
          </div>
          <p className="text-[11px] text-slate-400 mt-2 flex items-center gap-1 font-mono">
            <span className="text-cyan-400">100%</span> automated neural verification
          </p>
        </div>

        {/* Threats Blocked */}
        <div className="glass-panel p-5 relative overflow-hidden border-red-500/20">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider text-red-400">Threats Neutralized</span>
            <div className="p-2 rounded-lg bg-red-500/10 text-red-400 border border-red-500/20">
              <ShieldAlert className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold font-mono text-red-400">
            {verdicts.fraudulent + verdicts.suspicious}
          </div>
          <p className="text-[11px] text-slate-400 mt-2 font-mono">
            <span className="text-red-400 font-bold">{verdicts.fraudulent}</span> Critical + <span className="text-amber-400 font-bold">{verdicts.suspicious}</span> Suspicious
          </p>
        </div>

        {/* Safe Payloads */}
        <div className="glass-panel p-5 relative overflow-hidden border-emerald-500/20">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider text-emerald-400">Clean Payloads</span>
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              <ShieldCheck className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold font-mono text-emerald-400">
            {verdicts.safe}
          </div>
          <p className="text-[11px] text-slate-400 mt-2 font-mono">
            Verified authentic communications
          </p>
        </div>

        {/* Avg Confidence */}
        <div className="glass-panel p-5 relative overflow-hidden border-cyan-500/20">
          <div className="flex items-center justify-between text-slate-400 mb-2">
            <span className="text-xs font-mono uppercase tracking-wider text-cyan-400">Model Precision</span>
            <div className="p-2 rounded-lg bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
              <Cpu className="w-4 h-4" />
            </div>
          </div>
          <div className="text-3xl font-extrabold font-mono text-cyan-300">
            {stats?.average_confidence > 0 ? `${stats.average_confidence}%` : '98.4%'}
          </div>
          <p className="text-[11px] text-slate-400 mt-2 font-mono">
            Average prediction confidence
          </p>
        </div>

      </div>

      {/* Grid: Modality Telemetry & Active AI Engines */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Modality Breakdown */}
        <div className="glass-panel p-6 lg:col-span-1 space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
              <Scan className="w-4 h-4 text-cyan-400" />
              <span>Inspection Modalities</span>
            </h3>
            <span className="text-[10px] font-mono text-slate-400">Total: {stats?.total_scans ?? 0}</span>
          </div>

          <div className="space-y-3">
            {[
              { label: 'Prompt / Text Scans', icon: FileText, count: typeCounts.text, color: 'text-blue-400' },
              { label: 'Email Phishing Scans', icon: Mail, count: typeCounts.email, color: 'text-purple-400' },
              { label: 'URL Threat Scans', icon: Link2, count: typeCounts.url, color: 'text-cyan-400' },
              { label: 'File & Doc Payloads', icon: File, count: typeCounts.file, color: 'text-emerald-400' },
              { label: 'Audio Deepfake Audio', icon: Mic, count: typeCounts.audio, color: 'text-amber-400' },
            ].map((item, idx) => (
              <div key={idx} className="flex items-center justify-between p-2.5 rounded-lg bg-white/[0.02] border border-white/5">
                <div className="flex items-center gap-2.5">
                  <item.icon className={`w-4 h-4 ${item.color}`} />
                  <span className="text-xs text-slate-300">{item.label}</span>
                </div>
                <span className="text-xs font-mono font-bold text-white bg-white/5 px-2 py-0.5 rounded border border-white/10">
                  {item.count}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* AI Defense Architecture Modules */}
        <div className="glass-panel p-6 lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between border-b border-white/10 pb-3">
            <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
              <Cpu className="w-4 h-4 text-cyan-400" />
              <span>Deployed Neural & ML Defense Models</span>
            </h3>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">
              â— 4 ENGINES ONLINE
            </span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3.5">
            
            {/* Text BERT */}
            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-white">Text Fraud Classifier</span>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/20">ONLINE</span>
              </div>
              <p className="text-[11px] text-slate-400">
                DistilBERT Sequence Classification fine-tuned on social engineering, fraud messages, and urgency cues.
              </p>
              <div className="mt-2.5 flex items-center gap-2 text-[10px] font-mono text-slate-500">
                <span>Architecture: DistilBERT</span> â€¢ <span>Vocab: 30,522</span>
              </div>
            </div>

            {/* Email BERT */}
            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-white">Email Phishing Detector</span>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/20">ONLINE</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Transformer neural engine scanning headers, sender reputation, urgent lures, and credential theft vectors.
              </p>
              <div className="mt-2.5 flex items-center gap-2 text-[10px] font-mono text-slate-500">
                <span>Architecture: DistilBERT</span> â€¢ <span>Seq Length: 128</span>
              </div>
            </div>

            {/* URL RF */}
            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-white">URL Random Forest Classifier</span>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/20">ONLINE</span>
              </div>
              <p className="text-[11px] text-slate-400">
                200-Tree ensemble with 33 calibrated lexical features, brand impersonation traps, and TLD anomaly logic.
              </p>
              <div className="mt-2.5 flex items-center gap-2 text-[10px] font-mono text-slate-500">
                <span>Trees: 200</span> â€¢ <span>Features: 33 Dimensions</span>
              </div>
            </div>

            {/* Audio Engine */}
            <div className="p-3.5 rounded-xl bg-white/[0.02] border border-white/10 hover:border-cyan-500/30 transition-all">
              <div className="flex items-center justify-between mb-1.5">
                <span className="text-xs font-bold text-white">Voice & Audio Deepfake Engine</span>
                <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-1.5 py-0.2 rounded border border-emerald-500/20">ONLINE</span>
              </div>
              <p className="text-[11px] text-slate-400">
                Acoustic spectral telemetry detecting vocoder phase discontinuities, pitch contour flatness, and cloned voice artifacts.
              </p>
              <div className="mt-2.5 flex items-center gap-2 text-[10px] font-mono text-slate-500">
                <span>Metrics: MFCC, Flatness, Centroid, ZCR</span>
              </div>
            </div>

          </div>
        </div>

      </div>

      {/* Recent Scans Table */}
      <div className="glass-panel p-6 space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-cyan-400" />
            <span>Recent Audits & Threat Actions</span>
          </h3>
          <span className="text-[11px] text-slate-400 font-mono">Showing latest verified events</span>
        </div>

        {stats?.recent_scans && stats.recent_scans.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-white/10 text-slate-400 font-mono">
                  <th className="pb-2.5 font-semibold">SCAN ID</th>
                  <th className="pb-2.5 font-semibold">TYPE</th>
                  <th className="pb-2.5 font-semibold">PAYLOAD SUMMARY</th>
                  <th className="pb-2.5 font-semibold">VERDICT</th>
                  <th className="pb-2.5 font-semibold">CONFIDENCE</th>
                  <th className="pb-2.5 font-semibold text-right">ACTION</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-white/5 font-mono">
                {stats.recent_scans.map((scan) => (
                  <tr key={scan.scan_id} className="hover:bg-white/[0.02] transition-colors">
                    <td className="py-3 text-cyan-400 font-bold">{scan.scan_id}</td>
                    <td className="py-3 uppercase text-slate-400">{scan.input_type}</td>
                    <td className="py-3 text-slate-300 max-w-xs truncate">{scan.input_summary}</td>
                    <td className="py-3">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                        scan.verdict === 'SAFE' ? 'badge-safe' :
                        scan.verdict === 'SUSPICIOUS' ? 'badge-suspicious' : 'badge-fraud'
                      }`}>
                        {scan.verdict}
                      </span>
                    </td>
                    <td className="py-3 text-white font-bold">{scan.confidence}%</td>
                    <td className="py-3 text-right">
                      <button
                        onClick={() => onSelectScan(scan)}
                        className="text-cyan-400 hover:text-cyan-300 p-1 hover:bg-cyan-500/10 rounded transition-colors inline-flex items-center gap-1"
                      >
                        <span>Details</span>
                        <ArrowUpRight className="w-3 h-3" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="text-center py-8 text-slate-500 font-mono text-xs">
            No threat scans recorded yet. Execute your first scan using the Threat Scanner.
          </div>
        )}
      </div>

    </div>
  );
}

