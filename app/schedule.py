# ABOUTME: Study schedule system with exam countdown, progress tracking, and recommendations.
# ABOUTME: Implements daily study plans (90min/day), PM PrepCast video tracking, and smart recommendations.

import json
from pathlib import Path
from datetime import datetime, date, timedelta
from dataclasses import dataclass, asdict
from typing import Optional
import re


# ECO Domain Weights (as percentages) - matches CAPM exam distribution
ECO_DOMAIN_WEIGHTS = {
    1: 36,  # PM Fundamentals & Core Concepts
    2: 17,  # Predictive, Plan-Based Methodologies
    3: 20,  # Agile Frameworks/Methodologies
    4: 27,  # Business Analysis Frameworks
}

ECO_DOMAIN_NAMES = {
    1: "PM Fundamentals & Core Concepts",
    2: "Predictive, Plan-Based Methodologies",
    3: "Agile Frameworks/Methodologies",
    4: "Business Analysis Frameworks",
}


def get_eco_domain_from_topic(topic_name: str, topic_id: str = None) -> int:
    """Extract ECO domain from topic name or ID. Defaults to 2 (Predictive)."""
    # Check topic name for ECO Domain N pattern
    match = re.search(r'ECO Domain (\d)', topic_name)
    if match:
        return int(match.group(1))

    # Check topic_id for known patterns
    if topic_id:
        topic_lower = topic_id.lower()
        if any(t in topic_lower for t in ['fundamental', 'principles', 'life_cycle', 'glossary']):
            return 1
        if any(t in topic_lower for t in ['agile']):
            return 3
        if any(t in topic_lower for t in ['business_analysis', 'ba_', 'elicitation', 'requirements']):
            return 4

    # Default to Domain 2 (Predictive/PMBOK)
    return 2


@dataclass
class ScheduleConfig:
    """User's schedule configuration."""
    version: int
    certification: str
    exam_date: Optional[str]
    exam_date_confirmed: bool
    target_weeks: int
    daily_goal_minutes: int
    weekly_goal_days: int
    created: Optional[str]
    updated: Optional[str]


@dataclass
class Topic:
    """A study topic with associated materials."""
    id: str
    name: str
    description: str
    study_guide: Optional[str]
    flashcard_deck: Optional[str]
    quiz_bank: Optional[str]
    estimated_read_minutes: int
    priority: int
    prerequisites: list
    order: int
    eco_domain: Optional[int] = None
    eco_weight: Optional[int] = None


@dataclass
class Streaks:
    """Streak tracking data."""
    current_streak: int
    longest_streak: int
    last_study_date: Optional[str]
    streak_history: list


def load_config(config_path: Path) -> ScheduleConfig:
    """Load schedule configuration from JSON file."""
    if not config_path.exists():
        return ScheduleConfig(
            version=1,
            certification="CAPM",
            exam_date=None,
            exam_date_confirmed=False,
            target_weeks=8,
            daily_goal_minutes=30,
            weekly_goal_days=5,
            created=None,
            updated=None
        )

    with open(config_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return ScheduleConfig(**data)


def save_config(config: ScheduleConfig, config_path: Path):
    """Save schedule configuration to JSON file."""
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config.updated = datetime.now().isoformat()
    if config.created is None:
        config.created = config.updated

    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(asdict(config), f, indent=2)


def load_topics(topics_path: Path) -> list[Topic]:
    """Load topic registry from JSON file."""
    if not topics_path.exists():
        return []

    with open(topics_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    return [Topic(**t) for t in data.get('topics', [])]


def load_progress(progress_path: Path) -> dict:
    """Load progress data from JSON file."""
    if not progress_path.exists():
        return {
            "version": 1,
            "updated": None,
            "reading_progress": {},
            "sessions": [],
            "streaks": {
                "current_streak": 0,
                "longest_streak": 0,
                "last_study_date": None,
                "streak_history": []
            },
            "daily_summary": {},
            "weekly_summary": {}
        }

    with open(progress_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_progress(progress: dict, progress_path: Path):
    """Save progress data to JSON file."""
    progress_path.parent.mkdir(parents=True, exist_ok=True)
    progress['updated'] = datetime.now().isoformat()

    with open(progress_path, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=2)


def get_days_until_exam(config: ScheduleConfig) -> Optional[int]:
    """Calculate days remaining until exam date."""
    if not config.exam_date:
        return None

    exam = date.fromisoformat(config.exam_date)
    today = date.today()
    delta = exam - today
    return delta.days


def get_weeks_until_exam(config: ScheduleConfig) -> Optional[int]:
    """Calculate weeks remaining until exam date."""
    days = get_days_until_exam(config)
    if days is None:
        return None
    return max(0, days // 7)


def get_study_stats(progress: dict) -> dict:
    """Calculate study statistics from progress data."""
    sessions = progress.get('sessions', [])
    streaks = progress.get('streaks', {})
    daily = progress.get('daily_summary', {})

    # Today's stats
    today_str = date.today().isoformat()
    today_data = daily.get(today_str, {"total_minutes": 0, "sessions_count": 0})

    # Total stats
    total_minutes = sum(s.get('duration_minutes', 0) for s in sessions)
    total_sessions = len(sessions)

    # Reading progress
    reading = progress.get('reading_progress', {})
    chapters_read = sum(1 for r in reading.values() if r.get('status') == 'completed')
    chapters_in_progress = sum(1 for r in reading.values() if r.get('status') == 'in_progress')

    return {
        "today_minutes": today_data.get("total_minutes", 0),
        "today_sessions": today_data.get("sessions_count", 0),
        "total_minutes": total_minutes,
        "total_sessions": total_sessions,
        "current_streak": streaks.get("current_streak", 0),
        "longest_streak": streaks.get("longest_streak", 0),
        "chapters_read": chapters_read,
        "chapters_in_progress": chapters_in_progress
    }


def update_streak(progress: dict) -> dict:
    """Update streak based on today's activity."""
    streaks = progress.get('streaks', {
        "current_streak": 0,
        "longest_streak": 0,
        "last_study_date": None,
        "streak_history": []
    })

    today_str = date.today().isoformat()
    last_study = streaks.get('last_study_date')

    if last_study == today_str:
        # Already studied today, no change
        return progress

    if last_study:
        last_date = date.fromisoformat(last_study)
        days_since = (date.today() - last_date).days

        if days_since == 1:
            # Consecutive day - extend streak
            streaks['current_streak'] += 1
        elif days_since > 1:
            # Streak broken - record old streak and reset
            if streaks['current_streak'] > 0:
                streaks['streak_history'].append({
                    "start": (last_date - timedelta(days=streaks['current_streak']-1)).isoformat(),
                    "end": last_study,
                    "days": streaks['current_streak']
                })
            streaks['current_streak'] = 1
    else:
        # First ever study session
        streaks['current_streak'] = 1

    # Update longest streak
    if streaks['current_streak'] > streaks.get('longest_streak', 0):
        streaks['longest_streak'] = streaks['current_streak']

    streaks['last_study_date'] = today_str
    progress['streaks'] = streaks

    return progress


def log_session(progress: dict, session_type: str, topic_id: Optional[str],
                duration_minutes: int, details: dict = None) -> dict:
    """Log a study session."""
    session = {
        "id": f"sess_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
        "timestamp": datetime.now().isoformat(),
        "type": session_type,
        "topic_id": topic_id,
        "duration_minutes": duration_minutes,
        "details": details or {}
    }

    progress['sessions'].append(session)

    # Update daily summary
    today_str = date.today().isoformat()
    if today_str not in progress['daily_summary']:
        progress['daily_summary'][today_str] = {
            "total_minutes": 0,
            "sessions_count": 0,
            "activities": [],
            "topics_touched": [],
            "goal_met": False
        }

    daily = progress['daily_summary'][today_str]
    daily['total_minutes'] += duration_minutes
    daily['sessions_count'] += 1

    if session_type not in daily['activities']:
        daily['activities'].append(session_type)

    if topic_id and topic_id not in daily['topics_touched']:
        daily['topics_touched'].append(topic_id)

    # Update streak
    progress = update_streak(progress)

    return progress


def get_topic_by_id(topics: list[Topic], topic_id: str) -> Optional[Topic]:
    """Get a topic by its ID."""
    for topic in topics:
        if topic.id == topic_id:
            return topic
    return None


def get_reading_status(progress: dict, topic_id: str) -> str:
    """Get reading status for a topic."""
    reading = progress.get('reading_progress', {})
    topic_progress = reading.get(topic_id, {})
    return topic_progress.get('status', 'not_started')


def mark_reading_started(progress: dict, topic_id: str) -> dict:
    """Mark a topic's reading as started."""
    if 'reading_progress' not in progress:
        progress['reading_progress'] = {}

    if topic_id not in progress['reading_progress']:
        progress['reading_progress'][topic_id] = {
            "status": "in_progress",
            "started_at": datetime.now().isoformat(),
            "completed_at": None,
            "time_spent_minutes": 0,
            "comprehension_checked": False,
            "notes": ""
        }
    elif progress['reading_progress'][topic_id]['status'] == 'not_started':
        progress['reading_progress'][topic_id]['status'] = 'in_progress'
        progress['reading_progress'][topic_id]['started_at'] = datetime.now().isoformat()

    return progress


def mark_reading_completed(progress: dict, topic_id: str) -> dict:
    """Mark a topic's reading as completed."""
    if 'reading_progress' not in progress:
        progress['reading_progress'] = {}

    if topic_id not in progress['reading_progress']:
        progress['reading_progress'][topic_id] = {
            "status": "completed",
            "started_at": datetime.now().isoformat(),
            "completed_at": datetime.now().isoformat(),
            "time_spent_minutes": 0,
            "comprehension_checked": False,
            "notes": ""
        }
    else:
        progress['reading_progress'][topic_id]['status'] = 'completed'
        progress['reading_progress'][topic_id]['completed_at'] = datetime.now().isoformat()

    return progress


# =============================================================================
# STUDY PLAN GENERATION
# =============================================================================

@dataclass
class Activity:
    """A single planned study activity."""
    id: str
    activity_type: str  # read, flashcards, quiz, review
    topic_id: Optional[str]
    description: str
    target_date: str
    status: str  # pending, completed, skipped
    completed_date: Optional[str]


@dataclass
class WeekPlan:
    """A week's worth of planned activities."""
    week_number: int
    start_date: str
    end_date: str
    theme: str
    topic_ids: list
    activities: list  # List of Activity dicts


def load_plan(plan_path: Path) -> Optional[dict]:
    """Load study plan from JSON file."""
    if not plan_path.exists():
        return None

    with open(plan_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_plan(plan: dict, plan_path: Path):
    """Save study plan to JSON file."""
    plan_path.parent.mkdir(parents=True, exist_ok=True)

    with open(plan_path, 'w', encoding='utf-8') as f:
        json.dump(plan, f, indent=2)


def plan_needs_regeneration(plan: Optional[dict], config: ScheduleConfig) -> bool:
    """Check if the plan needs to be regenerated."""
    if plan is None:
        return True

    # Check if exam date changed
    if plan.get('exam_date') != config.exam_date:
        return True

    # Check if plan is from a different certification
    if plan.get('certification') != config.certification:
        return True

    return False


def generate_study_plan(config: ScheduleConfig, topics: list[Topic]) -> dict:
    """
    Generate a study plan distributing topics across available weeks.

    Principles:
    - Priority 1 topics get scheduled first
    - Respect topic order (which handles prerequisites)
    - Pattern: Read → Flashcards → (Quiz if available)
    - Final week is review only
    - Balance workload across days
    """
    from math import ceil

    today = date.today()

    # Determine end date
    if config.exam_date:
        exam = date.fromisoformat(config.exam_date)
        total_days = (exam - today).days
    else:
        total_days = config.target_weeks * 7

    total_weeks = max(1, total_days // 7)

    # Reserve final week for review
    study_weeks = max(1, total_weeks - 1)

    # Sort topics by order (respects prerequisites)
    ordered_topics = sorted(topics, key=lambda t: (t.priority, t.order))

    # Filter to topics with study guides
    study_topics = [t for t in ordered_topics if t.study_guide]

    # Calculate topics per week
    topics_per_week = ceil(len(study_topics) / study_weeks) if study_weeks > 0 else len(study_topics)

    # Group topics into weeks
    def chunk_list(lst, size):
        for i in range(0, len(lst), size):
            yield lst[i:i + size]

    topic_groups = list(chunk_list(study_topics, topics_per_week))

    # Build the plan
    plan = {
        "version": 1,
        "generated": datetime.now().isoformat(),
        "certification": config.certification,
        "exam_date": config.exam_date,
        "total_weeks": total_weeks,
        "weeks": []
    }

    # Week themes based on content
    def get_week_theme(week_topics: list[Topic]) -> str:
        if len(week_topics) == 0:
            return "Review"
        names = [t.name for t in week_topics]
        if any("Principle" in n for n in names):
            return "Foundations"
        if any("Scope" in n or "Schedule" in n or "Finance" in n for n in names):
            return "Planning Domains"
        if any("Stakeholder" in n or "Resource" in n for n in names):
            return "People & Resources"
        if any("Risk" in n or "Procurement" in n for n in names):
            return "Risk & Procurement"
        if any("Tailoring" in n or "Tools" in n for n in names):
            return "Advanced Topics"
        return "Core Topics"

    activity_counter = 0

    for week_idx, week_topics in enumerate(topic_groups):
        week_num = week_idx + 1
        week_start = today + timedelta(days=week_idx * 7)
        week_end = week_start + timedelta(days=6)

        week = {
            "week_number": week_num,
            "start_date": week_start.isoformat(),
            "end_date": week_end.isoformat(),
            "theme": get_week_theme(week_topics),
            "topic_ids": [t.id for t in week_topics],
            "activities": []
        }

        # Schedule activities within the week
        day_offset = 0
        days_per_topic = max(1, config.weekly_goal_days // len(week_topics)) if week_topics else 1

        for topic in week_topics:
            # Add reading activity
            activity_counter += 1
            read_date = week_start + timedelta(days=day_offset)
            week["activities"].append({
                "id": f"w{week_num}_a{activity_counter}",
                "activity_type": "read",
                "topic_id": topic.id,
                "description": f"Read: {topic.name}",
                "target_date": read_date.isoformat(),
                "status": "pending",
                "completed_date": None
            })

            # Add flashcards activity if deck exists
            if topic.flashcard_deck:
                activity_counter += 1
                fc_date = week_start + timedelta(days=day_offset + 1)
                week["activities"].append({
                    "id": f"w{week_num}_a{activity_counter}",
                    "activity_type": "flashcards",
                    "topic_id": topic.id,
                    "description": f"Flashcards: {topic.name}",
                    "target_date": fc_date.isoformat(),
                    "status": "pending",
                    "completed_date": None
                })

            day_offset += days_per_topic

        # Add end-of-week quiz if any topics have quizzes
        quiz_topics = [t for t in week_topics if t.quiz_bank]
        if quiz_topics:
            activity_counter += 1
            quiz_date = week_end
            quiz_names = ", ".join([t.name for t in quiz_topics[:2]])
            if len(quiz_topics) > 2:
                quiz_names += f" +{len(quiz_topics) - 2} more"
            week["activities"].append({
                "id": f"w{week_num}_a{activity_counter}",
                "activity_type": "quiz",
                "topic_id": None,
                "description": f"Quiz: {quiz_names}",
                "target_date": quiz_date.isoformat(),
                "status": "pending",
                "completed_date": None
            })

        plan["weeks"].append(week)

    # Add final review week
    if total_weeks > 1:
        final_week_start = today + timedelta(days=(total_weeks - 1) * 7)
        final_week_end = final_week_start + timedelta(days=6)

        activity_counter += 1
        final_week = {
            "week_number": total_weeks,
            "start_date": final_week_start.isoformat(),
            "end_date": final_week_end.isoformat(),
            "theme": "Final Review",
            "topic_ids": [],
            "activities": [
                {
                    "id": f"w{total_weeks}_a{activity_counter}",
                    "activity_type": "quiz",
                    "topic_id": None,
                    "description": "Full practice exam simulation",
                    "target_date": final_week_start.isoformat(),
                    "status": "pending",
                    "completed_date": None
                },
                {
                    "id": f"w{total_weeks}_a{activity_counter + 1}",
                    "activity_type": "review",
                    "topic_id": None,
                    "description": "Focus on weak areas from quizzes",
                    "target_date": (final_week_start + timedelta(days=2)).isoformat(),
                    "status": "pending",
                    "completed_date": None
                },
                {
                    "id": f"w{total_weeks}_a{activity_counter + 2}",
                    "activity_type": "review",
                    "topic_id": None,
                    "description": "Light review, rest before exam",
                    "target_date": (final_week_end - timedelta(days=1)).isoformat(),
                    "status": "pending",
                    "completed_date": None
                }
            ]
        }
        plan["weeks"].append(final_week)

    return plan


def get_current_week(plan: dict) -> Optional[dict]:
    """Get the current week from the plan based on today's date."""
    if not plan or not plan.get('weeks'):
        return None

    today = date.today()

    for week in plan['weeks']:
        start = date.fromisoformat(week['start_date'])
        end = date.fromisoformat(week['end_date'])

        if start <= today <= end:
            return week

    # If we're past all weeks, return the last one
    if plan['weeks']:
        last_week = plan['weeks'][-1]
        if today > date.fromisoformat(last_week['end_date']):
            return last_week

    # If we're before the first week, return the first one
    if plan['weeks']:
        first_week = plan['weeks'][0]
        if today < date.fromisoformat(first_week['start_date']):
            return first_week

    return None


def get_week_progress(week: dict) -> dict:
    """Calculate progress statistics for a week."""
    activities = week.get('activities', [])
    total = len(activities)
    completed = sum(1 for a in activities if a.get('status') == 'completed')
    pending = sum(1 for a in activities if a.get('status') == 'pending')

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "percent": int((completed / total) * 100) if total > 0 else 0
    }


def mark_activity_completed(plan: dict, activity_id: str) -> dict:
    """Mark a plan activity as completed."""
    for week in plan.get('weeks', []):
        for activity in week.get('activities', []):
            if activity.get('id') == activity_id:
                activity['status'] = 'completed'
                activity['completed_date'] = datetime.now().isoformat()
                return plan
    return plan


def mark_activity_pending(plan: dict, activity_id: str) -> dict:
    """Reset a plan activity to pending."""
    for week in plan.get('weeks', []):
        for activity in week.get('activities', []):
            if activity.get('id') == activity_id:
                activity['status'] = 'pending'
                activity['completed_date'] = None
                return plan
    return plan


def get_overdue_activities(plan: dict) -> list:
    """Get activities that are past their target date but not completed."""
    if not plan:
        return []

    today = date.today()
    overdue = []

    for week in plan.get('weeks', []):
        for activity in week.get('activities', []):
            if activity.get('status') == 'pending':
                target = date.fromisoformat(activity.get('target_date', today.isoformat()))
                if target < today:
                    overdue.append(activity)

    return overdue


def get_today_activities(plan: dict) -> list:
    """Get activities scheduled for today."""
    if not plan:
        return []

    today_str = date.today().isoformat()
    activities = []

    for week in plan.get('weeks', []):
        for activity in week.get('activities', []):
            if activity.get('target_date') == today_str:
                activities.append(activity)

    return activities


def reschedule_activity(plan: dict, activity_id: str, new_date: str) -> dict:
    """Reschedule a plan activity to a new date."""
    for week in plan.get('weeks', []):
        for activity in week.get('activities', []):
            if activity.get('id') == activity_id:
                activity['target_date'] = new_date
                return plan
    return plan


def reschedule_overdue_to_today(plan: dict) -> dict:
    """Reschedule all overdue activities to today."""
    today_str = date.today().isoformat()
    overdue = get_overdue_activities(plan)

    for overdue_activity in overdue:
        plan = reschedule_activity(plan, overdue_activity['id'], today_str)

    return plan


def skip_activity(plan: dict, activity_id: str) -> dict:
    """Mark a plan activity as skipped."""
    for week in plan.get('weeks', []):
        for activity in week.get('activities', []):
            if activity.get('id') == activity_id:
                activity['status'] = 'skipped'
                activity['completed_date'] = datetime.now().isoformat()
                return plan
    return plan


def get_plan_stats(plan: dict) -> dict:
    """Get overall plan statistics."""
    if not plan:
        return {"total": 0, "completed": 0, "pending": 0, "skipped": 0, "overdue": 0}

    total = 0
    completed = 0
    pending = 0
    skipped = 0

    for week in plan.get('weeks', []):
        for activity in week.get('activities', []):
            total += 1
            status = activity.get('status', 'pending')
            if status == 'completed':
                completed += 1
            elif status == 'skipped':
                skipped += 1
            else:
                pending += 1

    overdue = len(get_overdue_activities(plan))

    return {
        "total": total,
        "completed": completed,
        "pending": pending,
        "skipped": skipped,
        "overdue": overdue,
        "percent": int((completed / total) * 100) if total > 0 else 0
    }


# =============================================================================
# PM PREPCAST VIDEO TRACKING
# =============================================================================

@dataclass
class PrepCastLesson:
    """A PM PrepCast video lesson."""
    lesson_id: str
    module_id: str
    module_title: str
    title: str
    format: str
    is_core: bool
    duration_minutes: int
    eco_domain: str
    status: str  # not_watched, watched, rewatching
    watched_date: Optional[str]
    comprehension_rating: Optional[int]
    notes: str


def load_prepcast_lessons(lessons_path: Path) -> dict:
    """Load PM PrepCast lessons data."""
    if not lessons_path.exists():
        return {"lessons": [], "total_core_minutes": 0, "total_optional_minutes": 0}

    with open(lessons_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_prepcast_lessons(data: dict, lessons_path: Path):
    """Save PM PrepCast lessons data."""
    lessons_path.parent.mkdir(parents=True, exist_ok=True)
    data['updated'] = datetime.now().isoformat()

    with open(lessons_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


def mark_lesson_watched(data: dict, lesson_id: str, comprehension: int = None) -> dict:
    """Mark a PrepCast lesson as watched."""
    for lesson in data.get('lessons', []):
        if lesson.get('lesson_id') == lesson_id:
            lesson['status'] = 'watched'
            lesson['watched_date'] = date.today().isoformat()
            if comprehension:
                lesson['comprehension_rating'] = comprehension
            break
    return data


def get_next_unwatched_lesson(data: dict, core_only: bool = True) -> Optional[dict]:
    """Get the next unwatched lesson in sequence."""
    for lesson in data.get('lessons', []):
        if lesson.get('status') == 'not_watched':
            if core_only and not lesson.get('is_core', False):
                continue
            return lesson
    return None


def get_prepcast_stats(data: dict) -> dict:
    """Calculate PM PrepCast progress statistics."""
    lessons = data.get('lessons', [])
    core_lessons = [l for l in lessons if l.get('is_core', False)]
    optional_lessons = [l for l in lessons if not l.get('is_core', False)]

    core_watched = [l for l in core_lessons if l.get('status') == 'watched']
    optional_watched = [l for l in optional_lessons if l.get('status') == 'watched']

    core_minutes_watched = sum(l.get('duration_minutes', 0) for l in core_watched)
    optional_minutes_watched = sum(l.get('duration_minutes', 0) for l in optional_watched)

    total_core = data.get('total_core_minutes', 0)
    total_optional = data.get('total_optional_minutes', 0)

    return {
        "core_total": len(core_lessons),
        "core_watched": len(core_watched),
        "core_percent": int(len(core_watched) / len(core_lessons) * 100) if core_lessons else 0,
        "core_minutes_total": total_core,
        "core_minutes_watched": core_minutes_watched,
        "optional_total": len(optional_lessons),
        "optional_watched": len(optional_watched),
        "optional_minutes_watched": optional_minutes_watched,
        "next_lesson": get_next_unwatched_lesson(data)
    }


# =============================================================================
# DAILY STUDY PLAN GENERATION (90 min/day, mixed activities, evidence-based)
# =============================================================================

# Activity durations based on real usage
FLASHCARD_MINUTES_PER_CARD = 1  # 1 minute per card (10 cards = 10 min, 20 cards = 20 min)
QUIZ_SESSION_MINUTES = 20       # One quiz session
REVIEW_SESSION_MINUTES = 15     # Quick review

# Spacing constants (evidence-based)
FLASHCARD_DELAY_DAYS = 1    # Flashcards 1-2 days after learning
QUIZ_DELAY_DAYS = 3         # Quiz 3-5 days after learning


def get_flashcard_deck_card_count(deck_path: Path) -> int:
    """
    Get the number of cards in a flashcard deck.
    Returns the count for timing calculations (1 minute per card).
    """
    if not deck_path.exists():
        return 20  # Default assumption if file not found

    try:
        with open(deck_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return len(data.get('cards', []))
    except (json.JSONDecodeError, IOError):
        return 20  # Default on error


def get_flashcard_duration_minutes(deck_filename: str, flashcards_dir: Path = None) -> int:
    """
    Calculate flashcard review duration based on card count.
    1 minute per card.
    """
    if not deck_filename:
        return 20  # Default for unknown deck

    if flashcards_dir is None:
        # Default path - assumes standard project structure
        flashcards_dir = Path(__file__).parent.parent / "data" / "flashcards"

    deck_path = flashcards_dir / deck_filename
    card_count = get_flashcard_deck_card_count(deck_path)

    return card_count * FLASHCARD_MINUTES_PER_CARD


def get_flashcard_display_name(deck_filename: str) -> str:
    """
    Convert a flashcard deck filename to a consistent display name.
    This ensures schedule activities match the flashcard dropdown names.

    Example: "principles_domain.json" -> "Principles Domain"
    """
    if not deck_filename:
        return "Unknown Deck"

    # Remove .json extension if present
    name = deck_filename.replace('.json', '')

    # Replace underscores with spaces and title case
    return name.replace('_', ' ').title()


def generate_daily_plan(config: ScheduleConfig, topics: list[Topic],
                        prepcast_data: dict, progress: dict,
                        start_date: date = None,
                        flashcards_dir: Path = None) -> dict:
    """
    Generate a daily study plan with proper learning science principles.

    Evidence-based design:
    - Each day has MIXED activity types (no all-watch days)
    - Flashcards come 1-2 days AFTER watch/read (immediate retrieval)
    - Quiz comes 3-5 days after learning (spaced retrieval)
    - Quiz frequency increases as exam approaches
    - Interleaving: mix topics within sessions

    Every day = 90 minutes. No empty days.
    """
    # Start from today by default (or specified date)
    if start_date is None:
        start_date = date.today()

    daily_goal = config.daily_goal_minutes  # 90 minutes

    # Determine total days until exam
    if config.exam_date:
        exam = date.fromisoformat(config.exam_date)
        total_days = (exam - start_date).days
    else:
        total_days = config.target_weeks * 7

    if total_days <= 0:
        total_days = 7

    # Build content pools
    unwatched_videos = []
    for lesson in prepcast_data.get('lessons', []):
        if lesson.get('status') == 'not_watched' and lesson.get('is_core', True):
            unwatched_videos.append({
                "type": "watch",
                "lesson_id": lesson['lesson_id'],
                "title": lesson['title'],
                "duration": lesson['duration_minutes'],
                "eco_domain": lesson.get('eco_domain', 'domain1'),
                "topic_id": lesson.get('module_id')
            })

    reading_progress = progress.get('reading_progress', {})
    unread_chapters = []
    for topic in sorted(topics, key=lambda t: t.order):
        if topic.study_guide:
            status = reading_progress.get(topic.id, {}).get('status', 'not_started')
            if status != 'completed':
                # Get ECO domain from topic data
                eco_domain = topic.eco_domain or get_eco_domain_from_topic(topic.name, topic.id)
                unread_chapters.append({
                    "type": "read",
                    "topic_id": topic.id,
                    "title": f"Read: {topic.name}",
                    "duration": topic.estimated_read_minutes,
                    "has_flashcards": bool(topic.flashcard_deck),
                    "has_quiz": bool(topic.quiz_bank),
                    "deck": topic.flashcard_deck,
                    "quiz": topic.quiz_bank,
                    "eco_domain": eco_domain
                })

    # Available flashcard decks (for topics already learned)
    # Use deck filename for consistent naming with the Flashcards dropdown
    available_flashcard_topics = []
    for topic in topics:
        if topic.flashcard_deck:
            status = reading_progress.get(topic.id, {}).get('status', 'not_started')
            if status == 'completed':
                deck_display_name = get_flashcard_display_name(topic.flashcard_deck)
                deck_duration = get_flashcard_duration_minutes(topic.flashcard_deck, flashcards_dir)
                eco_domain = topic.eco_domain or get_eco_domain_from_topic(topic.name, topic.id)
                available_flashcard_topics.append({
                    "type": "flashcards",
                    "topic_id": topic.id,
                    "title": f"Flashcards: {deck_display_name}",
                    "duration": deck_duration,
                    "deck": topic.flashcard_deck,
                    "eco_domain": eco_domain
                })

    # Available quizzes
    available_quizzes = []
    seen_quizzes = set()
    for topic in topics:
        if topic.quiz_bank and topic.quiz_bank not in seen_quizzes:
            eco_domain = topic.eco_domain or get_eco_domain_from_topic(topic.name, topic.id)
            available_quizzes.append({
                "type": "quiz",
                "topic_id": topic.id,
                "title": f"Quiz: {topic.name}",
                "eco_domain": eco_domain,
                "duration": QUIZ_SESSION_MINUTES,
                "quiz_bank": topic.quiz_bank
            })
            seen_quizzes.add(topic.quiz_bank)

    # Initialize the plan
    plan = {
        "version": 3,
        "generated": datetime.now().isoformat(),
        "certification": config.certification,
        "exam_date": config.exam_date,
        "start_date": start_date.isoformat(),
        "daily_goal_minutes": daily_goal,
        "total_days": total_days,
        "days": []
    }

    # Track what's been scheduled and when
    # Format: {topic_id: {"learned_day": N, "flashcard_day": M, "quiz_day": P}}
    topic_schedule = {}
    activity_counter = 0
    video_idx = 0
    read_idx = 0

    # Calculate study phases
    early_phase_end = total_days // 3       # First third: focus on new content
    middle_phase_end = 2 * total_days // 3  # Middle third: balanced
    # Final third: heavy quiz focus

    for day_offset in range(total_days):
        current_date = start_date + timedelta(days=day_offset)
        day_number = day_offset + 1

        day_plan = {
            "date": current_date.isoformat(),
            "day_number": day_number,
            "target_minutes": daily_goal,
            "activities": []
        }

        remaining_minutes = daily_goal
        day_activities = []

        # Determine phase-based mix
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

        # 1. Add NEW CONTENT (watch or read) - front of day
        new_content_minutes = 0
        while new_content_minutes < new_content_target and remaining_minutes > 0:
            added = False

            # Try to add a video
            if video_idx < len(unwatched_videos):
                video = unwatched_videos[video_idx]
                if video['duration'] <= remaining_minutes + 10:
                    activity_counter += 1
                    day_activities.append({
                        "id": f"d{day_number}_a{activity_counter}",
                        "activity_type": "watch",
                        "title": video['title'],
                        "duration_minutes": video['duration'],
                        "topic_id": video.get('topic_id'),
                        "lesson_id": video.get('lesson_id'),
                        "status": "pending",
                        "completed_date": None,
                        "details": {"eco_domain": video.get('eco_domain')}
                    })
                    remaining_minutes -= video['duration']
                    new_content_minutes += video['duration']

                    # Schedule flashcards for later
                    topic_id = video.get('lesson_id', f"video_{video_idx}")
                    topic_schedule[topic_id] = {"learned_day": day_number}

                    video_idx += 1
                    added = True

            # Try to add reading if video didn't fit or we want variety
            if read_idx < len(unread_chapters) and (not added or new_content_minutes < 30):
                chapter = unread_chapters[read_idx]
                if chapter['duration'] <= remaining_minutes + 10:
                    activity_counter += 1
                    day_activities.append({
                        "id": f"d{day_number}_a{activity_counter}",
                        "activity_type": "read",
                        "title": chapter['title'],
                        "duration_minutes": chapter['duration'],
                        "topic_id": chapter['topic_id'],
                        "lesson_id": None,
                        "status": "pending",
                        "completed_date": None,
                        "details": {
                            "has_flashcards": chapter['has_flashcards'],
                            "eco_domain": chapter.get('eco_domain')
                        }
                    })
                    remaining_minutes -= chapter['duration']
                    new_content_minutes += chapter['duration']

                    # Schedule flashcards for later
                    topic_schedule[chapter['topic_id']] = {
                        "learned_day": day_number,
                        "deck": chapter.get('deck'),
                        "quiz": chapter.get('quiz'),
                        "eco_domain": chapter.get('eco_domain')
                    }

                    read_idx += 1
                    added = True

            if not added:
                break

        # 2. Add FLASHCARDS for topics learned 1-2 days ago
        # Only add flashcards when there's actually a deck file available
        # Timing: 1 minute per card (20 cards = 20 min, 10 cards = 10 min)
        flashcard_minutes = 0
        for topic_id, sched in topic_schedule.items():
            if flashcard_minutes >= flashcard_target:
                break

            # Skip if no deck file for this topic (e.g., videos don't have decks)
            deck_file = sched.get('deck')
            if not deck_file:
                continue

            # Calculate actual duration based on card count
            deck_duration = get_flashcard_duration_minutes(deck_file, flashcards_dir)

            if remaining_minutes < deck_duration:
                break

            learned_day = sched.get('learned_day', 0)
            days_since = day_number - learned_day

            # Add flashcards 1-2 days after learning
            if FLASHCARD_DELAY_DAYS <= days_since <= FLASHCARD_DELAY_DAYS + 2:
                if 'flashcard_day' not in sched:
                    # Use deck filename for consistent naming with dropdown
                    deck_display_name = get_flashcard_display_name(deck_file)

                    activity_counter += 1
                    # Get eco_domain from chapter data if available
                    fc_eco_domain = sched.get('eco_domain')
                    day_activities.append({
                        "id": f"d{day_number}_a{activity_counter}",
                        "activity_type": "flashcards",
                        "title": f"Flashcards: {deck_display_name}",
                        "duration_minutes": deck_duration,
                        "topic_id": topic_id,
                        "lesson_id": None,
                        "status": "pending",
                        "completed_date": None,
                        "details": {"deck": deck_file, "card_count": deck_duration, "eco_domain": fc_eco_domain}
                    })
                    remaining_minutes -= deck_duration
                    flashcard_minutes += deck_duration
                    sched['flashcard_day'] = day_number

        # Also add flashcards for already-read topics (spaced repetition)
        if flashcard_minutes < flashcard_target and available_flashcard_topics:
            for fc_topic in available_flashcard_topics:
                if flashcard_minutes >= flashcard_target:
                    break

                fc_duration = fc_topic['duration']  # Already calculated with actual card count
                if remaining_minutes < fc_duration:
                    break

                activity_counter += 1
                day_activities.append({
                    "id": f"d{day_number}_a{activity_counter}",
                    "activity_type": "flashcards",
                    "title": fc_topic['title'],
                    "duration_minutes": fc_duration,
                    "topic_id": fc_topic['topic_id'],
                    "lesson_id": None,
                    "status": "pending",
                    "completed_date": None,
                    "details": {"deck": fc_topic.get('deck'), "spaced_rep": True, "eco_domain": fc_topic.get('eco_domain')}
                })
                remaining_minutes -= fc_duration
                flashcard_minutes += fc_duration

        # 3. Add QUIZ for topics learned 3+ days ago
        quiz_minutes = 0
        if remaining_minutes >= QUIZ_SESSION_MINUTES and available_quizzes:
            # More quizzes in later phases
            quiz_count = 1 if day_number <= early_phase_end else (2 if day_number <= middle_phase_end else 3)

            quizzes_added_today = set()
            for i in range(quiz_count):
                if quiz_minutes >= quiz_target:
                    break
                if remaining_minutes < QUIZ_SESSION_MINUTES:
                    break
                if not available_quizzes:
                    break

                # Rotate through quizzes (interleaving) - different quiz each time
                quiz_idx = (day_number + i) % len(available_quizzes)
                quiz = available_quizzes[quiz_idx]

                # Avoid duplicate quizzes on same day
                if quiz['quiz_bank'] in quizzes_added_today:
                    # Try next quiz
                    for j in range(len(available_quizzes)):
                        alt_idx = (quiz_idx + j + 1) % len(available_quizzes)
                        alt_quiz = available_quizzes[alt_idx]
                        if alt_quiz['quiz_bank'] not in quizzes_added_today:
                            quiz = alt_quiz
                            break
                    else:
                        continue  # All quizzes already added today

                activity_counter += 1
                day_activities.append({
                    "id": f"d{day_number}_a{activity_counter}",
                    "activity_type": "quiz",
                    "title": quiz['title'],
                    "duration_minutes": QUIZ_SESSION_MINUTES,
                    "topic_id": quiz['topic_id'],
                    "lesson_id": None,
                    "status": "pending",
                    "completed_date": None,
                    "details": {"quiz_bank": quiz.get('quiz_bank'), "eco_domain": quiz.get('eco_domain')}
                })
                remaining_minutes -= QUIZ_SESSION_MINUTES
                quiz_minutes += QUIZ_SESSION_MINUTES
                quizzes_added_today.add(quiz['quiz_bank'])

        # 4. Fill remaining time with review
        if remaining_minutes >= REVIEW_SESSION_MINUTES:
            activity_counter += 1
            day_activities.append({
                "id": f"d{day_number}_a{activity_counter}",
                "activity_type": "review",
                "title": "Review: Weak areas or previous content",
                "duration_minutes": remaining_minutes,
                "topic_id": None,
                "lesson_id": None,
                "status": "pending",
                "completed_date": None,
                "details": {"focus": "weak_areas"}
            })

        # Ensure day is not empty
        if not day_activities:
            activity_counter += 1
            day_activities.append({
                "id": f"d{day_number}_a{activity_counter}",
                "activity_type": "review",
                "title": "Review: Full study session",
                "duration_minutes": daily_goal,
                "topic_id": None,
                "lesson_id": None,
                "status": "pending",
                "completed_date": None,
                "details": {"focus": "comprehensive"}
            })

        day_plan["activities"] = day_activities
        plan["days"].append(day_plan)

    # Calculate ECO domain coverage summary
    eco_coverage = {1: 0, 2: 0, 3: 0, 4: 0}
    total_content_minutes = 0
    for day in plan["days"]:
        for activity in day.get("activities", []):
            details = activity.get("details", {})
            eco_domain = details.get("eco_domain")
            if eco_domain:
                # Parse domain number from string like "domain1" or int
                if isinstance(eco_domain, str):
                    domain_num = int(eco_domain.replace("domain", ""))
                else:
                    domain_num = int(eco_domain)
                eco_coverage[domain_num] += activity.get("duration_minutes", 0)
                total_content_minutes += activity.get("duration_minutes", 0)

    # Calculate percentages
    eco_percentages = {}
    for domain, minutes in eco_coverage.items():
        pct = (minutes / total_content_minutes * 100) if total_content_minutes > 0 else 0
        eco_percentages[domain] = {
            "minutes": minutes,
            "percentage": round(pct, 1),
            "target_percentage": ECO_DOMAIN_WEIGHTS.get(domain, 0),
            "name": ECO_DOMAIN_NAMES.get(domain, f"Domain {domain}")
        }

    plan["eco_domain_coverage"] = eco_percentages

    return plan


def preserve_completion_status(new_plan: dict, old_plan: dict) -> dict:
    """
    Preserve completion status from old plan when regenerating.

    Matches activities by:
    1. Same date + activity_type + topic_id (primary match)
    2. Same date + lesson_id for watch activities (fallback for videos)
    3. Same date + activity_type + title (fallback for other activities)

    Returns the new plan with completion status preserved where matches found.
    """
    if not old_plan or not old_plan.get('days'):
        return new_plan

    if not new_plan or not new_plan.get('days'):
        return new_plan

    # Build lookup of old activities by date
    old_activities_by_date = {}
    for day in old_plan.get('days', []):
        day_date = day.get('date')
        if day_date:
            old_activities_by_date[day_date] = day.get('activities', [])

    # Track how many activities were preserved (for logging/verification)
    preserved_count = 0

    # Iterate through new plan and restore completion status
    for day in new_plan.get('days', []):
        day_date = day.get('date')
        if not day_date or day_date not in old_activities_by_date:
            continue

        old_activities = old_activities_by_date[day_date]

        for new_activity in day.get('activities', []):
            # Try to find matching activity in old plan
            matched_old = None

            # Primary match: date + activity_type + topic_id
            for old_activity in old_activities:
                if (old_activity.get('activity_type') == new_activity.get('activity_type') and
                    old_activity.get('topic_id') == new_activity.get('topic_id') and
                    old_activity.get('topic_id') is not None):
                    matched_old = old_activity
                    break

            # Fallback for watch activities: match by lesson_id
            if not matched_old and new_activity.get('activity_type') == 'watch':
                for old_activity in old_activities:
                    if (old_activity.get('activity_type') == 'watch' and
                        old_activity.get('lesson_id') == new_activity.get('lesson_id') and
                        old_activity.get('lesson_id') is not None):
                        matched_old = old_activity
                        break

            # Fallback: match by activity_type + title
            if not matched_old:
                for old_activity in old_activities:
                    if (old_activity.get('activity_type') == new_activity.get('activity_type') and
                        old_activity.get('title') == new_activity.get('title')):
                        matched_old = old_activity
                        break

            # Preserve completion status if match found and old was completed
            if matched_old and matched_old.get('status') == 'completed':
                new_activity['status'] = 'completed'
                new_activity['completed_date'] = matched_old.get('completed_date')
                preserved_count += 1

    # Store preservation metadata for verification
    new_plan['_preservation_info'] = {
        'preserved_count': preserved_count,
        'preservation_applied': True
    }

    return new_plan


def get_today_plan(plan: dict) -> Optional[dict]:
    """Get today's study plan."""
    if not plan or not plan.get('days'):
        return None

    today_str = date.today().isoformat()

    for day in plan['days']:
        if day.get('date') == today_str:
            return day

    return None


def get_day_plan_by_date(plan: dict, target_date: date) -> Optional[dict]:
    """Get a specific day's study plan by date."""
    if not plan or not plan.get('days'):
        return None

    target_str = target_date.isoformat()

    for day in plan['days']:
        if day.get('date') == target_str:
            return day

    return None


def get_day_plan_by_offset(plan: dict, day_offset: int) -> Optional[dict]:
    """Get a day's plan relative to today (0=today, -1=yesterday, 1=tomorrow)."""
    target_date = date.today() + timedelta(days=day_offset)
    return get_day_plan_by_date(plan, target_date)


def get_overdue_daily_activities(plan: dict) -> list:
    """Get activities from past days that are still pending."""
    if not plan or not plan.get('days'):
        return []

    today = date.today()
    overdue = []

    for day in plan['days']:
        day_date = date.fromisoformat(day['date'])
        if day_date < today:
            for activity in day.get('activities', []):
                if activity.get('status') == 'pending':
                    overdue.append({
                        **activity,
                        'original_date': day['date'],
                        'day_number': day.get('day_number')
                    })

    return overdue


def get_plan_date_range(plan: dict) -> tuple:
    """Get the first and last date of the plan."""
    if not plan or not plan.get('days'):
        return None, None

    days = plan['days']
    first_date = date.fromisoformat(days[0]['date'])
    last_date = date.fromisoformat(days[-1]['date'])

    return first_date, last_date


def get_day_progress(day: dict) -> dict:
    """Calculate progress for a single day."""
    activities = day.get('activities', [])
    total = len(activities)
    completed = sum(1 for a in activities if a.get('status') == 'completed')
    total_minutes = sum(a.get('duration_minutes', 0) for a in activities)
    completed_minutes = sum(a.get('duration_minutes', 0) for a in activities
                           if a.get('status') == 'completed')

    return {
        "total": total,
        "completed": completed,
        "pending": total - completed,
        "percent": int(completed / total * 100) if total > 0 else 0,
        "total_minutes": total_minutes,
        "completed_minutes": completed_minutes,
        "minutes_percent": int(completed_minutes / total_minutes * 100) if total_minutes > 0 else 0
    }


def mark_daily_activity_completed(plan: dict, activity_id: str) -> dict:
    """Mark a daily plan activity as completed."""
    for day in plan.get('days', []):
        for activity in day.get('activities', []):
            if activity.get('id') == activity_id:
                activity['status'] = 'completed'
                activity['completed_date'] = datetime.now().isoformat()
                return plan
    return plan


def get_daily_plan_stats(plan: dict) -> dict:
    """Get overall daily plan statistics."""
    if not plan or not plan.get('days'):
        return {"total_days": 0, "days_completed": 0, "total_activities": 0}

    days = plan['days']
    total_activities = 0
    completed_activities = 0
    days_with_all_complete = 0

    today = date.today()

    for day in days:
        day_date = date.fromisoformat(day['date'])
        activities = day.get('activities', [])
        total_activities += len(activities)
        day_completed = sum(1 for a in activities if a.get('status') == 'completed')
        completed_activities += day_completed

        if day_completed == len(activities) and len(activities) > 0:
            days_with_all_complete += 1

    return {
        "total_days": len(days),
        "days_completed": days_with_all_complete,
        "total_activities": total_activities,
        "completed_activities": completed_activities,
        "percent": int(completed_activities / total_activities * 100) if total_activities > 0 else 0
    }


def get_plan_adherence_stats(plan: dict) -> dict:
    """
    Calculate plan adherence statistics for the Progress page.

    Returns metrics showing how well the user is following their study plan.
    """
    if not plan or not plan.get('days'):
        return {
            "total_activities": 0,
            "completed_activities": 0,
            "adherence_percent": 0,
            "this_week_total": 0,
            "this_week_completed": 0,
            "this_week_percent": 0,
            "overdue_count": 0,
            "days_on_track": 0,
            "days_total": 0,
            "current_day_complete": False
        }

    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday of current week

    total_activities = 0
    completed_activities = 0
    this_week_total = 0
    this_week_completed = 0
    overdue_count = 0
    days_on_track = 0
    days_with_activities = 0
    current_day_complete = False

    for day in plan['days']:
        day_date = date.fromisoformat(day['date'])
        activities = day.get('activities', [])

        if not activities:
            continue

        day_completed_count = sum(1 for a in activities if a.get('status') == 'completed')
        day_total = len(activities)

        # Only count days up to today for adherence
        if day_date <= today:
            total_activities += day_total
            completed_activities += day_completed_count
            days_with_activities += 1

            # Count as "on track" if all activities done for that day
            if day_completed_count == day_total:
                days_on_track += 1

            # Count overdue (past days with pending activities)
            if day_date < today:
                overdue_count += sum(1 for a in activities if a.get('status') == 'pending')

        # This week stats
        if week_start <= day_date <= today:
            this_week_total += day_total
            this_week_completed += day_completed_count

        # Current day status
        if day_date == today:
            current_day_complete = (day_completed_count == day_total and day_total > 0)

    adherence_percent = int((completed_activities / total_activities) * 100) if total_activities > 0 else 0
    this_week_percent = int((this_week_completed / this_week_total) * 100) if this_week_total > 0 else 0

    return {
        "total_activities": total_activities,
        "completed_activities": completed_activities,
        "adherence_percent": adherence_percent,
        "this_week_total": this_week_total,
        "this_week_completed": this_week_completed,
        "this_week_percent": this_week_percent,
        "overdue_count": overdue_count,
        "days_on_track": days_on_track,
        "days_total": days_with_activities,
        "current_day_complete": current_day_complete
    }


def migrate_daily_plan_flashcard_names(plan: dict, topics: list[Topic],
                                        flashcards_dir: Path = None) -> dict:
    """
    Migrate existing daily plan to use consistent flashcard naming and timing.

    This fixes:
    1. Updates flashcard activity titles to match dropdown format (deck filename based)
    2. Removes flashcard activities that have no valid deck (null deck)
    3. Corrects flashcard durations to 1 minute per card (not flat 5 minutes)
    """
    if not plan or not plan.get('days'):
        return plan

    # Build a lookup from topic_id to deck filename
    topic_to_deck = {}
    for topic in topics:
        if topic.flashcard_deck:
            topic_to_deck[topic.id] = topic.flashcard_deck

    modified = False

    for day in plan['days']:
        activities_to_keep = []

        for activity in day.get('activities', []):
            if activity.get('activity_type') != 'flashcards':
                # Keep non-flashcard activities as-is
                activities_to_keep.append(activity)
                continue

            # Check if this flashcard activity has a valid deck
            deck = activity.get('details', {}).get('deck')
            topic_id = activity.get('topic_id')

            # Try to find deck from topic if not in details
            if not deck and topic_id:
                deck = topic_to_deck.get(topic_id)
                if deck:
                    activity['details']['deck'] = deck

            if not deck:
                # Remove activities with no deck - they can't be used
                modified = True
                continue

            # Update title to match dropdown format
            new_title = f"Flashcards: {get_flashcard_display_name(deck)}"
            if activity.get('title') != new_title:
                activity['title'] = new_title
                modified = True

            # Fix duration to be 1 minute per card
            correct_duration = get_flashcard_duration_minutes(deck, flashcards_dir)
            if activity.get('duration_minutes') != correct_duration:
                activity['duration_minutes'] = correct_duration
                modified = True

            activities_to_keep.append(activity)

        if len(activities_to_keep) != len(day.get('activities', [])):
            day['activities'] = activities_to_keep
            modified = True

    if modified:
        plan['migrated'] = datetime.now().isoformat()
        plan['version'] = max(plan.get('version', 1), 5)  # Version 5 = flashcard duration fix

    return plan
