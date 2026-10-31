# missminutes — Automated Meeting Minutes Generator (PSID 103)

This is an AI/ML project which helps in generating meeting minutes from the transcript provided by the attendee of the meeting. It converts raw meeting transcripts (pasted, or transcribed from audio with OpenAI Whisper) into a clean **executive summary**, a list of **key decisions**, and a table of **action items** with owners and due dates.

**Author:** Gaurav Kumar (2400321530077) · ABES Engineering College · Mentor: Dr Amit Bhatnagar
**Programme:** HCLTech Career Shaper Programme — III Year Industry Project 2025-26

## Architecture

Proper client–server web application (no Streamlit):

- **Frontend:** HTML5 + CSS3 + vanilla JavaScript single-page app (`templates/index.html`, `static/css/style.css`, `static/js/app.js`) — custom-designed "MinutesMate" dark UI with tabs, cards, mode chip, result blocks and a styled action-items table. JavaScript talks to the backend using `fetch` REST calls, no page reloads.
- **Backend:** Python **Flask** REST API (`app.py`) with endpoints:
  - `GET /` — serves the frontend page
  - `GET /api/sample` — bundled sample transcript
  - `POST /api/generate` — transcript in → summary, decisions, action items (JSON) out
  - `POST /api/transcribe` — audio file in → Whisper transcript (local)
  - `POST /api/export/docx` — minutes in → Word .docx download
- **Minutes engine:** `minutes_generator.py` — GPT (`gpt-4o-mini`, JSON mode) when an OpenAI key is set, with an automatic **offline rule-based extractor** (sentence segmentation + regex commitment/date detection) so the app always works with no key and no internet.
- **Speech-to-text (optional):** `transcribe.py` — OpenAI Whisper running locally (MIT licence).

```
 [HTML5/CSS3/JS frontend]  ──fetch/REST──►  [Flask backend]  ──►  [Minutes engine]
        MinutesMate SPA                          app.py            GPT / offline rules
                                                       │
                                                       ▼
                                            [Whisper (optional, local)]
```

## Features

- 📋 **Paste-transcript mode** — paste any meeting transcript and generate minutes in one click (works offline, no API key needed).
- 🎙️ **Audio mode** — upload a meeting recording (WAV/MP3/M4A) and transcribe it locally with OpenAI Whisper.
- 🤖 **GPT mode** — with an OpenAI API key, minutes are written by GPT (`gpt-4o-mini`, JSON mode) for best quality.
- 🔌 **Offline fallback** — a built-in rule-based extractor works with no key and no internet, so the app never fails.
- 🖥️ **Custom frontend** — a designed dark UI (hero header, cards, mode chip, styled result blocks), built with real HTML/CSS/JS.
- 📄 **Export** — download the minutes as Markdown (`.md`) or Word (`.docx`).

## Quick Start

```bash
python -m pip install -r requirements.txt
python app.py
```

Then open **http://127.0.0.1:5000** in your browser, paste a transcript (or click **Load sample transcript**) and press **✨ Generate Minutes**.

- **No API key?** Everything still works — the app automatically uses offline mode.
- **Have a key?** Paste it in the frontend's "Optional settings" (or copy `.env.example` to `.env` and set `OPENAI_API_KEY`) for higher-quality minutes.
- **Audio upload** needs Whisper: `python -m pip install openai-whisper torch` (heavy — install only if you need audio mode).

## Requirements

- Laptop with 8 GB RAM (Whisper `base` uses ~1 GB RAM; CPU-only is fine)
- Python 3.10+
- Whisper, GPT (optional), Python — as per the project minimum requirements
- A modern browser (Chrome / Edge / Firefox)

## Project Structure

| File | Purpose |
|---|---|
| `app.py` | Flask REST backend + web server (serves frontend, all API endpoints) |
| `templates/index.html` | Frontend page (HTML5 semantic structure) |
| `static/css/style.css` | Custom-designed frontend theme (CSS3) |
| `static/js/app.js` | Frontend logic (JavaScript: fetch REST calls, rendering, exports) |
| `minutes_generator.py` | Minutes engine — GPT JSON mode + offline rule-based fallback |
| `transcribe.py` | Optional local Whisper speech-to-text wrapper |
| `requirements.txt` | Python dependencies |
| `sample_transcript.txt` | Sample meeting transcript for testing |
| `HOW_TO_RUN.md` | Step-by-step run instructions (simple language) |
| `.env.example` | Template for the optional OpenAI API key |
| `.gitignore` | Keeps secrets and audio files out of version control |

## Note

AI-generated minutes are a starting point — always review before sharing. No transcript data leaves your machine unless you enable GPT mode. Get permission before recording or sharing meeting content.