// static/js/dashboard.js
// Live-polls /api/live every 1 second and updates sensor cards, live GPS map, and pre-crash telemetry.
// Displays prominent Crash Alert Card upon SW-420 vibration impact.

const POLL_MS = 1000;

// ── DOM helpers ───────────────────────────────────────────────────────────────
function el(id) { return document.getElementById(id); }

function setStatus(cls, text) {
  const banner = el('status-banner');
  if (!banner) return;
  banner.className = cls;
  banner.textContent = text;
}

function setCard(id, value, unit, statusClass, statusText) {
  const card = el(id);
  if (!card) return;
  const valEl = card.querySelector('.card-value');
  if (valEl) valEl.textContent = value;
  if (unit !== undefined) {
    const unitEl = card.querySelector('.card-unit');
    if (unitEl) unitEl.textContent = unit;
  }
  if (statusClass !== undefined) {
    card.className = `card ${statusClass === 'status-alert' ? 'alert' : statusClass === 'status-warn' ? 'warn' : 'ok'}`;
    const badge = card.querySelector('.card-status');
    if (badge) {
      badge.className = `card-status ${statusClass}`;
      badge.textContent = statusText;
    }
  }
}

// ── Reset Crash Action ────────────────────────────────────────────────────────
async function resetCrash() {
  try {
    await fetch('/api/reset_crash', { method: 'POST' });
    const box = el('crash-alert-box');
    if (box) box.style.display = 'none';
    setStatus('normal', '✅  SYSTEM NORMAL — Crash alert acknowledged');
    fetchAndUpdate();
  } catch (err) {
    console.error('Reset crash error:', err);
  }
}

// ── Fetch & update loop ───────────────────────────────────────────────────────
async function fetchAndUpdate() {
  try {
    const res  = await fetch('/api/live');
    const data = await res.json();

    // ── Mode Badge ───────────────────────────────────────────────────────────
    const modeBadge = el('mode-badge');
    if (modeBadge) {
      modeBadge.textContent = 'GPS ONLY';
      modeBadge.className = 'mode-badge gps-only';
    }

    const isCrash = data.crash_detected || (data.system_status === 'CRASH');
    const isAlcohol = data.alcohol_alert || (data.system_status === 'ALCOHOL_ALERT');

    // ── Status banner ────────────────────────────────────────────────────────
    if (isCrash) {
      setStatus('crash', '🚨  CRASH DETECTED — EMERGENCY TELEMETRY DUMPED');
    } else if (isAlcohol) {
      setStatus('alcohol', '⚠️  ALCOHOL DETECTED — Driver Safety Alert Active');
    } else {
      setStatus('normal', '✅  SYSTEM NORMAL — GPS Blackbox Sensors Active');
    }

    // ── Crash Alert Box ──────────────────────────────────────────────────────
    const crashBox = el('crash-alert-box');
    if (crashBox) {
      if (isCrash) {
        crashBox.style.display = 'block';
        const info = data.last_crash || {};
        el('crash-trigger').textContent = info.trigger || 'SW-420 Vibration Impact';

        const lat = (info.gps_lat || data.gps_lat || 12.8406).toFixed(5);
        const lon = (info.gps_lon || data.gps_lon || 80.1534).toFixed(5);
        el('crash-location').textContent = `${lat}° N, ${lon}° E`;

        el('crash-time').textContent    = info.time || new Date().toLocaleTimeString();
        el('crash-speed').textContent   = `${(info.speed_kmh ?? 0).toFixed(1)} km/h`;
        el('crash-temp').textContent    = `${(info.temperature_c ?? data.temperature_c ?? 25.0).toFixed(1)} °C`;
        el('crash-alc').textContent     = `${(info.alcohol_voltage ?? data.alcohol_voltage ?? 0.0).toFixed(3)} V (${(info.alcohol_ppm ?? data.alcohol_ppm ?? 0).toFixed(1)} PPM)`;

        if (info.filename) {
          const link = el('crash-dump-link');
          link.textContent = `${info.filename} (Click to inspect log)`;
          link.href = `/logs/${info.filename}`;
        }

        // ── Render 10-second Pre-Crash Telemetry Table ───────────────
        const tbody = el('pre-crash-table-body');
        const history = info.history_10s || [];
        if (tbody && history.length > 0) {
          const badge = el('pre-crash-samples-badge');
          if (badge) badge.textContent = `${info.samples_count || history.length} Samples (Last 10s)`;

          // Render last 20 rows leading directly to impact
          const rowsToRender = history.slice(-20);
          tbody.innerHTML = rowsToRender.map((row, idx) => {
            const isImpact = row.vibration;
            const rowClass = isImpact ? 'class="crash-row-impact"' : '';
            const spd = Number(row.speed || 0).toFixed(1);
            const tmp = Number(row.temp || 25.0).toFixed(1);
            const alc = Number(row.alc_v || 0).toFixed(3);
            const tStr = row.time || `-${((rowsToRender.length - idx) * 0.1).toFixed(1)}s`;

            return `<tr ${rowClass}>
              <td>${tStr}</td>
              <td>${spd}</td>
              <td>${isImpact ? '💥 IMPACT DETECTED' : 'Normal'}</td>
              <td>${tmp} °C</td>
              <td>${alc} V</td>
            </tr>`;
          }).join('');
        }
      } else {
        crashBox.style.display = 'none';
      }
    }

    // ── GPS Card & Live Map ───────────────────────────────────────────────────
    const gpsFix = data.gps_fix;
    const lat    = data.gps_lat ? data.gps_lat.toFixed(5) : '12.84060';
    const lon    = data.gps_lon ? data.gps_lon.toFixed(5) : '80.15340';
    el('gps-lat').textContent = lat;
    el('gps-lon').textContent = lon;
    el('gps-fix-badge').className   = `card-status ${gpsFix ? 'status-ok' : 'status-nofix'}`;
    el('gps-fix-badge').textContent = gpsFix ? 'FIX ACTIVE' : 'ACQUIRING';
    el('card-gps').className        = `card ${gpsFix ? 'ok' : ''}`;

    // ── GPS Speed ────────────────────────────────────────────────────────────
    const gpsSpd = Number(data.gps_speed_kmh ?? 0);
    setCard('card-gps-speed', gpsSpd.toFixed(1), 'km/h',
            'status-ok', gpsFix ? 'GPS SPEED' : 'ACQUIRING');
    const meterGps = el('meter-gps-speed');
    if (meterGps) {
      const pctGps = Math.min(100, Math.max(0, (gpsSpd / 100) * 100));
      meterGps.style.width = `${pctGps.toFixed(1)}%`;
    }

    // ── OpenStreetMap update ─────────────────────────────────────────────────
    if (data.gps_lat && data.gps_lon) {
      const mapsUrl = `https://maps.google.com/?q=${data.gps_lat},${data.gps_lon}`;
      const link = el('gps-link');
      if (link) link.href = mapsUrl;
      const iframe = el('map-iframe');
      if (iframe && !iframe.dataset.loaded) {
        iframe.src =
          `https://www.openstreetmap.org/export/embed.html?bbox=` +
          `${data.gps_lon - 0.005},${data.gps_lat - 0.005},` +
          `${data.gps_lon + 0.005},${data.gps_lat + 0.005}` +
          `&layer=mapnik&marker=${data.gps_lat},${data.gps_lon}`;
        iframe.dataset.loaded = "true";
      }
    }

    // ── Wheel Speed & RPM (Hall Effect) ──────────────────────────────────────
    const hall = Number(data.hall_speed_kmh ?? 0);
    const rpm  = Number(data.hall_rpm ?? 0);
    const hallStatus = hall > 80 ? 'status-warn' : 'status-ok';
    const hallText   = hall > 80 ? 'OVERSPEED' : (rpm > 0 ? `${rpm} RPM` : 'STOPPED');

    setCard('card-hall', hall.toFixed(1), 'km/h (from Hall Effect RPM on GPIO 22)',
            hallStatus, hallText);

    const rpmEl = el('val-hall-rpm');
    if (rpmEl) rpmEl.textContent = rpm;

    const rpmBadge = el('val-hall-rpm-badge');
    if (rpmBadge) {
      if (rpm > 0) {
        rpmBadge.classList.add('spinning');
      } else {
        rpmBadge.classList.remove('spinning');
      }
    }

    const meterHall = el('meter-hall-speed');
    if (meterHall) {
      const pctHall = Math.min(100, Math.max(0, (hall / 100) * 100));
      meterHall.style.width = `${pctHall.toFixed(1)}%`;
    }

    // ── Alcohol Sensor (MQ-3 via ADS1115 A0) ──────────────────────────────────
    const alcV   = data.alcohol_voltage ?? 0;
    const alcPpm = data.alcohol_ppm ?? 0;
    setCard('card-alcohol', `${alcV.toFixed(3)} V`, `${alcPpm.toFixed(1)} PPM (ADS1115 A0)`,
            isAlcohol ? 'status-alert' : 'status-ok',
            isAlcohol ? 'ALCOHOL DETECTED' : 'NORMAL');

    // ── Vibration Sensor (SW-420 on GPIO 18) ─────────────────────────────────
    const vib = data.vibration || isCrash;
    setCard('card-vib', vib ? 'IMPACT' : 'STABLE', 'Impact sensor (GPIO 18)',
            vib ? 'status-alert' : 'status-ok',
            vib ? 'CRASH DETECTED' : 'STABLE');

    // ── Temperature (LM35 via ADS1115 A2) ────────────────────────────────────
    const tempC = Number(data.temperature_c ?? 26.4);
    setCard('card-temp', tempC.toFixed(1), '°C (ADS1115 A2)',
            tempC > 60 ? 'status-alert' : tempC > 45 ? 'status-warn' : 'status-ok',
            tempC > 60 ? 'OVERHEAT' : tempC > 45 ? 'HIGH TEMP' : 'NORMAL');
    const meterTemp = el('meter-temp');
    if (meterTemp) {
      const pctTemp = Math.min(100, Math.max(0, (tempC / 80) * 100));
      meterTemp.style.width = `${pctTemp.toFixed(1)}%`;
    }

    // ── Timestamp ────────────────────────────────────────────────────────────
    if (data.timestamp) {
      el('last-updated').textContent = new Date(data.timestamp).toLocaleTimeString();
    }

  } catch (err) {
    setStatus('starting', '⚠️  Waiting for blackbox sensor stream …');
  }
}

// ── Initialize on page load ──────────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  fetchAndUpdate();
  setInterval(fetchAndUpdate, POLL_MS);
});
