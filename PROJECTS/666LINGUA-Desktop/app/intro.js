'use strict';

// Vor dem ersten Zeichnen aktivieren. Fällt das Skript aus, bleibt die App sichtbar.
document.documentElement.dataset.starting = '';
document.addEventListener('DOMContentLoaded', () => {
  const intro = document.getElementById('startup-intro');
  const status = document.getElementById('startup-status');
  const progress = document.getElementById('startup-progress');
  const skip = document.getElementById('startup-skip');
  const started = performance.now();
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  const close = () => {
    if (intro.hidden) return;
    clearTimeout(timeout);
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
  const timeout = setTimeout(close, 8000);
  skip.addEventListener('click', close);
  document.addEventListener('keydown', onKey);
  const label = (key) => typeof t === 'function' ? t(key) : key;
  const tasks = [
    Promise.allSettled(Array.from(intro.querySelectorAll('img'), image => image.decode())),
    typeof startupInfo !== 'undefined' ? startupInfo : false,
    typeof startupSettings !== 'undefined' ? startupSettings : false
  ];
  let completed = 0;
  for (const [index, task] of tasks.entries()) {
    tasks[index] = Promise.resolve(task).finally(() => {
      if (intro.hidden) return;
      completed++;
      progress.value = 15 + completed * 25;
      status.textContent = label('Oberfläche lädt …');
    });
  }
  progress.value = 15;
  status.textContent = label('666LINGUA startet …');
  Promise.allSettled(tasks).then(([, info, settings]) => {
    if (intro.hidden) return;
    if (info.value === true && settings.value === true) {
      progress.value = 100;
      status.textContent = label('Bereit');
    }
    const minimum = reducedMotion ? 350 : 1000;
    setTimeout(close, Math.max(0, minimum - (performance.now() - started)));
  });
}, {once:true});
