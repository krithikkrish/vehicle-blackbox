// static/js/dashboard.js
// Live-polls /api/live every 1 second and updates all cards.
// Uses /api/history for the mini speed chart (Chart.js).

const POLL_MS = 1000;

// ── Speed Chart setup (Chart.js via CDN) ─────────────────────────────────────
let speedChart = null;
const MAX_CHART_POINTS = 60;  // last 60 ticks

function initChart() {
  const ctx = document.getElementById('speed-chart').getContext('2d');
  speedChart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: Array(MAX_CHART_POINTS).fill(''),
      datasets: [
        {
          label: 'Hall Speed (km/h)',
          data: Array(MAX_CHART_POINTS).fill(null),
          borderColor: '#00d4ff',
          backgroundColor: 'rgba(0,212,255,0.08)',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
          fill: true,
        },
        {
          label: 'GPS Speed (km/h)',
          data: Array(MAX_CHART_POINTS).fill(null),
          borderColor: '#7c3aed',
          backgroundColor: 'rgba(124,58,237,0.06)',
          borderWidth: 2,
          pointRadius: 0,
          tension: 0.3,
          fill: false,
        },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      animation: { duration: 0 },
      plugins: { legend: { labels: { color: '#64748b', font: { size: 11 } } } },
      scales: {
        x: { display: false },
        y: {
          min: 0,
          grid:  { color: '#2a2d38' },
          ticks: { color: '#64748b', font: { size: 11 } },
        },
      },
    },
  });
}

function pushChartPoint(hallSpeed, gpsSpeed) {
  speedChart.data.datasets[0].data.push(hallSpeed);
  speedChart.data.datasets[0].data.shift();
  speedChart.data.datasets[1].data.push(gpsSpeed);
  speedChart.data.datasets[1].data.shift();
  speedChart.update();
}

// ── DOM helpers ───────────────────────────────────────────────────────────────
function el(id) { return document.getElementById(id); }

function setStatus(cls, text) {
  const banner = el('status-banner');
  banner.className = cls;
  banner.textContent = text;
}

function setCard(id, value, unit, statusClass, statusText) {
  const card = el(id);
  if (!card) return;
  card.querySelector('.card-value').textContent = value;
  if (unit !== undefined)      card.querySelector('.card-unit').textContent = unit;
  if (statusClass !== undefined) {
    card.className = `card ${statusClass === 'status-alert' ? 'alert' : statusClass === 'status-warn' ? 'warn' : 'ok'}`;
    card.querySelector('.card-status').className = `card-status ${statusClass}`;
    card.querySelector('.card-status').textContent = statusText;
  }
}

// ── Fetch & update ────────────────────────────────────────────────────────────
async function fetchAndUpdate() {
  try {
    const res  = await fetch('/api/live');
    const data = await res.json();

    // ── Status banner ──────────────────────────────────────────────────────
    switch (data.system_status) {
      case 'CRASH':
        setStatus('crash', '🚨  CRASH DETECTED — Emergency SMS Sent');
        break;
      case 'ALCOHOL_ALERT':
        setStatus('alcohol', '⚠️  ALCOHOL DETECTED — Driver Alert Active');
        break;
      case 'NORMAL':
        setStatus('normal', '✅  SYSTEM NORMAL — All sensors active');
        break;
      default:
        setStatus('starting', '⏳  SYSTEM STARTING …');
    }

    // ── GPS Card ───────────────────────────────────────────────────────────
    const gpsFix = data.gps_fix;
    const lat    = data.gps_lat  ? data.gps_lat.toFixed(5)  : '---';
    const lon    = data.gps_lon  ? data.gps_lon.toFixed(5)  : '---';
    el('gps-lat').textContent  = lat;
    el('gps-lon').textContent  = lon;
    el('gps-fix-badge').className   = `card-status ${gpsFix ? 'status-ok' : 'status-nofix'}`;
    el('gps-fix-badge').textContent = gpsFix ? 'FIX ACTIVE' : 'NO FIX';
    el('card-gps').className        = `card ${gpsFix ? 'ok' : ''}`;

    // Update map iframe + link
    if (gpsFix && data.gps_lat && data.gps_lon) {
      const mapsUrl = `https://maps.google.com/?q=${data.gps_lat},${data.gps_lon}`;
      el('gps-link').href = mapsUrl;
      el('map-iframe').src =
        `https://www.openstreetmap.org/export/embed.html?bbox=` +
        `${data.gps_lon - 0.005},${data.gps_lat - 0.005},` +
        `${data.gps_lon + 0.005},${data.gps_lat + 0.005}` +
        `&layer=mapnik&marker=${data.gps_lat},${data.gps_lon}`;
    }

    // ── Hall Effect Speed ──────────────────────────────────────────────────
    const hall = data.hall_speed_kmh ?? 0;
    setCard('card-hall', hall.toFixed(1), 'km/h',
            hall > 80 ? 'status-warn' : 'status-ok',
            hall > 80 ? 'OVERSPEED' : 'NORMAL');

    // ── GPS Speed ──────────────────────────────────────────────────────────
    const gpsSpd = data.gps_speed_kmh ?? 0;
    setCard('card-gps-speed', gpsSpd.toFixed(1), 'km/h',
            'status-ok', gpsFix ? 'GPS SPEED' : 'NO FIX');

    // ── Alcohol ────────────────────────────────────────────────────────────
    const alc   = data.alcohol_voltage ?? 0;
    const alert = data.alcohol_alert;
    setCard('card-alcohol', alc.toFixed(3), 'V',
            alert ? 'status-alert' : 'status-ok',
            alert ? 'ALERT' : 'NORMAL');

    // ── Vibration ─────────────────────────────────────────────────────────
    const vib = data.vibration;
    setCard('card-vib', vib ? 'YES' : 'NO', '',
            vib ? 'status-alert' : 'status-ok',
            vib ? 'IMPACT' : 'STABLE');

    // ── Timestamp ─────────────────────────────────────────────────────────
    if (data.timestamp) {
      el('last-updated').textContent = new Date(data.timestamp).toLocaleTimeString();
    }

    // ── Chart ──────────────────────────────────────────────────────────────
    pushChartPoint(hall, gpsSpd);

  } catch (err) {
    setStatus('starting', '⚠️  Connection lost — retrying …');
  }
}

// ── Init ───────────────────────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  initChart();
  fetchAndUpdate();
  setInterval(fetchAndUpdate, POLL_MS);
});
