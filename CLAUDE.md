# CAPM Study Project

## Project Purpose

This project helps Mister DragonFox prepare for and pass the CAPM (Certified Associate in Project Management) certification exam.

**Goal:** Own and breathe the PMBOK material, understand concepts deeply (not just memorize), and pass the 150-question multiple-choice exam.

**Design Philosophy:** Reusable framework - can be reconfigured for PMP or other certifications in the future.

## Project Structure

```
PM/
├── study-guides/           # Consolidated markdown study materials
│   ├── 00-learning-science.md      # Evidence-based learning research
│   ├── 01-capm-overview.md
│   ├── 02-twelve-pm-principles.md
│   ├── 03-exam-prep-tips.md
│   ├── 04-study-resources.md
│   └── pmbok/                       # PMBOK 8th Edition by Performance Domain
│       ├── 00_toc.md
│       ├── 01_principles_management.md
│       ├── 02_life_cycles_management.md
│       ├── 03_governance_management.md
│       ├── 04_scope_management.md
│       ├── 05_schedule_management.md
│       ├── 06_finance_management.md
│       ├── 07_stakeholders_management.md
│       ├── 08_resources_management.md
│       ├── 09_risk_management.md
│       ├── 10_tailoring_management.md
│       ├── 11_tools_techniques_management.md
│       ├── 12_procurement_management.md
│       └── 13_glossary_management.md
├── data/
│   ├── flashcards/         # JSON flashcard decks (16 decks, 325 cards)
│   │   ├── pm_fundamentals.json
│   │   ├── principles_domain.json
│   │   ├── life_cycles_domain.json
│   │   ├── governance_domain.json
│   │   ├── scope_domain.json
│   │   ├── schedule_domain.json
│   │   ├── finance_domain.json
│   │   ├── stakeholders_domain.json
│   │   ├── resources_domain.json
│   │   ├── risk_domain.json
│   │   ├── tailoring_domain.json
│   │   ├── tools_domain.json
│   │   ├── procurement_domain.json
│   │   ├── glossary_domain.json
│   │   ├── agile_domain.json            # ECO Domain 3 (60 cards)
│   │   └── business_analysis_domain.json # ECO Domain 4 (20 cards)
│   ├── quizzes/            # Quiz question banks (12 quizzes, 240 questions)
│   │   ├── governance_quiz.json
│   │   ├── scope_quiz.json
│   │   ├── schedule_quiz.json
│   │   ├── finance_quiz.json
│   │   ├── stakeholders_quiz.json
│   │   ├── resources_quiz.json
│   │   ├── risk_quiz.json
│   │   ├── tailoring_quiz.json
│   │   ├── tools_quiz.json
│   │   ├── procurement_quiz.json
│   │   ├── agile_quiz.json              # ECO Domain 3 (20 questions)
│   │   ├── business_analysis_quiz.json  # ECO Domain 4 (20 questions)
│   │   └── results.json         # Quiz history
│   ├── schedule/           # Study schedule system
│   │   ├── config.json          # Exam date, goals (90min/day)
│   │   ├── topics.json          # Topic registry
│   │   ├── plan.json            # Generated week-based study plan
│   │   ├── daily_plan.json      # Daily study plan (90min/day, no empty days)
│   │   └── progress.json        # Reading progress, sessions, streaks
│   ├── prepcast/           # PM PrepCast video tracking
│   │   └── lessons.json         # 85 lessons (56 core, 29 optional)
│   └── tidbits.json        # Random PMBOK facts for Home page
├── app/                    # Streamlit application for interactive study
│   ├── app.py              # Main Streamlit app
│   ├── eco_domains.py      # SINGLE SOURCE OF TRUTH for ECO domain mappings
│   ├── flashcards.py       # SM-2 spaced repetition implementation
│   ├── quizzes.py          # Quiz system with interleaving
│   ├── schedule.py         # Study schedule system
│   └── requirements.txt
├── docs/
│   └── schedule-feature-design.md  # Full Schedule feature specification
├── scripts/
│   └── extract_pmbok.py    # PDF extraction script
├── archive/
│   └── raw/                # Original scraped files and source materials
├── start_study.bat         # One-click launcher for Windows
├── pmbokguide_eighthed_eng.pdf  # PMBOK 8th Edition source
└── CLAUDE.md               # This file
```

## Quick Start

Double-click `start_study.bat` to launch the app. Browser opens automatically to http://localhost:8501.

## Key Decisions

- **Format:** Markdown files for study materials
- **Tech Stack:** Python + Streamlit for interactive features (flashcards, quizzes, schedule)
- **PMBOK Organization:** By Performance Domain (PMBOK 8th Edition structure)
- **No GitHub:** Files sync via Proton Drive - be careful not to break working features
- **Focus:** Understanding over memorization - every flashcard has "why_it_matters", every quiz explains WHY the answer is correct
- **Reusability:** Designed to be reconfigurable for future certifications (PMP, etc.)

## Learning Science Principles (Evidence-Based Design)

See `study-guides/00-learning-science.md` for full research. Core principles applied:

### 1. Retrieval Practice (Active Recall)
- Never show answer immediately - require mental retrieval first
- Testing IS learning, not just assessment

### 2. Spaced Repetition
- Cards you struggle with appear more often
- Mastered cards fade to longer intervals
- No cramming - spread sessions over time

### 3. Interleaving
- Mix Knowledge Areas in quizzes (don't block by topic)
- Forces discrimination between concepts

### 4. Elaborative Interrogation
- Ask "WHY does this work?" not just "WHAT is this called?"
- Connect concepts to real scenarios
- Explanations link new info to existing knowledge

### 5. Generation (Productive Struggle)
- Attempt answer BEFORE seeing solution
- Struggle primes deeper encoding

### 6. Bloom's Taxonomy Alignment
- CAPM tests Remember, Understand, Apply levels
- Include scenario-based questions (Apply level)
- Don't just test definitions - test application

### What to Memorize vs. Understand
| Memorize | Understand Deeply |
|----------|-------------------|
| PMI vocabulary/terms | WHY processes exist |
| Key formulas (EVA, CP) | HOW areas relate |
| Process inputs/outputs | WHEN to use approaches |
| The 12 principles | Scenario judgment |

### Avoid These (Ineffective)
- Re-reading without testing
- Highlighting
- Cramming
- Blocking (same topic repeatedly)

## CAPM Exam Quick Facts

- 150 multiple-choice questions (15 are pretest/unscored)
- 3 hours duration
- Based on PMBOK Guide
- Pass mark not published (aim for 75-80% on practice)
- No PM experience required

## Content Sources

- PMBOK Guide 8th Edition (primary - Domains 1 & 2)
- PMI Agile Practice Guide (ECO Domain 3 - Agile Frameworks)
- PMI Business Analysis Practitioner's Guide (ECO Domain 4 - BA Frameworks)
- PM PrepCast for CAPM - 23h mandatory video curriculum (external)
- Web-scraped study tips and guidance (archived in raw/)

## Work Guidelines

- Always test changes locally before considering them "done"
- Keep study content accurate to PMBOK - don't invent or assume
- Flashcards should test understanding, not just recall
- Quiz questions should mirror CAPM exam style (scenario-based where appropriate)
- When extracting from PMBOK PDF, organize by Knowledge Area

## Completed Work

1. ~~Extract and convert PMBOK PDF content to markdown~~ - Done (13 sections in study-guides/pmbok/)
2. ~~Build Streamlit app skeleton~~ - Done (app.py, flashcards.py, quizzes.py, schedule.py)
3. ~~Create flashcard system~~ - Done (SM-2 spaced repetition, 16 decks, 320 cards with "why_it_matters")
4. ~~Create quiz system~~ - Done (12 quizzes, 240 scenario-based questions with explanations)
5. ~~One-click launcher~~ - Done (start_study.bat)
6. ~~Random tidbits on Home page~~ - Done (50 PMBOK facts with sources)
7. ~~Schedule feature design~~ - Done (see docs/schedule-feature-design.md)
8. ~~Schedule Phase 1~~ - Done (exam countdown, reading progress checkboxes, smart recommendations)
9. ~~Schedule Phase 2~~ - Done (Study Guides page with progress tracking, session logging)
10. ~~Schedule Phase 3~~ - Done (auto-generated study plan, week view UI, activity completion tracking)
11. ~~Schedule Phase 4~~ - Done (smart recommendations, flashcards only for read chapters)
12. ~~Schedule Phase 5~~ - Done (session logging, streak tracking, enhanced Progress page)
13. ~~Schedule Phase 6~~ - Done (visual progress bars, plan adjustment, export data)
14. ~~PM PrepCast Integration~~ - Done (23h video tracking, 85 lessons, ECO domain mapping)
15. ~~Daily Study Plan~~ - Done (90min/day, no empty days, Watch→Read→Flashcards→Quiz flow)
16. ~~ECO Domain 3 Content~~ - Done (Agile Practice Guide: 20 flashcards + 20 quiz questions)
17. ~~ECO Domain 4 Content~~ - Done (BA Practitioner's Guide: 20 flashcards + 20 quiz questions)
18. ~~Home Page KPI Dashboard~~ - Done (ECO Domain Readiness scores, Study Progress KPIs, exam countdown)
19. ~~Interleaving Features~~ - Done (Mixed deck flashcards, quiz modes: ECO weighted/weak areas/random)
20. ~~Progress Page Enhancements~~ - Done (ECO Domains tab, Videos tab with detailed breakdowns)
21. ~~EVM Foundation Cards~~ - Done (PV, EV, AC, SPI, SV added to finance_domain.json)

## Schedule Feature - COMPLETE

## PM PrepCast Integration - COMPLETE

Integrated the 23-hour mandatory PM PrepCast video curriculum:

- **85 lessons** tracked (56 core = 23h, 29 optional = 11h)
- **ECO Domain mapping** - lessons tagged by exam domain (36% Fundamentals, 17% Predictive, 20% Agile, 27% BA)
- **Progress tracking** - mark videos watched, track completion percentage
- **Daily study plan** - 90 min/day, every day has activities, no empty days
- **Learning flow** - Watch → Read → Flashcards → Quiz sequence

### Key Files
- `data/prepcast/lessons.json` - Full curriculum with status tracking
- `data/schedule/daily_plan.json` - Day-by-day activities (auto-generated)
- `data/schedule/config.json` - Updated to 90min/day goal

### CAPM Exam Content Outline (ECO) Alignment

The CAPM exam is based on the ECO, NOT the PMBOK Guide directly:

| Domain | Weight | PrepCast Modules |
|--------|--------|------------------|
| PM Fundamentals & Core Concepts | 36% | M01-M05 |
| Predictive, Plan-Based Methodologies | 17% | M06, M08, M09 |
| Agile Frameworks/Methodologies | 20% | M07, M11 |
| Business Analysis Frameworks | 27% | M10 |

See `docs/schedule-feature-design.md` for full specification.

### Phase 1: Foundation (Data & Basic UI) - COMPLETE
- [x] Create `data/schedule/` directory structure
- [x] Create `config.json`, `topics.json` with CAPM data
- [x] Create `progress.json` skeleton
- [x] Add "Schedule" nav item
- [x] Basic Schedule page with streak and daily minutes
- [x] Setup modal for exam date
- [x] Reading progress checkboxes (moved to Study Guides page only)
- [x] Smart recommendations (due flashcards, weak areas, quiz frequency)

### Phase 2: Reading Integration - COMPLETE
- [x] Add reading progress tracking to Study Guides page
- [x] "Mark as Read" functionality
- [x] Reading session logging
- [x] Comprehension check prompt after reading

### Phase 3: Study Plan - COMPLETE
- [x] Plan generation algorithm
- [x] Create `plan.json`
- [x] Week view UI
- [x] Mark activities complete
- [x] Plan regeneration when exam date changes

### Phase 4: Smart Recommendations - COMPLETE
- [x] Implement recommendation algorithm
- [x] "Today's Focus" on Schedule page
- [x] Integration with existing flashcard due dates (only for read chapters)
- [x] Integration with quiz weak areas

### Phase 5: Tracking & Analytics - COMPLETE
- [x] Session logging for all activities (reading, flashcards, quizzes)
- [x] Streak tracking (auto-updates on activity)
- [x] Daily/weekly summaries (via session log)
- [x] Progress dashboard with metrics (tabs: Reading, Flashcards, Quizzes, Activity Log)

### Phase 6: Polish - COMPLETE
- [x] Visual progress indicators (progress bars for study & time)
- [x] Plan adjustment UI (reschedule/skip overdue activities)
- [x] Export progress data (JSON and TXT download)

## Future Enhancements (Post-Schedule)

- Formula practice module (interactive EVM calculations - cards added, drill mode pending)
- More quiz questions for comprehensive coverage
- Calendar sync (export to Google Calendar / iCal)
- Study timer (Pomodoro-style)
- Achievements/badges

## ECO Domain Architecture (IMPORTANT)

The `app/eco_domains.py` module is the **SINGLE SOURCE OF TRUTH** for all ECO domain mappings.

### Why This Matters
- Flashcards and quizzes use `knowledge_area` to categorize content
- Domain scores on the Home page depend on correct categorization
- Previously, mappings were duplicated across files with different defaults (BUG)

### Adding New Content
When adding new flashcards or quiz questions:
1. **CHECK** if your `knowledge_area` exists in `eco_domains.py`
2. **ADD IT** if missing (with correct domain 1-4)
3. **USE** the exact spelling from the mapping

### Domain Mapping Reference
| Domain | Weight | Content |
|--------|--------|---------|
| 1 | 36% | Fundamentals, Principles, Life Cycles, Glossary |
| 2 | 17% | PMBOK Performance Domains (Scope, Schedule, Finance, etc.) |
| 3 | 20% | Agile (Scrum, Kanban, XP, Lean, all Agile* areas) |
| 4 | 27% | Business Analysis (Requirements, Elicitation, etc.) |

### Validation
Run this to check for unmapped areas:
```python
cd app && python -c "from eco_domains import get_unmapped_areas; print(get_unmapped_areas())"
```

## PMBOK 8th Edition Performance Domains + ECO Domains

Note: PMBOK 8th Edition uses "Performance Domains" rather than the traditional "Knowledge Areas".
The CAPM exam tests ECO domains, which extend beyond PMBOK to include Agile and Business Analysis.

### PMBOK Performance Domains

| Domain | Flashcards | Quiz | Study Guide |
|--------|------------|------|-------------|
| Fundamentals | pm_fundamentals.json | - | - |
| Principles | principles_domain.json | - | 01_principles_management.md |
| Life Cycles | life_cycles_domain.json | - | 02_life_cycles_management.md |
| Governance | governance_domain.json | governance_quiz.json | 03_governance_management.md |
| Scope | scope_domain.json | scope_quiz.json | 04_scope_management.md |
| Schedule | schedule_domain.json | schedule_quiz.json | 05_schedule_management.md |
| Finance | finance_domain.json | finance_quiz.json | 06_finance_management.md |
| Stakeholders | stakeholders_domain.json | stakeholders_quiz.json | 07_stakeholders_management.md |
| Resources | resources_domain.json | resources_quiz.json | 08_resources_management.md |
| Risk | risk_domain.json | risk_quiz.json | 09_risk_management.md |
| Tailoring | tailoring_domain.json | tailoring_quiz.json | 10_tailoring_management.md |
| Tools & Techniques | tools_domain.json | tools_quiz.json | 11_tools_techniques_management.md |
| Procurement | procurement_domain.json | procurement_quiz.json | 12_procurement_management.md |
| Glossary | glossary_domain.json | - | 13_glossary_management.md |

### ECO-Specific Domains (Beyond PMBOK)

| ECO Domain | Weight | Flashcards | Quiz | Source |
|------------|--------|------------|------|--------|
| Domain 3: Agile | 20% | agile_domain.json | agile_quiz.json | Agile Practice Guide |
| Domain 4: Business Analysis | 27% | business_analysis_domain.json | business_analysis_quiz.json | BA Practitioner's Guide |

## Flashcard Design

Each flashcard includes:
- `question` - The concept being tested
- `answer` - Clear, concise answer
- `knowledge_area` - Topic/domain for organization
- `card_type` - "definition" or "why" (elaborative interrogation)
- `why_it_matters` - Deeper context for understanding, not just memorizing
- `related_concepts` - Links to build mental connections

SM-2 spaced repetition fields (managed by system):
- `easiness`, `interval`, `repetitions`, `next_review`

## Quiz Design

Each quiz question includes:
- `question` - Scenario-based or application-focused question
- `options` - 4 answer choices (A, B, C, D)
- `correct_answer` - Index of correct option (0-3)
- `explanation` - WHY the correct answer is correct (learning from mistakes)
- `knowledge_area` - Topic/domain
- `difficulty` - easy/medium/hard
- `question_type` - scenario/concept/application

## Schedule Feature Design Summary

See `docs/schedule-feature-design.md` for complete specification.

### Core Components

1. **Exam Countdown** - Set target date, see days remaining
2. **Auto-Generated Study Plan** - Distributes topics over available time
3. **Daily Tracker** - Time spent, activities, streaks
4. **Smart Recommendations** - "What to study today" based on due cards, weak areas, plan
5. **Reading Integration** - Track chapter progress, prompt comprehension checks

### Key Design Principle

**Reading isn't learning.** The system nudges users from passive reading toward active recall (flashcards, quizzes).

### Data Files

| File | Purpose |
|------|---------|
| `config.json` | Exam date, daily goals, preferences |
| `topics.json` | Topic registry mapping study materials (reusable across certs) |
| `plan.json` | Generated study schedule |
| `progress.json` | Reading progress, session logs, streaks |

### Recommendation Priority

1. Continue in-progress reading
2. Flashcards due (spaced repetition)
3. Overdue plan items
4. Weak areas from quiz results
5. Today's planned activities
6. Topics not touched in 7+ days
7. Next unread chapter

## Home Page KPI Dashboard

The Home page provides at-a-glance readiness metrics:

### ECO Domain Readiness Scores

Each of the 4 ECO domains gets a score (0-100%) based on:

**Score = Theoretical (50%) + Practical (50%)**

| Component | What it measures |
|-----------|------------------|
| **Theoretical Base** | Reading chapters complete + Videos watched |
| **Practical Application** | Flashcard mastery (≥21 day interval) + Quiz accuracy |

This ensures you both LEARN the material AND can RECALL it under test conditions.

### Study Progress KPIs

| Metric | Description |
|--------|-------------|
| Days Until Exam | Countdown from config.json exam date |
| Reading | X/Y study guide chapters completed |
| Videos (Core) | X/Y mandatory PrepCast lessons watched |
| Videos (Optional) | X/Y optional PrepCast lessons watched |

## Interleaving Features

Interleaving (mixing topics) builds discrimination skills - critical for exam success.

### Flashcards: Mixed Deck Mode

Select "**All Decks (Shuffled)**" to:
- Load due cards from ALL 16 decks
- Shuffle them together randomly
- Practice discrimination ("Is this a risk or stakeholder concept?")
- Cards save back to their original decks

### Quiz Modes

| Mode | Description |
|------|-------------|
| **ECO Weighted** | Matches exam distribution (36/17/20/27%) |
| **Focus on Weak Areas** | 70% from topics scoring <75%, 30% interleaved |
| **Random Interleaved** | Pure random shuffle across all domains |

## Progress Page Tabs

| Tab | Content |
|-----|---------|
| **ECO Domains** | Detailed domain breakdown, theoretical vs practical, smart recommendations |
| **Reading** | Chapter completion list with dates |
| **Videos** | PrepCast progress by ECO domain and module |
| **Flashcards** | Deck mastery rates with progress bars |
| **Quizzes** | Accuracy, weak areas, recent scores |
| **Activity Log** | Session history (last 20 activities) |
