(() => {
  const $ = (sel) => document.querySelector(sel);
  const chat = $("#chat");
  const input = $("#input");
  const sendBtn = $("#send");
  const apiBaseInput = $("#apiBase");
  const saveCfg = $("#saveCfg");

  // Persist API base and session locally
  const STORAGE_KEYS = { apiBase: "rag.apiBase", sessionId: "rag.sessionId" };
  apiBaseInput.value = localStorage.getItem(STORAGE_KEYS.apiBase) || apiBaseInput.value;

  let API_BASE = apiBaseInput.value;
  let sessionId = localStorage.getItem(STORAGE_KEYS.sessionId);

  saveCfg.addEventListener("click", () => {
    API_BASE = apiBaseInput.value.trim();
    localStorage.setItem(STORAGE_KEYS.apiBase, API_BASE);
    toast("API base guardada");
  });

  function toast(msg) {
    const el = document.createElement("div");
    el.textContent = msg;
    el.style.position = "fixed";
    el.style.bottom = "12px";
    el.style.right = "12px";
    el.style.background = "#111827";
    el.style.border = "1px solid #374151";
    el.style.padding = "8px 10px";
    el.style.borderRadius = "8px";
    el.style.color = "#e5e7eb";
    el.style.opacity = "0.95";
    document.body.appendChild(el);
    setTimeout(() => el.remove(), 1800);
  }

  function createMsg(role, text, sources=[]) {
    const tpl = document.getElementById("msgTemplate");
    const node = tpl.content.cloneNode(true);
    const msg = node.querySelector(".msg");
    msg.classList.add(role);
    const content = node.querySelector(".content");
    const time = node.querySelector(".time");
    const avatar = node.querySelector(".avatar");
    const sourcesEl = node.querySelector(".sources");
    content.textContent = text;
    time.textContent = new Date().toLocaleTimeString();
    avatar.textContent = role === "user" ? "👤" : "🤖";

    if (role === "assistant" && sources && sources.length) {
      sourcesEl.innerHTML = sources.map(s => {
        const name = (s.source || "fuente").toString().split("/").pop();
        return `<a href="#" title="${s.source}">${name}</a>`;
      }).join(" · ");
    }

    chat.appendChild(node);
    chat.scrollTop = chat.scrollHeight;
  }

  async function ensureSession() {
    if (sessionId) return sessionId;
    const resp = await fetch(`${API_BASE}/session`, { method: "POST" });
    if (!resp.ok) throw new Error(`No se pudo crear sesión: ${resp.status}`);
    const data = await resp.json();
    sessionId = data.session_id;
    localStorage.setItem(STORAGE_KEYS.sessionId, sessionId);
    return sessionId;
  }

  async function sendMessage() {
    const text = input.value.trim();
    if (!text) return;
    input.value = "";
    input.disabled = true;
    sendBtn.disabled = true;

    createMsg("user", text);
    const typingId = Math.random().toString(36).slice(2);
    createMsg("assistant", "Escribiendo...", []);
    const lastBubble = chat.querySelectorAll(".msg.assistant .bubble .content");
    const typingBubble = lastBubble[lastBubble.length - 1];
    typingBubble.classList.add("loading");

    try {
      await ensureSession();
      const resp = await fetch(`${API_BASE}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: sessionId, message: text, k: 4 })
      });
      if (!resp.ok) {
        const errText = await resp.text();
        throw new Error(`${resp.status} ${errText}`);
      }
      const data = await resp.json();
      // Replace typing bubble with final content
      typingBubble.textContent = data.reply || "(sin respuesta)";
      typingBubble.classList.remove("loading");

      // Render sources
      const sourcesWraps = chat.querySelectorAll(".msg.assistant .sources");
      const lastSources = sourcesWraps[sourcesWraps.length - 1];
      if (data.sources && data.sources.length) {
        lastSources.innerHTML = data.sources.map(s => {
          const name = (s.source || "fuente").toString().split("/").pop();
          return `<a href="#" title="${s.source}">${name}</a>`;
        }).join(" · ");
      }
    } catch (e) {
      typingBubble.textContent = `Error: ${e.message}`;
      typingBubble.classList.remove("loading");
    } finally {
      input.disabled = false;
      sendBtn.disabled = false;
      input.focus();
    }
  }

  sendBtn.addEventListener("click", sendMessage);
  input.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  });

  // Greet
  const greet = "¡Hola! Soy tu asistente RAG.\nEscribe una pregunta y usaré los documentos para ayudarte.";
  createMsg("assistant", greet);
})();