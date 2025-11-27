import React, { useState, useEffect, useCallback } from 'react';
import { Calendar, Users, Settings, Hourglass, Trash2, Plus, Zap, AlertCircle, Download } from 'lucide-react';
import { FileDropzone } from './components/FileDropzone';

// --- Environment Configuration ---
// If deployed, use the Env Var. If local, use localhost.
const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

interface Availability {
  day: string;
  time_slot: string;
}

interface Employee {
  id: number;
  name: string;
  ideal_shifts: number;
  preference_score: number;
  availabilities: Availability[];
}

interface ShiftDefinition {
  id: number;
  day: string;
  time_slot: string;
}

function App() {
  const [employees, setEmployees] = useState<Employee[]>([]);
  const [shiftDefs, setShiftDefs] = useState<ShiftDefinition[]>([]);
  const [schedule, setSchedule] = useState<string[]>([]);
  
  const [generating, setGenerating] = useState(false);
  const [uploading, setUploading] = useState(false);

  const [newDay, setNewDay] = useState("MON");
  const [newTime, setNewTime] = useState("2:30-7");

  // --- Fetch Data ---
  const fetchData = useCallback(async () => {
    try {
      const timestamp = Date.now();
      const [empRes, shiftRes, schedRes] = await Promise.all([
        fetch(`${API_URL}/employees?t=${timestamp}`),
        fetch(`${API_URL}/config/shifts?t=${timestamp}`),
        fetch(`${API_URL}/schedule?t=${timestamp}`)
      ]);

      const [empData, shiftData, schedData] = await Promise.all([
        empRes.json(),
        shiftRes.json(),
        schedRes.json()
      ]);

      setEmployees(empData);
      setShiftDefs(shiftData);
      if (schedData.roster) setSchedule(schedData.roster);
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  }, []);

  // --- WebSocket ---
  useEffect(() => {
    fetchData();
    
    // Auto-detect WebSocket protocol (ws:// or wss://)
    const wsUrl = API_URL.replace(/^http/, 'ws') + '/ws';
    console.log("🔌 Connecting to:", wsUrl);
    
    const ws = new WebSocket(wsUrl);
    
    ws.onmessage = (event) => {
      if (event.data === "roster_update" || event.data === "settings_update") {
        fetchData();
      }
    };

    return () => ws.close();
  }, [fetchData]);

  // --- Actions ---
  const handleFileUpload = async (file: File) => {
    setUploading(true);
    const formData = new FormData();
    formData.append("file", file);

    try {
      const res = await fetch(`${API_URL}/upload/roster`, {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      if (data.status === "success") {
        fetchData(); 
      } else {
        alert("Upload Error: " + data.message);
      }
    } catch (err) {
      console.error(err);
      alert("Upload failed.");
    } finally {
      setUploading(false);
    }
  };

  const generateSchedule = async () => {
    setGenerating(true);
    setSchedule([]);
    try {
      const response = await fetch(`${API_URL}/generate`, { method: 'POST' });
      const data = await response.json();
      if (data.roster) setSchedule(data.roster);
    } catch (error) {
      console.error(error);
    } finally {
      setGenerating(false);
    }
  };

  const addShiftDef = async () => {
    await fetch(`${API_URL}/config/shifts`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ day: newDay, time_slot: newTime })
    });
  };

  const deleteShiftDef = async (id: number) => {
    await fetch(`${API_URL}/config/shifts/${id}`, { method: 'DELETE' });
  };

  const downloadHomebaseCSV = () => {
    if (schedule.length === 0) return;
    let csvContent = "data:text/csv;charset=utf-8,Employee Name,Day,Start Time,End Time\n";
    schedule.forEach(row => {
      const [timePart, name] = row.split(": ");
      if (name === "UNFILLED") return;
      const [day, hours] = timePart.split(" ");
      const [start, end] = hours.split("-");
      csvContent += `${name},${day},${start},${end}\n`;
    });
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "homebase_import.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-[#0B1120] text-slate-300 font-sans selection:bg-blue-500/30">
      
      {/* NAVBAR */}
      <nav className="border-b border-slate-800 bg-[#0B1120]/80 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          
          {/* LOGO & BRANDING */}
          <div className="flex items-center gap-3">
            <div className="relative group cursor-pointer">
              <div className="absolute -inset-2 bg-blue-500/20 rounded-full blur-xl opacity-0 group-hover:opacity-100 transition duration-500"></div>
              <div className="relative w-10 h-10 bg-slate-900 rounded-xl flex items-center justify-center border border-slate-700/50 shadow-2xl">
                <Hourglass className="text-blue-400 w-5 h-5" />
              </div>
            </div>
            
            <div className="flex flex-col justify-center h-10">
              <span className="text-2xl font-black tracking-widest text-transparent bg-clip-text bg-linear-to-r from-white via-blue-100 to-blue-500 drop-shadow-sm font-sans">
                KAIROS
              </span>
              <span className="text-[10px] font-bold text-slate-500 uppercase tracking-[0.35em] ml-0.5">
                TIME, OPTIMIZED
              </span>
            </div>
          </div>
          
          {/* ACTION BUTTON */}
          <button 
            onClick={generateSchedule}
            disabled={generating}
            className={`flex items-center gap-2 px-6 py-2.5 rounded-full font-semibold transition-all shadow-lg ${
              generating 
                ? "bg-slate-800 text-slate-500 cursor-not-allowed border border-slate-700" 
                : "bg-linear-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white shadow-blue-600/20 hover:shadow-blue-600/40 active:scale-95 border border-transparent"
            }`}
          >
            {generating ? <Zap className="w-4 h-4 animate-pulse" /> : <Zap className="w-4 h-4 fill-current" />}
            {generating ? "Solving Constraints..." : "Generate Schedule"}
          </button>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* LEFT: CONFIGURATION */}
          <div className="lg:col-span-3 space-y-6">
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 shadow-xl">
              <div className="flex items-center gap-2 mb-4 text-slate-100">
                <Settings className="w-5 h-5 text-blue-400" />
                <h2 className="font-semibold">Shift Requirements</h2>
              </div>

              {/* Add New Shift */}
              <div className="bg-slate-800/50 p-3 rounded-xl border border-slate-700/50 mb-4">
                <div className="grid grid-cols-5 gap-2 mb-2">
                  <div className="col-span-2">
                    <select 
                      value={newDay} 
                      onChange={(e) => setNewDay(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-xs focus:ring-2 focus:ring-blue-500/50 outline-none transition-all"
                    >
                      {["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"].map(d => (
                        <option key={d} value={d}>{d}</option>
                      ))}
                    </select>
                  </div>
                  <div className="col-span-3">
                    <input 
                      type="text" 
                      value={newTime}
                      onChange={(e) => setNewTime(e.target.value)}
                      className="w-full bg-slate-900 border border-slate-700 rounded-lg px-2 py-1.5 text-xs focus:ring-2 focus:ring-blue-500/50 outline-none transition-all"
                    />
                  </div>
                </div>
                <button 
                  onClick={addShiftDef}
                  className="w-full flex items-center justify-center gap-2 bg-slate-700 hover:bg-slate-600 text-slate-200 text-xs font-medium py-2 rounded-lg transition-colors border border-slate-600"
                >
                  <Plus className="w-3 h-3" /> Add Slot
                </button>
              </div>

              {/* List */}
              <div className="space-y-1 max-h-[500px] overflow-y-auto pr-1 custom-scrollbar">
                {shiftDefs.map((def) => (
                  <div key={def.id} className="group flex justify-between items-center p-2 rounded-lg hover:bg-slate-800 transition-colors border border-transparent hover:border-slate-700/50">
                    <span className="text-xs font-mono">
                      <span className="font-bold text-blue-400 w-8 inline-block">{def.day}</span> 
                      <span className="text-slate-400">{def.time_slot}</span>
                    </span>
                    <button 
                      onClick={() => deleteShiftDef(def.id)}
                      className="text-slate-600 hover:text-red-400 opacity-0 group-hover:opacity-100 transition-all p-1"
                    >
                      <Trash2 className="w-3.5 h-3.5" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* CENTER: STAFF POOL */}
          <div className="lg:col-span-6 space-y-6">
            
            {/* Upload Area */}
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 shadow-xl">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2 text-slate-100">
                  <Users className="w-5 h-5 text-emerald-400" />
                  <h2 className="font-semibold">Staff Pool</h2>
                </div>
                <span className="text-xs font-medium bg-slate-800 text-slate-400 px-2.5 py-1 rounded-full border border-slate-700">
                  {employees.length} Active
                </span>
              </div>
              
              <FileDropzone onFileUpload={handleFileUpload} loading={uploading} />
            </div>

            {/* Employee Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {employees.map((emp) => (
                <div key={emp.id} className="bg-slate-900 p-4 rounded-xl border border-slate-800 hover:border-slate-600 transition-all group">
                  <div className="flex justify-between items-start mb-3">
                    <h3 className="font-bold text-slate-200">{emp.name}</h3>
                    {emp.preference_score > 0 && (
                      <span className="text-[10px] bg-slate-800 text-slate-500 px-2 py-0.5 rounded border border-slate-700">
                        Pref: {emp.preference_score}
                      </span>
                    )}
                  </div>
                  
                  <div className="flex flex-wrap gap-1.5">
                    {emp.availabilities.length > 0 ? emp.availabilities.map((avail, i) => (
                      <span key={i} className="px-2 py-1 rounded-md bg-blue-500/10 text-blue-400 text-[10px] font-mono border border-blue-500/20">
                        {avail.day} {avail.time_slot}
                      </span>
                    )) : (
                      <span className="text-xs text-slate-600 flex items-center gap-1">
                        <AlertCircle className="w-3 h-3" /> No availability
                      </span>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* RIGHT: ROSTER */}
          <div className="lg:col-span-3">
            <div className="bg-slate-900 rounded-2xl border border-slate-800 p-5 shadow-xl sticky top-24">
              <div className="flex items-center justify-between mb-6 text-slate-100">
                <div className="flex items-center gap-2">
                  <Calendar className="w-5 h-5 text-purple-400" />
                  <h2 className="font-semibold">Live Roster</h2>
                </div>
                {/* EXPORT BUTTON */}
                {schedule.length > 0 && (
                  <button 
                    onClick={downloadHomebaseCSV}
                    className="text-[10px] font-bold bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 px-3 py-1.5 rounded-md flex items-center gap-1.5 transition-colors"
                    title="Export CSV for Homebase"
                  >
                    <Download className="w-3 h-3" /> CSV
                  </button>
                )}
              </div>

              {schedule.length === 0 ? (
                <div className="text-center py-12 text-slate-600 border-2 border-dashed border-slate-800 rounded-xl">
                  <p className="text-sm">Ready to generate</p>
                </div>
              ) : (
                <div className="space-y-3 max-h-[calc(100vh-200px)] overflow-y-auto pr-2 custom-scrollbar">
                  {schedule.map((shift, idx) => {
                    const [time, name] = shift.split(": ");
                    const isUnfilled = name === "UNFILLED";
                    const [day, hours] = time.split(" ");
                    
                    return (
                      <div key={idx} className="flex items-stretch bg-slate-800/50 rounded-lg overflow-hidden border border-slate-700/50 hover:border-slate-600 transition-colors">
                        <div className="bg-slate-800 w-12 flex flex-col items-center justify-center border-r border-slate-700/50 px-1">
                          <span className="text-[10px] font-bold text-slate-400">{day}</span>
                        </div>
                        <div className="p-3 flex-1">
                          <div className="text-[10px] text-slate-500 font-mono mb-0.5">{hours}</div>
                          <div className={`font-medium text-sm ${isUnfilled ? 'text-red-400' : 'text-slate-200'}`}>
                            {name}
                          </div>
                        </div>
                      </div>
                    )
                  })}
                </div>
              )}
            </div>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;