/* Kineton Academy Wiki — render Mermaid diagrams themed for the active
   light/dark palette. The superfences custom fence emits <pre class="kx-mermaid">;
   the "kx-" prefix keeps MkDocs Material's built-in mermaid integration
   (which targets ".mermaid") from touching these blocks, so this script is
   the only renderer and uses the vendored mermaid.min.js. */
(function () {
  "use strict";

  var SELECTOR = "pre.kx-mermaid, div.kx-mermaid";

  var BASE = {
    startOnLoad: false,
    theme: "base",
    themeVariables: {
      fontFamily: "Inter, sans-serif",
      fontSize: "14px"
    }
  };

  var DARK_VARS = {
    background: "#0a0f1e",
    primaryColor: "#141b31",
    primaryBorderColor: "#7c6cff",
    primaryTextColor: "#e8ecf6",
    secondaryColor: "#10172b",
    tertiaryColor: "#10172b",
    lineColor: "#8b93a7",
    textColor: "#e8ecf6",
    clusterBkg: "#10172b",
    clusterBorder: "#2a3355",
    edgeLabelBackground: "#141b31",
    actorBkg: "#141b31",
    actorBorder: "#7c6cff",
    actorTextColor: "#e8ecf6",
    actorLineColor: "#8b93a7",
    signalColor: "#8b93a7",
    signalTextColor: "#e8ecf6",
    noteBkgColor: "#1a2240",
    noteBorderColor: "#7c6cff",
    noteTextColor: "#e8ecf6",
    activationBkgColor: "#1a2240",
    activationBorderColor: "#8b93a7",
    sequenceNumberColor: "#05070f"
  };

  var LIGHT_VARS = {
    background: "#ffffff",
    primaryColor: "#eef1f6",
    primaryBorderColor: "#5b4bd4",
    primaryTextColor: "#1c2333",
    secondaryColor: "#f4f6fa",
    tertiaryColor: "#f4f6fa",
    lineColor: "#8b93a7",
    textColor: "#1c2333",
    clusterBkg: "#f4f6fa",
    clusterBorder: "#d4dae6",
    edgeLabelBackground: "#eef1f6",
    actorBkg: "#eef1f6",
    actorBorder: "#5b4bd4",
    actorTextColor: "#1c2333",
    actorLineColor: "#8b93a7",
    signalColor: "#8b93a7",
    signalTextColor: "#1c2333",
    noteBkgColor: "#e5eaf2",
    noteBorderColor: "#5b4bd4",
    noteTextColor: "#1c2333",
    activationBkgColor: "#e5eaf2",
    activationBorderColor: "#8b93a7",
    sequenceNumberColor: "#ffffff"
  };

  function isDark() {
    return document.body.getAttribute("data-md-color-scheme") !== "default";
  }

  function config() {
    var vars = isDark() ? DARK_VARS : LIGHT_VARS;
    var merged = { startOnLoad: BASE.startOnLoad, theme: BASE.theme, themeVariables: {} };
    Object.keys(BASE.themeVariables).forEach(function (k) {
      merged.themeVariables[k] = BASE.themeVariables[k];
    });
    Object.keys(vars).forEach(function (k) {
      merged.themeVariables[k] = vars[k];
    });
    return merged;
  }

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
    window.mermaid.initialize(config());
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
    // palette toggle — re-render diagrams with the new scheme's colors
    new MutationObserver(function (mutations) {
      mutations.forEach(function (m) {
        if (m.attributeName === "data-md-color-scheme") render();
      });
    }).observe(document.body, { attributes: true });
  });
})();
