# ABOUTME: Quiz system with interleaving and Bloom's taxonomy levels.
# ABOUTME: Implements scenario-based questions for application-level learning with ECO domain weighting.

import json
from pathlib import Path
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import random

# Import ECO domain mappings from single source of truth
# NOTE: All ECO domain logic is centralized in eco_domains.py to prevent inconsistencies
from eco_domains import (
    ECO_DOMAIN_MAPPING,
    ECO_DOMAIN_WEIGHTS,
    get_eco_domain,
)


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


@dataclass
class QuizResult:
    """Result of a single quiz session."""
    quiz_id: str
    timestamp: str
    total_questions: int
    correct: int
    by_knowledge_area: dict
    by_difficulty: dict
    missed_questions: list[str]  # Question IDs for review


def load_questions(quiz_path: Path) -> list[Question]:
    """Load quiz questions from JSON file."""
    if not quiz_path.exists():
        return []

    with open(quiz_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return [Question(**q) for q in data.get('questions', [])]


def create_interleaved_quiz(
    all_questions: list[Question],
    num_questions: int = 20,
    knowledge_areas: list[str] = None
) -> list[Question]:
    """
    Create a quiz with interleaved questions from different knowledge areas.
    This forces discrimination between concepts (evidence-based).
    """
    available = all_questions.copy()

    # Filter by knowledge areas if specified
    if knowledge_areas:
        available = [q for q in available if q.knowledge_area in knowledge_areas]

    if len(available) <= num_questions:
        selected = available
    else:
        # Try to balance across knowledge areas
        by_area = {}
        for q in available:
            if q.knowledge_area not in by_area:
                by_area[q.knowledge_area] = []
            by_area[q.knowledge_area].append(q)

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

    # Shuffle final selection for true interleaving
    random.shuffle(selected)
    return selected


def create_eco_weighted_quiz(
    all_questions: list[Question],
    num_questions: int = 20,
    use_weights: bool = True
) -> list[Question]:
    """
    Create a quiz with questions weighted by ECO domain percentages.

    ECO Domain Weights:
    - Domain 1 (Fundamentals): 36% -> ~7 questions in a 20-question quiz
    - Domain 2 (Predictive): 17% -> ~3 questions
    - Domain 3 (Agile): 20% -> ~4 questions
    - Domain 4 (BA): 27% -> ~5 questions

    Falls back to round-robin if not enough questions in a domain.
    """
    if not use_weights:
        return create_interleaved_quiz(all_questions, num_questions)

    available = all_questions.copy()

    # Group questions by ECO domain
    by_domain = {1: [], 2: [], 3: [], 4: []}
    for q in available:
        domain = get_eco_domain(q.knowledge_area)
        by_domain[domain].append(q)

    # Calculate target questions per domain based on weights
    targets = {}
    remaining = num_questions
    for domain in [1, 2, 3, 4]:
        weight = ECO_DOMAIN_WEIGHTS[domain]
        target = round(num_questions * weight / 100)
        targets[domain] = min(target, len(by_domain[domain]))  # Cap at available
        remaining -= targets[domain]

    # Distribute any remaining questions to domains with available questions
    for domain in [4, 3, 1, 2]:  # Priority order: BA, Agile, Fundamentals, Predictive
        while remaining > 0 and len(by_domain[domain]) > targets[domain]:
            targets[domain] += 1
            remaining -= 1

    # Select questions from each domain
    selected = []
    for domain, target in targets.items():
        domain_questions = by_domain[domain]
        if len(domain_questions) <= target:
            selected.extend(domain_questions)
        else:
            selected.extend(random.sample(domain_questions, target))

    # If we still don't have enough, fill from any remaining
    if len(selected) < num_questions:
        used_ids = {q.id for q in selected}
        remaining_qs = [q for q in available if q.id not in used_ids]
        needed = num_questions - len(selected)
        if remaining_qs:
            selected.extend(random.sample(remaining_qs, min(needed, len(remaining_qs))))

    # Shuffle for interleaving
    random.shuffle(selected)
    return selected


def grade_quiz(
    questions: list[Question],
    answers: list[int]  # User's answers (indices)
) -> QuizResult:
    """Grade a completed quiz and return detailed results."""
    correct = 0
    by_area = {}
    by_difficulty = {}
    missed = []

    for q, user_answer in zip(questions, answers):
        is_correct = user_answer == q.correct_answer

        if is_correct:
            correct += 1
        else:
            missed.append(q.id)

        # Track by knowledge area
        if q.knowledge_area not in by_area:
            by_area[q.knowledge_area] = {'correct': 0, 'total': 0}
        by_area[q.knowledge_area]['total'] += 1
        if is_correct:
            by_area[q.knowledge_area]['correct'] += 1

        # Track by difficulty
        if q.difficulty not in by_difficulty:
            by_difficulty[q.difficulty] = {'correct': 0, 'total': 0}
        by_difficulty[q.difficulty]['total'] += 1
        if is_correct:
            by_difficulty[q.difficulty]['correct'] += 1

    return QuizResult(
        quiz_id=datetime.now().strftime("%Y%m%d_%H%M%S"),
        timestamp=datetime.now().isoformat(),
        total_questions=len(questions),
        correct=correct,
        by_knowledge_area=by_area,
        by_difficulty=by_difficulty,
        missed_questions=missed
    )


def save_result(result: QuizResult, results_path: Path):
    """Append quiz result to history file."""
    results_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing results
    if results_path.exists():
        with open(results_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {'results': []}

    data['results'].append(asdict(result))

    with open(results_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def get_weak_areas(results_path: Path, threshold: float = 0.7) -> list[str]:
    """Identify knowledge areas with accuracy below threshold."""
    if not results_path.exists():
        return []

    with open(results_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Aggregate across all results
    totals = {}
    for result in data.get('results', []):
        for area, stats in result.get('by_knowledge_area', {}).items():
            if area not in totals:
                totals[area] = {'correct': 0, 'total': 0}
            totals[area]['correct'] += stats['correct']
            totals[area]['total'] += stats['total']

    # Find weak areas
    weak = []
    for area, stats in totals.items():
        if stats['total'] > 0:
            accuracy = stats['correct'] / stats['total']
            if accuracy < threshold:
                weak.append((area, accuracy))

    weak.sort(key=lambda x: x[1])  # Sort by lowest accuracy
    return [area for area, _ in weak]
