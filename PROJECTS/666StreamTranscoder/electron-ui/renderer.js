'use strict';
// Layout navigation only; no sound, broadcast or settings actions.
for (const button of document.querySelectorAll('[data-view]')) {
  button.addEventListener('click', () => {
    for (const b of document.querySelectorAll('[data-view]')) {
      b.classList.toggle('active', b === button);
    }
    for (const view of document.querySelectorAll('.view')) {
      view.classList.toggle('current', view.id === button.dataset.view);
    }
  });
}


// Read-only status projection from the original Python GUI. No action channel.
const statusAPI = window.streamUi;
const stateBadge = document.querySelector('.pill');
const broadcastTitle = document.querySelector('.hero h2');
const broadcastInfo = document.querySelector('.hero p');
const inputValue = document.querySelector('.metrics .panel:nth-child(2) b');
const outputValue = document.querySelector('.metrics .panel:nth-child(3) b');
const inputMeter = document.querySelector('.metrics .panel:nth-child(2) .meter i');
const outputMeter = document.querySelector('.metrics .panel:nth-child(3) .meter i');
const componentLabels = document.querySelectorAll('.status-grid span b');
const inputNames = ['source','monitor','encoder','server','relay','error'];
const dbText = (x) => typeof x === 'number' ? x.toFixed(1) + ' dBFS' : '— dBFS';
function showOffline() {
  if (stateBadge) stateBadge.textContent = '● NICHT VERBUNDEN';
  if (broadcastTitle) broadcastTitle.textContent = 'OFF AIR';
  if (broadcastInfo) broadcastInfo.textContent = 'Keine aktuelle Engine-Telemetrie';
  if (inputValue) inputValue.textContent = '— dBFS';
  if (outputValue) outputValue.textContent = '— dBFS';
  if (inputMeter) inputMeter.style.width = '0%';
  if (outputMeter) outputMeter.style.width = '0%';
  componentLabels.forEach(n => { n.textContent = 'UNBEKANNT'; });
}
async function refreshReadOnlyStatus() {
  try {
    const snapshot = statusAPI && typeof statusAPI.getStatus === 'function'
      ? await statusAPI.getStatus() : null;
    if (!snapshot) return showOffline();
    if (stateBadge) stateBadge.textContent = '● ENGINE STATUS · ' + snapshot.status.toUpperCase();
    if (broadcastTitle) broadcastTitle.textContent = snapshot.on_air ? 'ON AIR' : 'OFF AIR';
    if (broadcastInfo) broadcastInfo.textContent = snapshot.on_air
      ? 'Status vom laufenden 3DX/Resin-3-Prozess' : 'Python-GUI verbunden, derzeit nicht live';
    if (inputValue) inputValue.textContent = dbText(snapshot.input_dbfs);
    if (outputValue) outputValue.textContent = dbText(snapshot.output_dbfs);
    const width = x => typeof x === 'number' ? Math.max(0,Math.min(100,((x+60)/60)*100)) + '%' : '0%';
    if (inputMeter) inputMeter.style.width = width(snapshot.input_dbfs);
    if (outputMeter) outputMeter.style.width = width(snapshot.output_dbfs);
    componentLabels.forEach((n,i) => { n.textContent = snapshot.components[inputNames[i]].toUpperCase(); });
  } catch (_) { showOffline(); }
}
showOffline();
refreshReadOnlyStatus();
setInterval(refreshReadOnlyStatus, 1500);
