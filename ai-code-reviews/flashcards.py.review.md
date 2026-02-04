# Code Review: flashcards.py

**File:** `app/flashcards.py`
**Lines:** 146
**Overall Quality:** Excellent
**Refactoring Effort:** Low

---

## Summary

This is a well-crafted implementation of the SM-2 spaced repetition algorithm. The code is clean, focused, and follows best practices. It's one of the strongest files in the codebase.

---

## Strengths

### 1. ABOUTME Headers (Lines 1-2)
Follows project convention perfectly:
```python
# ABOUTME: Flashcard system with SM-2 spaced repetition algorithm.
# ABOUTME: Implements evidence-based retrieval practice and spacing.
```

### 2. Clean Data Model (Lines 12-35)
The `Card` dataclass is well-designed with sensible defaults:
```python
@dataclass
class Card:
    """A single flashcard with spaced repetition metadata."""
    id: str
    question: str
    answer: str
    knowledge_area: str
    card_type: str  # "definition", "why", "scenario", "formula"

    # SM-2 algorithm fields
    easiness: float = 2.5  # E-Factor (1.3 minimum)
    interval: int = 1  # Days until next review
    repetitions: int = 0  # Successful repetitions in a row
    next_review: Optional[str] = None  # ISO date string

    # Learning context
    why_it_matters: str = ""  # Elaborative interrogation support
    related_concepts: list = None  # For connecting knowledge
```

### 3. Correct SM-2 Implementation (Lines 38-74)
The algorithm is implemented correctly per the original SM-2 specification:
- Quality ratings 0-5
- E-Factor minimum of 1.3
- Correct interval progression (1 -> 6 -> interval * E-Factor)
- Proper repetition reset on failure

### 4. Smart Due Card Selection (Lines 77-95)
Prioritizes overdue cards while maintaining interleaving through shuffling:
```python
# Sort by most overdue first, but then shuffle within groups for interleaving
due.sort(key=lambda x: -x[1])

# Take top cards but shuffle to interleave knowledge areas
selected = [c[0] for c in due[:limit * 2]]  # Get extra for shuffling
random.shuffle(selected)
```

### 5. Single Responsibility
Each function does one thing well:
- `sm2_update()` - Updates a card's SM-2 state
- `get_due_cards()` - Retrieves due cards
- `load_deck()` / `save_deck()` - Persistence
- `get_deck_stats()` - Statistics

---

## Issues & Recommendations

### Critical

**None identified.**

### Major

**None identified.**

### Moderate

#### 1. Mutable Default Argument
**Location:** Line 29
**Issue:** Using mutable default `list = None` pattern, but handled correctly in `__post_init__`.

```python
related_concepts: list = None  # For connecting knowledge

def __post_init__(self):
    if self.related_concepts is None:
        self.related_concepts = []
```

**Status:** This is the correct pattern for dataclasses. No change needed.

### Minor

#### 1. Type Hint Improvement
**Location:** Line 77
**Issue:** Could use more specific generic type hints.

```python
# Current:
def get_due_cards(cards: list[Card], limit: int = 20) -> list[Card]:

# Could be more explicit with:
from typing import List
def get_due_cards(cards: List[Card], limit: int = 20) -> List[Card]:
```

**Note:** The current syntax is valid Python 3.9+ and more modern. Keep as-is if targeting 3.9+.

#### 2. Missing Docstring for get_deck_stats Return Type
**Location:** Lines 123-145
**Issue:** The return dictionary structure is not documented.

```python
def get_deck_stats(cards: list[Card]) -> dict:
    """Get statistics about a deck."""
```

**Recommendation:** Document the return structure:
```python
def get_deck_stats(cards: list[Card]) -> dict:
    """
    Get statistics about a deck.

    Returns:
        dict with keys:
            - total_cards: int
            - due_today: int
            - by_knowledge_area: dict[str, dict]
            - avg_easiness: float
            - mastered: int
            - learning: int
    """
```

#### 3. Missing 'mastered' and 'learning' in Return Statement
**Location:** Lines 140-145
**Issue:** The return dict mentions `by_knowledge_area` with nested mastered counts, but doesn't include top-level `mastered` count that `app.py:1725` expects.

```python
# Current return:
return {
    'total_cards': len(cards),
    'due_today': due_count,
    'by_knowledge_area': by_area,
    'avg_easiness': sum(c.easiness for c in cards) / len(cards) if cards else 0
}

# app.py:1725 expects:
total_mastered += stats.get('mastered', 0)
```

**Recommendation:** Add top-level aggregations:
```python
return {
    'total_cards': len(cards),
    'due_today': due_count,
    'mastered': sum(v['mastered'] for v in by_area.values()),
    'learning': len(cards) - sum(v['mastered'] for v in by_area.values()),
    'by_knowledge_area': by_area,
    'avg_easiness': sum(c.easiness for c in cards) / len(cards) if cards else 0
}
```

---

## Performance Considerations

### 1. Deck Loading
**Location:** Lines 98-106
**Status:** Efficient - loads entire deck at once which is appropriate for the small deck sizes (10-20 cards each).

### 2. Due Card Calculation
**Location:** Lines 77-95
**Consideration:** Iterates through all cards twice (once for filtering, once for sorting). For small decks (<100 cards), this is fine. For larger decks, could be optimized.

---

## Security Review

### Passed
- No hardcoded secrets
- No external inputs processed unsafely
- File paths handled safely via `Path`
- JSON loading is safe (trusted data files)

---

## Test Coverage Gaps

Recommended tests:
1. **SM-2 algorithm tests:**
   - Quality 0-2 should reset repetitions
   - Quality 3-5 should increment repetitions
   - E-Factor minimum bound (1.3)
   - Interval progression verification

2. **Due card tests:**
   - Cards with past `next_review` are returned
   - Cards with future `next_review` are not returned
   - Limit parameter respected
   - Shuffling produces different orderings

3. **Edge cases:**
   - Empty deck handling
   - Single card deck
   - All cards due vs no cards due

---

## Adherence to Project Conventions

| Convention | Status | Notes |
|------------|--------|-------|
| ABOUTME headers | Pass | Lines 1-2 |
| No mock modes | Pass | Real algorithm implementation |
| Evergreen comments | Pass | No temporal references |
| Simple over clever | Pass | Clear, straightforward code |

---

## Recommendations Summary

### High Priority
1. Add top-level `mastered` and `learning` counts to `get_deck_stats()` return value

### Low Priority
2. Add docstring documenting return dict structure
3. Add unit tests for SM-2 algorithm

---

## Code Quality Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Cyclomatic Complexity | Low | Simple control flow |
| Lines of Code | 146 | Appropriately sized |
| Functions | 6 | Good separation |
| Comments | Adequate | Key concepts explained |
| Type Hints | Present | Used throughout |
