"use client";
import React, { useState, useEffect } from 'react';

export default function AdminPortal() {
  const [access, setAccess] = useState<boolean | null>(null);
  const [config, setConfig] = useState({
    active_mode: "local",
    provider: "ollama",
    model_name: "moondream",
    api_key: "",
    twilio_sid: "",
    twilio_auth: "",
    twilio_type: "SMS",
    twilio_from: "",
    twilio_to: ""
  });
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    fetch(`/api/admin_check`)
      .then(res => res.json())
      .then(data => setAccess(data.access))
      .catch(() => setAccess(false));
      
    fetch(`/api/config`)
      .then(res => res.json())
      .then(data => setConfig(data))
      .catch(() => {});
  }, []);

  const handleModeChange = (mode: string) => {
    if (mode === "local") {
      setConfig({...config, active_mode: "local", provider: "ollama", model_name: "moondream", api_key: ""});
    } else {
      setConfig({...config, active_mode: "cloud", provider: "gemini", model_name: "gemini-1.5-flash"});
    }
  };

  const handleProviderChange = (provider: string) => {
    let defaultModel = "";
    if (provider === "gemini") defaultModel = "gemini-1.5-flash";
    else if (provider === "groq") defaultModel = "llama3-8b-8192";
    else if (provider === "huggingface") defaultModel = "Salesforce/blip-image-captioning-large";
    else if (provider === "ollama") defaultModel = "moondream";
    
    setConfig({...config, provider: provider, model_name: defaultModel});
  };

  const handleSave = async () => {
    setSaving(true);
    await fetch(`/api/config`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(config)
    });
    setTimeout(() => setSaving(false), 800);
  };

  if (access === null) return <div className="min-h-screen bg-neutral-950 flex items-center justify-center text-white">Loading...</div>;
  if (access === false) return (
    <div className="min-h-screen bg-neutral-950 flex flex-col items-center justify-center text-white">
      <div className="w-16 h-16 bg-rose-500/10 text-rose-500 flex items-center justify-center rounded-2xl mb-4">
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" /></svg>
      </div>
      <h1 className="text-2xl font-bold mb-2">Access Denied</h1>
      <p className="text-neutral-400">Missing .admin_access token.</p>
      <a href="/" className="mt-6 text-indigo-400 hover:text-indigo-300 font-medium">Return to Dashboard</a>
    </div>
  );

  return (
    <div className="min-h-screen bg-neutral-950 text-white font-sans">
      <header className="border-b border-white/10 bg-neutral-950/50 backdrop-blur-xl">
        <div className="max-w-4xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center space-x-3 text-rose-400">
             <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
             <h1 className="text-xl font-semibold">AwareX Administration</h1>
          </div>
          <a href="/" className="text-sm font-medium text-neutral-400 hover:text-white transition-colors">Exit Admin</a>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-6 py-12">
        <div className="p-8 rounded-3xl bg-white/[0.02] border border-white/5 shadow-2xl">
          <h2 className="text-2xl font-bold mb-2">Model Configuration</h2>
          <p className="text-neutral-400 mb-8 text-sm">Select and configure the visual language model powering the intelligence hub.</p>

          <div className="space-y-6">
            <div>
              <label className="text-sm font-medium text-neutral-300 block mb-2">Execution Mode</label>
              <div className="flex bg-neutral-900 rounded-xl p-1 border border-white/5 max-w-sm">
                  <button onClick={() => handleModeChange("local")} className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${config.active_mode === "local" ? 'bg-indigo-500 text-white shadow' : 'text-neutral-400 hover:text-neutral-200'}`}>Local Edge</button>
                  <button onClick={() => handleModeChange("cloud")} className={`flex-1 py-2 text-sm font-medium rounded-lg transition-all ${config.active_mode === "cloud" ? 'bg-indigo-500 text-white shadow' : 'text-neutral-400 hover:text-neutral-200'}`}>Cloud API</button>
              </div>
            </div>

            {config.active_mode === "local" && (
              <div className="animate-in fade-in slide-in-from-top-2 duration-300 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Local Provider</label>
                  <select 
                    value={config.provider} 
                    onChange={e => handleProviderChange(e.target.value)}
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none text-white"
                  >
                    <option value="ollama">Ollama</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Model Name</label>
                  <select 
                    value={config.model_name}
                    onChange={e => setConfig({...config, model_name: e.target.value})}
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none text-white"
                  >
                    <option value="moondream">moondream</option>
                    <option value="llava">llava</option>
                    <option value="bakllava">bakllava</option>
                  </select>
                </div>
              </div>
            )}

            {config.active_mode === "cloud" && (
              <div className="animate-in fade-in slide-in-from-top-2 duration-300 grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Cloud Provider</label>
                  <select 
                    value={config.provider} 
                    onChange={e => handleProviderChange(e.target.value)}
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none text-white"
                  >
                    <option value="gemini">Google Gemini</option>
                    <option value="groq">Groq</option>
                    <option value="huggingface">Hugging Face</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Model Name</label>
                  <input 
                    type="text" 
                    value={config.model_name}
                    onChange={e => setConfig({...config, model_name: e.target.value})}
                    placeholder="e.g. gemini-1.5-flash"
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="text-sm font-medium text-neutral-300 block mb-2">API Key</label>
                  <input 
                    type="password" 
                    value={config.api_key}
                    onChange={e => setConfig({...config, api_key: e.target.value})}
                    placeholder="Enter your secret key"
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white"
                  />
                </div>
              </div>
            )}

            <div className="pt-8 mt-8 border-t border-white/5">
              <h2 className="text-xl font-bold mb-2">Communications & Alerts</h2>
              <p className="text-neutral-400 mb-6 text-sm">Configure Twilio credentials for SMS and WhatsApp incident alerting.</p>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Twilio Account SID</label>
                  <input 
                    type="text" 
                    value={(config as any).twilio_sid || ""}
                    onChange={e => setConfig({...config, twilio_sid: e.target.value})}
                    placeholder="AC..."
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Auth Token</label>
                  <input 
                    type="password" 
                    value={(config as any).twilio_auth || ""}
                    onChange={e => setConfig({...config, twilio_auth: e.target.value})}
                    placeholder="Enter secret token"
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Message Type</label>
                  <select 
                    value={(config as any).twilio_type || "SMS"}
                    onChange={e => setConfig({...config, twilio_type: e.target.value})}
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 appearance-none text-white"
                  >
                    <option value="SMS">Standard SMS</option>
                    <option value="WhatsApp">WhatsApp Message</option>
                  </select>
                </div>
                <div>
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Sender Number (Twilio)</label>
                  <input 
                    type="text" 
                    value={(config as any).twilio_from || ""}
                    onChange={e => setConfig({...config, twilio_from: e.target.value})}
                    placeholder="+1234567890"
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white"
                  />
                </div>
                <div className="md:col-span-2">
                  <label className="text-sm font-medium text-neutral-300 block mb-2">Receiver Authority Number</label>
                  <input 
                    type="text" 
                    value={(config as any).twilio_to || ""}
                    onChange={e => setConfig({...config, twilio_to: e.target.value})}
                    placeholder="+1234567890"
                    className="w-full bg-neutral-900 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500/50 text-white"
                  />
                </div>
              </div>
            </div>

            <div className="pt-6 border-t border-white/5 flex items-center justify-between">
              <a href="https://www.twilio.com/login" target="_blank" rel="noopener noreferrer" className="text-sm text-indigo-400 hover:text-indigo-300 transition-colors font-medium flex items-center gap-1">
                 Twilio Developer Dashboard
                 <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
              </a>
              <button 
                onClick={handleSave} 
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-6 py-2.5 rounded-xl font-medium text-sm transition-all flex items-center shadow-lg shadow-indigo-500/20"
              >
                {saving ? 'Saving...' : 'Save Configuration'}
              </button>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}
