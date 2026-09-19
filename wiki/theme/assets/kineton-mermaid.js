/* Kineton Academy Wiki — render Mermaid diagrams with the Constellation
   dark palette. The superfences custom fence emits <pre class="kx-mermaid">;
   the "kx-" prefix keeps MkDocs Material's built-in mermaid integration
   (which targets ".mermaid") from touching these blocks, so this script is
   the only renderer and uses the vendored mermaid.min.js. */
(function () {
  "use strict";

  var SELECTOR = "pre.kx-mermaid, div.kx-mermaid";

  var MERMAID_CONFIG = {
    startOnLoad: false,
    theme: "base",
    themeVariables: {
      background: "#0a0f1e",
      primaryColor: "#141b31",
      primaryBorderColor: "#7c6cff",
      primaryTextColor: "#e8ecf6",
      secondaryColor: "#10172b",
      tertiaryColor: "#10172b",
      lineColor: "#4dd8ff",
      textColor: "#e8ecf6",
      fontFamily: "Inter, sans-serif",
      fontSize: "14px",
      clusterBkg: "#10172b",
      clusterBorder: "#2a3355",
      edgeLabelBackground: "#141b31",
      actorBkg: "#141b31",
      actorBorder: "#7c6cff",
      actorTextColor: "#e8ecf6",
      actorLineColor: "#4dd8ff",
      signalColor: "#4dd8ff",
      signalTextColor: "#e8ecf6",
      noteBkgColor: "#1a2240",
      noteBorderColor: "#7c6cff",
      noteTextColor: "#e8ecf6",
      activationBkgColor: "#1a2240",
      activationBorderColor: "#4dd8ff",
      sequenceNumberColor: "#05070f"
    }
  };

  function capture(el) {
    if (!el.hasAttribute("data-kx-source")) {
      el.setAttribute("data-kx-source", el.textContent);
    }
  }

  // Synchronous capture — this file loads at the end of <body>, before
  // mermaid's own auto-run (DOMContentLoaded) can replace the content.
  document.querySelectorAll(SELECTOR).forEach(capture);

  function render() {
    if (!window.mermaid) return false;
    window.mermaid.initialize(MERMAID_CONFIG);
    document.querySelectorAll(SELECTOR).forEach(function (el) {
      capture(el);
      el.textContent = el.getAttribute("data-kx-source");
      el.removeAttribute("data-processed");
    });
    window.mermaid.run({ querySelector: SELECTOR });
    return true;
  }

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var attempts = 0;
    var timer = setInterval(function () {
      attempts += 1;
      if (render() || attempts > 30) clearInterval(timer);
    }, 250);
    // instant navigation (Material's document$ swap) — render new diagrams
    if (window.document$ && typeof window.document$.subscribe === "function") {
      window.document$.subscribe(function () {
        setTimeout(render, 100);
      });
    }
  });
})();
