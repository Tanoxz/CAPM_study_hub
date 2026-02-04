# Code Review: quizzes.py

**File:** `app/quizzes.py`
**Lines:** 177
**Overall Quality:** Excellent
**Refactoring Effort:** Low

---

## Summary

Clean, well-structured quiz system implementing evidence-based interleaved learning. The code demonstrates solid design principles with appropriate use of dataclasses and clear separation of concerns.

---

## Strengths

### 1. ABOUTME Headers (Lines 1-2)
Properly documented per project convention:
```python
# ABOUTME: Quiz system with interleaving and Bloom's taxonomy levels.
# ABOUTME: Implements scenario-based questions for application-level learning.
```

### 2. Clean Data Models (Lines 13-34)
Well-designed dataclasses with appropriate fields:
```python
@dataclass
class Question:
    """A single quiz question."""
    id: str
    question: str
    options: list[str]  # A, B, C, D
    correct_answer: int  # Index 0-3
    explanation: str  # WHY this answer is correct
    knowledge_area: str
    difficulty: str = "medium"  # "easy", "medium", "hard"
    question_type: str = "concept"  # "scenario", "concept", "application"
```

### 3. Evidence-Based Interleaving (Lines 48-87)
Correct implementation of interleaved practice:
```python
def create_interleaved_quiz(
    all_questions: list[Question],
    num_questions: int = 20,
    knowledge_areas: list[str] = None
) -> list[Question]:
    """
    Create a quiz with interleaved questions from different knowledge areas.
    This forces discrimination between concepts (evidence-based).
    """
```

The round-robin selection ensures topics are mixed:
```python
# Round-robin selection from each area
selected = []
areas = list(by_area.keys())
random.shuffle(areas)

while len(selected) < num_questions and any(by_area.values()):
    for area in areas:
        if by_area[area] and len(selected) < num_questions:
            q = random.choice(by_area[area])
            by_area[area].remove(q)
            selected.append(q)
```

### 4. Comprehensive Grading (Lines 90-130)
Tracks performance by multiple dimensions:
- Overall correct/incorrect
- By knowledge area
- By difficulty
- Missed question IDs for review

### 5. Weak Area Detection (Lines 150-176)
Good implementation for identifying areas needing focus:
```python
def get_weak_areas(results_path: Path, threshold: float = 0.7) -> list[str]:
    """Identify knowledge areas with accuracy below threshold."""
```

---

## Issues & Recommendations

### Critical

**None identified.**

### Major

**None identified.**

### Moderate

#### 1. Potential Issue with Empty Options List
**Location:** Line 18
**Issue:** No validation that options has exactly 4 items, but the UI expects A, B, C, D.

```python
options: list[str]  # A, B, C, D
correct_answer: int  # Index 0-3
```

**Recommendation:** Add validation in `__post_init__`:
```python
def __post_init__(self):
    if len(self.options) != 4:
        raise ValueError(f"Question must have exactly 4 options, got {len(self.options)}")
    if not 0 <= self.correct_answer <= 3:
        raise ValueError(f"correct_answer must be 0-3, got {self.correct_answer}")
```

### Minor

#### 1. Type Hint for knowledge_areas Parameter
**Location:** Line 51
**Issue:** Could use `Optional[list[str]]` for clarity.

```python
# Current:
knowledge_areas: list[str] = None

# Recommended:
knowledge_areas: Optional[list[str]] = None
```

#### 2. Unnecessary Copy Operation
**Location:** Line 57
**Issue:** `available = all_questions.copy()` is immediately filtered or used as-is.

```python
available = all_questions.copy()

# Filter by knowledge areas if specified
if knowledge_areas:
    available = [q for q in available if q.knowledge_area in knowledge_areas]
```

**Note:** This is a defensive programming pattern that prevents modification of the original list. Keep as-is - it's correct behavior.

#### 3. Missing ensure_ascii in save_result
**Location:** Lines 146-147
**Issue:** Inconsistent with other file writes in the codebase.

```python
# Current:
with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2)

# Consistent with flashcards.py:
with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)
```

#### 4. Aggregation Recalculates on Every Call
**Location:** Lines 150-176
**Issue:** `get_weak_areas()` reads and aggregates all results every time it's called.

**Consideration:** For current usage (small result sets), this is fine. If results grow large, consider caching.

---

## Performance Considerations

### 1. Round-Robin Selection Efficiency
**Location:** Lines 74-83
**Status:** O(n) complexity for selection, which is appropriate for typical quiz sizes (20-50 questions from pools of 200-500).

### 2. File Read in get_weak_areas
**Location:** Lines 152-156
**Status:** Reads entire file on each call. Acceptable for current use case.

---

## Security Review

### Passed
- No hardcoded secrets
- Safe file handling with `Path`
- No user-supplied file paths
- JSON data is trusted (internally generated)

### Note
- Quiz answers are stored locally only
- No sensitive data in quiz results

---

## Test Coverage Gaps

Recommended tests:

1. **Interleaving tests:**
   - Verify questions from different areas are mixed
   - Verify `knowledge_areas` filter works correctly
   - Edge case: fewer questions available than requested

2. **Grading tests:**
   - All correct -> 100%
   - All wrong -> 0%
   - Mixed results tracked by area/difficulty
   - Missed questions list accuracy

3. **Weak areas tests:**
   - No results -> empty list
   - All above threshold -> empty list
   - Multiple weak areas sorted by accuracy

4. **Edge cases:**
   - Empty question bank
   - Single question quiz
   - All questions from one area

---

## Adherence to Project Conventions

| Convention | Status | Notes |
|------------|--------|-------|
| ABOUTME headers | Pass | Lines 1-2 |
| No mock modes | Pass | Uses real quiz data |
| Evergreen comments | Pass | No temporal references |
| Simple over clever | Pass | Clear implementation |

---

## Recommendations Summary

### Medium Priority
1. Add validation for 4 options and correct_answer range in Question

### Low Priority
2. Add `ensure_ascii=False` to `save_result()` for consistency
3. Add type hint `Optional[list[str]]` for `knowledge_areas` parameter
4. Add unit tests for interleaving and grading

---

## Code Quality Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Cyclomatic Complexity | Low | Simple loops and conditionals |
| Lines of Code | 177 | Right-sized for the functionality |
| Functions | 5 | Good separation of concerns |
| Comments | Good | Key concepts explained |
| Type Hints | Present | Used consistently |

---

## Design Pattern Notes

### Builder Pattern Opportunity
The `create_interleaved_quiz()` function could evolve into a builder pattern if quiz customization needs grow:
```python
# Future consideration:
quiz = QuizBuilder(all_questions)
    .with_knowledge_areas(['Scope', 'Schedule'])
    .with_difficulty('hard')
    .with_count(20)
    .build()
```

**Current Status:** Not needed yet. The current function handles requirements well.
