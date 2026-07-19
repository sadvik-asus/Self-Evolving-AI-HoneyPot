document.addEventListener('DOMContentLoaded', () => {
    // --- MAP INITIALIZATION ---
    // Dark themed map tiles
    const map = L.map('map').setView([20, 0], 2);
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; OpenStreetMap contributors &copy; CARTO',
        subdomains: 'abcd',
        maxZoom: 20
    }).addTo(map);

    let currentMarkers = {};

    // --- TERMINAL LOGIC ---
    const termInput = document.getElementById('terminal-input');
    const termOutput = document.getElementById('terminal-output');

    termInput.addEventListener('keydown', async (e) => {
        if (e.key === 'Enter') {
            const command = termInput.value.trim();
            if (!command) return;

            // Echo command
            const cmdLine = document.createElement('div');
            cmdLine.className = 'terminal-line';
            cmdLine.innerHTML = `<span class="prompt">root@server:~#</span> ${command}`;
            termOutput.appendChild(cmdLine);
            termInput.value = '';

            // Loading state
            const loading = document.createElement('div');
            loading.className = 'terminal-line';
            loading.style.color = '#888';
            loading.innerText = '...';
            termOutput.appendChild(loading);
            termOutput.scrollTop = termOutput.scrollHeight;

            try {
                const res = await fetch('/api/terminal', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                const data = await res.json();
                
                loading.remove();

                const resLine = document.createElement('div');
                resLine.className = 'terminal-line';
                resLine.innerText = data.output;
                termOutput.appendChild(resLine);
                termOutput.scrollTop = termOutput.scrollHeight;
                
                // Immediately refresh dashboard to show this new interaction
                fetchDashboard();
            } catch (err) {
                loading.innerText = 'bash: internal error';
            }
        }
    });

    // --- DASHBOARD LOGIC ---
    const personaDisplay = document.getElementById('persona-display');
    const threatFeed = document.getElementById('threat-feed');
    let lastInteractionId = null;

    async function fetchDashboard() {
        try {
            const res = await fetch('/api/dashboard');
            const data = await res.json();

            // Update Persona
            personaDisplay.innerText = data.persona;

            // Update Map Markers
            data.connections.forEach(conn => {
                if (conn.latitude && conn.longitude && !currentMarkers[conn.id]) {
                    // Create a red glowing marker
                    const marker = L.circleMarker([conn.latitude, conn.longitude], {
                        color: '#ff007f',
                        fillColor: '#ff007f',
                        fillOpacity: 0.7,
                        radius: 8
                    }).addTo(map);
                    marker.bindPopup(`<b>IP:</b> ${conn.ip_address}<br><b>Loc:</b> ${conn.city || 'Unknown'}, ${conn.country || 'Unknown'}`);
                    currentMarkers[conn.id] = marker;
                }
            });

            // Update Threat Feed
            threatFeed.innerHTML = '';
            data.interactions.forEach(interaction => {
                const item = document.createElement('div');
                
                // High risk commands get a red danger border
                const isDanger = ['cat', 'ls', 'wget', 'curl', 'chmod', 'sudo'].some(cmd => interaction.command.startsWith(cmd));
                item.className = `feed-item ${isDanger ? 'danger' : ''}`;

                const time = new Date(interaction.timestamp).toLocaleTimeString();
                item.innerHTML = `
                    <div class="feed-time">${time} | IP: ${interaction.ip_address} (${interaction.country || 'Unknown'})</div>
                    <div class="feed-command">> ${interaction.command}</div>
                `;
                threatFeed.appendChild(item);
            });

        } catch (e) {
            console.error("Dashboard fetch error:", e);
        }
    }

    // --- EVOLUTION BUTTON ---
    document.getElementById('evolve-btn').addEventListener('click', async (e) => {
        const btn = e.target;
        const originalText = btn.innerText;
        btn.innerText = "Evolving Persona...";
        btn.disabled = true;

        try {
            await fetch('/api/evolve', { method: 'POST' });
            fetchDashboard(); // Refresh to show new persona
        } catch(err) {
            console.error(err);
        } finally {
            btn.innerText = originalText;
            btn.disabled = false;
        }
    });

    // Poll every 3 seconds
    setInterval(fetchDashboard, 3000);
    fetchDashboard();

    // Focus input to start
    termInput.focus();
});
