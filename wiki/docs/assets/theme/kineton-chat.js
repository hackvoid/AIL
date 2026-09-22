/* Kineton Academy Wiki — assistant panel (frontend shell).
   The panel shows a static placeholder reply until
   window.KX_CHAT_CONFIG.endpoint is set; once configured, askBackend()
   POSTs {message} there and renders the returned {reply}. */
(function () {
  "use strict";

  var PLACEHOLDER_REPLY =
    "Response will appear here once the API is configured.";

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var root = document.getElementById("kx-chat");
    if (!root) return;
    var handle = document.getElementById("kx-chat-handle");
    var thread = document.getElementById("kx-chat-thread");
    var form = document.getElementById("kx-chat-form");
    var input = document.getElementById("kx-chat-input");

    function setOpen(open) {
      root.setAttribute("data-state", open ? "open" : "collapsed");
      handle.setAttribute("aria-expanded", String(open));
      document.body.classList.toggle("kx-chat-open", open);
      try { localStorage.setItem("kx-chat-open", open ? "1" : "0"); } catch (e) {}
      if (open) setTimeout(function () { input.focus(); }, 250);
    }

    handle.addEventListener("click", function () {
      setOpen(root.getAttribute("data-state") !== "open");
    });

    var wasOpen = false;
    try { wasOpen = localStorage.getItem("kx-chat-open") === "1"; } catch (e) {}
    if (wasOpen || window.location.hash === "#assistant") setOpen(true);

    function scrollDown() { thread.scrollTop = thread.scrollHeight; }

    function addMsg(text, who) {
      var el = document.createElement("div");
      el.className = "kx-chat__msg kx-chat__msg--" + who;
      var p = document.createElement("p");
      p.textContent = text;
      el.appendChild(p);
      thread.appendChild(el);
      scrollDown();
      return el;
    }

    function askBackend(message) {
      var cfg = window.KX_CHAT_CONFIG || {};
      if (!cfg.endpoint) return Promise.resolve(null);
      return fetch(cfg.endpoint, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message, model: cfg.model || undefined })
      }).then(function (r) { return r.ok ? r.json() : null; })
        .then(function (d) { return (d && d.reply) || null; })
        .catch(function () { return null; });
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      addMsg(text, "user");
      input.value = "";
      askBackend(text).then(function (backendReply) {
        addMsg(backendReply || PLACEHOLDER_REPLY, "bot");
      });
    });
  });
})();
