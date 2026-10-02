/* Exam Mode results — engine spec section 5, item 7.
 *
 * Ported from the reference player's results screen, with one change of
 * principle: nothing here computes a score.
 *
 * The reference is a standalone file, so it marks the paper in the browser.
 * Telos marks it at submit and stores the metrics, and this page reads them.
 * That matters because the scale anchors are editable by design — recomputing
 * on each view would let a student's recorded score move under them months
 * later, and a result is a record of a sitting rather than a live query. It
 * also means the answers only ever arrive for an attempt that is already
 * finished, which is what section 6 requires.
 */
(function () {
  "use strict";

  var root = document.getElementById("results");
  if (!root) return;
  var ATTEMPT = root.dataset.attempt;
  var $ = function (s) { return document.querySelector(s); };

  function fmt(sec) {
    sec = Math.max(0, Math.round(sec || 0));
    var m = Math.floor(sec / 60), s = sec % 60;
    return m + "m " + String(s).padStart(2, "0") + "s";
  }

  function esc(t) {
    var d = document.createElement("div");
    d.textContent = t == null ? "" : String(t);
    return d.innerHTML;
  }

  fetch("/exam/attempt/" + ATTEMPT + "/results.json")
    .then(function (r) {
      if (!r.ok) throw new Error("results unavailable (" + r.status + ")");
      return r.json();
    })
    .then(render)
    .catch(function (e) {
      var el = $("#loadError");
      el.textContent = "Could not load the full breakdown: " + e.message +
                       " Your score is recorded and this page can be reopened.";
      el.classList.remove("hidden");
    });

  function render(data) {
    var m = data.metrics || {};
    var qs = data.questions || [];
    var N = m.max || qs.length;

    renderEventResult(data.event);

    $("#scaled").textContent = (m.scaled != null) ? Number(m.scaled).toFixed(1) : "—";
    $("#raw").textContent = m.raw + " / " + N;
    $("#rawLbl").textContent = "raw marks" + (m.unanswered ? ", " + m.unanswered + " unanswered" : "");

    if (m.next_whole_grade) {
      var gap = m.marks_to_next;
      $("#toNext").textContent = gap + " mark" + (gap === 1 ? "" : "s");
      $("#toNextLbl").textContent = "to reach " + Number(m.next_whole_grade).toFixed(1) +
                                    " (needs " + m.raw_needed_for_next + "/" + N + ")";
    } else {
      $("#toNext").textContent = "—";
      $("#toNextLbl").textContent = "top of the scale";
    }

    // 7.0 is the number most candidates are actually aiming at, so it gets its
    // own figure rather than being buried in the ladder — EXCEPT when 7.0 is
    // also the next whole grade, where the tile beside it already says the
    // same thing. Showing "2 marks" twice in a row reads like a bug.
    var to7 = document.getElementById("to7").parentNode;
    if (m.next_whole_grade === 7.0) {
      to7.classList.add("hidden");
    } else if (m.marks_to_7 != null && m.marks_to_7 > 0) {
      $("#to7").textContent = m.marks_to_7 + " mark" + (m.marks_to_7 === 1 ? "" : "s");
    } else if (m.raw_needed_for_7 != null) {
      // Already at or past 7.0 — say so rather than showing a zero.
      $("#to7").textContent = "reached";
    } else {
      to7.classList.add("hidden");
    }

    $("#timeUsed").textContent =
      fmt(m.time_total_sec) + " of " + fmt(data.paper.duration_sec);

    /* ---- ladder ---- */
    var ladder = m.grade_ladder || [];
    var rungs = document.getElementById("rungs");
    rungs.innerHTML = "";
    ladder.forEach(function (rung, i) {
      var next = ladder[i + 1];
      // "here" is the rung the student is standing on: they have reached this
      // one and not the one above.
      var here = m.raw >= rung.raw && (!next || m.raw < next.raw);
      var isNext = m.next_whole_grade && rung.score === m.next_whole_grade;
      var d = document.createElement("div");
      d.className = "rung" + (here ? " here" : (isNext ? " next" : ""));
      d.innerHTML = "<b>" + rung.score.toFixed(1) + "</b><span>" +
                    rung.raw + "/" + N + "</span>";
      rungs.appendChild(d);
    });

    /* ---- by topic ---- */
    var bt = document.getElementById("bytopic");
    bt.innerHTML = "";
    (m.by_topic || []).forEach(function (t) {
      var d = document.createElement("div");
      d.innerHTML = "<span>" + esc(t.topic) + "</span><b>" + t.correct + "/" + t.total + "</b>";
      bt.appendChild(d);
    });

    /* ---- every question ---- */
    var perQ = {};
    (m.per_question || []).forEach(function (r) { perQ[r.question_id] = r; });

    var list = document.getElementById("qlist");
    list.innerHTML = "";
    qs.forEach(function (q) {
      var r = perQ[q.id] || {};
      var cls = r.state === "unanswered" ? "skip" : (r.state === "correct" ? "ok" : "no");
      var tag = r.state === "unanswered" ? "No answer"
              : (r.state === "correct" ? "Correct" : "Wrong");

      var det = document.createElement("details");
      det.className = "qrow";

      var sum = document.createElement("summary");
      sum.innerHTML =
        '<span class="n">' + q.n + "</span>" +
        '<span class="t"><b>' + esc(q.topic || "") + "</b>" +
        esc((q.spec_refs || []).join(", ")) + "</span>" +
        '<span class="mark ' + cls + '">' + tag + "</span>" +
        '<span class="ans">You: ' + esc(r.selected || "—") +
        " · Key: " + esc(q.answer) + "</span>" +
        '<span class="time' + (r.slow ? " slow" : "") + '">' +
        fmt(r.time_sec) + (r.slow ? " slow" : "") + "</span>";
      det.appendChild(sum);

      var sol = document.createElement("div");
      sol.className = "sol";
      // Authored HTML from the paper file: stem, diagram, options, solution.
      var opts = Object.keys(q.options).sort().map(function (k) {
        return '<span class="opt"><span class="key">' + k + ")</span> " +
               q.options[k] + "</span>";
      }).join(" &nbsp; ");

      var trapHtml = "";
      // The spec promises "why your option is wrong" for a wrong answer, and
      // only for the option the student actually picked — showing every trap
      // would hand them the eliminations they did not earn.
      if (r.state === "wrong" && r.selected && q.traps && q.traps[r.selected]) {
        trapHtml = '<p class="trap"><strong>Why ' + esc(r.selected) +
                   " is wrong:</strong> " + q.traps[r.selected] + "</p>";
      }

      sol.innerHTML = (q.stem_html || "") + (q.diagram_svg || "") +
                      "<p>" + opts + "</p>" +
                      '<hr style="border:0;border-top:1px solid var(--t-line)">' +
                      (q.solution_html || "") + trapHtml;
      det.appendChild(sol);
      list.appendChild(det);
    });

    /* ---- actions ---- */
    document.getElementById("expandAll").addEventListener("click", function () {
      var open = document.querySelectorAll("#qlist details[open]").length !==
                 document.querySelectorAll("#qlist details").length;
      document.querySelectorAll("#qlist details").forEach(function (d) { d.open = open; });
      this.textContent = open ? "Close all solutions" : "Open all solutions";
    });

    document.getElementById("retry").addEventListener("click", function () {
      var b = this;
      b.disabled = true;
      // Sitting again is a fresh attempt, not a reload of this one — the old
      // result stays on record.
      fetch("/exam/" + data.paper.code + "/start", { method: "POST" })
        .then(function (r) { return r.json(); })
        .then(function (d) {
          if (d.attempt_id) { window.location = "/exam/attempt/" + d.attempt_id; }
          else { b.disabled = false; }
        })
        .catch(function () { b.disabled = false; });
    });
  }
})();

/* 1st, 2nd, 3rd, 4th ... 11th, 21st, 101st.
   The naive version — checking only for 1, 2 and 3 — produces "21th" and
   "101th", and a cohort of twenty-plus is exactly where this event lands, so
   those are the ranks people would actually have been shown. The real rule is
   on the last digit, with the teens as the exception. */
function ordinal(n) {
  var tens = n % 100;
  if (tens >= 11 && tens <= 13) return n + "th";
  switch (n % 10) {
    case 1: return n + "st";
    case 2: return n + "nd";
    case 3: return n + "rd";
    default: return n + "th";
  }
}

/* The National Mock position, when this attempt was an entry in one.
   Four outcomes, and each gets its own sentence rather than a shared one with
   a blank in it:

     * ranked        — they opted in and the paper made the threshold;
     * not published — the paper's cohort fell short, so there is no position
                       to give. Said as a fact about the paper, never as
                       something the student failed to qualify for;
     * opted out     — they chose not to join the comparison. Stated without
                       any nudge to change it: the choice was the point;
     * no event      — an ordinary sitting. The block stays hidden. */
function renderEventResult(ev) {
  var box = document.getElementById("nmres");
  if (!box || !ev) return;

  var label = document.getElementById("nmresLabel");
  var big = document.getElementById("nmresBig");
  var note = document.getElementById("nmresNote");

  if (!ev.in_cohort) {
    label.textContent = ev.title;
    big.textContent = "No position";
    note.textContent = "You didn't join the cohort comparison for this one, " +
                       "so your mark is yours alone. Everything else on this " +
                       "page still stands.";
  } else if (!ev.published || ev.percentile == null) {
    label.textContent = ev.title;
    big.textContent = "Not enough sitters";
    note.textContent = "Too few people sat this paper for a position to mean " +
                       "anything, so there isn't one. A rank among a handful " +
                       "of people would be a guess with a number on it.";
  } else {
    label.textContent = ev.title;
    /* "Higher than N%" rather than "Nth percentile" — the second phrasing gets
       read as a grade by about half the people who see it. */
    big.textContent = "Higher than " + ev.percentile + "% of the cohort";
    var bits = [];
    if (ev.rank && ev.cohort_size) {
      bits.push(ordinal(ev.rank) + " of " + ev.cohort_size +
                " who sat it and opted in");
    }
    if (ev.median != null) bits.push("the median was " + ev.median);
    note.textContent = bits.join(" · ") + ".";
  }
  box.classList.remove("hidden");
}
