# Code Review: extract_pmbok.py

**File:** `scripts/extract_pmbok.py`
**Lines:** 123
**Overall Quality:** Good
**Refactoring Effort:** Low

---

## Summary

A utility script for extracting PMBOK PDF content into markdown files. The code is straightforward, serves its purpose well, and follows project conventions. This is a one-time/occasional-use tool rather than production code.

---

## Strengths

### 1. ABOUTME Headers (Lines 1-2)
Follows project convention:
```python
# ABOUTME: Script to extract PMBOK PDF content into markdown files by section.
# ABOUTME: Processes large PDF safely in chunks, outputs to study-guides folder.
```

### 2. Safe Path Handling (Lines 8-10)
Uses `Path` for cross-platform compatibility:
```python
PROJECT_DIR = Path(__file__).parent.parent
PDF_PATH = PROJECT_DIR / "pmbokguide_eighthed_eng.pdf"
OUTPUT_DIR = PROJECT_DIR / "study-guides" / "pmbok"
```

### 3. Chunked Processing (Lines 28-39)
Processes pages in ranges to avoid memory issues:
```python
def extract_pages(pdf_path: Path, start_page: int, end_page: int) -> str:
    """Extract text from a range of pages."""
    doc = fitz.open(pdf_path)
    text = ""

    for page_num in range(start_page - 1, min(end_page, len(doc))):
        page = doc[page_num]
        text += f"\n\n--- Page {page_num + 1} ---\n\n"
        text += page.get_text()

    doc.close()
    return text
```

### 4. Clear Section Definitions (Lines 74-88)
Well-organized extraction targets:
```python
sections_to_find = [
    ("01_principles", "Project Management Principles", 58),
    ("02_life_cycles", "Project Life Cycles", 80),
    ("03_governance", "Governance Performance Domain", 115),
    # ...
]
```

### 5. Progress Feedback (Lines 103-116)
Helpful console output during extraction:
```python
print(f"  Extracting {short_name}: pages {start}-{end}")
# ...
print(f"    Saved to {output_file}")
```

---

## Issues & Recommendations

### Critical

**None identified.**

### Major

**None identified.**

### Moderate

#### 1. Missing Error Handling for File Operations
**Location:** Lines 48-52, 103-116
**Issue:** No try/except for PDF opening or file writing.

```python
# Current (line 15):
doc = fitz.open(pdf_path)  # Could raise if file corrupted

# Recommended:
try:
    doc = fitz.open(pdf_path)
except fitz.fitz.FileDataError as e:
    print(f"Error opening PDF: {e}")
    return []
```

#### 2. Hardcoded Page Numbers
**Location:** Lines 74-88
**Issue:** Page numbers are hardcoded and may not match different PDF versions.

```python
sections_to_find = [
    ("01_principles", "Project Management Principles", 58),
    # ...
]
```

**Consideration:** This is acceptable for a one-time extraction tool. Future versions of PMBOK would require manual updates anyway.

#### 3. Document Not Closed on Exception
**Location:** Lines 28-39
**Issue:** If an exception occurs during extraction, the document won't be closed.

```python
# Current:
doc = fitz.open(pdf_path)
text = ""
for page_num in range(...):
    # If exception here, doc.close() never called
doc.close()

# Recommended:
with fitz.open(pdf_path) as doc:
    text = ""
    for page_num in range(...):
        # ...
```

**Note:** PyMuPDF supports context manager, which handles cleanup automatically.

### Minor

#### 1. Comment Inconsistency
**Location:** Line 100
**Issue:** Comment says "Knowledge Area" but PMBOK 8th uses "Performance Domain".

```python
print(f"Found {len(sections_to_extract)} Knowledge Area sections to extract")
```

**Recommendation:** Update to:
```python
print(f"Found {len(sections_to_extract)} Performance Domain sections to extract")
```

#### 2. Unused Variable
**Location:** Lines 74-88 vs 91-98
**Issue:** `title` in `sections_to_find` duplicates information that could be derived.

**Status:** Acceptable - explicit is better than implicit for clarity.

#### 3. No Type Hints
**Location:** Throughout
**Issue:** Functions lack type hints (though this is a script, not a library).

```python
# Current:
def extract_pdf_structure(pdf_path: Path) -> list:

# Could be more specific:
def extract_pdf_structure(pdf_path: Path) -> list[tuple[int, str, int]]:
```

#### 4. Unicode Character Handling
**Location:** Lines 68, 113
**Issue:** Only handles one specific unicode space character (`\u2002`).

```python
title = title.replace('\u2002', ' ').strip()
text = text.replace('\u2002', ' ')
```

**Recommendation:** Handle multiple unicode space variants:
```python
import unicodedata
text = unicodedata.normalize('NFKC', text)
```

---

## Performance Considerations

### 1. Page-by-Page Processing
**Status:** Appropriate. Loading pages individually prevents memory issues with large PDFs.

### 2. String Concatenation
**Location:** Lines 35-36
**Issue:** String concatenation in loop (`text += ...`) is O(n²) for large texts.

```python
for page_num in range(...):
    text += f"\n\n--- Page {page_num + 1} ---\n\n"
    text += page.get_text()
```

**Recommendation:** Use list and join:
```python
parts = []
for page_num in range(...):
    parts.append(f"\n\n--- Page {page_num + 1} ---\n\n")
    parts.append(page.get_text())
text = ''.join(parts)
```

**Impact:** Minimal for this use case (small page counts per section).

---

## Security Review

### Passed
- No command injection
- No user input handling
- Fixed file paths (no path traversal)
- Local-only operations

### Note
- Script processes local PDF file only
- No network operations
- No sensitive data handling

---

## Test Coverage Gaps

Given this is a utility script, minimal testing is acceptable. However, these would be useful:

1. **Smoke test:** Verify script runs without error
2. **Output validation:** Check that markdown files are created with expected structure
3. **Edge cases:** Handle missing PDF gracefully

---

## Adherence to Project Conventions

| Convention | Status | Notes |
|------------|--------|-------|
| ABOUTME headers | Pass | Lines 1-2 |
| No mock modes | Pass | Processes real PDF |
| Evergreen comments | Pass | No temporal references |
| Simple over clever | Pass | Straightforward implementation |

---

## Recommendations Summary

### Medium Priority
1. Use context manager for PDF document handling
2. Add basic error handling for file operations

### Low Priority
3. Update "Knowledge Area" comment to "Performance Domain"
4. Consider more comprehensive unicode normalization
5. Use list join instead of string concatenation

---

## Code Quality Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| Cyclomatic Complexity | Low | Simple control flow |
| Lines of Code | 123 | Appropriate for utility script |
| Functions | 4 | Good separation |
| Type Hints | Partial | Present but basic |
| Error Handling | Minimal | Acceptable for utility script |

---

## Usage Notes

### Running the Script
```bash
cd PM/scripts
python extract_pmbok.py
```

### Prerequisites
- PyMuPDF installed: `pip install PyMuPDF`
- PMBOK PDF file at `PM/pmbokguide_eighthed_eng.pdf`

### Output
Creates markdown files in `PM/study-guides/pmbok/`:
- `00_toc.md` - Table of contents
- `01_principles_management.md` - PM Principles
- `02_life_cycles_management.md` - Life Cycles
- etc.

### Limitations
- Page numbers are for PMBOK 8th Edition specifically
- Re-running overwrites existing files
- No incremental extraction (always extracts all sections)
