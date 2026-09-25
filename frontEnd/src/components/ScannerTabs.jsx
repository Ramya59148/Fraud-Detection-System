import React, { useRef, useState } from 'react';
import {
  AlertCircle,
  ArrowRight,
  CheckCircle2,
  FileText,
  FileUp,
  Link2,
  Loader2,
  Mail,
  Mic,
  MicOff,
  Radio,
  Scan,
  Shield,
  ShieldCheck,
  Sparkles,
  Upload,
  Zap,
  Square,
  Activity,
  Database,
  BrainCircuit,
  Globe2,
  LockKeyhole,
} from 'lucide-react';

const MODES = [
  {
    id: 'text',
    label: 'Text Scanner',
    short: 'TEXT',
    description: 'Messages, prompts & social engineering',
    icon: FileText,
    color: 'cyan',
  },
  {
    id: 'email',
    label: 'Email Scanner',
    short: 'EMAIL',
    description: 'Phishing, headers & urgency signals',
    icon: Mail,
    color: 'violet',
  },
  {
    id: 'url',
    label: 'URL Scanner',
    short: 'URL',
    description: 'Domains, links & spoofing indicators',
    icon: Link2,
    color: 'blue',
  },
  {
    id: 'file',
    label: 'File Scanner',
    short: 'FILE',
    description: 'Documents & embedded threat extraction',
    icon: FileUp,
    color: 'amber',
  },
  {
    id: 'audio',
    label: 'Voice Scanner',
    short: 'VOICE',
    description: 'Synthetic voice & robocall analysis',
    icon: Mic,
    color: 'rose',
  },
];

export default function ScannerTabs({ onScanComplete, isScanning, setIsScanning }) {
  const [activeMode, setActiveMode] = useState('text');
  const [scanStep, setScanStep] = useState(0);

  const [textInput, setTextInput] = useState('');
  const [emailSubject, setEmailSubject] = useState('');
  const [emailSender, setEmailSender] = useState('');
  const [emailBody, setEmailBody] = useState('');
  const [urlInput, setUrlInput] = useState('');

  const [selectedFile, setSelectedFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const [audioBlob, setAudioBlob] = useState(null);
  const [audioUrl, setAudioUrl] = useState(null);
  const [isRecording, setIsRecording] = useState(false);
  const [recordTime, setRecordTime] = useState(0);

  const mediaRecorderRef = useRef(null);
  const timerRef = useRef(null);
  const fileInputRef = useRef(null);
  const audioInputRef = useRef(null);

  const [errorMessage, setErrorMessage] = useState(null);

  const currentMode = MODES.find((mode) => mode.id === activeMode);

  const loadTextSample = (type) => {
    if (type === 'fraud') {
      setTextInput(
        'URGENT NOTICE: Your Chase bank account has been flagged for fraudulent activity! Confirm your online password and verify your social security number immediately at our security desk or access will be suspended permanently.'
      );
    } else if (type === 'crypto') {
      setTextInput(
        'Congratulations Winner! You have won 1.5 Bitcoins ($98,000 USD) in our international crypto lottery promo. Wire a $50 claim processing fee immediately to unlock your wallet.'
      );
    } else {
      setTextInput(
        'Hi Alex, thanks for sending over the quarterly architecture report. Let us schedule our team sync for Thursday afternoon at 2:00 PM to review the deployment milestones.'
      );
    }
  };

  const loadEmailSample = (type) => {
    if (type === 'phish') {
      setEmailSubject('Action Required: Security Alert on Your PayPal Account');
      setEmailSender('service-security@paypal-auth-center.com@free-mail.com');
      setEmailBody(
        'Dear Valued Customer,\n\nWe noticed unauthorized login attempts to your PayPal account from an unrecognized IP address. For your security, your account has been temporarily restricted.\n\nPlease verify your identity immediately: click here to confirm your login credentials and credit card billing details.\n\nFailure to verify within 24 hours will result in permanent suspension.\n\nSincerely,\nPayPal Fraud Prevention Team'
      );
    } else if (type === 'invoice') {
      setEmailSubject('OVERDUE INVOICE #94821 - Immediate Payment Requested');
      setEmailSender('billing-department@supplier-direct.com');
      setEmailBody(
        'Please find attached the updated wire instructions for the outstanding invoice #94821. Kindly wire the payment of $14,200 to our new bank routing account immediately to prevent delivery cancellation.'
      );
    } else {
      setEmailSubject('Updated Engineering Roadmap - Sprint 42');
      setEmailSender('elena.rostova@acme-corp.internal');
      setEmailBody(
        'Hi team,\n\nHere is the summarized roadmap for Sprint 42. Please check your assigned tickets in Jira and reach out if you have any questions regarding the API integration deadline next Tuesday.\n\nBest regards,\nElena'
      );
    }
  };

  const loadUrlSample = (type) => {
    if (type === 'paypal') {
      setUrlInput('http://paypal-security-update.com/login.php');
    } else if (type === 'ip') {
      setUrlInput('http://192.168.1.1/admin/login');
    } else if (type === 'crypto') {
      setUrlInput('http://free-crypto-giveaway.online/claim?wallet=btc');
    } else if (type === 'google') {
      setUrlInput('https://www.google.com/search?q=cybersecurity');
    } else {
      setUrlInput('https://en.wikipedia.org/wiki/Artificial_intelligence');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      mediaRecorderRef.current = new MediaRecorder(stream);
      const chunks = [];

      mediaRecorderRef.current.ondataavailable = (event) => {
        if (event.data.size > 0) chunks.push(event.data);
      };

      mediaRecorderRef.current.onstop = () => {
        const blob = new Blob(chunks, { type: 'audio/wav' });
        setAudioBlob(blob);
        setAudioUrl(URL.createObjectURL(blob));
        stream.getTracks().forEach((track) => track.stop());
      };

      mediaRecorderRef.current.start();
      setIsRecording(true);
      setRecordTime(0);

      timerRef.current = setInterval(() => {
        setRecordTime((prev) => prev + 1);
      }, 1000);
    } catch {
      setErrorMessage('Microphone access denied or audio recording device not found.');
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      clearInterval(timerRef.current);
    }
  };

  const selectMode = (mode) => {
    if (isScanning) return;
    setActiveMode(mode);
    setErrorMessage(null);
  };

  const handleScan = async () => {
    setErrorMessage(null);

    if (activeMode === 'text' && !textInput.trim()) {
      setErrorMessage('Enter text content before starting the analysis.');
      return;
    }

    if (activeMode === 'email' && !emailBody.trim()) {
      setErrorMessage('Enter the email body before starting the analysis.');
      return;
    }

    if (activeMode === 'url' && !urlInput.trim()) {
      setErrorMessage('Enter a URL or domain before starting the inspection.');
      return;
    }

    if (activeMode === 'file' && !selectedFile) {
      setErrorMessage('Select or upload a document before starting the inspection.');
      return;
    }

    if (activeMode === 'audio' && !audioBlob && !selectedFile) {
      setErrorMessage('Record audio or upload an audio file before starting the analysis.');
      return;
    }

    setIsScanning(true);
    setScanStep(1);

    const stepTimer1 = setTimeout(() => setScanStep(2), 350);
    const stepTimer2 = setTimeout(() => setScanStep(3), 700);

    try {
      let response;

      if (activeMode === 'text') {
        response = await fetch('/api/scan/text', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: textInput.trim() }),
        });
      }

      if (activeMode === 'email') {
        response = await fetch('/api/scan/email', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            body: emailBody.trim(),
            subject: emailSubject.trim() || undefined,
            sender: emailSender.trim() || undefined,
          }),
        });
      }

      if (activeMode === 'url') {
        response = await fetch('/api/scan/url', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ url: urlInput.trim() }),
        });
      }

      if (activeMode === 'file') {
        const formData = new FormData();
        formData.append('file', selectedFile);

        response = await fetch('/api/scan/file', {
          method: 'POST',
          body: formData,
        });
      }

      if (activeMode === 'audio') {
        const formData = new FormData();

        if (audioBlob) {
          formData.append('file', audioBlob, 'mic_recording.wav');
        } else {
          formData.append('file', selectedFile);
        }

        response = await fetch('/api/scan/audio', {
          method: 'POST',
          body: formData,
        });
      }

      if (!response.ok) {
        let message = 'Threat analysis failed.';

        try {
          const errorData = await response.json();
          message = errorData.detail || message;
        } catch {
          // Keep fallback message.
        }

        throw new Error(message);
      }

      const data = await response.json();

      setScanStep(4);

      setTimeout(() => {
        setIsScanning(false);
        onScanComplete(data);
      }, 300);
    } catch (error) {
      clearTimeout(stepTimer1);
      clearTimeout(stepTimer2);
      setIsScanning(false);
      setErrorMessage(error.message || 'Connection error to backend analysis service.');
    }
  };

  const modeIcon = currentMode?.icon || FileText;

  return (
    <section className="relative overflow-hidden rounded-[26px] border border-white/[0.09] bg-[#0b111d]/95 shadow-[0_25px_80px_rgba(0,0,0,0.35)]">
      <div className="absolute -top-40 left-1/4 h-80 w-80 rounded-full bg-cyan-500/[0.07] blur-3xl pointer-events-none" />
      <div className="absolute -bottom-40 right-10 h-80 w-80 rounded-full bg-blue-600/[0.06] blur-3xl pointer-events-none" />

      {isScanning && (
        <div className="absolute inset-0 z-50 flex items-center justify-center bg-[#050a12]/90 backdrop-blur-xl">
          <div className="w-full max-w-lg px-8">
            <div className="relative mx-auto mb-8 flex h-28 w-28 items-center justify-center">
              <div className="absolute inset-0 rounded-full border border-cyan-400/20" />
              <div className="absolute inset-2 rounded-full border border-cyan-400/30 border-t-cyan-300 animate-spin" />
              <div className="absolute inset-5 rounded-full bg-cyan-400/10 shadow-[0_0_50px_rgba(34,211,238,0.2)]" />
              <Scan className="relative h-9 w-9 text-cyan-300 animate-pulse" />
            </div>

            <div className="text-center">
              <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.3em] text-cyan-400">
                SentriX AI AI AI NEURAL ANALYSIS
              </div>

              <h3 className="text-xl font-bold text-white">
                {scanStep === 1 && 'Ingesting threat payload'}
                {scanStep === 2 && 'Extracting behavioral features'}
                {scanStep === 3 && 'Running model inference'}
                {scanStep === 4 && 'Synthesizing security verdict'}
              </h3>

              <p className="mt-2 text-sm text-slate-500">
                Multi-layer detection pipeline is analyzing the submitted signal.
              </p>

              <div className="mx-auto mt-7 flex max-w-md gap-1.5">
                {[1, 2, 3, 4].map((step) => (
                  <div
                    key={step}
                    className={`h-1.5 flex-1 rounded-full transition-all duration-500 ${
                      step <= scanStep ? 'bg-cyan-400 shadow-[0_0_12px_rgba(34,211,238,0.55)]' : 'bg-white/10'
                    }`}
                  />
                ))}
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="relative border-b border-white/[0.07] px-5 py-6 sm:px-7 lg:px-9">
        <div className="flex flex-col gap-5 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <div className="mb-2 flex items-center gap-2">
              <span className="flex h-7 w-7 items-center justify-center rounded-lg bg-cyan-400/10 text-cyan-300 border border-cyan-400/20">
                <ShieldCheck className="h-4 w-4" />
              </span>
              <span className="text-[10px] font-bold uppercase tracking-[0.25em] text-cyan-400">
                Threat Intelligence Console
              </span>
            </div>

            <h1 className="text-2xl font-bold tracking-tight text-white sm:text-3xl">
              Analyze a <span className="text-cyan-300">Threat Signal</span>
            </h1>

            <p className="mt-1.5 max-w-2xl text-sm text-slate-500">
              Submit a message, email, URL, document, or voice sample. SentriX AI AI AI will
              correlate multiple security signals and produce a real-time verdict.
            </p>
          </div>

          <div className="flex shrink-0 items-center gap-3 rounded-2xl border border-emerald-400/15 bg-emerald-400/[0.04] px-4 py-3">
            <div className="relative">
              <span className="absolute inset-0 animate-ping rounded-full bg-emerald-400/30" />
              <span className="relative block h-2.5 w-2.5 rounded-full bg-emerald-400" />
            </div>
            <div>
              <div className="text-[10px] font-bold uppercase tracking-widest text-emerald-300">
                Engine Online
              </div>
              <div className="font-mono text-[9px] text-slate-500">
                REAL-TIME PROTECTION
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="relative px-4 py-5 sm:px-7 lg:px-9">
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2 lg:grid-cols-5">
          {MODES.map((mode) => {
            const Icon = mode.icon;
            const active = activeMode === mode.id;

            return (
              <button
                key={mode.id}
                type="button"
                disabled={isScanning}
                onClick={() => selectMode(mode.id)}
                className={`group relative overflow-hidden rounded-2xl border p-4 text-left transition-all duration-200 ${
                  active
                    ? 'border-cyan-400/40 bg-cyan-400/[0.09] shadow-[0_0_28px_rgba(34,211,238,0.08)]'
                    : 'border-white/[0.07] bg-white/[0.018] hover:border-white/15 hover:bg-white/[0.035]'
                }`}
              >
                {active && (
                  <span className="absolute right-3 top-3 h-1.5 w-1.5 rounded-full bg-cyan-300 shadow-[0_0_10px_rgba(34,211,238,0.9)]" />
                )}

                <div
                  className={`mb-3 flex h-9 w-9 items-center justify-center rounded-xl border transition-all ${
                    active
                      ? 'border-cyan-400/30 bg-cyan-400/10 text-cyan-300'
                      : 'border-white/10 bg-white/[0.03] text-slate-500 group-hover:text-slate-300'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                </div>

                <div className={`text-xs font-bold ${active ? 'text-white' : 'text-slate-300'}`}>
                  {mode.label}
                </div>

                <div className="mt-1 text-[10px] leading-4 text-slate-600">
                  {mode.description}
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {errorMessage && (
        <div className="mx-4 mb-5 flex items-start gap-3 rounded-2xl border border-red-400/20 bg-red-400/[0.06] px-4 py-3 sm:mx-7 lg:mx-9">
          <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-red-400" />
          <div>
            <div className="text-xs font-bold text-red-300">Analysis Input Error</div>
            <div className="mt-0.5 text-xs text-red-400/80">{errorMessage}</div>
          </div>
        </div>
      )}

      <div className="relative px-4 pb-7 sm:px-7 lg:px-9">
        <div className="mb-5 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-10 w-10 items-center justify-center rounded-xl border border-cyan-400/20 bg-cyan-400/[0.06] text-cyan-300">
              {React.createElement(modeIcon, { className: 'h-5 w-5' })}
            </div>
            <div>
              <div className="text-[10px] font-bold uppercase tracking-[0.22em] text-cyan-400">
                Active Detection Module
              </div>
              <div className="mt-0.5 text-base font-semibold text-white">
                {currentMode?.label}
              </div>
            </div>
          </div>

          <div className="flex items-center gap-2 font-mono text-[10px] text-slate-600">
            <Activity className="h-3.5 w-3.5 text-emerald-400" />
            MODEL PIPELINE READY
          </div>
        </div>

        {activeMode === 'text' && (
          <div className="space-y-4">
            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
              <label className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">
                Message Payload
              </label>

              <div className="flex flex-wrap gap-1.5">
                <span className="mr-1 self-center font-mono text-[9px] text-slate-600">SAMPLES</span>
                <button onClick={() => loadTextSample('fraud')} className="rounded-lg border border-red-400/20 bg-red-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-red-300 hover:bg-red-400/10">Bank Scam</button>
                <button onClick={() => loadTextSample('crypto')} className="rounded-lg border border-amber-400/20 bg-amber-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-amber-300 hover:bg-amber-400/10">Prize Scam</button>
                <button onClick={() => loadTextSample('safe')} className="rounded-lg border border-emerald-400/20 bg-emerald-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-emerald-300 hover:bg-emerald-400/10">Clean Text</button>
              </div>
            </div>

            <div className="relative">
              <textarea
                value={textInput}
                onChange={(e) => setTextInput(e.target.value)}
                placeholder="Paste an SMS, social engineering message, suspicious prompt, or any text payload..."
                rows={8}
                className="cyber-textarea min-h-[190px] border-white/[0.09] bg-[#070d17]/80 text-sm leading-6 placeholder:text-slate-700 focus:border-cyan-400/50"
              />

              <div className="pointer-events-none absolute bottom-3 left-4 flex items-center gap-2 text-[9px] font-mono text-slate-700">
                <LockKeyhole className="h-3 w-3" />
                LOCAL INPUT BUFFER
              </div>
            </div>

            <div className="flex justify-between font-mono text-[10px] text-slate-600">
              <span>{textInput.length.toLocaleString()} characters</span>
              <span>DistilBERT Sequence Classifier</span>
            </div>
          </div>
        )}

        {activeMode === 'email' && (
          <div className="space-y-4">
            <div className="flex flex-wrap gap-1.5">
              <span className="mr-1 self-center font-mono text-[9px] text-slate-600">QUICK LOAD</span>
              <button onClick={() => loadEmailSample('phish')} className="rounded-lg border border-red-400/20 bg-red-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-red-300">PayPal Phishing</button>
              <button onClick={() => loadEmailSample('invoice')} className="rounded-lg border border-amber-400/20 bg-amber-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-amber-300">Fake Invoice</button>
              <button onClick={() => loadEmailSample('safe')} className="rounded-lg border border-emerald-400/20 bg-emerald-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-emerald-300">Clean Email</button>
            </div>

            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <div className="rounded-2xl border border-white/[0.07] bg-white/[0.018] p-4">
                <label className="mb-2 block font-mono text-[9px] uppercase tracking-widest text-slate-600">Subject Line</label>
                <input
                  value={emailSubject}
                  onChange={(e) => setEmailSubject(e.target.value)}
                  placeholder="URGENT: Account Suspension Notice"
                  className="cyber-input border-white/[0.08] bg-[#070d17]"
                />
              </div>

              <div className="rounded-2xl border border-white/[0.07] bg-white/[0.018] p-4">
                <label className="mb-2 block font-mono text-[9px] uppercase tracking-widest text-slate-600">Sender Address</label>
                <input
                  value={emailSender}
                  onChange={(e) => setEmailSender(e.target.value)}
                  placeholder="security@example.com"
                  className="cyber-input border-white/[0.08] bg-[#070d17]"
                />
              </div>
            </div>

            <div className="rounded-2xl border border-white/[0.07] bg-white/[0.018] p-4">
              <label className="mb-2 block font-mono text-[9px] uppercase tracking-widest text-slate-600">Email Body</label>
              <textarea
                value={emailBody}
                onChange={(e) => setEmailBody(e.target.value)}
                placeholder="Paste the complete email body, links, payment instructions, or call-to-action..."
                rows={7}
                className="cyber-textarea min-h-[175px] border-white/[0.08] bg-[#070d17]"
              />
            </div>

            <div className="flex items-center gap-2 font-mono text-[10px] text-slate-600">
              <Mail className="h-3.5 w-3.5 text-violet-400" />
              Header + linguistic + urgency feature analysis enabled
            </div>
          </div>
        )}

        {activeMode === 'url' && (
          <div className="space-y-5">
            <div className="flex flex-wrap gap-1.5">
              <span className="mr-1 self-center font-mono text-[9px] text-slate-600">TEST LINKS</span>
              <button onClick={() => loadUrlSample('paypal')} className="rounded-lg border border-red-400/20 bg-red-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-red-300">PayPal Phish</button>
              <button onClick={() => loadUrlSample('ip')} className="rounded-lg border border-red-400/20 bg-red-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-red-300">IP Host</button>
              <button onClick={() => loadUrlSample('crypto')} className="rounded-lg border border-amber-400/20 bg-amber-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-amber-300">Crypto Scam</button>
              <button onClick={() => loadUrlSample('google')} className="rounded-lg border border-emerald-400/20 bg-emerald-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-emerald-300">Google Safe</button>
              <button onClick={() => loadUrlSample('wiki')} className="rounded-lg border border-emerald-400/20 bg-emerald-400/[0.06] px-2.5 py-1.5 font-mono text-[9px] text-emerald-300">Wikipedia Safe</button>
            </div>

            <div className="relative rounded-2xl border border-cyan-400/15 bg-cyan-400/[0.025] p-2 shadow-[0_0_30px_rgba(34,211,238,0.04)]">
              <div className="flex items-center">
                <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl text-cyan-300">
                  <Globe2 className="h-5 w-5" />
                </div>
                <input
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  placeholder="https://example.com/login"
                  className="w-full border-0 bg-transparent px-2 py-3 font-mono text-sm text-white outline-none placeholder:text-slate-700"
                />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-2 sm:grid-cols-3">
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-3">
                <div className="flex items-center gap-2 text-cyan-300"><Database className="h-3.5 w-3.5" /><span className="font-mono text-[9px]">33 FEATURES</span></div>
                <div className="mt-1 text-[9px] text-slate-600">Lexical URL analysis</div>
              </div>
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-3">
                <div className="flex items-center gap-2 text-blue-300"><Shield className="h-3.5 w-3.5" /><span className="font-mono text-[9px]">RF ENSEMBLE</span></div>
                <div className="mt-1 text-[9px] text-slate-600">Random Forest inference</div>
              </div>
              <div className="rounded-xl border border-white/[0.06] bg-white/[0.018] p-3">
                <div className="flex items-center gap-2 text-emerald-300"><CheckCircle2 className="h-3.5 w-3.5" /><span className="font-mono text-[9px]">DOMAIN FILTER</span></div>
                <div className="mt-1 text-[9px] text-slate-600">Whitelist + spoof checks</div>
              </div>
            </div>
          </div>
        )}

        {activeMode === 'file' && (
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-400">Document Payload</div>
                <div className="mt-1 font-mono text-[9px] text-slate-600">EML / MSG / TXT / PDF / JSON / LOG</div>
              </div>
              <FileUp className="h-5 w-5 text-amber-400/70" />
            </div>

            <input
              ref={fileInputRef}
              type="file"
              className="hidden"
              onChange={(e) => {
                if (e.target.files?.[0]) setSelectedFile(e.target.files[0]);
              }}
            />

            <div
              onDragOver={(e) => {
                e.preventDefault();
                setDragActive(true);
              }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                if (e.dataTransfer.files?.[0]) setSelectedFile(e.dataTransfer.files[0]);
              }}
              onClick={() => fileInputRef.current?.click()}
              className={`group cursor-pointer rounded-[22px] border border-dashed p-10 text-center transition-all ${
                dragActive
                  ? 'border-cyan-400 bg-cyan-400/[0.08]'
                  : selectedFile
                    ? 'border-emerald-400/30 bg-emerald-400/[0.04]'
                    : 'border-white/10 bg-white/[0.015] hover:border-cyan-400/30 hover:bg-cyan-400/[0.025]'
              }`}
            >
              <div className={`mx-auto flex h-16 w-16 items-center justify-center rounded-2xl border ${
                selectedFile
                  ? 'border-emerald-400/20 bg-emerald-400/10 text-emerald-300'
                  : 'border-cyan-400/20 bg-cyan-400/10 text-cyan-300'
              }`}>
                {selectedFile ? <CheckCircle2 className="h-7 w-7" /> : <Upload className="h-7 w-7" />}
              </div>

              {selectedFile ? (
                <>
                  <div className="mt-4 text-sm font-semibold text-white">{selectedFile.name}</div>
                  <div className="mt-1 font-mono text-[10px] text-emerald-400/70">
                    {(selectedFile.size / 1024).toFixed(1)} KB - READY FOR INSPECTION
                  </div>
                </>
              ) : (
                <>
                  <div className="mt-4 text-sm font-semibold text-slate-300">Drop a suspicious file here</div>
                  <div className="mt-1 text-xs text-slate-600">or click to browse your device</div>
                </>
              )}
            </div>

            <div className="flex items-center gap-2 font-mono text-[10px] text-slate-600">
              <Sparkles className="h-3.5 w-3.5 text-amber-400" />
              Automated text parsing and embedded-link extraction
            </div>
          </div>
        )}

        {activeMode === 'audio' && (
          <div className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
              <div className={`rounded-[22px] border p-6 text-center ${
                isRecording
                  ? 'border-red-400/30 bg-red-400/[0.05]'
                  : 'border-white/[0.07] bg-white/[0.018]'
              }`}>
                <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                  Live Microphone
                </div>

                <div className="relative mx-auto my-6 h-24 w-24">
                  {isRecording && (
                    <div className="absolute inset-0 animate-ping rounded-full border border-red-400/30" />
                  )}

                  <button
                    type="button"
                    onClick={isRecording ? stopRecording : startRecording}
                    className={`relative flex h-24 w-24 items-center justify-center rounded-full border transition-all ${
                      isRecording
                        ? 'border-red-400/40 bg-red-500/15 text-red-300 shadow-[0_0_45px_rgba(239,68,68,0.2)]'
                        : 'border-cyan-400/30 bg-cyan-400/[0.08] text-cyan-300 hover:bg-cyan-400/[0.14]'
                    }`}
                  >
                    {isRecording ? <Square className="h-7 w-7" /> : <Mic className="h-7 w-7" />}
                  </button>
                </div>

                <div className={`font-mono text-xs ${isRecording ? 'text-red-300' : 'text-slate-500'}`}>
                  {isRecording
                    ? `RECORDING ${recordTime}s`
                    : audioBlob
                      ? `AUDIO CAPTURED - ${recordTime}s`
                      : 'CLICK TO RECORD SAMPLE'}
                </div>

                {audioUrl && (
                  <audio controls src={audioUrl} className="mt-5 w-full" />
                )}
              </div>

              <div className="rounded-[22px] border border-white/[0.07] bg-white/[0.018] p-6 text-center">
                <div className="mb-2 text-[10px] font-bold uppercase tracking-[0.2em] text-slate-500">
                  Audio Upload
                </div>

                <input
                  ref={audioInputRef}
                  type="file"
                  accept="audio/*"
                  className="hidden"
                  onChange={(e) => {
                    if (e.target.files?.[0]) {
                      setSelectedFile(e.target.files[0]);
                      setAudioBlob(null);
                    }
                  }}
                />

                <div className="flex h-full min-h-[220px] flex-col items-center justify-center">
                  <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-2xl border border-violet-400/20 bg-violet-400/[0.08] text-violet-300">
                    <Radio className="h-6 w-6" />
                  </div>

                  <button
                    type="button"
                    onClick={() => audioInputRef.current?.click()}
                    className="rounded-xl border border-white/10 bg-white/[0.04] px-5 py-3 text-xs font-semibold text-slate-300 transition hover:bg-white/[0.08]"
                  >
                    Choose WAV / MP3
                  </button>

                  <div className="mt-3 max-w-full truncate font-mono text-[10px] text-slate-600">
                    {selectedFile ? selectedFile.name : 'No audio file selected'}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}

        <div className="mt-7 flex flex-col gap-4 border-t border-white/[0.07] pt-6 sm:flex-row sm:items-center sm:justify-between">
          <div className="flex items-center gap-3">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-cyan-400/15 bg-cyan-400/[0.05]">
              <BrainCircuit className="h-4 w-4 text-cyan-300" />
            </div>
            <div>
              <div className="text-[10px] font-bold text-slate-400">MULTI-MODEL VERDICT ENGINE</div>
              <div className="mt-0.5 font-mono text-[9px] text-slate-600">
                Neural inference + threat signal correlation
              </div>
            </div>
          </div>

          <button
            type="button"
            onClick={handleScan}
            disabled={isScanning}
            className="group relative flex items-center justify-center gap-3 overflow-hidden rounded-xl bg-gradient-to-r from-cyan-400 to-blue-500 px-7 py-4 text-sm font-bold text-[#031019] shadow-[0_10px_35px_rgba(34,211,238,0.2)] transition-all hover:-translate-y-0.5 hover:shadow-[0_14px_40px_rgba(34,211,238,0.3)] disabled:cursor-not-allowed disabled:opacity-60 disabled:hover:translate-y-0"
          >
            {isScanning ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Analyzing Threat Vector
              </>
            ) : (
              <>
                <ShieldCheck className="h-4 w-4" />
                Execute SentriX AI AI AI Scan
                <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
              </>
            )}
          </button>
        </div>
      </div>
    </section>
  );
}

