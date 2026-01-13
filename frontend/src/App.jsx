import React, { useEffect, useRef, useState } from 'react';
import Header from './components/Header';
import StatusBar from './components/StatusBar';
import TrafficGrid from './components/TrafficGrid';
import Sidebar from './components/Sidebar';
import MiniMap from './components/MiniMap';
import PlaybackBar from './components/PlaybackBar';
import CentralSignalHUD from './components/CentralSignalHUD';

export default function App() {
  const [data, setData] = useState({
    feeds: {},
    counts: { north: 0, east: 0, south: 0, west: 0, rain_trigger: 0 },
    logic: {
      active_dir: 'north',
      state: 'RED',
      mode: 'AUTO',
      signal_map: { north: 'RED', east: 'RED', south: 'RED', west: 'RED' },
    },
    analytics: { car: 0, bike: 0, bus: 0, truck: 0 },
    env: { is_night: false, weather_mode: 'CLEAR' },
  });

  const [connected, setConnected] = useState(false);
  const [violations, setViolations] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [voiceEnabled, setVoiceEnabled] = useState(true);
  const [simulateMode, setSimulateMode] = useState(false);
  const [layoutMode, setLayoutMode] = useState('GRID');

  // --- MEMORY LEAK FIX: LIMIT HISTORY ---
  const [history, setHistory] = useState([]);
  const [isPlayback, setIsPlayback] = useState(false);
  const [playbackIndex, setPlaybackIndex] = useState(0);
  const MAX_HISTORY = 40; // Kept low to prevent browser crash

  const addToHistory = snapshot => {
    setHistory(prev => {
      // Don't store full images in history to save RAM
      const leanSnapshot = { ...snapshot, feeds: {} }; 
      const next = [...prev, { timestamp: Date.now(), snapshot: leanSnapshot }];
      return next.length > MAX_HISTORY ? next.slice(-MAX_HISTORY) : next;
    });
  };

  const currentView = isPlayback && history[playbackIndex] ? history[playbackIndex].snapshot : data;
  const wsRef = useRef(null);

  useEffect(() => {
    let ws = null;
    if (!simulateMode) {
      ws = new WebSocket('ws://localhost:5500');
      wsRef.current = ws;

      ws.onopen = () => setConnected(true);
      ws.onclose = () => setConnected(false);
      ws.onmessage = ev => {
        try {
          const parsed = JSON.parse(ev.data);
          setData(prev => {
            const merged = { ...prev, ...parsed };
            if (!isPlayback) addToHistory(merged);
            return merged;
          });
          if (parsed.violation) setViolations(p => [parsed.violation, ...p].slice(0, 10));
        } catch (e) {}
      };
    }
    return () => { if (ws) ws.close(); };
  }, [simulateMode, isPlayback]);

  // --- RELAY CONTROL FUNCTION ---
  const sendCommand = cmd => {
    if (!simulateMode && wsRef.current?.readyState === WebSocket.OPEN) {
      console.log("Sending Relay Command:", cmd);
      wsRef.current.send(JSON.stringify({ command: cmd }));
    }
  };

  const { is_night, weather_mode } = currentView.env;
  const bgClass = is_night ? 'bg-slate-950 text-slate-200' : 'bg-slate-900 text-slate-100';

  return (
    <div className={`min-h-screen ${bgClass} p-4 flex flex-col md:flex-row gap-6`}>
      <div className='flex-1 flex flex-col gap-4'>
        <Header connected={connected} simulateMode={simulateMode} isEmergency={currentView.logic.state === 'EMERGENCY'} isManual={currentView.logic.mode === 'MANUAL'} isNight={is_night} weatherMode={weather_mode} />
        <StatusBar logic={currentView.logic} env={currentView.env} />
        
        <div className='relative flex-1'>
          <TrafficGrid feeds={currentView.feeds} counts={currentView.counts} logic={currentView.logic} env={currentView.env} layoutMode={layoutMode} />
          <CentralSignalHUD logic={currentView.logic} />
        </div>

        <PlaybackBar history={history} isPlayback={isPlayback} playbackIndex={playbackIndex} onTogglePlayback={() => setIsPlayback(!isPlayback)} onSeek={setPlaybackIndex} />
        <MiniMap logic={currentView.logic} counts={currentView.counts} />
      </div>

      <Sidebar analytics={currentView.analytics} violations={violations} alerts={alerts} sendCommand={sendCommand} voiceEnabled={voiceEnabled} setVoiceEnabled={setVoiceEnabled} simulateMode={simulateMode} setSimulateMode={setSimulateMode} history={history} layoutMode={layoutMode} setLayoutMode={setLayoutMode} />
    </div>
  );
}