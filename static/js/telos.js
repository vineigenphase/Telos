/* Telos — frontend utilities */

// ── Question mark rows ──────────────────────────────────────────────────────

let qRowCount = 0;

function addQRow(num, obtained, maxm, topic, topics) {
  qRowCount++;
  const idx = num || qRowCount;
  const container = document.getElementById('q-rows');

  const row = document.createElement('div');
  row.className = 'q-row';
  row.dataset.row = qRowCount;

  const topicOpts = (topics || [])
    .map(t => `<option value="${t}" ${t === topic ? 'selected' : ''}>${t}</option>`)
    .join('');

  row.innerHTML = `
    <input class="form-control" name="q_num[]"
           value="${idx}" placeholder="Q#" style="text-align:center;">
    <input class="form-control q-obtained" name="q_obtained[]" type="number"
           value="${obtained || ''}" placeholder="Got" step="0.5" min="0"
           oninput="recalcTotal()">
    <span class="q-sep" style="color:var(--muted); text-align:center;">/</span>
    <input class="form-control" name="q_max[]" type="number"
           value="${maxm || ''}" placeholder="Max" step="0.5" min="0"
           oninput="recalcTotal()">
    <select class="form-control q-topic" name="q_topic[]">
      <option value="">Topic…</option>
      ${topicOpts}
    </select>
    <button type="button" class="btn btn-danger btn-sm"
            onclick="removeQRow(this)" title="Remove">×</button>
  `;
  container.appendChild(row);
  recalcTotal();
}

function removeQRow(btn) {
  btn.closest('.q-row').remove();
  renumberRows();
  recalcTotal();
}

function renumberRows() {
  document.querySelectorAll('.q-row').forEach((row, i) => {
    const numInput = row.querySelector('input[name="q_num[]"]');
    if (numInput && !isNaN(parseInt(numInput.value))) {
      numInput.value = i + 1;
    }
  });
  qRowCount = document.querySelectorAll('.q-row').length;
}

function recalcTotal() {
  let total = 0, maxTotal = 0, hasAny = false;
  document.querySelectorAll('.q-obtained').forEach(inp => {
    const v = parseFloat(inp.value);
    if (!isNaN(v)) { total += v; hasAny = true; }
  });
  document.querySelectorAll('input[name="q_max[]"]').forEach(inp => {
    const v = parseFloat(inp.value);
    if (!isNaN(v)) maxTotal += v;
  });

  const scoreDisplay = document.getElementById('calc-score');
  const pctDisplay   = document.getElementById('calc-pct');
  const gradeDisplay = document.getElementById('calc-grade');

  if (scoreDisplay) scoreDisplay.textContent = hasAny ? total.toFixed(1) : '—';
  if (pctDisplay) {
    const pct = maxTotal > 0 ? (total / maxTotal * 100) : null;
    pctDisplay.textContent = pct !== null ? pct.toFixed(1) + '%' : '';
  }
  if (gradeDisplay && maxTotal > 0 && hasAny) {
    const pct = total / maxTotal * 100;
    const { label, color } = pctToGrade(pct);
    gradeDisplay.textContent = label;
    gradeDisplay.style.background = color + '22';
    gradeDisplay.style.color = color;
    gradeDisplay.style.border = `1px solid ${color}44`;
  }

  // Also sync hidden total input if present
  const hidden = document.getElementById('score_direct');
  if (hidden && hasAny) hidden.value = total.toFixed(1);
}

function pctToGrade(pct) {
  if (pct >= 90) return { label: 'A*', color: '#f59e0b' };
  if (pct >= 80) return { label: 'A',  color: '#22c55e' };
  if (pct >= 70) return { label: 'B',  color: '#3b82f6' };
  if (pct >= 60) return { label: 'C',  color: '#a78bfa' };
  if (pct >= 50) return { label: 'D',  color: '#f97316' };
  return { label: 'E', color: '#ef4444' };
}

// ── Template-aware add form ─────────────────────────────────────────────────

function onBoardChange() {
  updateTopics();
}

function onSubjectChange() {
  updateTopics();
}

function onCodeChange() {
  const board   = document.getElementById('board')?.value;
  const subject = document.getElementById('subject')?.value;
  const code    = document.getElementById('paper_code')?.value;
  if (!board || !subject || !code) return;

  fetch(`/api/template-info?board=${encodeURIComponent(board)}&subject=${encodeURIComponent(subject)}&code=${encodeURIComponent(code)}`)
    .then(r => r.json())
    .then(data => {
      if (data.info) {
        const mx = document.getElementById('max_marks');
        if (mx && !mx.dataset.userEdited) mx.value = data.info.max_marks;
      }
      window._currentTopics = data.topics || [];
      // Re-render any existing topic selects
      document.querySelectorAll('.q-topic').forEach(sel => {
        const cur = sel.value;
        sel.innerHTML = '<option value="">Topic…</option>' +
          (data.topics || []).map(t =>
            `<option value="${t}" ${t === cur ? 'selected' : ''}>${t}</option>`
          ).join('');
      });
    });
}

function updateTopics() {
  window._currentTopics = [];
  onCodeChange();
}

// ── Mobile "More" sheet ─────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  const tab      = document.getElementById('more-tab');
  const sheet    = document.getElementById('more-sheet');
  const backdrop = document.getElementById('sheet-backdrop');
  if (!tab || !sheet || !backdrop) return;

  const isOpen = () => sheet.classList.contains('open');

  function open() {
    sheet.hidden = false; backdrop.hidden = false;
    requestAnimationFrame(() => { sheet.classList.add('open'); backdrop.classList.add('open'); });
    tab.setAttribute('aria-expanded', 'true');
  }

  function close() {
    sheet.classList.remove('open'); backdrop.classList.remove('open');
    tab.setAttribute('aria-expanded', 'false');
    setTimeout(() => { sheet.hidden = true; backdrop.hidden = true; }, 220);
  }

  tab.addEventListener('click', () => isOpen() ? close() : open());
  backdrop.addEventListener('click', close);
  document.addEventListener('keydown', e => { if (e.key === 'Escape' && isOpen()) close(); });
});

// ── Tap-to-reveal tooltips ──────────────────────────────────────────────────
// Touch has no hover, so anything that only appeared on :hover was invisible
// on a phone. On touch devices a tap reveals it instead.

document.addEventListener('click', e => {
  if (!window.matchMedia('(hover: none)').matches) return;
  const el = e.target.closest('[data-tip]');
  document.querySelectorAll('[data-tip].tip-open').forEach(t => {
    if (t !== el) t.classList.remove('tip-open');
  });
  if (el) el.classList.add('tip-open');
});

// ── Flash auto-dismiss ──────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    document.querySelectorAll('.flash').forEach(el => {
      el.style.transition = 'opacity 0.4s';
      el.style.opacity = '0';
      setTimeout(() => el.remove(), 400);
    });
  }, 4000);
});

// ── PWA: service worker + update toast ──────────────────────────────────────
// See TELOS_V2_ADDENDUM.md Phase 2.5b. The service worker self-activates
// (skipWaiting/clients.claim) so a deploy always reaches an already-open tab
// within one refresh, but we never reload out from under the student —
// 'controllerchange' just surfaces a toast they can tap when ready.

if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {});
  });

  let refreshing = false;
  navigator.serviceWorker.addEventListener('controllerchange', () => {
    if (refreshing) return;
    const toast = document.getElementById('pwa-update-toast');
    const btn = document.getElementById('pwa-update-btn');
    if (!toast || !btn) return;
    toast.hidden = false;
    btn.addEventListener('click', () => {
      refreshing = true;
      location.reload();
    }, { once: true });
  });
}

// ── PWA: install prompt ──────────────────────────────────────────────────────
// Rules from Phase 2.5c: never on desktop, never on the first session, at
// most once per 14 days, dismissible and remembered. Good trigger: right
// after the third paper, once they've seen the value.
(function () {
  const FIRST_SEEN_KEY = 'telos_pwa_first_seen';
  const DISMISS_KEY = 'telos_pwa_dismissed_at';
  const DAY = 24 * 60 * 60 * 1000;

  function isStandalone() {
    return window.matchMedia('(display-mode: standalone)').matches
      || window.navigator.standalone === true;
  }
  function isMobile() {
    return window.matchMedia('(pointer: coarse)').matches;
  }
  function isIOS() {
    return /iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream;
  }
  function isSafari() {
    return /^((?!chrome|android|crios|fxios).)*safari/i.test(navigator.userAgent);
  }

  function eligible() {
    if (isStandalone() || !isMobile()) return false;
    if ((Number(document.body.dataset.papersCount) || 0) < 3) return false;

    const firstSeen = localStorage.getItem(FIRST_SEEN_KEY);
    if (!firstSeen) {
      localStorage.setItem(FIRST_SEEN_KEY, String(Date.now()));
      return false;                        // never on the first session
    }
    if (Date.now() - Number(firstSeen) < DAY) return false;

    const dismissed = localStorage.getItem(DISMISS_KEY);
    if (dismissed && Date.now() - Number(dismissed) < 14 * DAY) return false;

    return true;
  }

  let deferredPrompt = null;
  window.addEventListener('beforeinstallprompt', e => {
    e.preventDefault();
    deferredPrompt = e;
    showBanner();
  });

  function dismiss(banner) {
    banner.hidden = true;
    localStorage.setItem(DISMISS_KEY, String(Date.now()));
  }

  function showBanner() {
    if (!eligible()) return;
    const banner = document.getElementById('pwa-install-banner');
    const sub = document.getElementById('pwa-banner-sub');
    const btn = document.getElementById('pwa-install-btn');
    const closeBtn = document.getElementById('pwa-install-dismiss');
    if (!banner || !sub || !btn) return;

    if (isIOS() && isSafari()) {
      sub.textContent = 'Tap Share, then "Add to Home Screen"';
      btn.textContent = 'Show me';
      btn.addEventListener('click', () => {
        document.getElementById('pwa-ios-help').hidden = false;
      }, { once: true });
    } else if (deferredPrompt) {
      sub.textContent = 'Quick access, works offline.';
      btn.textContent = 'Add';
      btn.addEventListener('click', () => {
        banner.hidden = true;
        deferredPrompt.prompt();
        deferredPrompt = null;
      }, { once: true });
    } else {
      return;                              // Android before the browser event fires
    }

    banner.hidden = false;
    closeBtn?.addEventListener('click', () => dismiss(banner), { once: true });
  }

  document.addEventListener('DOMContentLoaded', () => {
    // iOS Safari never fires beforeinstallprompt, so it's checked directly.
    if (isIOS() && isSafari()) showBanner();
  });
})();
