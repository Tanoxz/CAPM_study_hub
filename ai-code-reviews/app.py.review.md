# Code Review: app.py

**File:** `app/app.py`
**Lines:** 1,839
**Overall Quality:** Good
**Refactoring Effort:** Medium

---

## Summary

The main Streamlit application is well-structured and implements a comprehensive CAPM study system. It follows evidence-based learning principles and provides a cohesive user experience. However, the file is quite large and could benefit from modularization.

---

## Strengths

### 1. ABOUTME Headers (Lines 1-2)
Follows the project convention for file documentation:
```python
# ABOUTME: Main Streamlit application for CAPM study tools.
# ABOUTME: Implements evidence-based learning: retrieval practice, spaced repetition, interleaving.
```

### 2. Clean Import Organization (Lines 4-24)
Imports are well-organized with standard library first, then third-party, then local modules.

### 3. Evidence-Based Design
The application correctly implements learning science principles:
- Retrieval practice through flashcards and quizzes
- Spaced repetition (SM-2 algorithm integration)
- Interleaving (mixed topics in quizzes)
- Elaborative interrogation (why_it_matters in flashcards)

### 4. Swedish Localization (Lines 46-57)
Nice touch providing Swedish month names for date formatting.

### 5. Session State Management
Proper use of `st.session_state` for maintaining state across Streamlit reruns.

---

## Issues & Recommendations

### Critical

**None identified** - The code is functional and safe.

### Major

#### 1. File Size (1,839 lines)
**Location:** Entire file
**Issue:** The file is too large for easy maintenance. Single Responsibility Principle violation.

**Recommendation:** Split into separate modules:
- `pages/home.py` - Home page
- `pages/schedule.py` - Schedule page UI
- `pages/prepcast.py` - PrepCast Videos page
- `pages/study_guides.py` - Study Guides page
- `pages/flashcards_page.py` - Flashcards UI
- `pages/quiz_page.py` - Quiz UI
- `pages/progress.py` - Progress page

#### 2. Duplicate Session Logging Logic
**Location:** Lines 336-343, 691-699, 730-738, 1037-1045, 1283-1294, 1497-1514
**Issue:** Session logging code is repeated in multiple places.

**Recommendation:** Create a centralized `log_study_activity()` function that handles all session logging uniformly.

### Moderate

#### 3. Missing Error Handling for File Operations
**Location:** Lines 64-68, 562-569, 1761-1762
**Issue:** File reads don't have try/except blocks for JSON parsing errors.

```python
# Current (line 64-68):
with open(TIDBITS_FILE, 'r', encoding='utf-8') as f:
    data = json.load(f)  # Could raise JSONDecodeError

# Suggested:
try:
    with open(TIDBITS_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)
except json.JSONDecodeError:
    return None
```

#### 4. Hardcoded Duration Estimates
**Location:** Lines 1290-1291, 1505
**Issue:** Card review time (1 min) and quiz time (2 min per question) are magic numbers.

```python
# Line 1290-1291:
duration_minutes=len(cards) * 1,  # Estimate ~1 min per card
```

**Recommendation:** Define constants at module level:
```python
MINUTES_PER_FLASHCARD = 1
MINUTES_PER_QUIZ_QUESTION = 2
```

#### 5. Potential Division by Zero
**Location:** Lines 370, 384, 883, 964, 1557, 1773
**Issue:** Several places calculate percentages without checking for zero denominators (though most do check).

```python
# Line 1773 is safe:
overall_pct = (total_correct / total_questions) * 100 if total_questions > 0 else 0

# But line 144 in get_deck_stats (flashcards.py) references cards that could be empty
```

### Minor

#### 6. Unused Import Possibility
**Location:** Lines 55-56, 361, 420, 560-569
**Issue:** `datetime` is imported inside functions multiple times when it could use the global import.

```python
# Line 55-56 (inside format_swedish_date):
from datetime import datetime

# Line 361 (inside show_visual_progress):
from datetime import date
```

**Recommendation:** Import once at the top of the file.

#### 7. Inconsistent Session State Key Naming
**Location:** Throughout
**Issue:** Mix of prefixes (`fc_`, `quiz_`, no prefix):
- `st.session_state.tidbit`
- `st.session_state.fc_deck`
- `st.session_state.quiz_questions`
- `st.session_state.guide_just_completed`

**Recommendation:** Use consistent naming: `session_state.flashcard_*`, `session_state.quiz_*`, etc.

#### 8. Long Functions
**Location:**
- `show_schedule()` (Lines 164-356) - 192 lines
- `get_today_recommendations()` (Lines 472-628) - 156 lines
- `show_flashcards()` (Lines 1218-1346) - 128 lines
- `show_quiz()` (Lines 1363-1522) - 159 lines

**Recommendation:** Extract logical sections into helper functions.

#### 9. Swedish/English Mix in UI
**Location:** Lines 224, 817
**Issue:** Mix of Swedish ("Bokad", "Mål", "överskriden") and English in the UI.

```python
# Line 224:
confirmed_text = " (Bokad)" if config.exam_date_confirmed else " (Mål)"
# Line 817:
st.markdown(f"{icon} ~~{description}~~ ⚠️ *överskriden*")
```

**Consideration:** This may be intentional for the user. Verify consistency is desired.

---

## Performance Considerations

### 1. Deck Loading on Every Page Load
**Location:** Lines 125-130, 492-518, 1705-1733
**Issue:** Flashcard decks are loaded from disk every time the Home page or Progress page loads.

**Recommendation:** Consider caching deck stats using `@st.cache_data` for read-only operations:
```python
@st.cache_data(ttl=60)  # Cache for 60 seconds
def get_cached_deck_stats():
    # Load and calculate stats
```

### 2. Multiple File Reads for Same Data
**Location:** Lines 168-171 vs 276-277
**Issue:** Config, topics, and progress are loaded multiple times within `show_schedule()`.

---

## Security Review

### Passed
- No hardcoded secrets or credentials
- No command injection vulnerabilities
- No SQL injection (not using SQL)
- No XSS vulnerabilities (Streamlit handles sanitization)
- File paths are constructed safely using `Path`

### Note
- All file operations are local-only
- No external API calls
- No user-supplied file paths (all paths are predetermined)

---

## Test Coverage Gaps

This file would benefit from:
1. **Unit tests** for helper functions (`get_random_tidbit`, `format_swedish_date`, `get_today_recommendations`)
2. **Integration tests** for session state management
3. **UI tests** using Streamlit's testing framework

---

## Adherence to Project Conventions

| Convention | Status | Notes |
|------------|--------|-------|
| ABOUTME headers | Pass | Lines 1-2 |
| No mock modes | Pass | Uses real data |
| Evergreen comments | Pass | No temporal references |
| No --no-verify | N/A | No git commands |
| Simple over clever | Pass | Straightforward implementation |

---

## Recommendations Summary

### High Priority
1. Split into multiple page modules
2. Centralize session logging logic

### Medium Priority
3. Add error handling for JSON parsing
4. Extract magic numbers to constants
5. Consider caching for deck stats

### Low Priority
6. Clean up internal imports
7. Standardize session state key naming
8. Extract long functions into helpers
