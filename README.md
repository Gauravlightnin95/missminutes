# missminutes — Automated Meeting Minutes Generator (PSID 103)

This is an AI/ML project which helps in generating meeting minutes from the transcript provided by the attendee of the meeting. It converts raw meeting transcripts (pasted, or transcribed from audio with OpenAI Whisper) into a clean **executive summary**, a list of **key decisions**, and a table of **action items** with owners and due dates.

**Author:** Gaurav Kumar (2400321530077) · ABES Engineering College · Mentor: Dr Amit Bhatnagar
**Programme:** HCLTech Career Shaper Programme — III Year Industry Project 2025-26

## Features

- 📋 **Paste-transcript mode** — paste any meeting transcript and generate minutes in one click (works offline, no API key needed).
- 🎙️ **Audio mode** — upload a meeting recording (WAV/MP3/M4A) and transcribe it locally with OpenAI Whisper.
- 🤖 **GPT mode** — with an OpenAI API key, minutes are written by GPT (`gpt-4o-mini`, JSON mode) for best quality.
- 🔌 **Offline fallback** — a built-in rule-based extractor works with no key and no internet, so the app never fails.
- 🖥️ **Custom frontend** — a designed "MinutesMate" dark UI (hero header, cards, mode chip, styled result blocks), not the default Streamlit look.
- 📄 **Export** — download the minutes as Markdown (`.md`) or Word (`.docx`).

## How It Works

```
Paste transcript ──────────────┐
                              ├──► [Whisper (optional, local)] ──► cleaned transcript
Upload audio (wav/mp3/m4a) ───┘                                            │
                                                                           v
                                            [Minutes engine] ◄── OpenAI API key (optional)
                                             │         │
                                  GPT mode   │         │  Offline mode (regex rules)
                                             ▼         ▼
                                  Executive summary • Key decisions • Action items table
                                             │
                                             ▼
                                  [MinutesMate UI] ──► Download .md / .docx
```

1. **Input** — a transcript is pasted, or audio is transcribed locally with Whisper (`tiny`/`base`/`small`).
2. **Generation** — the transcript is sent to GPT with a strict JSON prompt; without a key, a rule-based extractor (sentence segmentation + pattern matching for commitments, owners and dates) is used instead.
3. **Output** — structured minutes shown in the custom-designed UI, downloadable as `.md` / `.docx`.

## Quick Start

```bash
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Then: paste a transcript (or click **Load sample transcript**) and press **✨ Generate Minutes**.

- **No API key?** Everything still works — the app automatically uses offline mode.
- **Have a key?** Paste it in the sidebar (or copy `.env.example` to `.env` and set `OPENAI_API_KEY`) for higher-quality minutes.
- **Audio upload** needs Whisper: `python -m pip install openai-whisper torch` (heavy — install only if you need audio mode).

## Requirements

- Laptop with 8 GB RAM (Whisper `base` uses ~1 GB RAM; CPU-only is fine)
- Python 3.10+
- Whisper, GPT (optional), Python — as per the project minimum requirements

## Project Structure

| File | Purpose |
|---|---|
| `app.py` | MinutesMate Streamlit web app (custom frontend: input, results, export) |
| `minutes_generator.py` | Minutes engine — GPT JSON mode + offline rule-based fallback |
| `transcribe.py` | Optional local Whisper speech-to-text wrapper |
| `requirements.txt` | Python dependencies |
| `sample_transcript.txt` | Sample meeting transcript for testing |
| `HOW_TO_RUN.md` | Step-by-step run instructions (simple language) |
| `.env.example` | Template for the optional OpenAI API key |
| `.gitignore` | Keeps secrets and audio files out of version control |

## Note

AI-generated minutes are a starting point — always review before sharing. No transcript data leaves your machine unless you enable GPT mode. Get permission before recording or sharing meeting content.