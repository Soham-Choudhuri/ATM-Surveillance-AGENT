"use client";
import React, { useState, useEffect, useMemo } from 'react';

export default function Dashboard() {
  const [state, setState] = useState({
    monitoring: false,
    threat_level: "Waiting...",
    object_count: 0,
    latest_report: null,
    history: [],
    is_analyzing: false
  });
  
  const [source, setSource] = useState("Webcam");
  const [file, setFile] = useState<File | null>(null);
  const [intervalSeconds, setIntervalSeconds] = useState(10);
  const [activeConfig, setActiveConfig] = useState<any>({ provider: "Loading...", model_name: "...", alerts_enabled: false });

  useEffect(() => {
    fetch('http://localhost:8000/api/config')
      .then(res => res.json())
      .then(data => setActiveConfig(data))
      .catch(() => {});
      
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/api/state');
        const data = await res.json();
        setState(data);
      } catch (err) {
        // Silent fail on fetch error
      }
    }, 200);
    return () => clearInterval(interval);
  }, []);

  const handleStart = async () => {
    const formData = new FormData();
    formData.append("source", source);
    formData.append("interval", intervalSeconds.toString());
    if (source === "Upload Video" && file) {
      formData.append("file", file);
    }
    await fetch('http://localhost:8000/api/start', {
      method: 'POST',
      body: formData
    });
  };

  const handleStop = async () => {
    await fetch('http://localhost:8000/api/stop', { method: 'POST' });
  };

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans selection:bg-indigo-500/30">
      <header className="sticky top-0 z-50 border-b border-white/10 bg-neutral-950/50 backdrop-blur-xl">
        <div className="w-full mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
            </div>
            <h1 className="text-xl font-semibold tracking-tight">AI Surveillance Agent</h1>
          </div>
          <div className="flex items-center space-x-4">
             <div className="flex items-center space-x-2 text-sm font-medium">
               <span className="relative flex h-3 w-3">
                 <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${state.monitoring ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                 <span className={`relative inline-flex rounded-full h-3 w-3 ${state.monitoring ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
               </span>
               <span className="text-neutral-300">{state.monitoring ? 'System Online' : 'System Offline'}</span>
             </div>
             <a href="/admin" className="text-sm font-medium text-neutral-400 hover:text-white transition-colors">Admin Portal</a>
          </div>
        </div>
      </header>

      <main className="w-full mx-auto px-6 py-8 grid grid-cols-1 lg:grid-cols-12 gap-8">
        <aside className="lg:col-span-3 space-y-6">
          <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 shadow-2xl backdrop-blur-sm">
            <h2 className="text-lg font-medium mb-4 flex items-center text-neutral-200">
              <svg className="w-5 h-5 mr-2 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" /></svg>
              Control Panel
            </h2>
            
            <div className="space-y-4">
              <div>
                <label className="text-xs font-medium text-neutral-400 uppercase tracking-wider mb-2 block">Input Source</label>
                <div className="flex bg-neutral-900 rounded-lg p-1 border border-white/5">
                  <button onClick={() => setSource("Webcam")} className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${source === "Webcam" ? 'bg-neutral-800 text-white shadow' : 'text-neutral-400 hover:text-neutral-200'}`}>Webcam</button>
                  <button onClick={() => setSource("Upload Video")} className={`flex-1 py-1.5 text-sm font-medium rounded-md transition-all ${source === "Upload Video" ? 'bg-neutral-800 text-white shadow' : 'text-neutral-400 hover:text-neutral-200'}`}>Video File</button>
                </div>
              </div>

              {source === "Upload Video" && (
                <div className="animate-in fade-in slide-in-from-top-2 duration-200">
                  <label className="text-xs font-medium text-neutral-400 uppercase tracking-wider mb-2 block">Upload File</label>
                  <input type="file" accept="video/mp4,video/avi,video/mov" onChange={(e) => e.target.files && setFile(e.target.files[0])} className="w-full text-sm text-neutral-400 file:mr-3 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-xs file:font-semibold file:bg-indigo-500/10 file:text-indigo-400 hover:file:bg-indigo-500/20 cursor-pointer transition-all" />
                </div>
              )}

              <div className="pt-2">
                <label className="text-xs font-medium text-neutral-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Analysis Interval</span>
                  <span className="text-indigo-400 font-mono">{intervalSeconds}s</span>
                </label>
                <input 
                  type="range" 
                  min="1" max="60" 
                  value={intervalSeconds} 
                  onChange={(e) => setIntervalSeconds(parseInt(e.target.value))}
                  className="w-full accent-indigo-500"
                />
              </div>

              <div className="pt-2 flex items-center justify-between">
                <div>
                  <label className="text-xs font-medium text-neutral-400 uppercase tracking-wider block">Twilio Alerts</label>
                  <p className="text-[10px] text-neutral-500">Send SMS/WhatsApp on incident</p>
                </div>
                <button 
                  onClick={async () => {
                    const newState = !activeConfig.alerts_enabled;
                    setActiveConfig({...activeConfig, alerts_enabled: newState});
                    await fetch('http://localhost:8000/api/config', {
                      method: 'POST',
                      headers: { 'Content-Type': 'application/json' },
                      body: JSON.stringify({...activeConfig, alerts_enabled: newState})
                    });
                  }}
                  className={`w-11 h-6 rounded-full transition-colors relative ${activeConfig.alerts_enabled ? 'bg-indigo-500' : 'bg-neutral-700'}`}
                >
                  <div className={`w-4 h-4 bg-white rounded-full absolute top-1 transition-all ${activeConfig.alerts_enabled ? 'left-6' : 'left-1'}`}></div>
                </button>
              </div>

              <div className="grid grid-cols-2 gap-3 pt-2">
                <button onClick={handleStart} disabled={state.monitoring} className="relative overflow-hidden group bg-emerald-500/10 text-emerald-400 hover:bg-emerald-500/20 border border-emerald-500/20 disabled:opacity-50 disabled:cursor-not-allowed py-2 rounded-xl font-medium text-sm transition-all">
                  <span className="relative z-10">Start Stream</span>
                </button>
                <button onClick={handleStop} disabled={!state.monitoring} className="bg-rose-500/10 text-rose-400 hover:bg-rose-500/20 border border-rose-500/20 disabled:opacity-50 disabled:cursor-not-allowed py-2 rounded-xl font-medium text-sm transition-all">
                  Stop Stream
                </button>
              </div>

              <div className="pt-4 border-t border-white/5">
                <p className="text-xs font-medium text-neutral-400 uppercase tracking-wider mb-2 flex items-center justify-between">
                  <span>Active Intelligence</span>
                  {activeConfig.alerts_enabled ? (
                    <span className="bg-rose-500/10 text-rose-400 text-[10px] px-2 py-0.5 rounded-full font-bold">ALERTS ON</span>
                  ) : (
                    <span className="bg-neutral-800 text-neutral-500 text-[10px] px-2 py-0.5 rounded-full font-bold">MUTED</span>
                  )}
                </p>
                <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-3 flex items-center">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 mr-2 animate-pulse"></div>
                  <span className="text-sm text-indigo-300 font-medium capitalize">
                    {activeConfig.provider} ({activeConfig.model_name})
                  </span>
                </div>
              </div>
            </div>
          </div>
        </aside>

        <div className="lg:col-span-9 space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div className="lg:col-span-2 rounded-2xl overflow-hidden bg-neutral-900 border border-white/5 shadow-2xl relative flex items-center justify-center group min-h-[400px] max-h-[75vh]">
              {useMemo(() => state.monitoring ? (
                <img src="http://localhost:8000/api/video_feed" alt="Live Feed" className="w-full h-full object-contain" />
              ) : (
                <div className="text-center text-neutral-500 py-24">
                  <svg className="w-12 h-12 mx-auto mb-3 opacity-20" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" /></svg>
                  <p className="text-sm font-medium">Camera Offline</p>
                </div>
              ), [state.monitoring])}
              
              {state.monitoring && (
                <div className="absolute top-4 left-4 flex space-x-2">
                  <div className="bg-black/50 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 flex items-center space-x-2 text-xs font-mono">
                    <span className="w-2 h-2 rounded-full bg-rose-500 animate-pulse"></span>
                    <span>LIVE</span>
                  </div>
                  <div className="bg-black/50 backdrop-blur-md px-3 py-1.5 rounded-lg border border-white/10 text-xs font-mono">
                    Objects: {state.object_count}
                  </div>
                </div>
              )}

              {(state as any).is_analyzing && (
                <div className="absolute inset-0 bg-black/40 backdrop-blur-[2px] flex items-center justify-center z-10 transition-all">
                  <div className="bg-neutral-900/90 border border-white/10 px-6 py-4 rounded-2xl flex items-center space-x-4 shadow-2xl">
                    <svg className="animate-spin -ml-1 mr-3 h-6 w-6 text-indigo-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                    </svg>
                    <div>
                      <h3 className="text-sm font-semibold text-white">Analyzing Feed</h3>
                      <p className="text-xs text-neutral-400">Please wait while the VLM processes the incident...</p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="space-y-6">
              <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 shadow-2xl h-full flex flex-col">
                <h2 className="text-lg font-medium mb-6 flex items-center text-neutral-200">
                  <svg className="w-5 h-5 mr-2 text-purple-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                  Intelligence Hub
                </h2>
                
                <div className="mb-6">
                  <p className="text-xs font-medium text-neutral-400 uppercase tracking-wider mb-1">Current Threat Level</p>
                  <div className={`text-2xl font-bold tracking-tight ${state.threat_level.includes('CRITICAL') ? 'text-rose-400' : state.threat_level.includes('MEDIUM') ? 'text-amber-400' : state.threat_level === 'Waiting...' ? 'text-neutral-500' : 'text-emerald-400'}`}>
                    {state.threat_level}
                  </div>
                </div>

                <div className="flex-1 bg-neutral-900/50 rounded-xl border border-white/5 p-4 overflow-y-auto max-h-[300px]">
                  <p className="text-xs font-medium text-neutral-400 uppercase tracking-wider mb-3">AI Incident Report</p>
                  {state.latest_report ? (
                    <div className="space-y-3 text-sm">
                      <p><span className="text-neutral-400">Class:</span> <span className="font-medium text-white">{(state.latest_report as any).classification}</span></p>
                      <p className="text-neutral-300 leading-relaxed"><span className="text-neutral-400">Analysis:</span> {(state.latest_report as any).description}</p>
                      <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-3 mt-4">
                        <p className="text-indigo-300 font-medium mb-1">Recommendation</p>
                        <p className="text-indigo-200/80">{(state.latest_report as any).recommendation}</p>
                      </div>
                    </div>
                  ) : (
                    <p className="text-sm text-neutral-500 text-center mt-8">Awaiting analysis...</p>
                  )}
                </div>
              </div>
            </div>
          </div>
          
          {/* History Section */}
          <div className="lg:col-span-12 mt-8">
            <div className="p-6 rounded-2xl bg-white/[0.02] border border-white/5 shadow-2xl">
              <h2 className="text-lg font-medium mb-6 flex items-center text-neutral-200">
                <svg className="w-5 h-5 mr-2 text-indigo-400" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
                Analysis History & Logs
              </h2>
              <div className="space-y-4 max-h-[500px] overflow-y-auto pr-2 custom-scrollbar">
                {state.history.length === 0 ? (
                  <p className="text-neutral-500 text-sm text-center py-8">No historical reports available yet.</p>
                ) : (
                  state.history.map((log: any, idx) => (
                    <details key={idx} className="group bg-neutral-900/50 rounded-xl border border-white/5 overflow-hidden">
                      <summary className="flex items-center justify-between p-4 cursor-pointer hover:bg-neutral-800/50 transition-colors list-none">
                        <div className="flex items-center space-x-4">
                          <span className={`px-2.5 py-1 rounded-md text-xs font-bold tracking-wide ${log.Severity === 'HIGH' ? 'bg-rose-500/20 text-rose-400' : log.Severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                            {log.Severity}
                          </span>
                          <span className="text-sm font-medium text-white">{log.Type}</span>
                          <span className="text-xs text-neutral-400">{log.Time}</span>
                        </div>
                        <svg className="w-5 h-5 text-neutral-500 group-open:rotate-180 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" /></svg>
                      </summary>
                      <div className="p-4 pt-0 border-t border-white/5 mt-2 text-sm text-neutral-300">
                        <p className="mb-4">{log.Summary}</p>
                        {log.Details?.recommendation && (
                           <div className="bg-indigo-500/10 border border-indigo-500/20 rounded-lg p-3">
                             <p className="text-indigo-300 font-medium mb-1">Action Recommendation</p>
                             <p className="text-indigo-200/80">{log.Details.recommendation}</p>
                           </div>
                        )}
                      </div>
                    </details>
                  ))
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
