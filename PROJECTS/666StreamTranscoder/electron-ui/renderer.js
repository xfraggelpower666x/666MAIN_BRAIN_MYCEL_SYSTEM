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
