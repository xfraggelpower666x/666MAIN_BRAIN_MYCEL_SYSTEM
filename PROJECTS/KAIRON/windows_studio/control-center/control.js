// Only predefined action IDs can reach the privileged Electron main process.
'use strict';
const status=document.getElementById('status');
document.getElementById('actions').addEventListener('click',async e=>{
  const button=e.target.closest('button[data-action]'); if(!button)return;
  const id=button.dataset.action;
  button.disabled=true;status.textContent=`Starte: ${id}`;
  try {await window.buildkit.action(id);status.textContent=`Aktion ${id} im Buildfenster gestartet.`;}
  catch(error){status.textContent=`Startfehler: ${error.message}`;}
  finally{button.disabled=false;}
});
document.getElementById('quit').addEventListener('click',()=>window.buildkit.quit());
