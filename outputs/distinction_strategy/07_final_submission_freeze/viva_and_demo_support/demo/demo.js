/* Offline examiner demo — no network fetches beyond local evidence JSON. */
(function () {
  "use strict";

  var CASE_META = {
    "case-016": {
      title: "phase1-016 — Strong Yes × High candidate",
      teach: "Traceability and journal validity align in this case.",
      proves: "A quoted public-record measure can pass mechanical traceability and still meet the operational journal definition under author review.",
      notProves: "This case does not prove corpus-wide accuracy, inter-rater reliability, or that the recalled COBR action is independently verified beyond hearing testimony.",
      discourse: "Policy-decision candidate with aligned quote support."
    },
    "case-082": {
      title: "phase1-082 — No × High wrong-artefact candidate (centrepiece)",
      teach: "A quotation may strongly support the generated wording while the item still does not belong in a policy decision journal.",
      proves: "Evidence strength (Rubric B) and journal membership (Rubric A) must be rated separately; procedural hearing administration is a wrong artefact type.",
      notProves: "This case does not imply all high-evidence items are invalid, nor that extraction always fails on policy content.",
      discourse: "Procedural hearing adjournment / schedule language."
    },
    "case-090": {
      title: "phase1-090 — Materially unsupported or altered statement",
      teach: "Source availability does not establish that a generated summary preserves meaning.",
      proves: "Mechanical presence of tokens/quote can coexist with a semantically altered decision claim (counsel question rendered as an enacted commissioning statement).",
      notProves: "This is not a general hallucination rate for the corpus; it is a purposive faithfulness illustration from the n=60 review.",
      discourse: "Counsel question in source vs asserted decision in candidate."
    },
    "case-246": {
      title: "phase1-246 — JEE P3 and Decision Quality interpretation",
      teach: "Recognised frameworks can support structured interpretation only after source evidence has been validated.",
      proves: "After a near-verbatim source match, human review can assign JEE capacity P3 and Decision Quality commitment_to_follow_through as interpretive labels.",
      notProves: "Mapping is not a judgement that the underlying decision or preparedness performance was good.",
      discourse: "Inter-agency agreement on school messaging (Long Covid signposting)."
    }
  };

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) node.className = cls;
    if (text != null) node.textContent = text;
    return node;
  }

  function row(dl, label, value) {
    var dt = el("dt", null, label);
    var dd = el("dd", null, value == null || value === "" ? "—" : String(value));
    dl.appendChild(dt);
    dl.appendChild(dd);
  }

  function evidencePath(data, field) {
    return "evidence/" + data.journal_id + ".json → " + field;
  }

  function renderCase(section, data, meta) {
    section.innerHTML = "";
    section.appendChild(el("h2", null, meta.title));

    var teach = el("p", "proposition teach", meta.teach);
    section.appendChild(teach);

    var grid = el("div", "case-grid");

    // 1 Source and provenance
    var b1 = el("div", "block source");
    b1.appendChild(el("h3", null, "1. Source and provenance"));
    var dl1 = el("dl", "meta");
    row(dl1, "Journal ID", data.journal_id);
    row(dl1, "Hearing date", data.hearing_date);
    row(dl1, "Document slug", data.slug);
    row(dl1, "Extraction run ID", data.run_id);
    row(dl1, "Source location (chunk)", data.source_location);
    b1.appendChild(dl1);
    b1.appendChild(el("p", "diff-label", "Validated source quotation"));
    b1.appendChild(el("p", "quote", data.source_quote));
    b1.appendChild(el("p", "path", evidencePath(data, "source_quote / hearing_date / slug")));
    grid.appendChild(b1);

    // 2 Frozen LLM candidate
    var b2 = el("div", "block machine");
    b2.appendChild(el("h3", null, "2. Frozen LLM candidate"));
    b2.appendChild(el("p", "diff-label", "Candidate decision"));
    b2.appendChild(el("p", "decision", data.decision));
    b2.appendChild(el("p", "diff-label", "Model evidence field"));
    b2.appendChild(el("p", "decision", data.evidence));
    b2.appendChild(el("p", "path", evidencePath(data, "decision / evidence")));
    grid.appendChild(b2);

    // 3 Automated traceability
    var b3 = el("div", "block auto");
    b3.appendChild(el("h3", null, "3. Automated traceability result"));
    var dl3 = el("dl", "meta");
    row(dl3, "traceability_ok", data.traceability_ok === true ? "PASS (true)" : String(data.traceability_ok));
    row(dl3, "Review flags", (data.review_flags && data.review_flags.length) ? data.review_flags.join(", ") : "none");
    b3.appendChild(dl3);
    b3.appendChild(el("p", "path", evidencePath(data, "traceability_ok / review_flags")));
    grid.appendChild(b3);

    // 4 Human review
    var b4 = el("div", "block human");
    b4.appendChild(el("h3", null, "4. Human review outcome"));
    var dl4 = el("dl", "meta");
    if (data.rubric_a != null) row(dl4, "Rubric A (journal validity)", String(data.rubric_a).toUpperCase());
    if (data.rubric_b != null) row(dl4, "Rubric B (evidence strength)", String(data.rubric_b).toUpperCase());
    if (data.n50_notes) row(dl4, "Author notes (n=50)", data.n50_notes);
    if (data.faithfulness_category) row(dl4, "Faithfulness class (n=60)", data.faithfulness_category);
    if (data.jee_decision) row(dl4, "JEE decision", data.jee_decision);
    if (data.jee_primary) row(dl4, "JEE primary", data.jee_primary);
    if (data.dq_decision) row(dl4, "Decision Quality decision", data.dq_decision);
    if (data.dq_primary) row(dl4, "Decision Quality primary", data.dq_primary);
    b4.appendChild(dl4);
    b4.appendChild(el("p", "path", evidencePath(data, "rubric_* / faithfulness_category / jee_* / dq_*")));
    grid.appendChild(b4);

    // 5 Interpretation (semantic highlight for 090)
    var b5 = el("div", "block");
    b5.appendChild(el("h3", null, "5. Interpretation"));
    b5.appendChild(el("p", null, meta.discourse));
    if (data.journal_id === "phase1-090") {
      var pair = el("div", "diff-pair");
      var left = el("div");
      left.appendChild(el("p", "diff-label", "Source (counsel question)"));
      left.appendChild(el("p", "quote", data.source_quote));
      var right = el("div");
      right.appendChild(el("p", "diff-label", "Generated candidate (asserted decision)"));
      right.appendChild(el("p", "decision", data.decision));
      pair.appendChild(left);
      pair.appendChild(right);
      b5.appendChild(pair);
    }
    if (data.journal_id === "phase1-246") {
      var warn = el("p", "warn-box");
      warn.textContent = "Warning: JEE and Decision Quality mappings are interpretive aids after source validation. They are not judgements that the decision or preparedness performance was good.";
      b5.appendChild(warn);
    }
    grid.appendChild(b5);

    // 6 proves
    var b6 = el("div", "block");
    b6.appendChild(el("h3", null, "6. What this case proves"));
    b6.appendChild(el("p", "teach", meta.proves));
    grid.appendChild(b6);

    // 7 does not prove
    var b7 = el("div", "block");
    b7.appendChild(el("h3", null, "7. What this case does not prove"));
    b7.appendChild(el("p", "teach", meta.notProves));
    grid.appendChild(b7);

    section.appendChild(grid);
  }

  function showPanel(id) {
    var panels = document.querySelectorAll(".panel");
    for (var i = 0; i < panels.length; i++) {
      panels[i].classList.remove("active");
      panels[i].hidden = panels[i].id !== id;
    }
    var target = document.getElementById(id);
    if (target) {
      target.hidden = false;
      target.classList.add("active");
    }
    var buttons = document.querySelectorAll("[data-target]");
    for (var j = 0; j < buttons.length; j++) {
      var btn = buttons[j];
      if (btn.classList.contains("nav-btn") || btn.classList.contains("card")) {
        btn.classList.toggle("active", btn.getAttribute("data-target") === id);
      }
    }
  }

  function journalIdFromSection(sectionId) {
    return sectionId.replace("case-", "phase1-");
  }

  function getEmbedded(journalId) {
    var bag = window.__DEMO_EVIDENCE || {};
    return bag[journalId] || null;
  }

  function applyCase(section, sectionId, data) {
    renderCase(section, data, CASE_META[sectionId]);
    section.setAttribute("data-loaded", "1");
    showPanel(sectionId);
  }

  function loadCase(sectionId) {
    var section = document.getElementById(sectionId);
    if (!section || section.getAttribute("data-loaded") === "1") {
      showPanel(sectionId);
      return;
    }
    var path = section.getAttribute("data-evidence");
    var journalId = journalIdFromSection(sectionId);
    var embedded = getEmbedded(journalId);
    if (embedded) {
      applyCase(section, sectionId, embedded);
      return;
    }
    fetch(path)
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status + " for " + path);
        return res.json();
      })
      .then(function (data) {
        applyCase(section, sectionId, data);
      })
      .catch(function (err) {
        section.hidden = false;
        section.classList.add("active");
        section.textContent =
          "Could not load " +
          path +
          ". Prefer python demo/launch_demo.py, or ensure evidence_embed.js is present for file://. " +
          String(err);
      });
  }

  function loadHashes() {
    var list = document.getElementById("hash-list");
    if (!list) return;
    function paint(man) {
      list.innerHTML = "";
      var files = man.files || {};
      Object.keys(files).sort().forEach(function (name) {
        var meta = files[name];
        var li = el("li", null, null);
        li.appendChild(el("code", null, meta.journal_id || name));
        li.appendChild(document.createTextNode(" — "));
        li.appendChild(el("span", "hash", meta.sha256));
        list.appendChild(li);
      });
    }
    if (window.__DEMO_MANIFEST) {
      paint(window.__DEMO_MANIFEST);
      return;
    }
    fetch("DEMO_EVIDENCE_MANIFEST.json")
      .then(function (res) {
        return res.json();
      })
      .then(paint)
      .catch(function () {
        list.textContent = "Open DEMO_EVIDENCE_MANIFEST.json for SHA-256 values.";
      });
  }

  function onNav(id) {
    if (id === "landing") {
      showPanel("landing");
      return;
    }
    loadCase(id);
  }

  function bind() {
    var nodes = document.querySelectorAll("[data-target]");
    for (var i = 0; i < nodes.length; i++) {
      nodes[i].addEventListener("click", function (ev) {
        onNav(ev.currentTarget.getAttribute("data-target"));
      });
    }
    loadHashes();
    showPanel("landing");
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", bind);
  } else {
    bind();
  }
})();
