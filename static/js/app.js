/* MinutesMate frontend logic — talks to the Flask REST API (no page reloads). */
"use strict";

const $ = (id) => document.getElementById(id);

let currentResult = null;
let currentTitle = "Meeting Minutes";

/* ---------- Tabs ---------- */
document.querySelectorAll(".tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".tab").forEach((t) => t.classList.remove("active"));
    tab.classList.add("active");
    document.querySelectorAll(".panel").forEach((p) => p.classList.add("hidden"));
    $("panel-" + tab.dataset.tab).classList.remove("hidden");
  });
});

/* ---------- Mode chip ---------- */
function updateModeChip() {
  const chip = $("modeChip");
  if ($("apiKey").value.trim()) {
    chip.classList.add("gpt");
    $("modeChipText").textContent = "GPT MODE — " + $("gptModel").value;
  } else {
    chip.classList.remove("gpt");
    $("modeChipText").textContent = "OFFLINE MODE — no key, no internet, no cost";
  }
}
$("apiKey").addEventListener("input", updateModeChip);
$("gptModel").addEventListener("input", updateModeChip);

/* ---------- Status helpers ---------- */
function setStatus(msg, cls) {
  $("status").textContent = msg || "";
  $("status").className = "status-msg" + (cls ? " " + cls : "");
}

/* ---------- Buttons ---------- */
$("loadSample").addEventListener("click", async () => {
  setStatus("Loading sample…", "spin");
  try {
    const res = await fetch("/api/sample");
    const data = await res.json();
    $("transcript").value = data.transcript || "";
    setStatus("Sample transcript loaded.", "ok");
  } catch (err) {
    setStatus("Could not load the sample: " + err.message, "error");
  }
});

$("clearText").addEventListener("click", () => {
  $("transcript").value = "";
  setStatus("");
});

$("transcribeBtn").addEventListener("click", async () => {
  const file = $("audioFile").files[0];
  if (!file) {
    setStatus("Choose an audio file first (WAV/MP3/M4A).", "error");
    return;
  }
  const form = new FormData();
  form.append("audio", file);
  form.append("model", $("whisperModel").value);
  form.append("language", $("language").value);

  const btn = $("transcribeBtn");
  btn.disabled = true;
  setStatus("Transcribing locally with Whisper — this can take a while on CPU…", "spin");
  try {
    const res = await fetch("/api/transcribe", { method: "POST", body: form });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Transcription failed.");
    $("audioTranscript").value = data.transcript;
    setStatus("Transcription complete. Review the text, then press Generate Minutes.", "ok");
  } catch (err) {
    setStatus(err.message, "error");
  } finally {
    btn.disabled = false;
  }
});

$("generateBtn").addEventListener("click", async () => {
  const activeTab = document.querySelector(".tab.active").dataset.tab;
  const transcript =
    activeTab === "paste" ? $("transcript").value.trim() : $("audioTranscript").value.trim();

  if (!transcript) {
    setStatus("Please paste a transcript or transcribe an audio file first.", "error");
    return;
  }

  currentTitle = $("meetingTitle").value.trim() || "Meeting Minutes";
  const payload = {
    title: currentTitle,
    transcript,
    api_key: $("apiKey").value.trim(),
    model: $("gptModel").value.trim() || "gpt-4o-mini",
  };

  const btn = $("generateBtn");
  btn.disabled = true;
  setStatus("Preparing meeting minutes…", "spin");
  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Generation failed.");
    currentResult = data;
    renderResults(data);
    setStatus("Done — mode: " + (data.mode || "unknown"), "ok");
  } catch (err) {
    setStatus(err.message, "error");
  } finally {
    btn.disabled = false;
  }
});

/* ---------- Render ---------- */
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = String(text);
  return div.innerHTML;
}

function renderResults(result) {
  const decisions = result.decisions || [];
  const actions = result.action_items || [];

  const actionsRows = actions
    .map(
      (a) => `<tr>
        <td>${escapeHtml(a.task)}</td>
        <td class="owner">${escapeHtml(a.owner)}</td>
        <td class="due">${escapeHtml(a.due)}</td>
      </tr>`
    )
    .join("");

  const decisionsHtml = decisions.length
    ? `<ul class="result-list">${decisions.map((d) => `<li>${escapeHtml(d)}</li>`).join("")}</ul>`
    : "<p>None detected.</p>";

  const actionsHtml = actions.length
    ? `<div class="table-wrap"><table>
        <thead><tr><th>Task</th><th>Owner</th><th>Due</th></tr></thead>
        <tbody>${actionsRows}</tbody>
      </table></div>`
    : "<p>No action items were detected.</p>";

  $("results").innerHTML = `
    <div class="result-block">
      <h4>📋 Executive summary</h4>
      <p>${escapeHtml(result.summary || "No summary was extracted.")}</p>
    </div>
    <div class="result-block">
      <h4>⚖️ Key decisions</h4>
      ${decisionsHtml}
    </div>
    <div class="result-block">
      <h4>✅ Action items</h4>
      ${actionsHtml}
      <p class="hint" style="margin:12px 0 0">Review names, dates and tasks before sharing — AI output is a starting point, not the final word.</p>
    </div>
    <div class="result-block">
      <h4>⬇️ Export</h4>
      <div class="export-row">
        <button class="btn" id="downloadMd" type="button">Download Markdown (.md)</button>
        <button class="btn" id="downloadDocx" type="button">Download Word (.docx)</button>
      </div>
    </div>`;

  $("downloadMd").addEventListener("click", () => downloadMarkdown(result));
  $("downloadDocx").addEventListener("click", () => downloadDocx(result));
}

/* ---------- Export ---------- */
function downloadMarkdown(result) {
  const lines = [
    `# Meeting Minutes — ${currentTitle}`,
    "",
    "## Executive Summary",
    "",
    result.summary || "",
    "",
    "## Key Decisions",
    "",
  ];
  const decisions = result.decisions || [];
  lines.push(...(decisions.length ? decisions.map((d) => `- ${d}`) : ["- No explicit decisions detected."]));
  lines.push("", "## Action Items", "", "| Task | Owner | Due |", "|---|---|---|");
  const actions = result.action_items || [];
  if (actions.length) {
    actions.forEach((a) => {
      const clean = (v) => String(v || "Not specified").replace(/\|/g, "\\|").replace(/\n/g, " ");
      lines.push(`| ${clean(a.task)} | ${clean(a.owner)} | ${clean(a.due)} |`);
    });
  } else {
    lines.push("| — | — | — |");
  }
  const blob = new Blob([lines.join("\n") + "\n"], { type: "text/markdown" });
  triggerDownload(blob, "meeting_minutes.md");
}

async function downloadDocx(result) {
  try {
    setStatus("Building Word document…", "spin");
    const res = await fetch("/api/export/docx", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: currentTitle, result }),
    });
    if (!res.ok) throw new Error("Word export failed.");
    const blob = await res.blob();
    triggerDownload(blob, "meeting_minutes.docx");
    setStatus("", "");
  } catch (err) {
    setStatus(err.message, "error");
  }
}

function triggerDownload(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}