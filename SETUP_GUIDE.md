# Offline Text-to-SQL Tool — Complete Setup Guide

This guide takes you from a blank laptop to a working offline AI tool that
turns plain-English questions into SQL queries and runs them against your
own CSV files — no internet required after setup, no API keys, no cost.

Follow the steps **in order**. Each step builds on the last.

---

## What you're building

```
You type a question in a Streamlit web page
        |
        v
Your question + CSV column names are sent to a local AI model (via Ollama)
        |
        v
The model returns a SQL query
        |
        v
DuckDB runs that SQL query against your actual CSV file
        |
        v
Streamlit displays the result as a table
```

Everything after the initial one-time model download happens on your own
machine. Nothing is sent over the internet.

---   

## Step 1 — Install Python (skip if already installed)

Check if you have it:
```bash
python3 --version
```
You need 3.9 or higher. If missing, install from https://www.python.org/downloads/

---

## Step 2 — Install Ollama

Ollama is the program that runs AI models locally and exposes them through
a small local API on your machine.

**Windows / Mac / Linux:** Download and install from https://ollama.com/download

After installing, confirm it works:
```bash
ollama --version
```

---

## Step 3 — Download a model

This is a one-time download. Once downloaded, no internet is needed to use it.

```bash
ollama pull llama3.2
```

This downloads a small, capable model (~2GB). It will take a few minutes
depending on your internet speed — this is the only step that needs internet.

**Alternative model (often better at code/SQL specifically):**
```bash
ollama pull qwen2.5-coder:3b
```

You can have multiple models downloaded and switch between them later.

---

## Step 4 — Start Ollama running in the background

```bash
ollama serve
```

Leave this running in its own terminal window. This is what creates the
local API your Python code will talk to. (On Mac/Windows, the Ollama app
often starts this automatically — if `ollama serve` says the address is
already in use, it's already running, which is fine.)

**Quick test — open a second terminal and run:**
```bash
ollama run llama3.2
```
Type a question like "what is 2+2" and confirm you get a response. Type
`/bye` to exit. If this works, Ollama is fully functional.

---

## Step 5 — Set up your project folder

Create a new folder anywhere on your laptop, e.g. `texttosql-project`, and
place these three files inside it (provided alongside this guide):

- `pipeline.py` — the core logic (schema reading, prompt building, SQL execution)
- `app.py` — the Streamlit interface
- `requirements.txt` — list of Python packages needed
- `sample_data.csv` — a small test file to try things out with

---

## Step 6 — Create a virtual environment (recommended)

This keeps your project's packages separate from the rest of your system.

```bash
cd texttosql-project
python3 -m venv venv
```

Activate it:
- **Mac/Linux:** `source venv/bin/activate`
- **Windows:** `venv\Scripts\activate`

You'll see `(venv)` appear at the start of your terminal line when it's active.

---

## Step 7 — Install the required Python packages

```bash
pip install -r requirements.txt
```

This installs: `duckdb`, `streamlit`, `pandas`, `ollama` (the Python client
library, separate from the Ollama application itself).

---

## Step 8 — Run the app

```bash
streamlit run app.py
```

This opens a browser tab automatically (usually at `http://localhost:8501`).

---

## Step 9 — Test it

1. Upload `sample_data.csv` using the file uploader
2. You should see a preview table with 8 rows (products, prices, ratings, categories)
3. In the question box, type: **"which products have a rating above 4.5?"**
4. Click **Run**
5. You should see:
   - The generated SQL query displayed
   - A results table with 3 products (Yoga Mat, Running Shoes, Resistance Bands)

If this works, your full offline pipeline is functioning correctly.

---

## Step 10 — Try your own questions

Some examples to try on the sample data:
- "what is the average price by category?"
- "show me all products under $20"
- "which category has the most products?"

Try uploading your own CSV files too — any CSV with clear column headers
should work.

---

## Troubleshooting

**"Connection refused" or similar error calling Ollama**
→ Make sure `ollama serve` is running in a terminal (Step 4).

**The generated SQL looks wrong or doesn't match the question**
→ Smaller models sometimes make mistakes, especially with complex questions.
   Try rephrasing more simply, or try the `qwen2.5-coder` model instead of
   `llama3.2` — it's specifically trained on code-related tasks.

**"Module not found" errors**
→ Make sure your virtual environment is activated (you should see `(venv)`
   in your terminal) and that you ran `pip install -r requirements.txt`
   inside it.

**The app is slow to respond**
→ This is normal on first use — the model loads into memory once, then
   subsequent questions are faster. If your laptop has a lower-end CPU and
   no dedicated GPU, expect each question to take a few seconds to a
   couple of minutes; this is real local inference, not a hung process.

---

## What to put on your CV / GitHub once this works

1. Push this project to a new GitHub repo (e.g. `text-to-sql-offline`)
2. Write a short README explaining what it does, the architecture diagram
   above, and how to run it
3. Record a short screen recording or a few screenshots showing a question
   being asked and the SQL + result appearing
4. CV bullet example (only once it's genuinely working and pushed):
   *"Built an offline text-to-SQL tool using DuckDB, Streamlit, and a
   locally-run LLM (via Ollama), translating plain-English questions into
   SQL queries executed entirely on-device with no internet dependency."*

---

## What comes next — Phase 2 (your own fine-tuned model)

This guide builds **Phase 1**: a working pipeline using an existing general
model (llama3.2 or qwen2.5-coder) as the translator. Once this is solid and
working, Phase 2 is fine-tuning your own small model specifically for SQL
generation using LoRA — a separate, bigger project, with its own dedicated
guide when you're ready to start it. Nothing from Phase 1 gets thrown away;
Phase 2 simply swaps which model sits inside the `call_llm` function.
