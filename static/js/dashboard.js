// static/js/dashboard.js

const API = {
  status: '/api/status', // Unified Endpoint
  mode: '/set_mode',
  arduino: '/set_arduino',
  manual: '/manual_control',
};

function $(id) { return document.getElementById(id); }

function updateStatus() {
  fetch(API.status)
    .then(res => res.json())
    .then(data => {
      // 1. UPDATE TIMER & DIRECTION
      if ($('currentDirection')) $('currentDirection').innerText = data.current_direction.toUpperCase();
      
      // FIX: Ensure remaining_time is displayed
      if ($('remainingTime')) {
          $('remainingTime').innerText = data.remaining_time + " sec";
      }

      // 2. UPDATE COUNTS
      if ($('northCount')) $('northCount').innerText = data.counts.north || 0;
      if ($('southCount')) $('southCount').innerText = data.counts.south || 0;
      if ($('eastCount')) $('eastCount').innerText = data.counts.east || 0;
      if ($('westCount')) $('westCount').innerText = data.counts.west || 0;

      // 3. UPDATE BADGES (Green/Red indicators)
      const directions = ['north', 'south', 'east', 'west'];
      directions.forEach(dir => {
          const badge = document.getElementById(`badge-${dir}`);
          if (badge) {
              if (dir === data.current_direction) {
                  badge.className = "w-3 h-3 rounded-full bg-emerald-500 shadow-[0_0_8px_#10b981] animate-pulse";
              } else {
                  badge.className = "w-3 h-3 rounded-full bg-red-500 shadow-none";
              }
          }
      });
      
      // 4. Update Arduino Badge
      const ardBadge = $('arduinoStatusBadge');
      if (ardBadge) {
        ardBadge.innerText = data.arduino ? "ON" : "OFF";
        ardBadge.className = data.arduino 
            ? "text-[10px] bg-emerald-500 px-2 py-0.5 rounded text-white"
            : "text-[10px] bg-red-500 px-2 py-0.5 rounded text-white";
      }
    })
    .catch(err => console.log("API Error:", err));
}

function setMode(mode) {
    fetch(API.mode, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({mode})
    }).then(() => location.reload());
}

function setArduino(enabled) {
    fetch(API.arduino, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({enabled})
    }).then(() => updateStatus()); // Instant update
}

document.addEventListener('DOMContentLoaded', () => {
    updateStatus();
    setInterval(updateStatus, 1000); // 1-second refresh
});