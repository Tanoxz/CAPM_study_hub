# ABOUTME: Flashcard system with SM-2 spaced repetition algorithm.
# ABOUTME: Implements evidence-based retrieval practice and spacing.

import json
from pathlib import Path
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
from typing import Optional
import random

# Import ECO domain mappings from single source of truth
# NOTE: All ECO domain logic is centralized in eco_domains.py to prevent inconsistencies
from eco_domains import (
    ECO_DOMAIN_MAPPING,
    ECO_DOMAIN_WEIGHTS,
    ECO_DOMAIN_NAMES,
    get_eco_domain,
    get_deck_eco_domain,
)


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

    def __post_init__(self):
        if self.related_concepts is None:
            self.related_concepts = []
        if self.next_review is None:
            self.next_review = datetime.now().isoformat()


def sm2_update(card: Card, quality: int) -> Card:
    """
    Update card using SM-2 algorithm.

    Quality ratings:
    0 - Complete blackout, no recall
    1 - Incorrect, but recognized answer
    2 - Incorrect, but easy to recall once seen
    3 - Correct with serious difficulty
    4 - Correct with some hesitation
    5 - Perfect recall
    """
    if quality < 0 or quality > 5:
        raise ValueError("Quality must be 0-5")

    # Update easiness factor
    card.easiness = max(1.3, card.easiness + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

    if quality < 3:
        # Failed recall - reset repetitions
        card.repetitions = 0
        card.interval = 1
    else:
        # Successful recall
        if card.repetitions == 0:
            card.interval = 1
        elif card.repetitions == 1:
            card.interval = 6
        else:
            card.interval = round(card.interval * card.easiness)
        card.repetitions += 1

    # Set next review date
    next_date = datetime.now() + timedelta(days=card.interval)
    card.next_review = next_date.isoformat()

    return card


def get_due_cards(cards: list[Card], limit: int = 20) -> list[Card]:
    """Get cards due for review, prioritizing overdue and mixing knowledge areas."""
    now = datetime.now()

    due = []
    for card in cards:
        review_date = datetime.fromisoformat(card.next_review)
        if review_date <= now:
            days_overdue = (now - review_date).days
            due.append((card, days_overdue))

    # Sort by most overdue first, but then shuffle within groups for interleaving
    due.sort(key=lambda x: -x[1])

    # Take top cards but shuffle to interleave knowledge areas
    selected = [c[0] for c in due[:limit * 2]]  # Get extra for shuffling
    random.shuffle(selected)

    return selected[:limit]


def load_deck(deck_path: Path) -> list[Card]:
    """Load flashcard deck from JSON file."""
    if not deck_path.exists():
        return []

    with open(deck_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return [Card(**card_data) for card_data in data.get('cards', [])]


def save_deck(cards: list[Card], deck_path: Path):
    """Save flashcard deck to JSON file."""
    deck_path.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'version': 1,
        'updated': datetime.now().isoformat(),
        'cards': [asdict(card) for card in cards]
    }

    with open(deck_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_deck_stats(cards: list[Card]) -> dict:
    """Get statistics about a deck."""
    now = datetime.now()

    due_count = sum(1 for c in cards if datetime.fromisoformat(c.next_review) <= now)

    by_area = {}
    for card in cards:
        area = card.knowledge_area
        if area not in by_area:
            by_area[area] = {'total': 0, 'due': 0, 'mastered': 0}
        by_area[area]['total'] += 1
        if datetime.fromisoformat(card.next_review) <= now:
            by_area[area]['due'] += 1
        if card.interval >= 21:  # Consider mastered if interval > 3 weeks
            by_area[area]['mastered'] += 1

    return {
        'total_cards': len(cards),
        'due_today': due_count,
        'by_knowledge_area': by_area,
        'avg_easiness': sum(c.easiness for c in cards) / len(cards) if cards else 0
    }


def get_eco_domain_stats(cards: list[Card]) -> dict:
    """Get statistics grouped by ECO domain."""
    now = datetime.now()

    by_domain = {1: {'total': 0, 'due': 0, 'mastered': 0},
                 2: {'total': 0, 'due': 0, 'mastered': 0},
                 3: {'total': 0, 'due': 0, 'mastered': 0},
                 4: {'total': 0, 'due': 0, 'mastered': 0}}

    for card in cards:
        domain = get_eco_domain(card.knowledge_area)
        by_domain[domain]['total'] += 1
        if datetime.fromisoformat(card.next_review) <= now:
            by_domain[domain]['due'] += 1
        if card.interval >= 21:
            by_domain[domain]['mastered'] += 1

    return by_domain
