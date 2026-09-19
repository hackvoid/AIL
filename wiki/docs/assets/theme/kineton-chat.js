/* Kineton Academy Wiki — AI assistant panel (frontend shell).
   Visual-preview mode: canned placeholder replies. When
   window.KX_CHAT_CONFIG.endpoint is set in a later step, askBackend()
   will POST {message} there and render {reply} instead. */
(function () {
  "use strict";

  var PLACEHOLDER_REPLIES = [
    "Great question! Once I'm connected to the academy knowledge base, I'll answer this with links to the exact lesson. For now, try the search bar above — the wiki covers it.",
    "I'm still in preview mode, so I can't look that up yet. A good place to check: the MIL1 fundamentals module — it builds up the concepts step by step.",
    "That's covered in the bootcamp material! When my backend is connected I'll point you straight to the right article. Meanwhile, the glossary has a quick definition.",
    "Nice one — that's exactly the kind of question I'll handle once the API is wired up. For now, browse the module pages; each topic lists its articles and exercises."
  ];

  function ready(fn) {
    if (document.readyState !== "loading") fn();
    else document.addEventListener("DOMContentLoaded", fn);
  }

  ready(function () {
    var root = document.getElementById("kx-chat");
    if (!root) return;
    var handle = document.getElementById("kx-chat-handle");
    var closeBtn = document.getElementById("kx-chat-close");
    var thread = document.getElementById("kx-chat-thread");
    var form = document.getElementById("kx-chat-form");
    var input = document.getElementById("kx-chat-input");
    var suggestions = document.getElementById("kx-chat-suggestions");
    var replyIdx = 0;

    function setOpen(open) {
      root.setAttribute("data-state", open ? "open" : "collapsed");
      handle.setAttribute("aria-expanded", String(open));
      document.body.classList.toggle("kx-chat-open", open);
      try { localStorage.setItem("kx-chat-open", open ? "1" : "0"); } catch (e) {}
      if (open) setTimeout(function () { input.focus(); }, 250);
    }

    handle.addEventListener("click", function () { setOpen(true); });
    closeBtn.addEventListener("click", function () { setOpen(false); });

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

    function addTyping() {
      var el = document.createElement("div");
      el.className = "kx-chat__msg kx-chat__msg--bot kx-chat__msg--typing";
      el.innerHTML = "<span></span><span></span><span></span>";
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

    function respond(message) {
      var typing = addTyping();
      askBackend(message).then(function (backendReply) {
        setTimeout(function () {
          typing.remove();
          var reply = backendReply || PLACEHOLDER_REPLIES[replyIdx++ % PLACEHOLDER_REPLIES.length];
          addMsg(reply, "bot");
        }, backendReply ? 0 : 850);
      });
    }

    form.addEventListener("submit", function (ev) {
      ev.preventDefault();
      var text = input.value.trim();
      if (!text) return;
      if (suggestions) { suggestions.remove(); suggestions = null; }
      addMsg(text, "user");
      input.value = "";
      respond(text);
    });

    if (suggestions) {
      suggestions.addEventListener("click", function (ev) {
        var chip = ev.target.closest(".kx-chip");
        if (!chip) return;
        input.value = chip.getAttribute("data-prompt") || chip.textContent;
        form.requestSubmit();
      });
    }
  });
})();
