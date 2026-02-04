# Code Review: schedule.py

**File:** `app/schedule.py`
**Lines:** 1,261
**Overall Quality:** Good
**Refactoring Effort:** Medium

---

## Summary

A comprehensive study schedule system that implements evidence-based learning principles including spaced timing, phase-based study allocation, and adaptive scheduling. While functional and well-designed, the file has grown large and could benefit from modularization.

---

## Strengths

### 1. ABOUTME Headers (Lines 1-2)
Excellent project convention adherence:
```python
# ABOUTME: Study schedule system with exam countdown, progress tracking, and recommendations.
# ABOUTME: Implements daily study plans (90min/day), PM PrepCast video tracking, and smart recommendations.
```

### 2. Well-Designed Data Models (Lines 11-47)
Clean dataclasses with sensible defaults:
```python
@dataclass
class ScheduleConfig:
    """User's schedule configuration."""
    version: int
    certification: str
    exam_date: Optional[str]
    # ...
```

### 3. Evidence-Based Constants (Lines 826-832)
Learning science principles codified:
```python
# Activity durations based on real usage
FLASHCARD_DECK_MINUTES = 5  # ~5 min per deck of 10-20 cards
QUIZ_SESSION_MINUTES = 20   # One quiz session
REVIEW_SESSION_MINUTES = 15 # Quick review

# Spacing constants (evidence-based)
FLASHCARD_DELAY_DAYS = 1    # Flashcards 1-2 days after learning
QUIZ_DELAY_DAYS = 3         # Quiz 3-5 days after learning
```

### 4. Phase-Based Study Allocation (Lines 965-979)
Smart adaptation based on exam proximity:
```python
if day_number <= early_phase_end:
    # Early phase: 60% new content, 25% flashcards, 15% quiz
    new_content_target = 55
    flashcard_target = 25
    quiz_target = 10
elif day_number <= middle_phase_end:
    # Middle phase: 40% new content, 35% flashcards, 25% quiz
    new_content_target = 40
    flashcard_target = 30
    quiz_target = 20
else:
    # Final phase: 20% new content, 30% flashcards, 50% quiz
    new_content_target = 20
    flashcard_target = 25
    quiz_target = 45
```

### 5. Streak Management (Lines 173-216)
Proper streak tracking with history:
```python
def update_streak(progress: dict) -> dict:
    """Update streak based on today's activity."""
    # ... handles consecutive days, broken streaks, history
```

### 6. Clear Section Organization
The file is organized into logical sections with clear headers:
- Configuration & Progress (Lines 1-171)
- Streak & Session Management (Lines 173-268)
- Study Plan Generation (Lines 319-564)
- PM PrepCast Tracking (Lines 732-818)
- Daily Plan Generation (Lines 821-1261)

---

## Issues & Recommendations

### Critical

**None identified.**

### Major

#### 1. File Size (1,261 lines)
**Issue:** The file has grown too large, mixing multiple concerns.

**Recommendation:** Split into separate modules:
```
schedule/
    __init__.py
    config.py          # ScheduleConfig, load/save config, topics
    progress.py        # Progress tracking, streaks, sessions
    weekly_plan.py     # WeekPlan generation and management
    daily_plan.py      # Daily plan generation (the 90min/day system)
    prepcast.py        # PM PrepCast video tracking
```

#### 2. Missing Import at Module Level
**Location:** Lines 200, 222
**Issue:** `timedelta` is imported inside functions but used elsewhere without import.

```python
# Line 200 (inside update_streak):
from datetime import timedelta  # ERROR: timedelta used but not imported at line 200

# Line 222 (inside log_session):
from datetime import timedelta  # Import here to avoid circular issues
```

**Issue Details:** The import comment on line 222 suggests there may have been a circular import issue, but the current structure doesn't have circular imports.

**Recommendation:** Import `timedelta` at the top of the file with other datetime imports:
```python
from datetime import datetime, date, timedelta
```

### Moderate

#### 3. Inconsistent None Handling
**Location:** Lines 126, 137
**Issue:** Different return patterns for None exam_date.

```python
# Line 126-131:
def get_days_until_exam(config: ScheduleConfig) -> Optional[int]:
    if not config.exam_date:
        return None
    # ...

# But line 543 uses:
if days_since_quiz is None or days_since_quiz >= quiz_interval_days:
```

**Status:** This is actually correct - the code properly handles None cases. No change needed.

#### 4. Magic Numbers in Theme Detection
**Location:** Lines 434-448
**Issue:** Theme determination has hardcoded string matching.

```python
def get_week_theme(week_topics: list[Topic]) -> str:
    if any("Principle" in n for n in names):
        return "Foundations"
    if any("Scope" in n or "Schedule" in n or "Finance" in n for n in names):
        return "Planning Domains"
    # ...
```

**Recommendation:** Consider making this configurable or adding a `theme_category` field to Topic dataclass.

#### 5. Potential Memory Issue with Large Plans
**Location:** Lines 951-1182
**Issue:** `generate_daily_plan()` builds the entire plan in memory at once. For a 90-day plan with 3-4 activities/day, this is ~360 activity objects.

**Status:** This is acceptable for current use. Monitor if exam periods extend significantly.

### Minor

#### 1. Unused Dataclass
**Location:** Lines 40-47
**Issue:** `Streaks` dataclass is defined but progress uses a dict directly.

```python
@dataclass
class Streaks:
    """Streak tracking data."""
    current_streak: int
    longest_streak: int
    last_study_date: Optional[str]
    streak_history: list
```

**Recommendation:** Either use the dataclass consistently or remove it if the dict approach is preferred.

#### 2. Inconsistent Activity ID Format
**Location:** Lines 475-476 vs 998
**Issue:** Week plan uses `w{week}_a{counter}`, daily plan uses `d{day}_a{counter}`.

```python
# Week plan (line 475):
"id": f"w{week_num}_a{activity_counter}",

# Daily plan (line 998):
"id": f"d{day_number}_a{activity_counter}",
```

**Status:** This is actually good - it distinguishes between the two plan types. Keep as-is.

#### 3. Duplicate Quiz Detection Logic
**Location:** Lines 1124-1133
**Issue:** Complex nested loop for avoiding duplicate quizzes on same day.

```python
if quiz['quiz_bank'] in quizzes_added_today:
    # Try next quiz
    for j in range(len(available_quizzes)):
        alt_idx = (quiz_idx + j + 1) % len(available_quizzes)
        alt_quiz = available_quizzes[alt_idx]
        if alt_quiz['quiz_bank'] not in quizzes_added_today:
            quiz = alt_quiz
            break
    else:
        continue
```

**Recommendation:** Extract to a helper function:
```python
def get_next_unique_quiz(available_quizzes, used_quizzes, start_idx):
    """Get next quiz not already used today."""
    for i in range(len(available_quizzes)):
        idx = (start_idx + i) % len(available_quizzes)
        if available_quizzes[idx]['quiz_bank'] not in used_quizzes:
            return available_quizzes[idx]
    return None
```

#### 4. PrepCast Lesson Status Values
**Location:** Line 748
**Issue:** Status values are strings without constants.

```python
status: str  # not_watched, watched, rewatching
```

**Recommendation:** Use an Enum:
```python
class LessonStatus(str, Enum):
    NOT_WATCHED = "not_watched"
    WATCHED = "watched"
    REWATCHING = "rewatching"
```

---

## Performance Considerations

### 1. Plan Generation Complexity
**Location:** Lines 835-1182
**Analysis:** The `generate_daily_plan()` function has O(n*m) complexity where n is days and m is content items. For typical usage (90 days, 100 items), this is ~9,000 operations.

**Status:** Acceptable performance. Plan regeneration is infrequent.

### 2. File I/O on Every Save
**Location:** Lines 70-78, 114-120, 355-360
**Status:** Appropriate for the application. User-triggered saves are infrequent.

---

## Security Review

### Passed
- No hardcoded secrets
- Safe file handling with `Path`
- All paths are internal (no user-supplied paths)
- Date/time parsing uses ISO format (safe)

---

## Test Coverage Gaps

Recommended tests:

1. **Configuration tests:**
   - Default config values
   - Config save/load round-trip
   - Exam date change detection

2. **Streak tests:**
   - First day establishes streak
   - Consecutive days extend streak
   - Missed day resets streak
   - Longest streak tracking

3. **Plan generation tests:**
   - Plans have no empty days
   - Phase transitions at correct boundaries
   - Activity distribution matches targets

4. **PrepCast tests:**
   - Lesson watching marks correct status
   - Progress stats calculation
   - Next unwatched lesson selection

5. **Edge cases:**
   - Exam date in past
   - Zero days until exam
   - No topics configured
   - All videos already watched

---

## Adherence to Project Conventions

| Convention | Status | Notes |
|------------|--------|-------|
| ABOUTME headers | Pass | Lines 1-2 |
| No mock modes | Pass | Uses real scheduling data |
| Evergreen comments | Pass | No temporal references |
| Simple over clever | Mixed | Some complex algorithms, but necessary |

---

## Recommendations Summary

### High Priority
1. Move `timedelta` import to module level
2. Consider splitting into multiple modules as file grows

### Medium Priority
3. Extract duplicate quiz selection logic to helper function
4. Consider using Enum for lesson status values

### Low Priority
5. Remove unused `Streaks` dataclass or use it consistently
6. Make week theme detection configurable
7. Add comprehensive unit tests

---

## Code Quality Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Cyclomatic Complexity | Medium | Complex plan generation, but necessary |
| Lines of Code | 1,261 | Could be split |
| Functions | 34 | Good granularity |
| Dataclasses | 6 | Well-designed |
| Comments | Good | Section headers help navigation |
| Type Hints | Present | Used consistently |

---

## Architecture Notes

### Current Structure
```
schedule.py
├── Data Models (dataclasses)
├── Config Management
├── Progress Tracking
├── Streak Management
├── Session Logging
├── Weekly Plan Generation
├── Weekly Plan Management
├── PrepCast Video Tracking
└── Daily Plan Generation
```

### Suggested Modular Structure
```
schedule/
├── __init__.py (re-exports main functions)
├── models.py (all dataclasses)
├── config.py (config management)
├── progress.py (progress, streaks, sessions)
├── weekly_plan.py (week-based planning)
├── daily_plan.py (90min/day system)
└── prepcast.py (video tracking)
```

This refactoring would improve:
- Testability (smaller units)
- Maintainability (clear boundaries)
- Import efficiency (load only what's needed)
