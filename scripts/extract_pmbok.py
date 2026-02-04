# ABOUTME: Script to extract PMBOK PDF content into markdown files by section.
# ABOUTME: Processes large PDF safely in chunks, outputs to study-guides folder.

import fitz  # PyMuPDF
from pathlib import Path
import re

PROJECT_DIR = Path(__file__).parent.parent
PDF_PATH = PROJECT_DIR / "pmbokguide_eighthed_eng.pdf"
OUTPUT_DIR = PROJECT_DIR / "study-guides" / "pmbok"


def extract_pdf_structure(pdf_path: Path) -> list:
    """Extract table of contents and page ranges from PDF."""
    doc = fitz.open(pdf_path)

    print(f"PDF has {len(doc)} pages")

    # Get TOC if available
    toc = doc.get_toc()
    if toc:
        print(f"Found {len(toc)} TOC entries")

    doc.close()
    return toc


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


def extract_first_pages(pdf_path: Path, num_pages: int = 10) -> str:
    """Extract first N pages to understand structure."""
    return extract_pages(pdf_path, 1, num_pages)


def main():
    if not PDF_PATH.exists():
        print(f"PDF not found at {PDF_PATH}")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    print("PMBOK PDF Structure Analysis")
    print("=" * 60)

    # First, get the structure
    toc = extract_pdf_structure(PDF_PATH)

    # Save full TOC
    if toc:
        toc_path = OUTPUT_DIR / "00_toc.md"
        with open(toc_path, 'w', encoding='utf-8') as f:
            f.write("# PMBOK 8th Edition - Table of Contents\n\n")
            for item in toc:
                level, title, page = item
                # Clean up title
                title = title.replace('\u2002', ' ').strip()
                indent = "  " * (level - 1)
                f.write(f"{indent}- {title} (p.{page})\n")
        print(f"Saved TOC to {toc_path}")

    # PMBOK 8th Edition structure - Performance Domains (not Knowledge Areas)
    sections_to_find = [
        ("01_principles", "Project Management Principles", 58),
        ("02_life_cycles", "Project Life Cycles", 80),
        ("03_governance", "Governance Performance Domain", 115),
        ("04_scope", "Scope Performance Domain", 140),
        ("05_schedule", "Schedule Performance Domain", 152),
        ("06_finance", "Finance Performance Domain", 163),
        ("07_stakeholders", "Stakeholders Performance Domain", 172),
        ("08_resources", "Resources Performance Domain", 184),
        ("09_risk", "Risk Performance Domain", 197),
        ("10_tailoring", "Tailoring", 208),
        ("11_tools_techniques", "Tools and Techniques", 250),
        ("12_procurement", "Procurement", 350),
        ("13_glossary", "Glossary", 370),
    ]

    # Define page ranges based on TOC
    sections_to_extract = {}
    for i, (filename, title, start_page) in enumerate(sections_to_find):
        # End page is start of next section (or +30 if last)
        if i + 1 < len(sections_to_find):
            end_page = sections_to_find[i + 1][2] - 1
        else:
            end_page = start_page + 12  # Glossary is about 12 pages
        sections_to_extract[filename] = (start_page, end_page, title)

    print(f"\nFound {len(sections_to_extract)} Knowledge Area sections to extract")

    # Extract each section
    for short_name, (start, end, title) in sections_to_extract.items():
        print(f"  Extracting {short_name}: pages {start}-{end}")
        text = extract_pages(PDF_PATH, start, end)

        output_file = OUTPUT_DIR / f"{short_name.lower()}_management.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"# {title}\n\n")
            f.write(f"*Source: PMBOK Guide 8th Edition, pages {start}-{end}*\n\n")
            f.write("---\n\n")
            # Clean up text
            text = text.replace('\u2002', ' ')
            f.write(text)

        print(f"    Saved to {output_file}")

    print("\nDone!")


if __name__ == "__main__":
    main()
