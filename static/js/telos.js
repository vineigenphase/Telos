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
