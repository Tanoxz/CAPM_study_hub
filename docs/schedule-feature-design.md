# Schedule Feature Design

## Overview

The Schedule feature provides structured study planning, progress tracking, and smart recommendations to guide effective exam preparation. Designed to be reusable across certifications (CAPM now, PMP later, etc.).

## Core Design Principles

1. **Reading isn't learning** - Push users from passive reading toward active recall (flashcards, quizzes)
2. **Evidence-based progression** - Read → Flashcards → Quiz for each topic
3. **Flexibility** - Exam date can be set/changed anytime; plan adjusts
4. **Reusability** - Topic registry is configurable per certification
5. **Low friction** - Smart recommendations reduce decision fatigue

---

## Data Models

### 1. Schedule Configuration (`data/schedule/config.json`)

Stores exam settings and user preferences.

```json
{
  "version": 1,
  "certification": "CAPM",
  "exam_date": "2026-03-17",
  "exam_date_confirmed": false,
  "target_weeks": 8,
  "daily_goal_minutes": 30,
  "weekly_goal_days": 5,
  "created": "2026-01-17T10:00:00",
  "updated": "2026-01-17T10:00:00"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `certification` | string | Current cert being studied (CAPM, PMP, etc.) |
| `exam_date` | date/null | Target exam date, null if not set |
| `exam_date_confirmed` | bool | True if exam is actually booked |
| `target_weeks` | int | Fallback study duration if no exam date |
| `daily_goal_minutes` | int | Daily study time goal |
| `weekly_goal_days` | int | Days per week goal (for streak calculation) |

---

### 2. Topic Registry (`data/schedule/topics.json`)

Maps topics to their study materials. This is the key to reusability - swap this file for a different certification.

```json
{
  "version": 1,
  "certification": "CAPM",
  "source": "PMBOK 8th Edition",
  "topics": [
    {
      "id": "principles",
      "name": "PM Principles",
      "description": "The 12 guiding principles of project management",
      "study_guide": "01_principles_management.md",
      "flashcard_deck": "principles_domain.json",
      "quiz_bank": null,
      "estimated_read_minutes": 45,
      "priority": 1,
      "prerequisites": [],
      "order": 1
    },
    {
      "id": "life_cycles",
      "name": "Project Life Cycles",
      "description": "Predictive, adaptive, and hybrid approaches",
      "study_guide": "02_life_cycles_management.md",
      "flashcard_deck": "life_cycles_domain.json",
      "quiz_bank": null,
      "estimated_read_minutes": 40,
      "priority": 1,
      "prerequisites": ["principles"],
      "order": 2
    },
    {
      "id": "governance",
      "name": "Governance",
      "description": "Project governance, charter, and change control",
      "study_guide": "03_governance_management.md",
      "flashcard_deck": "governance_domain.json",
      "quiz_bank": "governance_quiz.json",
      "estimated_read_minutes": 50,
      "priority": 1,
      "prerequisites": ["principles"],
      "order": 3
    },
    {
      "id": "scope",
      "name": "Scope Management",
      "description": "WBS, requirements, scope control",
      "study_guide": "04_scope_management.md",
      "flashcard_deck": "scope_domain.json",
      "quiz_bank": "scope_quiz.json",
      "estimated_read_minutes": 55,
      "priority": 1,
      "prerequisites": ["governance"],
      "order": 4
    },
    {
      "id": "schedule",
      "name": "Schedule Management",
      "description": "Critical path, PERT, compression techniques",
      "study_guide": "05_schedule_management.md",
      "flashcard_deck": "schedule_domain.json",
      "quiz_bank": "schedule_quiz.json",
      "estimated_read_minutes": 60,
      "priority": 1,
      "prerequisites": ["scope"],
      "order": 5
    },
    {
      "id": "finance",
      "name": "Finance/Cost Management",
      "description": "Budgeting, EVM, cost control",
      "study_guide": "06_finance_management.md",
      "flashcard_deck": "finance_domain.json",
      "quiz_bank": "finance_quiz.json",
      "estimated_read_minutes": 55,
      "priority": 1,
      "prerequisites": ["schedule"],
      "order": 6
    },
    {
      "id": "stakeholders",
      "name": "Stakeholder Management",
      "description": "Identification, engagement, communication",
      "study_guide": "07_stakeholders_management.md",
      "flashcard_deck": "stakeholders_domain.json",
      "quiz_bank": "stakeholders_quiz.json",
      "estimated_read_minutes": 45,
      "priority": 1,
      "prerequisites": ["principles"],
      "order": 7
    },
    {
      "id": "resources",
      "name": "Resource Management",
      "description": "Team development, RACI, resource leveling",
      "study_guide": "08_resources_management.md",
      "flashcard_deck": "resources_domain.json",
      "quiz_bank": "resources_quiz.json",
      "estimated_read_minutes": 50,
      "priority": 1,
      "prerequisites": ["stakeholders"],
      "order": 8
    },
    {
      "id": "risk",
      "name": "Risk Management",
      "description": "Identification, analysis, response strategies",
      "study_guide": "09_risk_management.md",
      "flashcard_deck": "risk_domain.json",
      "quiz_bank": "risk_quiz.json",
      "estimated_read_minutes": 55,
      "priority": 1,
      "prerequisites": ["scope"],
      "order": 9
    },
    {
      "id": "tailoring",
      "name": "Tailoring",
      "description": "Adapting processes to project context",
      "study_guide": "10_tailoring_management.md",
      "flashcard_deck": null,
      "quiz_bank": null,
      "estimated_read_minutes": 30,
      "priority": 2,
      "prerequisites": ["life_cycles"],
      "order": 10
    },
    {
      "id": "tools",
      "name": "Tools & Techniques",
      "description": "Common PM tools and techniques",
      "study_guide": "11_tools_techniques_management.md",
      "flashcard_deck": null,
      "quiz_bank": null,
      "estimated_read_minutes": 40,
      "priority": 2,
      "prerequisites": [],
      "order": 11
    },
    {
      "id": "procurement",
      "name": "Procurement Management",
      "description": "Contracts, vendor management",
      "study_guide": "12_procurement_management.md",
      "flashcard_deck": null,
      "quiz_bank": null,
      "estimated_read_minutes": 35,
      "priority": 2,
      "prerequisites": ["risk"],
      "order": 12
    },
    {
      "id": "glossary",
      "name": "Glossary & Terms",
      "description": "Key PM terminology",
      "study_guide": "13_glossary_management.md",
      "flashcard_deck": null,
      "quiz_bank": null,
      "estimated_read_minutes": 20,
      "priority": 3,
      "prerequisites": [],
      "order": 13
    }
  ]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique topic identifier |
| `name` | string | Display name |
| `study_guide` | string/null | Filename in study-guides/pmbok/ |
| `flashcard_deck` | string/null | Filename in data/flashcards/ |
| `quiz_bank` | string/null | Filename in data/quizzes/ |
| `estimated_read_minutes` | int | Estimated reading time |
| `priority` | int | 1=core, 2=important, 3=supplementary |
| `prerequisites` | array | Topic IDs that should be studied first |
| `order` | int | Recommended study order |

---

### 3. Study Plan (`data/schedule/plan.json`)

Auto-generated study schedule. Regenerated when exam date changes.

```json
{
  "version": 1,
  "generated": "2026-01-17T10:00:00",
  "exam_date": "2026-03-17",
  "total_weeks": 8,
  "weeks": [
    {
      "week_number": 1,
      "start_date": "2026-01-20",
      "end_date": "2026-01-26",
      "theme": "Foundations",
      "topics": ["principles", "life_cycles"],
      "activities": [
        {
          "id": "w1_a1",
          "type": "read",
          "topic_id": "principles",
          "target_date": "2026-01-20",
          "status": "pending",
          "completed_date": null
        },
        {
          "id": "w1_a2",
          "type": "flashcards",
          "topic_id": "principles",
          "target_date": "2026-01-21",
          "status": "pending",
          "completed_date": null
        },
        {
          "id": "w1_a3",
          "type": "read",
          "topic_id": "life_cycles",
          "target_date": "2026-01-22",
          "status": "pending",
          "completed_date": null
        },
        {
          "id": "w1_a4",
          "type": "flashcards",
          "topic_id": "life_cycles",
          "target_date": "2026-01-23",
          "status": "pending",
          "completed_date": null
        },
        {
          "id": "w1_a5",
          "type": "review",
          "topic_id": null,
          "description": "Review week's flashcards",
          "target_date": "2026-01-25",
          "status": "pending",
          "completed_date": null
        }
      ]
    }
  ],
  "final_week": {
    "week_number": 8,
    "theme": "Final Review",
    "activities": [
      {"type": "quiz", "description": "Full practice exam simulation"},
      {"type": "review", "description": "Focus on weak areas"},
      {"type": "review", "description": "Light review, rest before exam"}
    ]
  }
}
```

| Activity Type | Description |
|---------------|-------------|
| `read` | Read the study guide for a topic |
| `flashcards` | Complete flashcard session for a topic |
| `quiz` | Take quiz (single topic or mixed) |
| `review` | General review / catch-up |

---

### 4. Progress Tracking (`data/schedule/progress.json`)

Tracks all study activity, reading status, and streaks.

```json
{
  "version": 1,
  "updated": "2026-01-17T15:30:00",

  "reading_progress": {
    "principles": {
      "status": "completed",
      "started_at": "2026-01-17T10:00:00",
      "completed_at": "2026-01-17T10:45:00",
      "time_spent_minutes": 45,
      "comprehension_checked": true,
      "notes": ""
    },
    "governance": {
      "status": "in_progress",
      "started_at": "2026-01-17T14:00:00",
      "completed_at": null,
      "time_spent_minutes": 20,
      "comprehension_checked": false,
      "notes": ""
    }
  },

  "sessions": [
    {
      "id": "sess_20260117_001",
      "timestamp": "2026-01-17T10:00:00",
      "type": "reading",
      "topic_id": "principles",
      "duration_minutes": 45,
      "details": {}
    },
    {
      "id": "sess_20260117_002",
      "timestamp": "2026-01-17T11:00:00",
      "type": "flashcards",
      "topic_id": "principles",
      "duration_minutes": 15,
      "details": {
        "cards_reviewed": 20,
        "cards_correct": 16
      }
    },
    {
      "id": "sess_20260117_003",
      "timestamp": "2026-01-17T14:00:00",
      "type": "reading",
      "topic_id": "governance",
      "duration_minutes": 20,
      "details": {}
    }
  ],

  "streaks": {
    "current_streak": 5,
    "longest_streak": 12,
    "last_study_date": "2026-01-17",
    "streak_history": [
      {"start": "2026-01-13", "end": "2026-01-17", "days": 5}
    ]
  },

  "daily_summary": {
    "2026-01-17": {
      "total_minutes": 80,
      "sessions_count": 3,
      "activities": ["reading", "flashcards"],
      "topics_touched": ["principles", "governance"],
      "goal_met": true
    }
  },

  "weekly_summary": {
    "2026-W03": {
      "total_minutes": 180,
      "days_studied": 4,
      "topics_completed": ["principles"],
      "quizzes_taken": 1,
      "average_quiz_score": 0.75
    }
  }
}
```

---

## UI Design

### Navigation

Add "Schedule" to sidebar navigation (between "Study Guides" and "Flashcards"):

```
Home
Study Guides
Schedule        <-- NEW
Flashcards
Quiz
Progress
```

### Schedule Page - Main View

```
┌─────────────────────────────────────────────────────────────┐
│  SCHEDULE                                          [⚙ Setup]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   59 days   │  │  🔥 5 days  │  │  80 min     │         │
│  │  until exam │  │   streak    │  │   today     │         │
│  │  Mar 17     │  │             │  │  Goal: 30   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  TODAY'S FOCUS                           [Refresh]          │
│                                                             │
│  ┌─ Recommended ────────────────────────────────────────┐  │
│  │ 📖 Continue reading: Governance (20 min in)          │  │
│  │    [Continue Reading]                                 │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ 🎴 12 flashcards due                                 │  │
│  │    Principles (8) • Governance (4)                   │  │
│  │    [Start Review]                                    │  │
│  ├──────────────────────────────────────────────────────┤  │
│  │ ⚠️  Weak area: Risk Management (62% quiz accuracy)   │  │
│  │    [Review Flashcards] [Take Quiz]                   │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│  THIS WEEK (Week 3 of 8)                    [View Full Plan]│
│                                                             │
│  Mon   Tue   Wed   Thu   Fri   Sat   Sun                   │
│  ────  ────  ────  ────  ────  ────  ────                  │
│   ✓     ✓     ✓    📖    🎴    📝    ─                     │
│  done  done  done  read  cards quiz  rest                  │
│                    Gov.  Gov.  mixed                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Schedule Setup Modal/Page

```
┌─────────────────────────────────────────────────────────────┐
│  STUDY PLAN SETUP                                    [Close]│
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Certification: CAPM                                        │
│                                                             │
│  Exam Date                                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ [📅 March 17, 2026    ]  ☐ Exam is booked           │   │
│  │                                                      │   │
│  │ Or study for: [8 weeks ▼] without specific date     │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  Daily Goals                                                │
│  ┌─────────────────────────────────────────────────────┐   │
│  │ Study time:    [30] minutes/day                      │   │
│  │ Days per week: [5 ]                                  │   │
│  └─────────────────────────────────────────────────────┘   │
│                                                             │
│  [Generate Study Plan]                                      │
│                                                             │
│  ⚠️  Changing exam date will regenerate your study plan.   │
│     Progress tracking is preserved.                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Full Study Plan View

```
┌─────────────────────────────────────────────────────────────┐
│  STUDY PLAN                                          [Back] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Week 1: Foundations (Jan 20-26)               ████████ 100%│
│  ├─ ✓ Read: PM Principles                                  │
│  ├─ ✓ Flashcards: PM Principles                            │
│  ├─ ✓ Read: Life Cycles                                    │
│  ├─ ✓ Flashcards: Life Cycles                              │
│  └─ ✓ Review                                               │
│                                                             │
│  Week 2: Core Planning (Jan 27 - Feb 2)        ██████░░ 75% │
│  ├─ ✓ Read: Governance                                     │
│  ├─ ✓ Flashcards: Governance                               │
│  ├─ ◐ Read: Scope (in progress)                            │
│  ├─ ○ Flashcards: Scope                                    │
│  └─ ○ Quiz: Governance + Scope                             │
│                                                             │
│  Week 3: Schedule & Cost (Feb 3-9)             ░░░░░░░░ 0%  │
│  ├─ ○ Read: Schedule Management                            │
│  ├─ ○ Flashcards: Schedule Management                      │
│  ...                                                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Reading Page Enhancement

After marking a chapter complete, show comprehension prompt:

```
┌─────────────────────────────────────────────────────────────┐
│  ✓ Chapter Complete: Governance                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Great! You've finished reading the Governance chapter.     │
│                                                             │
│  Reading isn't learning - test your understanding:          │
│                                                             │
│  [🎴 Start Governance Flashcards]                           │
│                                                             │
│  [📝 Take Governance Quiz]                                  │
│                                                             │
│  [Skip for now]                                             │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Smart Recommendations Algorithm

"What to study today" uses this priority order:

```python
def get_recommendations():
    recommendations = []

    # 1. Continue in-progress reading (highest priority - finish what you started)
    if has_in_progress_reading():
        recommendations.append(in_progress_reading)

    # 2. Flashcards due today (spaced repetition is time-sensitive)
    due_cards = get_due_flashcards()
    if due_cards:
        recommendations.append(due_cards_by_topic)

    # 3. Overdue plan activities (you're falling behind)
    overdue = get_overdue_activities()
    if overdue:
        recommendations.append(overdue)

    # 4. Weak areas from quiz results (need reinforcement)
    weak_areas = get_weak_areas(threshold=0.70)
    if weak_areas:
        recommendations.append(weak_area_review)

    # 5. Today's planned activities
    today_plan = get_today_activities()
    if today_plan:
        recommendations.append(today_plan)

    # 6. Topics not touched in 7+ days (prevent forgetting)
    stale_topics = get_stale_topics(days=7)
    if stale_topics:
        recommendations.append(stale_review)

    # 7. Next unread chapter (make progress)
    next_chapter = get_next_unread()
    if next_chapter:
        recommendations.append(next_chapter)

    return recommendations[:5]  # Show top 5 max
```

---

## Plan Generation Algorithm

```python
def generate_study_plan(exam_date, topics, config):
    """
    Distributes topics across available weeks.

    Principles:
    - Priority 1 topics get more time
    - Respect prerequisites
    - Pattern: Read → Flashcards → (Quiz if available)
    - Final week is review only
    - Balance workload across days
    """

    weeks_available = calculate_weeks(today, exam_date)

    # Reserve final week for review
    study_weeks = weeks_available - 1

    # Sort topics by order (respects prerequisites)
    ordered_topics = sort_by_order(topics)

    # Group into weeks
    topics_per_week = ceil(len(ordered_topics) / study_weeks)

    plan = []
    for week_num, topic_group in enumerate(chunk(ordered_topics, topics_per_week)):
        week = {
            "week_number": week_num + 1,
            "start_date": calculate_week_start(week_num),
            "topics": topic_group,
            "activities": []
        }

        for topic in topic_group:
            # Add reading
            week["activities"].append({
                "type": "read",
                "topic_id": topic.id
            })

            # Add flashcards if deck exists
            if topic.flashcard_deck:
                week["activities"].append({
                    "type": "flashcards",
                    "topic_id": topic.id
                })

        # Add end-of-week quiz if quizzes exist for any topic
        quiz_topics = [t for t in topic_group if t.quiz_bank]
        if quiz_topics:
            week["activities"].append({
                "type": "quiz",
                "topics": [t.id for t in quiz_topics]
            })

        plan.append(week)

    # Add final review week
    plan.append(generate_final_week())

    return plan
```

---

## Integration Points

### 1. Flashcard Session End
After completing a flashcard session, log it:
```python
log_session(type="flashcards", topic_id=deck_topic, duration=session_time,
            details={"cards_reviewed": count, "cards_correct": correct})
```

### 2. Quiz Completion
After submitting a quiz:
```python
log_session(type="quiz", topic_id=None, duration=session_time,
            details={"score": pct, "topics": quiz_topics})
```

### 3. Study Guide Page
Add "Mark as Read" button and track reading sessions:
```python
# When starting to read
start_reading_session(topic_id)

# When marking complete
complete_reading(topic_id)
show_comprehension_prompt(topic_id)
```

### 4. Home Page
Replace current "Today's Focus" with smart recommendations from Schedule system.

---

## Implementation Phases

### Phase 1: Foundation (Data & Basic UI)
- [ ] Create `data/schedule/` directory structure
- [ ] Create `config.json`, `topics.json` with CAPM data
- [ ] Create `progress.json` skeleton
- [ ] Add "Schedule" nav item
- [ ] Basic Schedule page with exam countdown
- [ ] Setup modal for exam date

### Phase 2: Reading Integration
- [ ] Add reading progress tracking to Study Guides page
- [ ] "Mark as Read" functionality
- [ ] Reading session logging
- [ ] Comprehension check prompt after reading

### Phase 3: Study Plan
- [ ] Plan generation algorithm
- [ ] Create `plan.json`
- [ ] Week view UI
- [ ] Mark activities complete
- [ ] Plan regeneration when exam date changes

### Phase 4: Smart Recommendations
- [ ] Implement recommendation algorithm
- [ ] "Today's Focus" on Schedule page
- [ ] Integration with existing flashcard due dates
- [ ] Integration with quiz weak areas

### Phase 5: Tracking & Analytics
- [ ] Session logging for all activities
- [ ] Streak tracking
- [ ] Daily/weekly summaries
- [ ] Progress dashboard with metrics

### Phase 6: Polish
- [ ] Visual progress indicators
- [ ] Notifications/reminders (if feasible in Streamlit)
- [ ] Export progress data
- [ ] Plan adjustment UI (reschedule activities)

---

## File Structure Summary

```
PM/
├── data/
│   ├── schedule/
│   │   ├── config.json       # Exam date, goals
│   │   ├── topics.json       # Topic registry (CAPM)
│   │   ├── plan.json         # Generated study plan
│   │   └── progress.json     # Reading progress, sessions, streaks
│   ├── flashcards/           # (existing)
│   ├── quizzes/              # (existing)
│   └── tidbits.json          # (existing)
├── app/
│   ├── app.py                # Add Schedule page
│   ├── schedule.py           # NEW: Schedule logic
│   ├── flashcards.py         # (existing)
│   └── quizzes.py            # (existing)
└── docs/
    └── schedule-feature-design.md  # This document
```

---

## Future Enhancements (Post-MVP)

1. **Calendar sync** - Export to Google Calendar / iCal
2. **Mobile-friendly** - Optimize for phone study sessions
3. **Study timer** - Pomodoro-style timer with logging
4. **Achievements** - Badges for streaks, completion milestones
5. **Multi-certification** - Switch between CAPM/PMP profiles
6. **Collaborative** - Share progress with study buddy
