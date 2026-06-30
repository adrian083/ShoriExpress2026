/**
 * Tutorial guiado (cliente / admin). Se muestra una vez; se puede reabrir con el botón ❓.
 */
(function () {
  function readConfig() {
    const el = document.getElementById('shori-tutorial-data');
    if (!el) return null;
    try {
      return JSON.parse(el.textContent);
    } catch (e) {
      console.warn('Tutorial: JSON inválido', e);
      return null;
    }
  }

  function buildModal() {
    if (document.getElementById('shoriTutorial')) return document.getElementById('shoriTutorial');

    const wrap = document.createElement('div');
    wrap.id = 'shoriTutorial';
    wrap.className = 'shori-tutorial';
    wrap.hidden = true;
    wrap.innerHTML =
      '<div class="shori-tutorial-backdrop" data-tutorial-close></div>' +
      '<div class="shori-tutorial-card" role="dialog" aria-modal="true" aria-labelledby="tutorialTitle">' +
      '<div class="shori-tutorial-header">' +
      '<span class="shori-tutorial-badge" id="tutorialBadge">Guía</span>' +
      '<button type="button" class="shori-tutorial-close" data-tutorial-close aria-label="Cerrar">×</button>' +
      '</div>' +
      '<div class="shori-tutorial-progress"><div class="shori-tutorial-progress-bar" id="tutorialProgress"></div></div>' +
      '<h3 class="shori-tutorial-title" id="tutorialTitle"></h3>' +
      '<p class="shori-tutorial-body" id="tutorialBody"></p>' +
      '<div class="shori-tutorial-actions">' +
      '<button type="button" class="se-btn se-btn-outline se-btn-sm" id="tutorialSkip">Omitir</button>' +
      '<div style="display:flex;gap:8px;">' +
      '<button type="button" class="se-btn se-btn-outline se-btn-sm" id="tutorialPrev">Anterior</button>' +
      '<button type="button" class="se-btn se-btn-primary se-btn-sm" id="tutorialNext">Siguiente</button>' +
      '</div></div></div>';
    document.body.appendChild(wrap);
    return wrap;
  }

  function createController(config) {
    const modal = buildModal();
    const titleEl = document.getElementById('tutorialTitle');
    const bodyEl = document.getElementById('tutorialBody');
    const progressEl = document.getElementById('tutorialProgress');
    const badgeEl = document.getElementById('tutorialBadge');
    const btnPrev = document.getElementById('tutorialPrev');
    const btnNext = document.getElementById('tutorialNext');
    const btnSkip = document.getElementById('tutorialSkip');
    let index = 0;

    function render() {
      const step = config.steps[index];
      if (!step) return;
      titleEl.textContent = step.title;
      bodyEl.textContent = step.body;
      badgeEl.textContent = (index + 1) + ' / ' + config.steps.length;
      progressEl.style.width = ((index + 1) / config.steps.length * 100) + '%';
      btnPrev.disabled = index === 0;
      btnNext.textContent = index === config.steps.length - 1 ? 'Finalizar' : 'Siguiente';
    }

    function close(markDone) {
      modal.hidden = true;
      document.body.style.overflow = '';
      if (markDone) {
        localStorage.setItem(config.storageKey, '1');
      }
    }

    function open() {
      index = 0;
      render();
      modal.hidden = false;
      document.body.style.overflow = 'hidden';
    }

    btnPrev.addEventListener('click', function () {
      if (index > 0) {
        index -= 1;
        render();
      }
    });

    btnNext.addEventListener('click', function () {
      if (index < config.steps.length - 1) {
        index += 1;
        render();
      } else {
        close(true);
      }
    });

    btnSkip.addEventListener('click', function () {
      close(true);
    });

    modal.querySelectorAll('[data-tutorial-close]').forEach(function (el) {
      el.addEventListener('click', function () {
        close(false);
      });
    });

    return { open: open, close: close };
  }

  function init() {
    const config = readConfig();
    if (!config || !config.steps || !config.steps.length) return;

    const controller = createController(config);
    window.ShoriTutorial = controller;

    document.querySelectorAll('[data-tutorial-open]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.preventDefault();
        controller.open();
      });
    });

    if (!localStorage.getItem(config.storageKey)) {
      setTimeout(function () {
        controller.open();
      }, 800);
    }
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
