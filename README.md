# DuckBrain SQL

An elite, multi-table autonomous data analytics agent powered by **Qwen Cloud** (`qwen-plus`) and **DuckDB**. This application allows users to upload multiple relational datasets simultaneously, automatically profiles schema structures, suggests analytical queries, and processes complex multi-table joins—all protected by a strict security firewall and a human-in-the-loop verification gate.

---
## STREAMLIT LINK 

https://new-version-of-text-to-sql-maorm5edxb4e6ymu5ziotb.streamlit.app/

---
## 🌟 Key Features

* **Multi-CSV Relational Engine:** Upload 2 to 5 CSV files at once. DuckDB dynamically maps files into interactive database views.
* **Qwen Cloud Brainpower:** Leverages flagship-class cloud reasoning models for complex schema comprehension and join strategy formulation.
* **Human-in-the-Loop Gate (Track 4 Compliance):** The agent halts and displays generated SQL syntax for human approval before execution.
* **Security & Access Firewall:** Strictly blocks destructive commands (`DROP`, `DELETE`, `ALTER`, `UPDATE`) directly at the prompt level.
* **Local to Cloud Parity:** Fully compatible with local architectures and seamlessly deployable via Streamlit Community Cloud.

---

## 🛠️ Tech Stack

* **Frontend UI:** Streamlit (Custom Charcoal Theme)
* **LLM Orchestration:** Qwen Cloud API via OpenAI-compatible SDK
* **Database Engine:** DuckDB (In-memory, high-performance analytical engine)
* **Data Manipulation:** Pandas

---



