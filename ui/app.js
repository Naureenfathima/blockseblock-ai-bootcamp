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

/** Send the current input value to /api/chat and display the reply. */
async function sendMessage() {
  const text = chatInput.value.trim();
  if (!text) return;

  chatInput.value = "";
  sendBtn.disabled = true;

  appendMessage("user", text);

  const thinkingEl = appendMessage("ai", "", true);

  // Feature 2: route to /api/chat/structured when Structured Mode is on.
  const isStructured = structuredToggle?.checked ?? false;

  try {
    const endpoint = isStructured ? "/api/chat/structured" : "/api/chat";
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

    if (isStructured) {
      appendStructuredResponse(data);
    } else {
      appendMessage("ai", data.response ?? "(no response)");
    }

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
// Future features will add their JS sections below this line.
// Each section should be clearly commented with the feature name and number.
// =============================================================================
