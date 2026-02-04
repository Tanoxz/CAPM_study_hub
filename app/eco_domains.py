# ABOUTME: Single source of truth for ECO domain mappings and functions.
# ABOUTME: Centralizes domain logic to prevent inconsistencies across modules.

"""
ECO (Exam Content Outline) Domain Management

This module is the SINGLE SOURCE OF TRUTH for all ECO domain mappings.
All other modules (flashcards.py, quizzes.py, app.py) must import from here.

CAPM Exam Content Outline Domains:
- Domain 1: PM Fundamentals & Core Concepts (36%)
- Domain 2: Predictive, Plan-Based Methodologies (17%)
- Domain 3: Agile Frameworks/Methodologies (20%)
- Domain 4: Business Analysis Frameworks (27%)

MAINTENANCE NOTES:
- When adding new flashcard knowledge_areas, ADD THEM HERE FIRST
- When adding new quiz knowledge_areas, ADD THEM HERE FIRST
- Run validate_knowledge_area() during development to catch unmapped areas
- The default domain is 1 (PM Fundamentals) for any unmapped area
"""

from typing import Optional
import warnings


# =============================================================================
# ECO DOMAIN DEFINITIONS
# =============================================================================

ECO_DOMAIN_NAMES = {
    1: "PM Fundamentals & Core Concepts",
    2: "Predictive, Plan-Based Methodologies",
    3: "Agile Frameworks/Methodologies",
    4: "Business Analysis Frameworks",
}

ECO_DOMAIN_WEIGHTS = {
    1: 36,  # PM Fundamentals & Core Concepts
    2: 17,  # Predictive, Plan-Based Methodologies
    3: 20,  # Agile Frameworks/Methodologies
    4: 27,  # Business Analysis Frameworks
}


# =============================================================================
# KNOWLEDGE AREA TO ECO DOMAIN MAPPING
# =============================================================================
# This is the comprehensive mapping of all knowledge_area values to ECO domains.
# IMPORTANT: Add new knowledge areas here BEFORE using them in flashcards/quizzes.

ECO_DOMAIN_MAPPING = {
    # -------------------------------------------------------------------------
    # Domain 1: PM Fundamentals & Core Concepts (36%)
    # Foundational PM concepts, principles, life cycles, glossary terms
    # -------------------------------------------------------------------------
    "Fundamentals": 1,
    "PM Fundamentals": 1,
    "Principles": 1,
    "Life Cycles": 1,
    "Glossary": 1,
    "Project Management Basics": 1,
    "Ethics": 1,
    "PMI Code of Ethics": 1,

    # -------------------------------------------------------------------------
    # Domain 2: Predictive, Plan-Based Methodologies (17%)
    # Traditional/waterfall PM, PMBOK Performance Domains
    # -------------------------------------------------------------------------
    "Finance": 2,
    "Governance": 2,
    "Procurement": 2,
    "Resources": 2,
    "Risk": 2,
    "Schedule": 2,
    "Scope": 2,
    "Stakeholders": 2,
    "Stakeholder Management": 2,  # Alternate naming
    "Tailoring": 2,
    "Tools & Techniques": 2,
    "Quality": 2,
    "Communications": 2,
    "Integration": 2,
    "Integration Management": 2,  # Alternate naming

    # -------------------------------------------------------------------------
    # Domain 3: Agile Frameworks/Methodologies (20%)
    # Scrum, Kanban, XP, Lean, and all Agile concepts
    # -------------------------------------------------------------------------
    # Core Agile frameworks
    "Agile Frameworks": 3,
    "Agile Fundamentals": 3,
    "Scrum": 3,
    "Kanban": 3,
    "XP": 3,
    "Lean": 3,
    "Lean/Agile": 3,

    # Agile roles and teams
    "Agile Leadership": 3,
    "Agile Teams": 3,

    # Agile practices and techniques
    "Agile Practices": 3,
    "Agile Planning": 3,
    "Agile Estimation": 3,
    "Agile Prioritization": 3,
    "Agile Requirements": 3,
    "Agile Quality": 3,
    "Agile Value": 3,

    # Agile artifacts and metrics
    "Scrum Artifacts": 3,
    "Agile Metrics": 3,
    "Agile Principles": 3,

    # Continuous improvement (Agile/Lean concept)
    "Continuous Improvement": 3,
    "Kaizen": 3,

    # -------------------------------------------------------------------------
    # Domain 4: Business Analysis Frameworks (27%)
    # BA techniques, requirements, stakeholder analysis, solution design
    # -------------------------------------------------------------------------
    "Elicitation": 4,
    "Needs Assessment": 4,
    "Product Management": 4,
    "Requirements": 4,
    "Requirements Management": 4,
    "Root Cause Analysis": 4,
    "Solution Design": 4,
    "Solution Evaluation": 4,
    "Stakeholder Analysis": 4,
    "Business Analysis": 4,
    "BA Fundamentals": 4,  # Alternate naming
    "Traceability": 4,
    "Change Control": 4,
}

# Default domain for unmapped knowledge areas
DEFAULT_ECO_DOMAIN = 1  # PM Fundamentals

# Track unmapped areas encountered (for debugging/development)
_unmapped_areas_encountered: set = set()


# =============================================================================
# DOMAIN LOOKUP FUNCTIONS
# =============================================================================

def get_eco_domain(knowledge_area: str, warn_unmapped: bool = False) -> int:
    """
    Get the ECO domain for a knowledge area.

    Args:
        knowledge_area: The knowledge_area string from a flashcard or quiz question
        warn_unmapped: If True, emit a warning for unmapped areas (useful during development)

    Returns:
        ECO domain number (1-4). Defaults to Domain 1 (PM Fundamentals) if unknown.

    Note:
        If you see warnings about unmapped areas, add them to ECO_DOMAIN_MAPPING above.
    """
    domain = ECO_DOMAIN_MAPPING.get(knowledge_area)

    if domain is None:
        _unmapped_areas_encountered.add(knowledge_area)
        if warn_unmapped:
            warnings.warn(
                f"Unmapped knowledge_area '{knowledge_area}' - defaulting to Domain {DEFAULT_ECO_DOMAIN}. "
                f"Add this to ECO_DOMAIN_MAPPING in eco_domains.py",
                UserWarning,
                stacklevel=2
            )
        return DEFAULT_ECO_DOMAIN

    return domain


def get_deck_eco_domain(deck_name: str) -> int:
    """
    Get ECO domain based on deck filename.

    This function maps entire deck files to domains based on naming conventions.
    Used when we want to assign all cards in a deck to a single domain.

    Args:
        deck_name: The deck filename (without .json extension)

    Returns:
        ECO domain number (1-4)
    """
    deck_lower = deck_name.lower()

    # Domain 3: Agile
    if "agile" in deck_lower:
        return 3

    # Domain 4: Business Analysis
    if "business_analysis" in deck_lower or "ba_" in deck_lower:
        return 4

    # Domain 1: Fundamentals (principles, life cycles, glossary, fundamentals)
    if any(term in deck_lower for term in ["fundamentals", "principles", "life_cycles", "glossary"]):
        return 1

    # Domain 2: Predictive (default for PMBOK performance domain decks)
    # This includes: governance, scope, schedule, finance, stakeholders, resources,
    #                risk, tailoring, tools, procurement
    return 2


# =============================================================================
# VALIDATION AND DEBUGGING FUNCTIONS
# =============================================================================

def validate_knowledge_area(knowledge_area: str) -> bool:
    """
    Check if a knowledge_area is properly mapped.

    Use this during development to ensure new knowledge areas are added to the mapping.

    Args:
        knowledge_area: The knowledge_area to validate

    Returns:
        True if mapped, False if it would fall back to default
    """
    return knowledge_area in ECO_DOMAIN_MAPPING


def get_unmapped_areas() -> set:
    """
    Get all unmapped knowledge areas encountered during runtime.

    Useful for development/debugging to find areas that need to be added to the mapping.

    Returns:
        Set of knowledge_area strings that weren't in ECO_DOMAIN_MAPPING
    """
    return _unmapped_areas_encountered.copy()


def get_all_mapped_areas() -> dict[str, int]:
    """
    Get all currently mapped knowledge areas and their domains.

    Returns:
        Copy of the ECO_DOMAIN_MAPPING dictionary
    """
    return ECO_DOMAIN_MAPPING.copy()


def get_areas_for_domain(domain: int) -> list[str]:
    """
    Get all knowledge areas mapped to a specific domain.

    Args:
        domain: ECO domain number (1-4)

    Returns:
        List of knowledge_area strings for that domain
    """
    return [area for area, d in ECO_DOMAIN_MAPPING.items() if d == domain]


# =============================================================================
# DOMAIN STATISTICS HELPERS
# =============================================================================

def get_domain_weight(domain: int) -> int:
    """Get the exam weight percentage for a domain."""
    return ECO_DOMAIN_WEIGHTS.get(domain, 0)


def get_domain_name(domain: int) -> str:
    """Get the full name of a domain."""
    return ECO_DOMAIN_NAMES.get(domain, f"Unknown Domain {domain}")
