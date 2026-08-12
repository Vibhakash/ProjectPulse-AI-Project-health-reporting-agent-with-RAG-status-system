<h1 align="center">🚀 ProjectPulse AI</h1>
<h3 align="center">Health Reporting Agent & RAG Status System</h3>

<p align="center">
  <img src="https://readme-typing-svg.demolab.com?font=Fira+Code&size=18&pause=1200&color=764BA2&center=true&vCenter=true&width=750&lines=Deterministic+RAG+Scoring+%2B+LLM+Narrative+Insights;Multi-Sheet+Excel+Ingestion+%E2%86%92+Auditable+Health+Reports;Interactive+Gantt+Charts+%7C+Historical+Trend+Tracking;One-Click+Premium+PDF+Executive+Reports" alt="Typing SVG"/>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/></a>
  <a href="https://nodejs.org/"><img src="https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=nodedotjs&logoColor=white"/></a>
  <a href="https://projectpulse-ai-project-health-reporting.onrender.com"><img src="https://img.shields.io/badge/Backend-Render-46E3B7?style=flat-square&logo=render&logoColor=white"/></a>
  <a href="https://project-pulse-ai-project-health-rep.vercel.app/"><img src="https://img.shields.io/badge/Frontend-Vercel-000000?style=flat-square&logo=vercel&logoColor=white"/></a>
  <a href="./LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=flat-square"/></a>
  <img src="https://img.shields.io/badge/PRs-Welcome-brightgreen?style=flat-square"/>
</p>

<p align="center">
  <img src="https://skillicons.dev/icons?i=python,fastapi,react,nodejs,sqlite,js,html,css,vercel,git,github" alt="Tech stack icons"/>
</p>

<p align="center"><i>An intelligent project-health reporting &amp; RAG synthesis agent — it parses messy multi-sheet Excel schedules, computes a deterministic RAG score, layers LLM-derived stakeholder sentiment and narrative summaries on top, and presents it all in a modern React dashboard with historical trends and premium PDF exports.</i></p>

---

## 📑 Table of Contents

- [📖 Overview](#overview)
  - [🎯 The Problem](#the-problem)
  - [💡 The Solution](#the-solution)
- [🌟 Core Features](#features)
- [🏗️ System Architecture](#architecture)
- [🔄 Workflow / Data Pipeline](#workflow)
- [🛠️ Tech Stack](#tech-stack)
- [🎬 Demo](#demo)
- [📦 Deliverables Map](#deliverables)
- [⚙️ Getting Started](#getting-started)
- [▶️ Running the Application](#running)
- [🚀 Deployment](#deployment)
- [🧩 Design Decisions & Architecture Rationale](#design-decisions)
- [📄 License](#license)
- [👩‍💻 Author](#author)

---

<a name="overview"></a>
## 📖 Overview

<a name="the-problem"></a>
### 🎯 The Problem

Traditional project status reporting is manual, subjective, and disconnected. Health calls depend on whoever compiled the spreadsheet that week, stakeholder sentiment buried in free-text comment cells goes unread, and by the time an executive summary lands on someone's desk there's no way to trace **why** a project was marked Red, Amber, or Green.

<a name="the-solution"></a>
### 💡 The Solution

ProjectPulse AI splits **scoring** and **storytelling** into two separate jobs:

1. A **deterministic rule engine** reads the evidence — schedule health, progress gaps, milestone status, blockers, sentiment, budget — and computes an auditable RAG score first.
2. An **LLM layer** then turns that computed evidence into an executive-ready narrative: key drivers, top risks, and recommendations.

Every score traces back to a source row, a task comment, or a signal — nothing is a black box.

---

<a name="features"></a>
## 🌟 Core Features

| Feature | What it does |
|---|---|
| 🎯 **Dynamic RAG Scoring Engine** | Deterministic rule engine computing schedule health, unmitigated risks, and milestone slips into an auditable RAG score |
| 🤖 **AI Agent Insights** | LLM-powered narrative generation — Key Drivers, Top Risks, and Recommendations — grounded in the rule engine's signals |
| 📈 **Historical Trend Tracking** | Groups snapshots over time and visualizes RAG trajectory via an interactive Recharts line graph |
| 📊 **Interactive Gantt Charts** | Visual timeline of every task, highlighting baseline drift and schedule slippage |
| 🌐 **Multi-Language Sentiment Analysis** | Detects, translates, and incorporates non-English stakeholder comments (e.g., French) into sentiment summaries |
| 📄 **Premium PDF Exports** | One-click, polished, offline executive reports built with ReportLab, matching the dashboard's aesthetic |
| 🗂️ **Robust Bulk Ingestion** | Drop in `.zip` archives spanning multiple weeks — processed entirely in-memory, bypassing file-lock issues |

---

<a name="architecture"></a>
## 🏗️ System Architecture

<p align="center">
  <img src="docs/system_architecture.png" alt="System Architecture Diagram" width="90%"/>
</p>

---

<a name="workflow"></a>
## 🔄 Workflow / Data Pipeline

<p align="center">
  <img src="docs/data_pipeline.png" alt="Data Pipeline Diagram" width="90%"/>
</p>

---

<a name="tech-stack"></a>
## 🛠️ Tech Stack

<table>
<tr><td><b>Backend</b></td><td>
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white"/>
</td></tr>
<tr><td><b>Frontend</b></td><td>
<img src="https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
<img src="https://img.shields.io/badge/Node.js-339933?style=for-the-badge&logo=nodedotjs&logoColor=white"/>
</td></tr>
<tr><td><b>Data Visualization</b></td><td>
<img src="https://img.shields.io/badge/Recharts-22B5BF?style=for-the-badge"/>
</td></tr>
<tr><td><b>Reporting</b></td><td>
<img src="https://img.shields.io/badge/ReportLab-CC3333?style=for-the-badge"/>
</td></tr>
<tr><td><b>Database</b></td><td>
<img src="https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white"/>
</td></tr>
<tr><td><b>Deployment</b></td><td>
<img src="https://img.shields.io/badge/Vercel-000000?style=for-the-badge&logo=vercel&logoColor=white"/>
<img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=white"/>
</td></tr>
<tr><td><b>Tooling</b></td><td>
<img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"/>
<img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/>
</td></tr>
</table>

---

<a name="demo"></a>
## 🎬 Demo

> 🎥 A full walkthrough — **`Zycus-ProjectPulse AI-by Vibha Kashyap.mp4`** — is available in the project folder locally.
>
> It isn't committed to this repository because it's **~172 MB**, over GitHub's 100 MB per-file limit. Everything else — source code, docs, sample inputs, generated reports, and the runnable app — lives in this repo. Share the video separately, or host it via **Git LFS**, an unlisted YouTube upload, or cloud storage, then link it here.

<!--
Add real screenshots once available, then uncomment:
<p align="center">
  <img src="docs/screenshots/dashboard.png" alt="Dashboard Screenshot" width="80%"/>
</p>
-->

---

<a name="deliverables"></a>
## 📦 Deliverables Map

| # | Deliverable | Location |
|---|---|---|
| 1 | Features & Tech Stack | [`Features and techstack.md`](./Features%20and%20techstack.md) |
| 2 | One-Page RAG Methodology | [`docs/rag_methodology.md`](./docs/rag_methodology.md) — also browsable in-app under the **Methodology** tab |
| 3 | Working AI Agent (Code + Instructions) | See [Getting Started](#getting-started) below |
| 4 | Sample Test Data Generator | Run `python generate_test_data.py` → produces a `Test_Suite.zip` exercising Gantt, Trends, Multi-language, and more |
| 5 | Final Monthly Presentation (6 slides, 16:9) | [`outputs/monthly/monthly_project_health.pptx`](./outputs/monthly/monthly_project_health.pptx) |

> ℹ️ **Note:** the original file paths pointed to a local `C:\Users\...` machine location, which only resolves on that one computer. The links above use repo-relative paths instead, so they'll work correctly once pushed to GitHub — just make sure each file lives at that path relative to the repo root.

---

<a name="getting-started"></a>
## ⚙️ Getting Started

### Prerequisites

<img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=flat-square&logo=python&logoColor=white"/> <img src="https://img.shields.io/badge/Node.js-18+-339933?style=flat-square&logo=nodedotjs&logoColor=white"/>

### 1. Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install -e .
```

### 2. Frontend Setup

```bash
cd frontend
npm install
```

---

<a name="running"></a>
## ▶️ Running the Application

| Terminal | Command | Runs on |
|---|---|---|
| **1 — Backend (FastAPI)** | `cd backend && .venv\Scripts\python run_api.py` | `http://localhost:8001` |
| **2 — Frontend (Dev Server)** | `cd frontend && npm run dev` | `http://localhost:3000` |

Then open **[http://localhost:3000](http://localhost:3000)** in your browser. 🎉

---

<a name="deployment"></a>
## 🚀 Deployment

| Layer | Platform | Live URL |
|---|---|---|
| **Backend — FastAPI** | [![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white)](https://projectpulse-ai-project-health-reporting.onrender.com) | [projectpulse-ai-project-health-reporting.onrender.com](https://projectpulse-ai-project-health-reporting.onrender.com) |
| **Frontend — React** | [![Vercel](https://img.shields.io/badge/Vercel-000000?style=flat-square&logo=vercel&logoColor=white)](https://project-pulse-ai-project-health-rep.vercel.app/) | [project-pulse-ai-project-health-rep.vercel.app](https://project-pulse-ai-project-health-rep.vercel.app/) |

The frontend's `VITE_API_BASE_URL` environment variable is set to the live Render backend URL so the two services communicate in production.

---

<a name="design-decisions"></a>
## 🧩 Design Decisions & Architecture Rationale

<details>
<summary><b>1. Deterministic RAG First, LLM Second</b></summary>
<br>

The final Red, Amber, or Green status is calculated by a deterministic weighted rule engine in `src/project_health/rag_engine.py`, rather than asking an LLM to infer project health directly from spreadsheets.

This is intentional: executive status reporting needs traceability. The scoring model uses inspectable signals — schedule health, progress gap, milestone health, blockers, stakeholder sentiment, and budget availability. The LLM layer is used only *after* these signals are computed, turning the evidence into executive summaries, risk themes, and next-step recommendations.
</details>

<details>
<summary><b>2. Evidence-Based Reporting</b></summary>
<br>

The system preserves source row numbers, parsed task details, inline task comments, warnings, and signal-level reasoning — making each RAG decision auditable instead of a black-box summary.

SQLite is the persistence layer because it's lightweight, portable, and easy for reviewers to inspect. It stores project snapshots, tasks, comments, RAG signals, and data quality issues, so weekly reports and monthly synthesis can be regenerated from the same evidence base.
</details>

<details>
<summary><b>3. Resilient Excel Ingestion & Grouping</b></summary>
<br>

The Excel parser is built for messy project-plan exports: it detects useful sheets and columns from workbook content, normalizes inconsistent field names, handles missing or malformed values, reconstructs WBS hierarchy from level/ancestor fields, and explicitly extracts inline comments from task rows.

The database schema (`UNIQUE(name)`) intentionally groups uploads by their internal **Project Name** rather than filename, letting the system merge `Week1.xlsx`, `Week2.xlsx`, and `Week3.xlsx` into one unified chronological timeline for trend tracking.
</details>

<details>
<summary><b>4. Frontend and Backend Separation</b></summary>
<br>

The backend owns ingestion, scoring, persistence, report generation, and synthesis via FastAPI. The React frontend focuses on uploading project plans, browsing portfolio health, rendering interactive Gantt and Trend charts, and navigating generated insights.

This split keeps the analytical logic reusable across CLI, API, scheduler, or dashboard workflows.
</details>

---

<a name="license"></a>
## 📄 License

This project is licensed under the **[MIT License](./LICENSE)**.

```
MIT License — Copyright (c) 2026 Vibha Kashyap

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software.
```

---

<a name="author"></a>
## 👩‍💻 Author

**Vibha Kashyap** — B.Tech AIML Student
<!-- Add your GitHub / LinkedIn / portfolio links here, e.g.:
[![GitHub](https://img.shields.io/badge/GitHub-181717?style=flat-square&logo=github&logoColor=white)](your-link)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](your-link)
-->

---

<p align="center"><i>✨ Because project status shouldn't be a guessing game — deterministic where it matters, intelligent where it helps. ✨</i></p>

<hr/>
