// app.js
const base = "";

// Fetch JSON helper
async function fetchJson(path){
  try {
    const res = await fetch(base + path);
    if (!res.ok) throw new Error("HTTP "+res.status);
    return await res.json();
  } catch(e) {
    console.error("fetch", path, e);
    return null;
  }
}

function setHtml(id, html){ document.getElementById(id).innerHTML = html; }

// Update dashboard content
async function refreshNow(){
  const app = await fetchJson("/api/app");
  const metrics = await fetchJson("/api/metrics");
  const alerts = await fetchJson("/api/alerts");
  const dt = await fetchJson("/api/dt_problems");
  const tickets = await fetchJson("/api/tickets");
  const release = await fetchJson("/api/release");

  // Health
  if (app && app.up === 1) {
    setHtml("health", '<span class="green">All OK</span>');
  } else {
    setHtml("health", '<span class="red">DOWN</span>');
  }

  // OPEN ALERTS column
  if (alerts) {
    setHtml("alerts",
      `<span class="badge red">S1 ${alerts.sev1}</span>` +
      `<span class="badge orange">S2 ${alerts.sev2}</span>` +
      `<span class="badge" style="background:#f1c40f">S3 ${alerts.sev3}</span>`
    );
  }

  // OPEN PROBLEMS column
  if (dt) {
    const t = dt.total;
    let html = `<div>Auto S1:${dt.auto.sev1} S2:${dt.auto.sev2} S3:${dt.auto.sev3}</div>` +
               `<div>Manual S1:${dt.manual.sev1.length} S2:${dt.manual.sev2.length} S3:${dt.manual.sev3.length}</div>` +
               `<div style="margin-top:6px"><strong>Total S1:${t.sev1} S2:${t.sev2} S3:${t.sev3}</strong></div>`;

    for (const sev of ["sev1", "sev2", "sev3"]) {
      if (dt.manual[sev] && dt.manual[sev].length > 0) {
        html += `<div style="margin-top:5px"><strong>${sev.toUpperCase()} Alerts:</strong><ul>`;
        dt.manual[sev].forEach(msg => {
          html += `<li>${msg}</li>`;
        });
        html += `</ul></div>`;
      }
    }
    setHtml("dt-problems", html);
  }

  // Tickets
  if (tickets) {
    setHtml("tickets", `Inc: ${tickets.open_incidents} / Changes: ${tickets.open_changes}`);
  }

  // Release
  if (release) {
    setHtml("release", `Deploys: ${release.deployments_last_24h} / DB: ${release.db_changes_last_24h}`);
  }

  // CPU/Disk tooltip
  if (metrics) {
    const m = `CPU: ${metrics.cpu_percent ?? 'N/A'}% , Disk: ${metrics.disk_percent ?? 'N/A'}%`;
    document.getElementById("health").title = m;
  }
}

// Timer function (runs continuously)
function startTimer(){
  function updateClock(){
    const now = new Date();
    const timeString = now.toLocaleTimeString();
    document.getElementById("timer").textContent = timeString;
  }
  updateClock();
  setInterval(updateClock, 1000);
}

// -------- Start --------
startTimer();        // start timer immediately
refreshNow();        // load first data
setInterval(refreshNow, 10000); // auto-refresh every 10 sec

