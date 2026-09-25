import React, { useState } from 'react';
import {
  ShieldCheck,
  ShieldAlert,
  AlertTriangle,
  Copy,
  Check,
  ArrowLeft,
  Info,
  Activity,
  FileText,
  Sparkles,
  Zap,
  LockKeyhole
} from 'lucide-react';

export default function ResultCard({ result, onReset, onViewHistory }) {
  const [copied, setCopied] = useState(false);

  if (!result) return null;

  const isFraud = result.verdict === 'FRAUDULENT';
  const isSuspicious = result.verdict === 'SUSPICIOUS';
  const isSafe = result.verdict === 'SAFE';

  const theme = isFraud
    ? {
        text: 'text-rose-400',
        bg: 'bg-rose-400/[0.08]',
        border: 'border-rose-400/30',
        glow: 'rgba(244,63,94,0.22)',
        bar: 'bg-rose-400',
        label: 'CRITICAL THREAT',
        icon: ShieldAlert
      }
    : isSuspicious
      ? {
          text: 'text-amber-400',
          bg: 'bg-amber-400/[0.08]',
          border: 'border-amber-400/30',
          glow: 'rgba(251,191,36,0.20)',
          bar: 'bg-amber-400',
          label: 'SUSPICIOUS SIGNAL',
          icon: AlertTriangle
        }
      : {
          text: 'text-emerald-400',
          bg: 'bg-emerald-400/[0.08]',
          border: 'border-emerald-400/30',
          glow: 'rgba(34,197,94,0.20)',
          bar: 'bg-emerald-400',
          label: 'THREAT CLEARED',
          icon: ShieldCheck
        };

  const VerdictIcon = theme.icon;

  const handleCopyJson = () => {
    navigator.clipboard.writeText(JSON.stringify(result, null, 2));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const risk = Number(result.risk_score ?? 0);
  const confidence = Number(result.confidence ?? 0);

  return (
    <div className="space-y-5">

      {/* Toolbar */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <button
          onClick={onReset}
          className="group flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-xs font-semibold text-slate-400 transition-all hover:border-cyan-400/25 hover:bg-cyan-400/[0.05] hover:text-white"
        >
          <ArrowLeft className="h-4 w-4 transition-transform group-hover:-translate-x-1" />
          Scan Another Payload
        </button>

        <button
          onClick={handleCopyJson}
          className="flex items-center gap-2 rounded-xl border border-white/[0.08] bg-white/[0.025] px-4 py-2.5 text-xs font-mono text-slate-400 transition-all hover:border-cyan-400/25 hover:bg-white/[0.05] hover:text-white"
        >
          {copied ? (
            <Check className="h-4 w-4 text-emerald-400" />
          ) : (
            <Copy className="h-4 w-4 text-cyan-400" />
          )}
          {copied ? 'COPIED' : 'EXPORT JSON'}
        </button>
      </div>

      {/* Main Result */}
      <section
        className={`relative overflow-hidden rounded-[26px] border ${theme.border} bg-[#090F1B]/95 p-5 shadow-2xl lg:p-8`}
        style={{
          boxShadow: `0 30px 90px ${theme.glow}, inset 0 1px 0 rgba(255,255,255,0.04)`
        }}
      >

        {/* Ambient glow */}
        <div
          className="pointer-events-none absolute -right-32 -top-32 h-96 w-96 rounded-full blur-3xl"
          style={{ background: theme.glow }}
        />

        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(94,231,255,0.035),transparent_30%)]" />

        <div className="relative z-10">

          {/* Result Header */}
          <div className="flex flex-col gap-7 border-b border-white/[0.07] pb-7 xl:flex-row xl:items-center xl:justify-between">

            <div className="flex items-center gap-5">

              <div
                className={`relative flex h-20 w-20 shrink-0 items-center justify-center rounded-3xl border ${theme.border} ${theme.bg}`}
              >
                <div
                  className={`absolute inset-2 rounded-2xl border ${theme.border} opacity-40`}
                />
                <VerdictIcon className={`relative h-10 w-10 ${theme.text}`} />

                <span
                  className={`absolute -right-1 -top-1 h-3 w-3 rounded-full ${theme.bar} shadow-[0_0_12px_currentColor]`}
                />
              </div>

              <div>
                <div className="mb-2 flex flex-wrap items-center gap-2">
                  <span className="rounded-md border border-cyan-400/15 bg-cyan-400/[0.06] px-2 py-1 font-mono text-[9px] font-bold tracking-[0.16em] text-cyan-300">
                    DEFENSE VERDICT
                  </span>

                  <span className="font-mono text-[9px] text-slate-600">
                    {result.scan_id || 'SCN-LOCAL'}
                  </span>
                </div>

                <h1 className={`text-4xl font-black tracking-tight lg:text-5xl ${theme.text}`}>
                  {result.verdict}
                </h1>

                <div className="mt-2 flex items-center gap-2 font-mono text-[10px] text-slate-500">
                  <FileText className="h-3.5 w-3.5 text-cyan-400" />
                  INPUT TYPE:
                  <span className="font-bold text-slate-300">
                    {result.input_type}
                  </span>
                </div>
              </div>
            </div>

            {/* Status */}
            <div className={`rounded-2xl border ${theme.border} ${theme.bg} px-5 py-4`}>
              <div className="flex items-center gap-2">
                <Sparkles className={`h-4 w-4 ${theme.text}`} />
                <span className={`font-mono text-[10px] font-bold tracking-[0.15em] ${theme.text}`}>
                  {theme.label}
                </span>
              </div>

              <div className="mt-2 flex items-center gap-2 font-mono text-[9px] text-slate-500">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" />
                ANALYSIS COMPLETE
              </div>
            </div>

          </div>

          {/* Metrics */}
          <div className="grid gap-4 py-7 md:grid-cols-2">

            {/* Risk */}
            <div className="rounded-2xl border border-white/[0.07] bg-black/20 p-5">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Activity className="h-4 w-4 text-cyan-400" />
                  <span className="font-mono text-[10px] font-bold tracking-widest text-slate-400">
                    RISK INDEX
                  </span>
                </div>

                <span className={`font-mono text-3xl font-black ${theme.text}`}>
                  {risk}
                  <span className="text-sm text-slate-600"> /100</span>
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
                <div
                  className={`h-full rounded-full ${theme.bar} transition-all duration-700`}
                  style={{
                    width: `${Math.min(Math.max(risk, 0), 100)}%`,
                    boxShadow: `0 0 14px ${theme.glow}`
                  }}
                />
              </div>

              <div className="mt-3 flex justify-between font-mono text-[9px] text-slate-600">
                <span>LOW</span>
                <span>MODERATE</span>
                <span>CRITICAL</span>
              </div>
            </div>

            {/* Confidence */}
            <div className="rounded-2xl border border-white/[0.07] bg-black/20 p-5">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Zap className="h-4 w-4 text-cyan-400" />
                  <span className="font-mono text-[10px] font-bold tracking-widest text-slate-400">
                    MODEL CONFIDENCE
                  </span>
                </div>

                <span className="font-mono text-3xl font-black text-cyan-300">
                  {confidence}%
                </span>
              </div>

              <div className="h-2 overflow-hidden rounded-full bg-white/[0.06]">
                <div
                  className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-indigo-400"
                  style={{ width: `${Math.min(Math.max(confidence, 0), 100)}%` }}
                />
              </div>

              <div className="mt-3 flex items-center justify-between font-mono text-[9px] text-slate-600">
                <span>NEURAL CONSENSUS</span>
                <span>HIGH PRECISION</span>
              </div>
            </div>

          </div>

          {/* Explanation */}
          <div className="border-t border-white/[0.07] pt-6">

            <div className="mb-3 flex items-center gap-2">
              <Info className="h-4 w-4 text-cyan-400" />
              <span className="font-mono text-[10px] font-bold tracking-[0.16em] text-slate-400">
                INTELLIGENCE NARRATIVE
              </span>
            </div>

            <div className="rounded-2xl border border-white/[0.06] bg-white/[0.025] p-5">
              <p className="text-sm leading-7 text-slate-300">
                {result.explanation}
              </p>
            </div>

          </div>

          {/* Indicators */}
          {result.indicators && result.indicators.length > 0 && (
            <div className="mt-6">

              <div className="mb-3 flex items-center gap-2">
                <LockKeyhole className="h-4 w-4 text-cyan-400" />
                <span className="font-mono text-[10px] font-bold tracking-[0.16em] text-slate-400">
                  DETECTED THREAT SIGNALS
                </span>
              </div>

              <div className="flex flex-wrap gap-2">
                {result.indicators.map((ind, i) => (
                  <span
                    key={i}
                    className={`flex items-center gap-2 rounded-xl border ${theme.border} ${theme.bg} px-3 py-2 font-mono text-[10px] text-slate-300`}
                  >
                    <span className={`h-1.5 w-1.5 rounded-full ${theme.bar}`} />
                    {ind}
                  </span>
                ))}
              </div>

            </div>
          )}

          {/* Probability Distribution */}
          {result.probabilities &&
            Object.keys(result.probabilities).length > 0 && (
              <div className="mt-7">

                <div className="mb-3 flex items-center justify-between">
                  <span className="font-mono text-[10px] font-bold tracking-[0.16em] text-slate-400">
                    MODEL PROBABILITY DISTRIBUTION
                  </span>

                  <span className="font-mono text-[9px] text-slate-600">
                    CLASSIFICATION ENGINE
                  </span>
                </div>

                <div className="grid gap-3 md:grid-cols-3">
                  {Object.entries(result.probabilities).map(
                    ([className, prob]) => (
                      <div
                        key={className}
                        className="rounded-2xl border border-white/[0.06] bg-black/20 p-4"
                      >
                        <div className="mb-3 flex items-center justify-between">
                          <span className="font-mono text-[10px] text-slate-500">
                            {className}
                          </span>

                          <span className="font-mono text-sm font-bold text-white">
                            {prob}%
                          </span>
                        </div>

                        <div className="h-1.5 overflow-hidden rounded-full bg-white/[0.06]">
                          <div
                            className="h-full rounded-full bg-gradient-to-r from-cyan-400 to-indigo-400"
                            style={{
                              width: `${Math.min(Number(prob) || 0, 100)}%`
                            }}
                          />
                        </div>
                      </div>
                    )
                  )}
                </div>

              </div>
            )}

          {/* Voice Transcript */}
          {result.input_type === 'audio' && result.metadata?.transcript && (
            <div className="mt-7">
              <div className="mb-3 flex items-center gap-2">
                <Activity className="h-4 w-4 text-cyan-400" />
                <span className="font-mono text-[10px] font-bold tracking-[0.16em] text-slate-400">
                  SPEECH TRANSCRIPT
                </span>
                <span className="ml-auto rounded-md border border-cyan-400/15 bg-cyan-400/[0.05] px-2 py-1 font-mono text-[9px] text-cyan-300">
                  WHISPER • {result.metadata.transcription_language || 'en'}
                </span>
              </div>

              <div className="rounded-2xl border border-cyan-400/10 bg-cyan-400/[0.025] p-5">
                <p className="text-sm leading-7 text-slate-300">
                  {result.metadata.transcript}
                </p>
              </div>
            </div>
          )}
          {/* Payload */}
          {result.input_summary && (
            <div className="mt-7">

              <div className="mb-3 flex items-center gap-2">
                <FileText className="h-4 w-4 text-cyan-400" />
                <span className="font-mono text-[10px] font-bold tracking-[0.16em] text-slate-400">
                  ANALYZED PAYLOAD
                </span>
              </div>

              <pre className="max-h-64 overflow-auto rounded-2xl border border-white/[0.06] bg-[#04070D] p-5 font-mono text-xs leading-6 text-slate-400">
                {result.raw_input || result.input_summary}
              </pre>

            </div>
          )}

        </div>
      </section>
    </div>
  );
}

