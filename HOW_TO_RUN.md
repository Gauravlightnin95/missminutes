# How to Run missminutes — Simple Steps (PSID 103)

A proper web app: **HTML/CSS/JavaScript frontend + Python Flask backend**. No Streamlit anywhere.

## What you need
- A laptop with 8 GB RAM (normal Windows/Mac/Linux laptop is fine)
- Python 3.10 or newer installed (check with: `python --version`)
- A modern browser (Chrome / Edge / Firefox)
- Internet for installing the Python packages (about 50 MB)
- Optional: an OpenAI API key for GPT-quality minutes. Without it, the app runs locally in offline mode — no key, no internet, no cost.

## Step 1 — Get the project
Download the ZIP from GitHub: open https://github.com/Gauravlightnin95/missminutes, click the green **Code** button, then **Download ZIP**, and extract it. Or clone it:

```bash
git clone https://github.com/Gauravlightnin95/missminutes.git
cd missminutes
```

## Step 2 — Open a terminal in the project folder
On **Windows**: open the extracted folder, click in the address bar, type `cmd`, press Enter.
On **Mac/Linux**: open Terminal and use `cd` to go into the folder.

## Step 3 — Install the required libraries (one time, 2–3 minutes)
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Step 4 — Start the web server
```bash
python app.py
```
You will see: `MinutesMate running at http://127.0.0.1:5000`

## Step 5 — Open the frontend
Open your browser and go to: **http://127.0.0.1:5000**

The MinutesMate web page loads — this is the HTML/CSS/JS frontend served by Flask.

## Step 6 — Generate minutes
1. Type a meeting title (e.g., "Weekly Product Sync").
2. In the **Paste transcript** tab, click **Load sample transcript** (or paste your own).
3. Click **✨ Generate Minutes**.
4. The right side shows the executive summary, key decisions and the action-items table (built by JavaScript from the JSON the backend returns).
5. Click **Download Markdown** or **Download Word** to save the minutes.

## Optional: use GPT for better quality
1. Get a key from https://platform.openai.com/api-keys
2. On the page, open **⚙️ Optional settings**, paste the key in "OpenAI API key", and the mode chip switches from OFFLINE MODE to GPT MODE.
   (Alternative: copy `.env.example` to a new file named `.env`, set `OPENAI_API_KEY=your-key-here`, save, and restart the server.)
3. Keep the key private — never commit `.env` to GitHub.

## Optional: transcribe a recording with Whisper
Whisper + PyTorch is a big download (~2 GB). Install it only if you want audio upload:
```bash
python -m pip install openai-whisper torch
```
Then restart the server (`python app.py`), open the **🎙️ Upload audio** tab, choose a recording, pick the **tiny** or **base** model (best for 8 GB RAM laptops), and click **Transcribe audio**. The first run downloads the Whisper model; CPU transcription can take longer than the audio duration.

## How the frontend and backend talk (for your understanding)
- You click **Generate Minutes** in the browser.
- JavaScript (`static/js/app.js`) sends a REST request to `POST /api/generate` on the Flask server.
- Flask (`app.py`) runs the minutes engine (`minutes_generator.py`) — GPT or offline rules.
- The backend replies with JSON; JavaScript renders the summary, decisions and action-items table in the page. No page reload.
- Download buttons: `.md` is built fully in JavaScript; `.docx` is built by the backend at `POST /api/export/docx`.

## Common problems and fixes
- **`python` is not recognized** → install Python 3.10+ from python.org and tick "Add Python to PATH", then reopen the terminal.
- **`pip install` fails** → run `python -m pip install --upgrade pip` first.
- **Page doesn't open** → make sure `python app.py` is still running in the terminal, then refresh the browser; use http://127.0.0.1:5000 exactly.
- **Port 5000 already in use** → run the app on another port: `python -c "import app; app.app.run(host='127.0.0.1', port=5001)"` and open http://127.0.0.1:5001
- **Whisper error "not installed"** → run `python -m pip install openai-whisper torch`, or use the paste-transcript tab instead.
- **To stop the server** → press `Ctrl + C` in the terminal.

## Privacy
- Offline mode: the transcript is processed only on your computer.
- GPT mode: transcript text is sent to the OpenAI API for processing.
- Get permission before recording a meeting, and review AI output before sharing.