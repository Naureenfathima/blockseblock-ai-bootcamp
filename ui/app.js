/* =============================================================================
   AI Engineering Bootcamp · BlockseBlock
   app.js — grows additively; each feature adds a new section.
   ============================================================================= */

// The base URL of the FastAPI server.
// When opening index.html directly from disk (file://) the API won't be reachable
// and requests will fail — run `uvicorn main:app` and open http://localhost:8000.
const API_BASE = "";

// =============================================================================
// Feature 1: Basic Chat
// =============================================================================

const messageHistory = document.getElementById("message-history");
const chatInput      = document.getElementById("chat-input");
const sendBtn        = document.getElementById("send-btn");
const emptyState     = document.getElementById("empty-state");

/**
 * Append a message bubble to the conversation history.
 *
 * @param {"user"|"ai"} role
 * @param {string} text
 * @param {boolean} [isThinking=false]  - show animated dots instead of text
 * @returns {HTMLElement} the created message element (useful for updating it later)
 */
function appendMessage(role, text, isThinking = false) {
  if (emptyState) emptyState.remove();

  const wrapper = document.createElement("div");
  wrapper.className = `message ${role}${isThinking ? " thinking" : ""}`;

  const label = document.createElement("span");
  label.className = "role-label";
  label.textContent = role === "user" ? "You" : "Assistant";

  const bubble = document.createElement("div");
  bubble.className = "bubble";

  if (isThinking) {
    // Animated typing indicator — three bouncing dots.
    for (let i = 0; i < 3; i++) {
      const dot = document.createElement("span");
      dot.className = "dot";
      bubble.appendChild(dot);
    }
  } else {
    bubble.textContent = text;
  }

  wrapper.appendChild(label);
  wrapper.appendChild(bubble);
  messageHistory.appendChild(wrapper);

  // Keep the latest message in view.
  messageHistory.scrollTop = messageHistory.scrollHeight;

  return wrapper;
}

/** Send the current input value to the appropriate chat endpoint. */
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  sendBtn.disabled = true;

  appendMessage("user", text);
  const thinkingEl = appendMessage("ai", "", true);

  const isStructured = structuredToggle?.checked ?? false;

  // Feature 3: if a session is active, all messages go through the session endpoint
  // (which always returns a StructuredResponse). Fall back to Feature 1/2 endpoints
  // only when no session is active.
  let endpoint;
  if (currentSessionId) {
    endpoint = `/api/sessions/${currentSessionId}/chat`;
  } else if (isStructured) {
    endpoint = "/api/chat/structured";
  } else {
    endpoint = "/api/chat";
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message: text }),
    });

    if (!response.ok) {
      const err = await response.json().catch(() => ({}));
      throw new Error(err.detail || `Server error ${response.status}`);
    }

    const data = await response.json();
    thinkingEl.remove();

    // Session endpoint and structured mode both return StructuredResponse.
    if (currentSessionId || isStructured) {
      appendStructuredResponse(data);
    } else {
      appendMessage("ai", data.response ?? "(no response)");
    }

    // Refresh the sidebar after each message so the session title and count update.
    if (currentSessionId) loadSessions();

  } catch (err) {
    thinkingEl.remove();
    appendMessage("ai", `Error: ${err.message}. Is the server running?`);
  } finally {
    sendBtn.disabled = false;
    chatInput.focus();
  }
}

// Send on button click or Enter key.
sendBtn.addEventListener("click", sendMessage);
chatInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    sendMessage();
  }
});

// =============================================================================
// Provider info card
// Fetches /api/provider-info once on load and shows which provider is active.
// This endpoint is added in shared/llm_client.py — the card shows a gentle
// error message if it's not yet available.
// =============================================================================

async function loadProviderInfo() {
  const card = document.getElementById("provider-info-card");
  if (!card) return;

  try {
    const res = await fetch(`${API_BASE}/api/provider-info`);
    if (!res.ok) throw new Error("endpoint not available yet");

    const info = await res.json();

    card.innerHTML = `
      <span>LLM Provider: <span class="badge">${info.llm_provider ?? "—"}</span></span>
      <span>Model: <code>${info.llm_model ?? "—"}</code></span>
      ${info.voice_provider ? `<span>Voice: <span class="badge">${info.voice_provider}</span> (${info.voice_model ?? "—"})</span>` : ""}
    `;
  } catch {
    card.innerHTML = `<span style="color:var(--color-pistache)">Provider info not available — server may not be running yet.</span>`;
  }
}

loadProviderInfo();

// =============================================================================
// Feature 2: Structured Mode
// =============================================================================

const structuredToggle = document.getElementById("structured-toggle");

// Keep the aria-checked attribute in sync with checkbox state for accessibility.
structuredToggle?.addEventListener("change", () => {
  structuredToggle.setAttribute("aria-checked", String(structuredToggle.checked));
});

/**
 * Render a StructuredResponse as a visual card in the message history.
 *
 * @param {{ intent: string, answer: string, confidence: number, sources_needed: boolean }} data
 */
function appendStructuredResponse(data) {
  // Remove the empty-state placeholder on first message (same as appendMessage).
  document.getElementById("empty-state")?.remove();

  // Outer wrapper mirrors the .message.ai layout so it aligns with plain messages.
  const wrapper = document.createElement("div");
  wrapper.className = "message ai";

  const label = document.createElement("span");
  label.className = "role-label";
  label.textContent = "Assistant";

  // Card body
  const card = document.createElement("div");
  card.className = "response-card";

  // ── Header row: intent badge + confidence meter ──
  const header = document.createElement("div");
  header.className = "response-card-header";

  // Intent badge
  const badge = document.createElement("span");
  badge.className = "intent-badge";
  badge.dataset.intent = data.intent ?? "unclear";
  badge.textContent = (data.intent ?? "unclear").replace(/_/g, " ");
  header.appendChild(badge);

  // Confidence meter
  const pct = Math.round((data.confidence ?? 0) * 100);
  const level = pct >= 70 ? "high" : pct >= 40 ? "medium" : "low";

  const confidenceWrap = document.createElement("div");
  confidenceWrap.className = "confidence-wrap";
  confidenceWrap.innerHTML = `
    <span class="confidence-label">Confidence</span>
    <div class="confidence-bar-track">
      <div class="confidence-bar-fill" data-level="${level}" style="width:${pct}%"></div>
    </div>
    <span class="confidence-pct">${pct}%</span>
  `;
  header.appendChild(confidenceWrap);

  card.appendChild(header);

  // ── Answer text ──
  const answer = document.createElement("p");
  answer.className = "response-card-answer";
  answer.textContent = data.answer ?? "";
  card.appendChild(answer);

  // ── Sources needed hint ──
  if (data.sources_needed) {
    const hint = document.createElement("span");
    hint.className = "sources-tag";
    hint.textContent = "⚠ This answer would improve with domain documents (added in Feature 4).";
    card.appendChild(hint);
  }

  wrapper.appendChild(label);
  wrapper.appendChild(card);
  messageHistory.appendChild(wrapper);
  messageHistory.scrollTop = messageHistory.scrollHeight;
}

// =============================================================================
// Feature 3: Session management
// =============================================================================

/** The currently active session ID, or null when no session is selected. */
let currentSessionId = null;

const newChatBtn    = document.getElementById("new-chat-btn");
const sessionList   = document.getElementById("session-list");
const sessionLabel  = document.getElementById("session-label");

/** Clear the message history area and reset the empty-state placeholder. */
function clearChat() {
  messageHistory.innerHTML = `
    <div class="empty-state" id="empty-state">
      Start a <strong>New Chat</strong> or ask anything about <strong>[YOUR_DOMAIN]</strong>.
    </div>`;
}

/** Mark one session item as active in the sidebar. */
function setActiveSession(sessionId) {
  document.querySelectorAll(".session-item").forEach((el) => {
    el.classList.toggle("active", el.dataset.sessionId === sessionId);
  });

  if (sessionLabel) {
    if (sessionId) {
      sessionLabel.textContent = `session: ${sessionId.slice(0, 8)}…`;
      sessionLabel.removeAttribute("hidden");
    } else {
      sessionLabel.setAttribute("hidden", "");
    }
  }
}

/**
 * Fetch all sessions from the API and render them in the sidebar.
 * Silently does nothing if the /api/sessions endpoint isn't available yet
 * (Feature 1 and 2 servers don't have it).
 */
async function loadSessions() {
  if (!sessionList) return;

  try {
    const res = await fetch(`${API_BASE}/api/sessions`);
    if (!res.ok) throw new Error("sessions endpoint not available");

    const sessions = await res.json();

    if (!sessions.length) {
      sessionList.innerHTML = `<p class="sidebar-empty">No sessions yet.<br>Click <strong>New Chat</strong> to start.</p>`;
      return;
    }

    sessionList.innerHTML = "";
    sessions.forEach((s) => {
      const btn = document.createElement("button");
      btn.className = "session-item";
      btn.dataset.sessionId = s.id;
      if (s.id === currentSessionId) btn.classList.add("active");

      btn.innerHTML = `
        <div class="session-item-title">${escapeHtml(s.title)}</div>
        <div class="session-item-meta">${s.message_count} message${s.message_count !== 1 ? "s" : ""}</div>
      `;
      btn.addEventListener("click", () => switchToSession(s.id));
      sessionList.appendChild(btn);
    });
  } catch {
    // /api/sessions isn't available on the Feature 1/2 server — sidebar stays empty gracefully.
    sessionList.innerHTML = `<p class="sidebar-empty" style="font-size:0.75rem">Session history requires the Feature 3 server.</p>`;
  }
}

/**
 * Create a new session via the API and switch to it.
 */
async function createNewSession() {
  try {
    const res = await fetch(`${API_BASE}/api/sessions`, { method: "POST" });
    if (!res.ok) throw new Error(`Server error ${res.status}`);

    const data = await res.json();
    currentSessionId = data.session_id;
    clearChat();
    setActiveSession(currentSessionId);
    await loadSessions();
    chatInput.focus();
  } catch (err) {
    alert(`Could not create a new session: ${err.message}\nIs the Feature 3 server running?`);
  }
}

/**
 * Load a session's history from the API and render it in the chat area.
 */
async function switchToSession(sessionId) {
  try {
    const res = await fetch(`${API_BASE}/api/sessions/${sessionId}/history`);
    if (!res.ok) throw new Error(`Server error ${res.status}`);

    const messages = await res.json();
    currentSessionId = sessionId;
    clearChat();

    messages.forEach((msg) => {
      if (msg.role === "user") {
        appendMessage("user", msg.content);
      } else {
        // History messages are stored as plain answer text — render as plain bubbles.
        appendMessage("ai", msg.content);
      }
    });

    setActiveSession(sessionId);
    chatInput.focus();
  } catch (err) {
    appendMessage("ai", `Could not load session: ${err.message}`);
  }
}

/** Minimal HTML escape to prevent XSS in the session title. */
function escapeHtml(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

newChatBtn?.addEventListener("click", createNewSession);

// Load session list on page load so the sidebar populates immediately.
loadSessions();

// =============================================================================
// Future features will add their JS sections below this line.
// Each section should be clearly commented with the feature name and number.
// =============================================================================
