"""MinutesMate — Automated Meeting Minutes Generator (PSID 103).

Streamlit web app that converts meeting transcripts (pasted or Whisper-transcribed audio)
into an executive summary, key decisions, and action items, using GPT or an offline
rule-based engine, with a custom-designed frontend.
"""
from __future__ import annotations

import os
import tempfile
from io import BytesIO
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from docx import Document

from minutes_generator import generate_minutes
from transcribe import transcribe_audio, WhisperUnavailableError

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

SAMPLE_PATH = BASE_DIR / "sample_transcript.txt"
SAMPLE_TRANSCRIPT = SAMPLE_PATH.read_text(encoding="utf-8") if SAMPLE_PATH.exists() else ""

st.set_page_config(
    page_title="MinutesMate | Automated Meeting Minutes Generator",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --------------------------------------------------------------------------- #
#  Custom frontend: MinutesMate theme (dark "meeting room" UI)                  #
# --------------------------------------------------------------------------- #
st.markdown(
    """
    <style>
      :root {
        --ink:#f2f5ff; --muted:#96a3c0; --blue:#4c7dff; --blue-soft:#22314f;
        --card:#0e1526; --line:#22304d; --green:#39cf91; --amber:#f4b63f;
      }
      .stApp {
        background:radial-gradient(ellipse at 85% -10%, #16264d 0%, #0a1120 55%, #070c17 100%);
        color:var(--ink);
      }
      .block-container { max-width:1150px; padding-top:1.2rem; padding-bottom:4rem; }
      html, body, [class*="css"] { font-family:'Segoe UI', Inter, ui-sans-serif, system-ui, sans-serif; }
      h1, h2, h3, p, label { color:var(--ink) !important; }
      code { color:#a9c0ff !important; }

      /* Top bar */
      .topbar { display:flex; justify-content:space-between; align-items:center;
          padding:0 4px 14px; border-bottom:1px solid rgba(90,110,150,.25); margin-bottom:4px; }
      .brand { font-size:14px; font-weight:800; letter-spacing:.14em; color:#fff; }
      .brand span { color:var(--blue); }
      .status { color:var(--muted); font-size:11px; letter-spacing:.06em; }
      .status i { display:inline-block; width:7px; height:7px; border-radius:50%;
          background:var(--green); margin:0 7px 1px 0; box-shadow:0 0 9px rgba(57,207,145,.7); }

      /* Hero */
      .hero { display:flex; align-items:center; gap:18px; margin:20px 0 26px; }
      .hero-icon { width:58px; height:58px; border:1px solid #2c4270; border-radius:16px;
          display:grid; place-items:center; font-size:29px;
          background:linear-gradient(145deg,#182c58,#101a32); }
      .eyebrow { color:#83a4ff; text-transform:uppercase; letter-spacing:.18em;
          font-size:10px; font-weight:800; margin-bottom:6px; }
      .hero-title { font:800 32px/1.15 'Segoe UI', ui-sans-serif, system-ui, sans-serif;
          letter-spacing:-.04em; margin:0; color:#fff; }
      .hero-sub { color:var(--muted); font-size:14px; margin:7px 0 0; }

      /* Cards / panels */
      .card { background:var(--card); border:1px solid var(--line); border-radius:18px;
          padding:22px 24px; margin:0 0 18px; }
      .card h3 { margin:0 0 4px; font-size:17px; font-weight:750; }
      .card .hint { color:var(--muted); font-size:12.5px; margin:0 0 14px; }
      .pill { display:inline-block; border:1px solid #2a4173; background:#111e39; color:#9bb5ff;
          padding:5px 11px; border-radius:99px; font-size:11px; font-weight:700;
          margin:0 6px 8px 0; }
      .mode-chip { display:inline-flex; align-items:center; gap:7px; border:1px solid #2a4173;
          background:#111e39; color:#9bb5ff; padding:6px 13px; border-radius:99px;
          font-size:11.5px; font-weight:700; }
      .mode-chip i { width:7px; height:7px; border-radius:50%; background:var(--amber); }

      /* Result blocks */
      .result-grid { display:grid; grid-template-columns:1fr 1fr; gap:18px; }
      .result-block { background:var(--card); border:1px solid var(--line); border-radius:18px;
          padding:20px 22px; }
      .result-block h4 { margin:0 0 10px; font-size:15px; font-weight:750; color:#e8eeff;
          display:flex; align-items:center; gap:8px; }
      .result-block p { color:#c8d3ec; font-size:13.5px; line-height:1.65; margin:0; }
      .result-list { margin:0; padding-left:20px; color:#c8d3ec; font-size:13.5px; line-height:1.75; }
      .result-list li { margin-bottom:4px; }

      /* Tables */
      div[data-testid="stDataFrame"] { border:1px solid var(--line); border-radius:14px; }

      /* Streamlit widgets */
      div.stButton > button, div[data-testid="stFormSubmitButton"] > button {
          border-radius:11px; font-weight:700; border-color:#2a3852;
          background:#111b2f; color:#e8eeff; min-height:42px; }
      div.stButton > button:hover, div[data-testid="stFormSubmitButton"] > button:hover {
          border-color:#638cff; background:#172849; color:#fff; }
      div[data-testid="stFormSubmitButton"] > button[kind="primary"], .stButton > button[kind="primary"] {
          background:linear-gradient(100deg,#3569f6,#5684ff); color:#fff; border:0;
          box-shadow:0 7px 22px rgba(55,105,246,.28); }
      div[data-testid="stTextInput"] input, div[data-testid="stTextArea"] textarea {
          border-radius:11px; background:#0a1221; color:#e6edff; border-color:#2a3852; font-size:13px; }
      [data-testid="stSidebar"] { background:#0a1120; border-right:1px solid var(--line); }
      [data-testid="stSidebar"] * { color:#d7e0f5; }
      [data-testid="stAlert"] { border-radius:12px; }
      [data-testid="stExpander"] { border-color:var(--line); border-radius:12px; background:#0b1425; }
      [data-testid="stExpander"] summary { color:#dbe5ff; font-weight:600; }
      footer { visibility:hidden; }
      [data-testid="stCaptionContainer"], [data-testid="stCaption"] { color:var(--muted); }
    </style>
    """,
    unsafe_allow_html=True,
)


def hero(icon: str, eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(
        f"""
        <div class="topbar">
          <div class="brand">MINUTES<span>/</span>MATE</div>
          <div class="status"><i></i>READY — PSID 103</div>
        </div>
        <div class="hero">
          <div class="hero-icon">{icon}</div>
          <div>
            <div class="eyebrow">{eyebrow}</div>
            <h1 class="hero-title">{title}</h1>
            <p class="hero-sub">{subtitle}</p>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


hero(
    "📝",
    "Automated Meeting Minutes Generator",
    "From raw transcript to ready minutes in one click",
    "Paste a transcript or upload a recording — get an executive summary, key decisions and a trackable action-item table.",
)

# --------------------------------------------------------------------------- #
#  Sidebar — settings                                                          #
# --------------------------------------------------------------------------- #
with st.sidebar:
    st.markdown('<p class="eyebrow">SETTINGS</p>', unsafe_allow_html=True)
    api_key = st.text_input(
        "OpenAI API key (optional)",
        value=os.getenv("OPENAI_API_KEY", ""),
        type="password",
        help="Leave blank for fully local, offline minutes generation.",
    )
    model = st.text_input("GPT model", value="gpt-4o-mini", disabled=not bool(api_key.strip()))
    st.markdown("---")
    st.markdown(
        '<div class="card" style="padding:14px 16px">'
        "<h3 style='font-size:13px'>How it works</h3>"
        "<p class='hint' style='margin:0;font-size:12px;line-height:1.6'>"
        "• Transcript stays on this laptop in offline mode.<br>"
        "• With a key, GPT writes higher-quality minutes.<br>"
        "• Audio is transcribed locally by Whisper (if installed).<br>"
        "• Export minutes as Markdown or Word.</p></div>",
        unsafe_allow_html=True,
    )

mode_chip = (
    '<span class="mode-chip"><i></i>GPT MODE</span>'
    if api_key.strip()
    else '<span class="mode-chip" style="color:#8fd9b4;border-color:#22573f;background:#0e1f2e">'
    "<i style='background:#39cf91'></i>OFFLINE MODE — no key, no internet, no cost</span>"
)
st.markdown(mode_chip, unsafe_allow_html=True)

# --------------------------------------------------------------------------- #
#  Left column — input                                                          #
# --------------------------------------------------------------------------- #
left, right = st.columns([1.15, 1], gap="large")

with left:
    st.markdown(
        """
        <div class="card">
          <h3>Meeting transcript</h3>
          <p class="hint">Choose how your meeting text gets in. Nothing is uploaded anywhere in offline mode.</p>
          <span class="pill">Paste text</span><span class="pill">Upload audio (Whisper)</span><span class="pill">Sample included</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    meeting_title = st.text_input("Meeting title", value="Weekly Product Sync")
    input_mode = st.radio("Transcript source", ["Paste transcript", "Upload audio"], horizontal=True)
    transcript = ""
    if input_mode == "Paste transcript":
        if st.button("Load sample transcript"):
            st.session_state["meeting_transcript"] = SAMPLE_TRANSCRIPT
        transcript = st.text_area(
            "Paste or edit transcript",
            value=st.session_state.get("meeting_transcript", SAMPLE_TRANSCRIPT),
            height=330,
            placeholder="e.g.\nPriya: Good morning everyone. Let's start the weekly sync…\nRahul: I will fix the login bug by Thursday.",
            key="meeting_transcript",
        )
    else:
        audio_file = st.file_uploader(
            "Choose a meeting recording",
            type=["wav", "mp3", "m4a", "mpeg", "mpga", "webm"],
        )
        col_m, col_l = st.columns(2)
        with col_m:
            whisper_model = st.selectbox("Whisper model", ["tiny", "base", "small"], index=1, help="tiny = fastest & lowest RAM")
        with col_l:
            language = st.text_input("Language (optional; e.g. en)", value="")
        if audio_file is not None and st.button("🎙️ Transcribe audio"):
            temp_path = None
            suffix = Path(audio_file.name).suffix or ".audio"
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp:
                    temp.write(audio_file.getvalue())
                    temp_path = temp.name
                with st.spinner("Transcribing locally with Whisper…"):
                    transcript = transcribe_audio(temp_path, model_name=whisper_model, language=language.strip() or None)
                st.session_state["meeting_transcript"] = transcript
                st.success("Transcription complete. Review the text before generating minutes.")
            except WhisperUnavailableError as exc:
                st.error(str(exc))
            except Exception as exc:
                st.error(f"Audio transcription failed: {exc}")
            finally:
                if temp_path and os.path.exists(temp_path):
                    os.remove(temp_path)
        transcript = st.text_area(
            "Review or edit transcript",
            value=st.session_state.get("meeting_transcript", ""),
            height=260,
            key="audio_transcript",
        )

    generate = st.button("✨ Generate Minutes", type="primary", use_container_width=True)

# --------------------------------------------------------------------------- #
#  Generate                                                                     #
# --------------------------------------------------------------------------- #
if generate:
    if not transcript.strip():
        st.warning("Please paste a transcript or transcribe an audio file first.")
    else:
        try:
            with st.spinner("Preparing meeting minutes…"):
                result = generate_minutes(
                    transcript,
                    api_key=api_key.strip() or None,
                    model=model.strip() or "gpt-4o-mini",
                    meeting_title=meeting_title.strip() or "Meeting Minutes",
                )
            st.session_state["minutes_result"] = result
            st.session_state["minutes_title"] = meeting_title.strip() or "Meeting Minutes"
        except Exception as exc:
            st.error(f"Could not generate minutes: {exc}")

result = st.session_state.get("minutes_result")

# --------------------------------------------------------------------------- #
#  Right column — results with custom frontend                                  #
# --------------------------------------------------------------------------- #
with right:
    if result:
        st.markdown(
            '<div class="card"><h3>Generated minutes</h3>'
            "<p class='hint'>Review names, dates and extracted tasks before sharing — "
            "AI output is a starting point, not the final word.</p></div>",
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="result-grid">
              <div class="result-block">
                <h4>📋 Executive summary</h4>
                <p>SUMMARY_PLACEHOLDER</p>
              </div>
              <div class="result-block">
                <h4>⚖️ Key decisions</h4>
                DECISIONS_PLACEHOLDER
              </div>
            </div>
            """.replace(
                "SUMMARY_PLACEHOLDER", (result.get("summary") or "No summary was extracted.").replace("\n", "<br>")
            ).replace(
                "DECISIONS_PLACEHOLDER",
                "<ul class='result-list'>"
                + "".join(f"<li>{d}</li>" for d in result.get("decisions", []))
                + "</ul>"
                if result.get("decisions")
                else "<p>None detected.</p>",
            ),
            unsafe_allow_html=True,
        )

        st.markdown(
            """
            <div class="result-block" style="margin-top:18px">
              <h4>✅ Action items</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )
        actions = result.get("action_items", [])
        if actions:
            st.dataframe(actions, use_container_width=True, hide_index=True)
        else:
            st.markdown("<p style='color:#96a3c0;font-size:13px'>No action items were detected.</p>", unsafe_allow_html=True)
        st.caption(f"Generation mode: {result.get('mode', 'unknown')}")
    else:
        st.markdown(
            """
            <div class="card">
              <h3>Your minutes will appear here</h3>
              <p class="hint">Fill in a transcript on the left and press <b>Generate Minutes</b>.</p>
              <span class="pill">Summary</span><span class="pill">Decisions</span><span class="pill">Action items</span><span class="pill">Export .md / .docx</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

# --------------------------------------------------------------------------- #
#  Exports                                                                      #
# --------------------------------------------------------------------------- #
if result:
    title = st.session_state.get("minutes_title", "Meeting Minutes")
    lines = [f"# Meeting Minutes — {title}", "", "## Executive Summary", "", result.get("summary", ""), "", "## Key Decisions", ""]
    lines.extend([f"- {x}" for x in result.get("decisions", [])] or ["- No explicit decisions detected."])
    lines.extend(["", "## Action Items", "", "| Task | Owner | Due |", "|---|---|---|"])
    for item in result.get("action_items", []):
        vals = [str(item.get(k, "Not specified")).replace("|", "\\|").replace("\n", " ") for k in ("task", "owner", "due")]
        lines.append("| " + " | ".join(vals) + " |")
    markdown = "\n".join(lines) + "\n"

    doc = Document()
    doc.add_heading(f"Meeting Minutes — {title}", 0)
    doc.add_heading("Executive Summary", level=1)
    doc.add_paragraph(result.get("summary", ""))
    doc.add_heading("Key Decisions", level=1)
    for decision in result.get("decisions", []) or ["No explicit decisions detected."]:
        doc.add_paragraph(decision, style="List Bullet")
    doc.add_heading("Action Items", level=1)
    table = doc.add_table(rows=1, cols=3)
    table.style = "Light Shading Accent 1"
    for cell, text in zip(table.rows[0].cells, ["Task", "Owner", "Due"]):
        cell.text = text
    for item in result.get("action_items", []):
        cells = table.add_row().cells
        cells[0].text = str(item.get("task", ""))
        cells[1].text = str(item.get("owner", "Not specified"))
        cells[2].text = str(item.get("due", "Not specified"))
    buffer = BytesIO()
    doc.save(buffer)

    c1, c2 = st.columns(2)
    c1.download_button("⬇️ Download Markdown (.md)", markdown, file_name="meeting_minutes.md", mime="text/markdown", use_container_width=True)
    c2.download_button("⬇️ Download Word (.docx)", buffer.getvalue(), file_name="meeting_minutes.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document", use_container_width=True)

st.markdown(
    "<p style='color:#96a3c0;font-size:11.5px;margin-top:26px'>Privacy: in offline mode the transcript is processed only on this "
    "computer. If an OpenAI key is set, transcript text is sent to the OpenAI API. Get permission before recording or sharing "
    "meeting content. — MinutesMate, PSID 103 (Gaurav Kumar · ABES Engineering College)</p>",
    unsafe_allow_html=True,
)