# How to Run missminutes — Simple Steps (PSID 103)

## What you need
- A laptop with 8 GB RAM (normal Windows/Mac/Linux laptop is fine)
- Python 3.10 or newer installed (check with: `python --version`)
- Internet for installing the Python packages (about 100 MB)
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

## Step 3 — Install the required libraries (one time, 2–5 minutes)
```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Step 4 — Run the app
```bash
python -m streamlit run app.py
```
Your browser opens automatically at **http://localhost:8501** with the MinutesMate app running.

## Step 5 — Generate minutes
1. Type a meeting title (e.g., "Weekly Product Sync").
2. In the "Paste transcript" tab, click **Load sample transcript** (or paste your own).
3. Click **✨ Generate Minutes**.
4. Read the summary, decisions and action items in the right panel.
5. Click **⬇️ Download Markdown** or **⬇️ Download Word** to save the minutes.

## Optional: use GPT for better quality
1. Get a key from https://platform.openai.com/api-keys
2. Copy `.env.example` to a new file named `.env`, open it, and set:
   ```
   OPENAI_API_KEY=your-key-here
   ```
   (Or simply paste the key in the app sidebar.)
3. Save and restart the app. Keep `.env` private — never commit it to GitHub.

## Optional: transcribe a recording with Whisper
Whisper + PyTorch is a big download (~2 GB). Install it only if you want audio upload:
```bash
python -m pip install openai-whisper torch
```
Then select **Upload audio**, choose a recording, pick the **tiny** or **base** model (best for 8 GB RAM laptops), and click **🎙️ Transcribe audio**. The first run downloads the Whisper model; CPU transcription can take longer than the audio duration.

## Common problems and fixes
- **`python` is not recognized** → install Python 3.10+ from python.org and tick "Add Python to PATH", then reopen the terminal.
- **`streamlit` is not recognized** → use `python -m streamlit run app.py` as shown above.
- **pip install fails** → run `python -m pip install --upgrade pip` first.
- **Whisper is slow / laptop lags** → choose the "tiny" model in the app, or paste the transcript instead.
- **Page does not open** → manually visit http://localhost:8501
- **Port already in use** → run `python -m streamlit run app.py --server.port 8502`

## Privacy
- Offline mode: the transcript is processed only on your computer.
- GPT mode: transcript text is sent to the OpenAI API for processing.
- Get permission before recording a meeting, and review AI output before sharing.