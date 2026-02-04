# CAPM Study Hub

An evidence-based study tool for the **CAPM (Certified Associate in Project Management)** certification exam.

## Purpose

This app helps you **own and breathe** the PMBOK material through active learning techniques proven by cognitive science research:

- **Retrieval Practice** - Testing yourself beats re-reading
- **Spaced Repetition** - SM-2 algorithm schedules reviews at optimal intervals
- **Interleaving** - Mixed practice builds discrimination skills
- **Elaborative Interrogation** - Every card explains WHY, not just WHAT

## Features

| Feature | Description |
|---------|-------------|
| **Flashcards** | 365+ cards across 16 decks with SM-2 spaced repetition |
| **Quizzes** | 240+ scenario-based questions weighted by ECO domains |
| **Study Schedule** | Daily planning with 90-min/day goal and streak tracking |
| **Video Tracking** | PM PrepCast curriculum integration (85 lessons) |
| **Progress Dashboard** | ECO domain readiness scores and KPIs |
| **Study Guides** | Comprehensive notes for all PMBOK 8th Edition domains |

## ECO Domain Coverage

The CAPM exam tests four domains:

| Domain | Weight | Coverage |
|--------|--------|----------|
| PM Fundamentals & Core Concepts | 36% | Principles, Life Cycles, Glossary |
| Predictive, Plan-Based Methodologies | 17% | Scope, Schedule, Cost, Risk, etc. |
| Agile Frameworks/Methodologies | 20% | Scrum, Kanban, XP, Lean |
| Business Analysis Frameworks | 27% | Requirements, Elicitation, Solution Design |

## Quick Start

### Prerequisites

- Python 3.10+
- **PMBOK Guide 8th Edition PDF** (see note below)

### Installation

```bash
git clone https://github.com/Tanoxz/CAPM_study_hub.git
cd CAPM_study_hub
pip install -r app/requirements.txt
```

### Running the App

**Windows:** Double-click `start_study.bat`

**Manual:**
```bash
cd app
streamlit run app.py
```

Browser opens automatically to http://localhost:8501

## Important: PMBOK PDF Not Included

The **PMBOK Guide 8th Edition PDF** is required for the extraction script but is **not included** in this repository.

**Why?** The PMBOK Guide is copyrighted by PMI (Project Management Institute). Your purchase grants personal use only - redistribution would violate copyright and PMI's terms of service.

**To use this app:**
1. Purchase the PMBOK Guide from [PMI.org](https://www.pmi.org/)
2. Place the PDF in the project root as `pmbokguide_eighthed_eng.pdf`
3. The study guides are already extracted and included - you only need the PDF if you want to re-run extraction

## Project Structure

```
CAPM_study_hub/
├── app/                    # Streamlit application
│   ├── app.py              # Main app
│   ├── eco_domains.py      # ECO domain mappings (single source of truth)
│   ├── flashcards.py       # SM-2 spaced repetition
│   ├── quizzes.py          # Quiz system with interleaving
│   └── schedule.py         # Study planning
├── data/
│   ├── flashcards/         # 16 JSON flashcard decks
│   ├── quizzes/            # 12 JSON quiz banks
│   ├── schedule/           # Progress and plan data
│   └── prepcast/           # Video curriculum tracking
├── study-guides/           # Markdown study materials
│   └── pmbok/              # PMBOK 8th Edition by domain
└── start_study.bat         # Windows launcher
```

## Learning Science

This app is designed around research from cognitive psychology. See `study-guides/00-learning-science.md` for the evidence behind:

- Why testing > re-reading (Roediger & Karpicke, 2006)
- Why spacing > cramming (Cepeda et al., 2006)
- Why interleaving > blocking (Rohrer & Taylor, 2007)
- Why "why" questions deepen learning (Pressley et al., 1987)

## License

This project is for personal educational use. The PMBOK Guide and related PMI materials are property of the Project Management Institute.

---

*Built with Streamlit and evidence-based learning principles.*
