'use strict';

// Vor dem ersten Zeichnen aktivieren. Fällt das Skript aus, bleibt die App sichtbar.
document.documentElement.dataset.starting = '';
document.addEventListener('DOMContentLoaded', () => {
  const intro = document.getElementById('startup-intro');
  const status = document.getElementById('startup-status');
  const progress = document.getElementById('startup-progress');
  const skip = document.getElementById('startup-skip');
  const bootDuration = 7000;
  const readyHold = 2500;
  const stages = [
    {at: 0, text: '666LINGUA BOOTING', progress: 12},
    {at: 1750, text: 'GERMAN INJECTED', progress: 34},
    {at: 3500, text: 'AMERICA INJECTED', progress: 57},
    {at: 5250, text: 'SEMANTIC BOOST', progress: 82}
  ];
  const timers = [];
  let bootFinished = false;
  let startupReady;

  const later = (task, delay) => timers.push(window.setTimeout(task, delay));
  const show = (text, value) => {
    status.textContent = text;
    progress.value = value;
  };
  const close = () => {
    if (intro.hidden) return;
    for (const timer of timers) clearTimeout(timer);
    delete document.documentElement.dataset.starting;
    intro.hidden = true;
    document.removeEventListener('keydown', onKey);
    if (document.activeElement === skip || document.activeElement === document.body) {
      document.getElementById('source').focus({preventScroll: true});
    }
  };
  const onKey = (event) => {
    if (event.key === 'Escape') {
      event.preventDefault();
      close();
    }
  };
  const finishWhenReady = () => {
    if (intro.hidden || !bootFinished || startupReady === undefined) return;
    clearTimeout(deadline);
    if (startupReady) {
      show('666LINGUA READY', 100);
    } else {
      status.textContent = typeof t === 'function' ? t('Startprüfung unvollständig.') : 'Startup check incomplete.';
    }
    later(close, readyHold);
  };

  const deadline = window.setTimeout(close, 15000);
  timers.push(deadline);
  skip.addEventListener('click', close);
  document.addEventListener('keydown', onKey);
  show(stages[0].text, stages[0].progress);
  for (const stage of stages.slice(1)) later(() => show(stage.text, stage.progress), stage.at);
  later(() => {
    bootFinished = true;
    finishWhenReady();
  }, bootDuration);

  const tasks = [
    typeof startupInfo !== 'undefined' ? startupInfo : false,
    typeof startupSettings !== 'undefined' ? startupSettings : false
  ];
  Promise.allSettled(tasks).then(results => {
    startupReady = results.every(result => result.status === 'fulfilled' && result.value === true);
    finishWhenReady();
  });
}, {once:true});
