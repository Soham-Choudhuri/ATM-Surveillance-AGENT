"use client";
import React, { useState, useEffect } from 'react';

export default function DispatchCenter() {
  const [state, setState] = useState<any>(null);
  const [acknowledgedId, setAcknowledgedId] = useState<string | null>(null);

  useEffect(() => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch('http://localhost:8000/api/state');
        const data = await res.json();
        setState(data);
      } catch (err) {
        // Silent fail
      }
    }, 500);
    return () => clearInterval(interval);
  }, []);

  const isCritical = state?.latest_report?.severity?.toUpperCase() === 'HIGH' || state?.threat_level?.includes('CRITICAL');
  
  // Use the description as a unique key for the current incident
  const currentIncidentKey = state?.latest_report?.description;
  const isAlarming = isCritical && currentIncidentKey && currentIncidentKey !== acknowledgedId;

  return (
    <div className={`min-h-screen transition-colors duration-300 flex flex-col font-sans ${isAlarming ? 'bg-rose-600 animate-[pulse_1s_ease-in-out_infinite]' : 'bg-neutral-950'} text-white`}>
      <header className="border-b border-white/10 bg-black/50 backdrop-blur-xl p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-black tracking-tight uppercase">Central Dispatch Center</h1>
            <p className="text-white/70 mt-1">Live Threat Monitoring</p>
          </div>
          <div className="flex items-center space-x-4">
             <div className="flex items-center space-x-2 text-sm font-bold bg-black/30 px-4 py-2 rounded-lg">
               <span className="relative flex h-3 w-3">
                 <span className={`animate-ping absolute inline-flex h-full w-full rounded-full opacity-75 ${state?.monitoring ? 'bg-emerald-400' : 'bg-rose-400'}`}></span>
                 <span className={`relative inline-flex rounded-full h-3 w-3 ${state?.monitoring ? 'bg-emerald-500' : 'bg-rose-500'}`}></span>
               </span>
               <span>{state?.monitoring ? 'FEED ACTIVE' : 'FEED OFFLINE'}</span>
             </div>
             <a href="/" className="text-white/50 hover:text-white transition-colors underline">Return to Dashboard</a>
          </div>
        </div>
      </header>

      <main className="flex-1 p-8 flex flex-col items-center justify-center">
        {isAlarming ? (
          <div className="bg-black/40 backdrop-blur-2xl border border-white/20 p-12 rounded-3xl max-w-4xl w-full text-center shadow-2xl">
            <svg className="w-32 h-32 text-white mx-auto mb-6 animate-bounce" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
            <h2 className="text-6xl font-black mb-4 tracking-tight drop-shadow-lg">CRITICAL INCIDENT DETECTED</h2>
            <div className="bg-rose-900/50 p-6 rounded-xl border border-rose-500/30 mb-8">
                <p className="text-2xl font-medium mb-2">{state?.latest_report?.classification}</p>
                <p className="text-xl text-rose-100">{state?.latest_report?.description}</p>
            </div>
            <button 
              onClick={() => setAcknowledgedId(currentIncidentKey)}
              className="bg-white text-rose-600 hover:bg-neutral-200 px-12 py-6 rounded-2xl text-2xl font-black uppercase tracking-widest transition-transform hover:scale-105 active:scale-95 shadow-xl"
            >
              Acknowledge & Dispatch Units
            </button>
          </div>
        ) : (
          <div className="text-center opacity-50">
             <svg className="w-24 h-24 mx-auto mb-6" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" /></svg>
             <h2 className="text-3xl font-medium tracking-widest uppercase">All Clear</h2>
             <p className="text-lg mt-2 font-light">Monitoring active feeds for critical events...</p>
             {state?.latest_report && (
                 <div className="mt-12 bg-white/5 border border-white/10 p-6 rounded-2xl max-w-2xl mx-auto text-left">
                     <p className="text-sm font-bold uppercase tracking-wider text-neutral-500 mb-2">Last Logged Event</p>
                     <p className="text-neutral-300">{state.latest_report.description}</p>
                 </div>
             )}
          </div>
        )}
      </main>
    </div>
  );
}
