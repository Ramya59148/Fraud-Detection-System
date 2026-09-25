import React, { useState, useEffect } from 'react';
import { Cpu, Server, Database, Shield, CheckCircle2, Zap, GitBranch, Layers } from 'lucide-react';

export default function TelemetryModal() {
  const [modelStatus, setModelStatus] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch('/api/models/status')
      .then((res) => res.json())
      .then((data) => {
        setModelStatus(data);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Error fetching model status', err);
        setLoading(false);
      });
  }, []);

  return (
    <div className="space-y-6">
      
      {/* System Architecture Overview */}
      <div className="glass-panel p-6 lg:p-8 space-y-4">
        <div className="flex items-center justify-between border-b border-white/10 pb-3">
          <h2 className="text-xl font-extrabold text-white flex items-center gap-2">
            <Cpu className="w-5 h-5 text-cyan-400" />
            <span>SentriX AI AI AI System Architecture & Neural Specifications</span>
          </h2>
          <span className="text-xs font-mono text-cyan-400 bg-cyan-950/80 px-2 py-0.5 rounded border border-cyan-700/50">
            SentriX AI AI AI PIPELINE v2.0
          </span>
        </div>

        <p className="text-slate-300 text-sm leading-relaxed">
          SentriX AI AI AI is structured as a multi-modal, defense-in-depth cybersecurity framework. Inbound payloads flow through rigorous feature extractors, specialized neural models (fine-tuned DistilBERT) and ensemble classifiers (Random Forest with 33 lexical dimensions), before passing into a hybrid Verdict Engine that aggregates heuristics, brand impersonation traps, and confidence calibrations.
        </p>

        {/* Diagram Flow Card */}
        <div className="p-4 rounded-xl bg-black/40 border border-white/5 space-y-3 font-mono text-xs">
          <span className="text-slate-400 font-bold uppercase tracking-wider block">End-To-End Execution Flow:</span>
          
          <div className="grid grid-cols-1 md:grid-cols-4 gap-3 text-center">
            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/10">
              <span className="text-cyan-400 font-bold block mb-1">1. User Payload</span>
              <span className="text-slate-400 text-[11px]">Text / Email / URL / Document / Audio</span>
            </div>

            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/10">
              <span className="text-blue-400 font-bold block mb-1">2. Preprocessing</span>
              <span className="text-slate-400 text-[11px]">Tokenization, 33-Dim URL extraction, Acoustic FFT</span>
            </div>

            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/10">
              <span className="text-purple-400 font-bold block mb-1">3. Neural Inference</span>
              <span className="text-slate-400 text-[11px]">DistilBERT (Text/Email) + Random Forest (URL)</span>
            </div>

            <div className="p-3 rounded-lg bg-white/[0.03] border border-white/10">
              <span className="text-emerald-400 font-bold block mb-1">4. Verdict Engine</span>
              <span className="text-slate-400 text-[11px]">Heuristic Consensus, SQLite Audit, UI Telemetry</span>
            </div>
          </div>
        </div>
      </div>

      {/* Model Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        
        {/* Text Model Spec */}
        <div className="glass-panel p-5 space-y-3 border-l-4 border-l-blue-500">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-white">Text Classification Engine</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">ONLINE</span>
          </div>
          <p className="text-xs text-slate-400">
            Fine-tuned DistilBERT transformer evaluating linguistic urgency, financial manipulation, and scam hooks.
          </p>
          <div className="p-2.5 rounded bg-black/30 font-mono text-[11px] text-slate-300 space-y-1">
            <div><span className="text-slate-500">Architecture:</span> DistilBertForSequenceClassification</div>
            <div><span className="text-slate-500">Max Sequence Length:</span> 128 tokens</div>
            <div><span className="text-slate-500">Classes:</span> Safe (0), Critical (1)</div>
            <div><span className="text-slate-500">Parameters:</span> 66.95M parameters (267.8 MB)</div>
          </div>
        </div>

        {/* Email Model Spec */}
        <div className="glass-panel p-5 space-y-3 border-l-4 border-l-purple-500">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-white">Email Phishing Detection Engine</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">ONLINE</span>
          </div>
          <p className="text-xs text-slate-400">
            Transformer sequence model analyzing structured email headers, spoofed sender domains, and deceptive call-to-actions.
          </p>
          <div className="p-2.5 rounded bg-black/30 font-mono text-[11px] text-slate-300 space-y-1">
            <div><span className="text-slate-500">Architecture:</span> DistilBertForSequenceClassification</div>
            <div><span className="text-slate-500">Max Sequence Length:</span> 128 tokens</div>
            <div><span className="text-slate-500">Classes:</span> Critical (0), Safe (1)</div>
            <div><span className="text-slate-500">Cross-Validation Accuracy:</span> 97.4%</div>
          </div>
        </div>

        {/* URL Model Spec */}
        <div className="glass-panel p-5 space-y-3 border-l-4 border-l-cyan-500">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-white">URL Random Forest Classifier</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">ONLINE</span>
          </div>
          <p className="text-xs text-slate-400">
            200-Tree Random Forest trained on 641,125 URLs with fixed pipeline, brand impersonation guardrails, and whitelisting.
          </p>
          <div className="p-2.5 rounded bg-black/30 font-mono text-[11px] text-slate-300 space-y-1">
            <div><span className="text-slate-500">Estimators:</span> 200 Trees</div>
            <div><span className="text-slate-500">Feature Count:</span> 33 Lexical & Structural Dimensions</div>
            <div><span className="text-slate-500">Dataset Size:</span> 641,125 samples</div>
            <div><span className="text-slate-500">Classes:</span> Safe (0), Critical (1), Suspicious (2)</div>
          </div>
        </div>

        {/* Audio Engine Spec */}
        <div className="glass-panel p-5 space-y-3 border-l-4 border-l-amber-500">
          <div className="flex items-center justify-between">
            <span className="text-sm font-bold text-white">Acoustic Deepfake & Voice Scam Engine</span>
            <span className="text-[10px] font-mono text-emerald-400 bg-emerald-500/10 px-2 py-0.5 rounded border border-emerald-500/20">ONLINE</span>
          </div>
          <p className="text-xs text-slate-400">
            Fourier transform and spectral variance telemetry assessing pitch stability, formant richness, and vocoder artifacts.
          </p>
          <div className="p-2.5 rounded bg-black/30 font-mono text-[11px] text-slate-300 space-y-1">
            <div><span className="text-slate-500">Acoustic Telemetry:</span> FFT, Centroid, Flatness, RMS, ZCR</div>
            <div><span className="text-slate-500">Input Formats:</span> Live Mic (Web Audio API), .wav, .mp3</div>
            <div><span className="text-slate-500">Sampling Rate:</span> 16,000 Hz Normalized</div>
            <div><span className="text-slate-500">Detection Type:</span> Synthetic Voice Cloning & Robocalls</div>
          </div>
        </div>

      </div>

      {/* Storage and Runtime Details */}
      <div className="glass-panel p-6 space-y-3">
        <h3 className="text-sm font-bold text-white font-mono flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" />
          <span>Storage & Telemetry Persistence</span>
        </h3>
        <p className="text-xs text-slate-400 leading-relaxed font-mono">
          Database: <span className="text-white">SQLite (`backEnd/SentriX AI AI AI.db`)</span> with SQLAlchemy ORM. All payload audits, confidence vectors, threat indicators, and risk scores are persisted with unique IDs (SCN-YYYYMMDD-XXXX).
        </p>
      </div>

    </div>
  );
}

