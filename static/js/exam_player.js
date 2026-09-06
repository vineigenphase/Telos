/* Exam Mode player — engine spec section 5.
 *
 * Ported from content/exam_papers/authoring/player_template.html, with the
 * standalone version's in-memory state replaced by calls to the attempt
 * routes. The screen flow is deliberately identical: instructions, one
 * question per screen, navigator drawer, review table, end-test confirmation,
 * automatic submit at zero.
 *
 * Two things this file does NOT do, and both are the point:
 *
 *   * It never sees an answer. The payload carries stems, diagrams and options
 *     and nothing else, because the route selects only those columns. There is
 *     no marking here to get wrong or to read out of the page source.
 *   * It does not own the clock. The countdown is cosmetic; `remaining_sec`
 *     comes from the server on load and every write revalidates against
 *     `ends_at`. Editing the countdown in a console buys nothing.
 */
(function () {
  "use strict";

  var PAYLOAD = JSON.parse(document.getElementById("exam-payload").textContent);
  var QS = PAYLOAD.questions;
  var N = QS.length;
  var ATTEMPT = PAYLOAD.attempt_id;

  var state = {
    cur: 0,
    remaining: PAYLOAD.remaining_sec,
    started: false,
    finished: false,
    lastSwitch: 0,
    pending: {}          // question_id -> seconds not yet sent
  };

  var $ = function (s) { return document.querySelector(s); };
  var screens = { intro: $("#intro"), exam: $("#exam"), review: $("#review") };

  function show(name) {
    Object.keys(screens).forEach(function (k) {
      screens[k].classList.toggle("hidden", k !== name);
    });
  }

  function mmss(s) {
    s = Math.max(0, s | 0);
    return String((s / 60) | 0).padStart(2, "0") + ":" + String(s % 60).padStart(2, "0");
  }

  /* ---------------------------------------------------------------- timer */

  function paintTimer() {
    var t = mmss(state.remaining);
    ["#timer", "#timer2"].forEach(function (sel) {
      var el = $(sel);
      if (!el) return;
      el.textContent = t;
      // Red at five minutes, as the real player does.
      el.classList.toggle("warn", state.remaining <= 300);
    });
  }

  function tick() {
    if (state.finished) return;
    state.remaining -= 1;
    paintTimer();
    if (state.remaining <= 0) {
      state.remaining = 0;
      autoSubmit();
    }
  }

  /* ------------------------------------------------------------- questions */

  function q() { return QS[state.cur]; }

  function renderQuestion() {
    var cq = q();
    $("#qcount").textContent = "Question " + (state.cur + 1) + " of " + N;
    $("#qnum").textContent = "Question " + cq.n;
    $("#flagState").textContent = cq.flagged ? "Flagged for review" : "";
    $("#stem").innerHTML = cq.stem_html || "";

    var d = $("#diagram");
    // The diagram is authored SVG from the paper file, not user input.
    d.innerHTML = cq.diagram_svg || "";
    d.classList.toggle("hidden", !cq.diagram_svg);

    var opts = $("#opts");
    opts.innerHTML = "";
    Object.keys(cq.options).sort().forEach(function (letter) {
      var li = document.createElement("li");
      li.className = "opt" + (cq.selected === letter ? " sel" : "");
      li.setAttribute("role", "radio");
      li.setAttribute("aria-checked", cq.selected === letter ? "true" : "false");
      li.tabIndex = 0;
      li.innerHTML = '<span class="key">' + letter + "</span><span class="val"></span>";
      li.querySelector(".val").innerHTML = cq.options[letter];
      li.addEventListener("click", function () { choose(letter); });
      li.addEventListener("keydown", function (e) {
        if (e.key === " " || e.key === "Enter") { e.preventDefault(); choose(letter); }
      });
      opts.appendChild(li);
    });

    $("#prevBtn").disabled = state.cur === 0;
    $("#nextBtn").disabled = state.cur === N - 1;
    $("#flagBtn").classList.toggle("on", !!cq.flagged);
    paintNav();
  }

  function goto(i) {
    if (i < 0 || i >= N || state.finished) return;
    flushTime();
    state.cur = i;
    state.lastSwitch = Date.now();
    renderQuestion();
  }

  function choose(letter) {
    var cq = q();
    // Clicking the chosen option again clears it. A student who wants to leave
    // a question blank should not have to guess how.
    cq.selected = cq.selected === letter ? null : letter;
    renderQuestion();
    save(cq);
  }

  function toggleFlag() {
    var cq = q();
    cq.flagged = !cq.flagged;
    renderQuestion();
    save(cq);
  }

  /* ----------------------------------------------------------------- saves */

  function save(cq) {
    if (state.finished) return;
    fetch("/exam/attempt/" + ATTEMPT + "/answer", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: cq.id, selected: cq.selected,
                             flagged: !!cq.flagged })
    }).then(function (r) {
      if (r.status === 409) { onExpired(); return null; }
      return r.json();
    }).then(function (d) {
      // The server's clock wins. If it says less time is left than we think,
      // take its number — the browser may have been asleep.
      if (d && typeof d.remaining_sec === "number" &&
          d.remaining_sec < state.remaining) {
        state.remaining = d.remaining_sec;
        paintTimer();
      }
    }).catch(function () { /* a dropped save retries on the next change */ });
  }

  /* Time is accumulated locally and posted in batches, per section 4, so a
     20-question paper costs a handful of writes rather than one per second. */
  function flushTime() {
    var cq = q();
    if (!state.started || !cq) return;
    var secs = Math.round((Date.now() - state.lastSwitch) / 1000);
    state.lastSwitch = Date.now();
    if (secs > 0) state.pending[cq.id] = (state.pending[cq.id] || 0) + secs;
  }

  function sendTime() {
    if (state.finished) return;
    flushTime();
    Object.keys(state.pending).forEach(function (qid) {
      var delta = state.pending[qid];
      if (!delta) return;
      delete state.pending[qid];
      fetch("/exam/attempt/" + ATTEMPT + "/time", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: Number(qid), delta_sec: delta })
      }).catch(function () {
        // Put it back so the next flush retries rather than losing the time.
        state.pending[qid] = (state.pending[qid] || 0) + delta;
      });
    });
  }

  /* ------------------------------------------------------------- navigator */

  function paintNav() {
    var g = $("#navgrid");
    g.innerHTML = "";
    QS.forEach(function (cq, i) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = cq.n;
      // .ans / .flg / .cur are the reference stylesheet's own class names.
      // Inventing parallel ones would mean restyling what already works.
      b.className = (cq.selected ? "ans " : "") +
                    (cq.flagged ? "flg " : "") +
                    (i === state.cur ? "cur" : "");
      b.addEventListener("click", function () {
        goto(i);
        $("#navdrawer").classList.add("hidden");
      });
      g.appendChild(b);
    });
  }

  /* ---------------------------------------------------------------- review */

  function paintReview(filter) {
    var un = QS.filter(function (c) { return !c.selected; }).length;
    var fl = QS.filter(function (c) { return c.flagged; }).length;
    $("#revSummary").textContent =
      (N - un) + " answered · " + un + " unanswered · " + fl + " flagged";

    var body = $("#revBody");
    body.innerHTML = "";
    QS.forEach(function (cq, i) {
      if (filter === "un" && cq.selected) return;
      if (filter === "fl" && !cq.flagged) return;
      var tr = document.createElement("tr");
      var status = cq.selected ? "Answered" : "Unanswered";
      if (cq.flagged) status += " · Flagged";
      tr.innerHTML = "<td>Question " + cq.n + "</td><td>" + status +
                     "</td><td>" + (cq.selected || "—") + "</td>";
      var td = document.createElement("td");
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = "Go to question";
      b.addEventListener("click", function () { goto(i); show("exam"); });
      td.appendChild(b);
      tr.appendChild(td);
      body.appendChild(tr);
    });
  }

  /* ---------------------------------------------------------------- ending */

  function onExpired() {
    if (state.finished) return;
    state.finished = true;
    $("#expiredModal").classList.remove("hidden");
  }

  function finish(auto) {
    if (state.finished) return;
    state.finished = true;
    sendTime();
    fetch("/exam/attempt/" + ATTEMPT + "/submit", { method: "POST" })
      .then(function (r) { return r.json(); })
      .then(function () {
        if (auto) { $("#expiredModal").classList.remove("hidden"); }
        else { window.location = "/exam/attempt/" + ATTEMPT + "/results"; }
      })
      .catch(function () {
        // Even if the submit call fails, the attempt expires server-side on
        // next touch, so the results page is still the right destination.
        window.location = "/exam/attempt/" + ATTEMPT + "/results";
      });
  }

  function autoSubmit() { finish(true); }

  /* ------------------------------------------------------------------ wire */

  $("#startBtn").addEventListener("click", function () {
    state.started = true;
    state.lastSwitch = Date.now();
    show("exam");
    renderQuestion();
    paintTimer();
    setInterval(tick, 1000);
    setInterval(sendTime, 10000);
  });

  $("#prevBtn").addEventListener("click", function () { goto(state.cur - 1); });
  $("#nextBtn").addEventListener("click", function () { goto(state.cur + 1); });
  $("#flagBtn").addEventListener("click", toggleFlag);
  $("#navBtn").addEventListener("click", function () {
    $("#navdrawer").classList.toggle("hidden");
    paintNav();
  });
  $("#navClose").addEventListener("click", function () {
    $("#navdrawer").classList.add("hidden");
  });
  $("#reviewBtn").addEventListener("click", function () {
    flushTime(); paintReview("all"); show("review");
  });
  $("#revBack").addEventListener("click", function () {
    state.lastSwitch = Date.now(); show("exam");
  });

  document.querySelectorAll(".filters button").forEach(function (b) {
    b.addEventListener("click", function () {
      document.querySelectorAll(".filters button").forEach(function (o) {
        o.classList.remove("on");
      });
      b.classList.add("on");
      paintReview(b.dataset.f);
    });
  });

  $("#endBtn").addEventListener("click", function () {
    var un = QS.filter(function (c) { return !c.selected; }).length;
    $("#endModalBody").textContent = un
      ? un + " question" + (un === 1 ? " is" : "s are") + " unanswered. There is " +
        "no penalty for a wrong answer, so a guess is always worth more than a blank."
      : "Every question is answered.";
    $("#endModal").classList.remove("hidden");
  });
  $("#mCancel").addEventListener("click", function () {
    $("#endModal").classList.add("hidden");
  });
  $("#mEnd").addEventListener("click", function () {
    $("#endModal").classList.add("hidden");
    finish(false);
  });
  $("#mExpired").addEventListener("click", function () {
    window.location = "/exam/attempt/" + ATTEMPT + "/results";
  });

  /* Keyboard, per section 5. Ignored while a modal is open so Enter cannot
     both confirm a dialog and select an option. */
  document.addEventListener("keydown", function (e) {
    if (!state.started || state.finished) return;
    if (!$("#endModal").classList.contains("hidden")) return;
    if (screens.exam.classList.contains("hidden")) return;
    var k = e.key.toUpperCase();
    if (e.key === "ArrowRight") { goto(state.cur + 1); }
    else if (e.key === "ArrowLeft") { goto(state.cur - 1); }
    else if (k === "F") { toggleFlag(); }
    else if (/^[1-8]$/.test(k)) { pickIndex(parseInt(k, 10) - 1); }
    else if (/^[A-H]$/.test(k)) { if (q().options[k]) choose(k); }
  });

  function pickIndex(i) {
    var keys = Object.keys(q().options).sort();
    if (keys[i]) choose(keys[i]);
  }

  /* Light is the default because light is what the real test looks like. The
     choice is remembered per browser, which is a convenience and nothing more. */
  function applyTheme(dark) {
    // data-theme on the root, matching the reference stylesheet's
    // [data-theme="dark"] block rather than a second mechanism.
    document.documentElement.dataset.theme = dark ? "dark" : "";
    ["#themeBtn1", "#themeBtn2"].forEach(function (s) {
      var b = $(s);
      if (b) b.textContent = dark ? "Light player" : "Dark player";
    });
    try { localStorage.setItem("telos-exam-dark", dark ? "1" : "0"); } catch (e) {}
  }
  var startDark = false;
  try { startDark = localStorage.getItem("telos-exam-dark") === "1"; } catch (e) {}
  applyTheme(startDark);
  ["#themeBtn1", "#themeBtn2"].forEach(function (s) {
    var b = $(s);
    if (b) b.addEventListener("click", function () {
      applyTheme(document.documentElement.dataset.theme !== "dark");
    });
  });

  // Time already spent should not be lost to a closed tab.
  window.addEventListener("beforeunload", function () {
    if (state.started && !state.finished) sendTime();
  });

  $("#paperFmt").textContent =
    N + " multiple-choice questions in " +
    Math.round(PAYLOAD.paper.duration_sec / 60) + " minutes.";
  paintTimer();
})();
