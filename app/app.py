# ABOUTME: Main Streamlit application for CAPM study tools.
# ABOUTME: Implements evidence-based learning: retrieval practice, spaced repetition, interleaving.

import streamlit as st
from pathlib import Path
import json
import random

# Import ECO domain mappings from single source of truth
from eco_domains import (
    ECO_DOMAIN_NAMES,
    ECO_DOMAIN_WEIGHTS,
    get_eco_domain,
    get_deck_eco_domain,
)

# Import our modules
from flashcards import (Card, load_deck, save_deck, get_due_cards, sm2_update,
                        get_deck_stats)
from quizzes import Question, load_questions, create_interleaved_quiz, create_eco_weighted_quiz, grade_quiz, save_result, get_weak_areas
from schedule import (
    load_config, save_config, load_topics, load_progress, save_progress,
    get_days_until_exam, get_weeks_until_exam, get_study_stats, ScheduleConfig,
    log_session, mark_reading_completed,
    load_plan, save_plan,
    load_prepcast_lessons, save_prepcast_lessons, mark_lesson_watched,
    get_next_unwatched_lesson, get_prepcast_stats,
    generate_daily_plan, get_today_plan, get_day_progress,
    mark_daily_activity_completed,
    get_day_plan_by_offset, get_overdue_daily_activities, get_plan_date_range,
    get_flashcard_display_name, migrate_daily_plan_flashcard_names,
    get_plan_adherence_stats,
    preserve_completion_status
)

# Page configuration
st.set_page_config(
    page_title="CAPM Study Hub",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paths
APP_DIR = Path(__file__).parent
PROJECT_DIR = APP_DIR.parent
STUDY_GUIDES_DIR = PROJECT_DIR / "study-guides"
DATA_DIR = PROJECT_DIR / "data"
FLASHCARDS_DIR = DATA_DIR / "flashcards"
QUIZZES_DIR = DATA_DIR / "quizzes"
PROGRESS_FILE = DATA_DIR / "progress.json"
TIDBITS_FILE = DATA_DIR / "tidbits.json"
SCHEDULE_DIR = DATA_DIR / "schedule"
PREPCAST_DIR = DATA_DIR / "prepcast"

# Swedish month names
SWEDISH_MONTHS = [
    "", "januari", "februari", "mars", "april", "maj", "juni",
    "juli", "augusti", "september", "oktober", "november", "december"
]

# Swedish day abbreviations (Monday=0)
SWEDISH_DAYS = ["mån", "tis", "ons", "tor", "fre", "lör", "sön"]


def format_swedish_date(date_str: str) -> str:
    """Format ISO date string to Swedish format (23 mars 2026)."""
    from datetime import datetime
    dt = datetime.fromisoformat(date_str)
    return f"{dt.day} {SWEDISH_MONTHS[dt.month]} {dt.year}"


def get_random_tidbit():
    """Load a random PMBOK tidbit for the home page."""
    if not TIDBITS_FILE.exists():
        return None
    try:
        with open(TIDBITS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        return None
    tidbits = data.get('tidbits', [])
    if not tidbits:
        return None
    return random.choice(tidbits)


def calculate_eco_domain_scores():
    """
    Calculate ECO domain scores (0-100%) for each of the 4 domains.

    Scoring Formula:
    ================
    Domain Score = (Theoretical Base × 50%) + (Practical Application × 50%)

    Theoretical Base (content consumption):
    - Reading: % of chapters completed in this domain
    - Videos: % of PrepCast videos watched in this domain

    Practical Application (retrieval practice):
    - Flashcards: % of cards mastered (interval >= 21 days) in this domain
    - Quizzes: % correct answers in this domain

    This structure allows future additions:
    - Add more theoretical sources → add to theoretical_components list
    - Add more practical sources → add to practical_components list

    Returns dict with domain scores and component breakdowns.
    """
    from schedule import get_eco_domain_from_topic

    # Initialize result structure
    scores = {
        1: {"name": "PM Fundamentals", "theoretical": [], "practical": [], "score": 0},
        2: {"name": "Predictive/Plan-Based", "theoretical": [], "practical": [], "score": 0},
        3: {"name": "Agile Frameworks", "theoretical": [], "practical": [], "score": 0},
        4: {"name": "Business Analysis", "theoretical": [], "practical": [], "score": 0},
    }

    # --- THEORETICAL COMPONENTS ---

    # 1. Reading Progress
    try:
        topics = load_topics(SCHEDULE_DIR / "topics.json")
        progress = load_progress(SCHEDULE_DIR / "progress.json")
        reading_progress = progress.get('reading_progress', {})

        # Count chapters per domain
        domain_chapters = {1: {"total": 0, "completed": 0}, 2: {"total": 0, "completed": 0},
                          3: {"total": 0, "completed": 0}, 4: {"total": 0, "completed": 0}}

        for topic in topics:
            if topic.study_guide:
                domain = topic.eco_domain or get_eco_domain_from_topic(topic.name, topic.id)
                domain_chapters[domain]["total"] += 1
                if reading_progress.get(topic.id, {}).get('status') == 'completed':
                    domain_chapters[domain]["completed"] += 1

        for domain in scores:
            total = domain_chapters[domain]["total"]
            completed = domain_chapters[domain]["completed"]
            pct = (completed / total * 100) if total > 0 else 0
            scores[domain]["theoretical"].append({
                "name": "Reading",
                "value": pct,
                "detail": f"{completed}/{total} chapters"
            })
    except Exception:
        for domain in scores:
            scores[domain]["theoretical"].append({"name": "Reading", "value": 0, "detail": "No data"})

    # 2. Video Progress (PrepCast)
    try:
        prepcast_path = PREPCAST_DIR / "lessons.json"
        if prepcast_path.exists():
            with open(prepcast_path, 'r', encoding='utf-8') as f:
                prepcast_data = json.load(f)

            domain_videos = {1: {"total": 0, "watched": 0}, 2: {"total": 0, "watched": 0},
                            3: {"total": 0, "watched": 0}, 4: {"total": 0, "watched": 0}}

            for lesson in prepcast_data.get('lessons', []):
                eco_str = lesson.get('eco_domain', '')
                if eco_str.startswith('domain'):
                    try:
                        domain = int(eco_str.replace('domain', ''))
                        if domain in domain_videos:
                            domain_videos[domain]["total"] += 1
                            if lesson.get('status') == 'watched':
                                domain_videos[domain]["watched"] += 1
                    except ValueError:
                        pass

            for domain in scores:
                total = domain_videos[domain]["total"]
                watched = domain_videos[domain]["watched"]
                pct = (watched / total * 100) if total > 0 else 0
                scores[domain]["theoretical"].append({
                    "name": "Videos",
                    "value": pct,
                    "detail": f"{watched}/{total} watched"
                })
        else:
            for domain in scores:
                scores[domain]["theoretical"].append({"name": "Videos", "value": 0, "detail": "No data"})
    except Exception:
        for domain in scores:
            scores[domain]["theoretical"].append({"name": "Videos", "value": 0, "detail": "No data"})

    # --- PRACTICAL COMPONENTS ---

    # 3. Flashcard Mastery
    try:
        deck_files = list(FLASHCARDS_DIR.glob("*.json"))
        domain_cards = {1: {"total": 0, "mastered": 0}, 2: {"total": 0, "mastered": 0},
                        3: {"total": 0, "mastered": 0}, 4: {"total": 0, "mastered": 0}}

        for deck_file in deck_files:
            domain = get_deck_eco_domain(deck_file.stem)
            cards = load_deck(deck_file)
            for card in cards:
                domain_cards[domain]["total"] += 1
                if card.interval >= 21:  # Mastered = 3+ week interval
                    domain_cards[domain]["mastered"] += 1

        for domain in scores:
            total = domain_cards[domain]["total"]
            mastered = domain_cards[domain]["mastered"]
            pct = (mastered / total * 100) if total > 0 else 0
            scores[domain]["practical"].append({
                "name": "Flashcards",
                "value": pct,
                "detail": f"{mastered}/{total} mastered"
            })
    except Exception:
        for domain in scores:
            scores[domain]["practical"].append({"name": "Flashcards", "value": 0, "detail": "No data"})

    # 4. Quiz Performance
    try:
        results_file = QUIZZES_DIR / "results.json"
        if results_file.exists():
            with open(results_file, 'r', encoding='utf-8') as f:
                quiz_data = json.load(f)

            # Aggregate quiz results by knowledge area, then map to domains
            # get_eco_domain is imported from eco_domains at module level
            area_stats = {}
            for result in quiz_data.get('results', []):
                for area, stats in result.get('by_knowledge_area', {}).items():
                    if area not in area_stats:
                        area_stats[area] = {'correct': 0, 'total': 0}
                    area_stats[area]['correct'] += stats.get('correct', 0)
                    area_stats[area]['total'] += stats.get('total', 0)

            # Map to domains
            domain_quiz = {1: {"correct": 0, "total": 0}, 2: {"correct": 0, "total": 0},
                          3: {"correct": 0, "total": 0}, 4: {"correct": 0, "total": 0}}

            for area, stats in area_stats.items():
                domain = get_eco_domain(area)
                domain_quiz[domain]["correct"] += stats["correct"]
                domain_quiz[domain]["total"] += stats["total"]

            for domain in scores:
                total = domain_quiz[domain]["total"]
                correct = domain_quiz[domain]["correct"]
                pct = (correct / total * 100) if total > 0 else 0
                scores[domain]["practical"].append({
                    "name": "Quizzes",
                    "value": pct,
                    "detail": f"{correct}/{total} correct"
                })
        else:
            for domain in scores:
                scores[domain]["practical"].append({"name": "Quizzes", "value": 0, "detail": "No data"})
    except Exception:
        for domain in scores:
            scores[domain]["practical"].append({"name": "Quizzes", "value": 0, "detail": "No data"})

    # --- CALCULATE FINAL SCORES ---
    for domain in scores:
        theoretical_values = [c["value"] for c in scores[domain]["theoretical"]]
        practical_values = [c["value"] for c in scores[domain]["practical"]]

        theoretical_avg = sum(theoretical_values) / len(theoretical_values) if theoretical_values else 0
        practical_avg = sum(practical_values) / len(practical_values) if practical_values else 0

        # 50% theoretical + 50% practical
        scores[domain]["theoretical_avg"] = theoretical_avg
        scores[domain]["practical_avg"] = practical_avg
        scores[domain]["score"] = (theoretical_avg * 0.5) + (practical_avg * 0.5)

    return scores


def main():
    st.title("CAPM Study Hub")
    st.caption("Evidence-based learning: retrieval practice, spaced repetition, interleaving")

    # Sidebar navigation
    # Order: Schedule-driven study flow first, reference materials last
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Study Mode",
        ["Home", "Schedule", "PrepCast Videos", "Study Guides", "Flashcards", "Quiz", "Progress"]
    )

    if page == "Home":
        show_home()
    elif page == "Schedule":
        show_schedule()
    elif page == "PrepCast Videos":
        show_prepcast()
    elif page == "Study Guides":
        show_study_guides()
    elif page == "Flashcards":
        show_flashcards()
    elif page == "Quiz":
        show_quiz()
    elif page == "Progress":
        show_progress()


def show_home():
    st.header("Welcome")

    # Random PMBOK tidbit
    if 'tidbit' not in st.session_state:
        st.session_state.tidbit = get_random_tidbit()

    tidbit = st.session_state.tidbit
    if tidbit:
        st.subheader("Did You Know?")
        tidbit_col, btn_col = st.columns([5, 1])
        with tidbit_col:
            st.info(f"**{tidbit['fact']}**")
            st.caption(f"Topic: {tidbit['topic']} | Source: `study-guides/pmbok/{tidbit['source']}`")
        with btn_col:
            if st.button("New Tidbit", use_container_width=True):
                st.session_state.tidbit = get_random_tidbit()
                st.rerun()
        st.divider()

    # ECO Domain Scores - Study KPIs
    st.subheader("ECO Domain Readiness")

    # Explanation expander for future reference
    with st.expander("How scores are calculated", expanded=False):
        st.markdown("""
        **Domain Score = Theoretical (50%) + Practical (50%)**

        **Theoretical Base** (content consumption):
        - Reading: % of study guide chapters completed
        - Videos: % of PrepCast videos watched

        **Practical Application** (retrieval practice):
        - Flashcards: % of cards mastered (3+ week interval)
        - Quizzes: % of questions answered correctly

        *This balanced approach ensures you both learn the material AND can recall it under test conditions.*
        """)

    # Calculate and display scores
    eco_scores = calculate_eco_domain_scores()

    # ECO Domain weights for reference
    domain_weights = {1: 36, 2: 17, 3: 20, 4: 27}

    score_cols = st.columns(4)
    for i, (domain, data) in enumerate(sorted(eco_scores.items())):
        with score_cols[i]:
            score = data["score"]
            # Color-code: green >= 70, yellow >= 40, red < 40
            if score >= 70:
                color = "🟢"
            elif score >= 40:
                color = "🟡"
            else:
                color = "🔴"

            st.metric(
                f"{color} Domain {domain}",
                f"{score:.0f}%",
                delta=f"{domain_weights[domain]}% of exam"
            )
            st.caption(data["name"])

            # Show component breakdown on hover/expand
            with st.popover("Details"):
                st.markdown(f"**Theoretical: {data['theoretical_avg']:.0f}%**")
                for comp in data["theoretical"]:
                    st.caption(f"  {comp['name']}: {comp['value']:.0f}% ({comp['detail']})")

                st.markdown(f"**Practical: {data['practical_avg']:.0f}%**")
                for comp in data["practical"]:
                    st.caption(f"  {comp['name']}: {comp['value']:.0f}% ({comp['detail']})")

    st.divider()

    # Study KPIs - Progress Overview
    st.subheader("Study Progress")

    # Load data for KPIs
    config = load_config(SCHEDULE_DIR / "config.json")
    topics = load_topics(SCHEDULE_DIR / "topics.json")
    progress = load_progress(SCHEDULE_DIR / "progress.json")

    # Calculate reading progress
    reading_topics = [t for t in topics if t.study_guide]
    reading_progress = progress.get('reading_progress', {})
    chapters_read = sum(1 for t in reading_topics
                        if reading_progress.get(t.id, {}).get('status') == 'completed')
    total_chapters = len(reading_topics)

    # Calculate video progress
    prepcast_path = PREPCAST_DIR / "lessons.json"
    mandatory_watched, mandatory_total = 0, 0
    optional_watched, optional_total = 0, 0
    if prepcast_path.exists():
        try:
            with open(prepcast_path, 'r', encoding='utf-8') as f:
                prepcast_data = json.load(f)
            for lesson in prepcast_data.get('lessons', []):
                if lesson.get('is_core', False):
                    mandatory_total += 1
                    if lesson.get('status') == 'watched':
                        mandatory_watched += 1
                else:
                    optional_total += 1
                    if lesson.get('status') == 'watched':
                        optional_watched += 1
        except (json.JSONDecodeError, IOError):
            pass

    # Calculate exam countdown
    days_until_exam = get_days_until_exam(config)

    # Display KPIs in columns
    kpi_cols = st.columns(4)

    with kpi_cols[0]:
        if days_until_exam is not None:
            if days_until_exam > 0:
                st.metric("Days Until Exam", days_until_exam)
            elif days_until_exam == 0:
                st.metric("Exam Day", "Today!")
            else:
                st.metric("Days Since Exam", abs(days_until_exam))
        else:
            st.metric("Exam Date", "Not set")
            st.caption("Set in Schedule")

    with kpi_cols[1]:
        reading_pct = int((chapters_read / total_chapters) * 100) if total_chapters > 0 else 0
        st.metric("Reading", f"{chapters_read}/{total_chapters}", delta=f"{reading_pct}%")
        st.caption("Study guide chapters")

    with kpi_cols[2]:
        mandatory_pct = int((mandatory_watched / mandatory_total) * 100) if mandatory_total > 0 else 0
        st.metric("Videos (Core)", f"{mandatory_watched}/{mandatory_total}", delta=f"{mandatory_pct}%")
        st.caption("PrepCast mandatory")

    with kpi_cols[3]:
        optional_pct = int((optional_watched / optional_total) * 100) if optional_total > 0 else 0
        st.metric("Videos (Optional)", f"{optional_watched}/{optional_total}", delta=f"{optional_pct}%")
        st.caption("PrepCast optional")

    st.divider()

    st.subheader("CAPM Exam at a Glance")
    exam_cols = st.columns(4)
    exam_cols[0].metric("Questions", "150")
    exam_cols[1].metric("Duration", "3 hours")
    exam_cols[2].metric("Target Score", "75-80%")
    exam_cols[3].metric("Pretest (unscored)", "15")

    st.divider()

    # Learning Principles - at the bottom for reference
    with st.expander("Learning Principles (Evidence-Based)", expanded=False):
        st.markdown("""
        This app uses evidence-based learning techniques:

        1. **Retrieval Practice** - Test yourself, don't just re-read
        2. **Spaced Repetition** - Review at optimal intervals
        3. **Interleaving** - Mix topics to build discrimination
        4. **Elaboration** - Ask "why?" not just "what?"

        *See `study-guides/00-learning-science.md` for the research behind these principles.*
        """)


def show_schedule():
    st.header("Study Schedule")

    # Load data
    config = load_config(SCHEDULE_DIR / "config.json")
    topics = load_topics(SCHEDULE_DIR / "topics.json")
    progress = load_progress(SCHEDULE_DIR / "progress.json")
    stats = get_study_stats(progress)

    # Setup section (in expander or if no exam date set)
    if config.exam_date is None:
        st.info("Set your target exam date to get started with a personalized study plan.")
        show_schedule_setup(config)
        return

    # Top metrics row (countdown and reading progress are on Home page)
    days_left = get_days_until_exam(config)

    col1, col2 = st.columns(2)

    with col1:
        streak = stats.get('current_streak', 0)
        streak_emoji = "🔥" if streak >= 3 else ""
        st.metric(f"{streak_emoji} Study Streak", f"{streak} days")

    with col2:
        today_min = stats.get('today_minutes', 0)
        goal = config.daily_goal_minutes
        st.metric("Today", f"{today_min} min", delta=f"Goal: {goal}")

    # Visual progress section
    st.divider()
    show_visual_progress(config, topics, progress, days_left)

    # Load PrepCast data (needed for plan generation)
    prepcast_path = PREPCAST_DIR / "lessons.json"
    prepcast_data = load_prepcast_lessons(prepcast_path) if prepcast_path.exists() else {"lessons": []}

    # Settings section with regenerate option
    with st.expander("Settings", expanded=False):
        show_schedule_setup(config)

        st.divider()
        st.markdown("**Plan Management**")
        st.caption("Regenerate your study plan if you want a fresh start or to apply new settings.")

        if st.button("Regenerate Plan", type="secondary", use_container_width=True):
            daily_plan_path = SCHEDULE_DIR / "daily_plan.json"
            old_plan = load_plan(daily_plan_path)  # Load existing plan to preserve completion status
            new_plan = generate_daily_plan(config, topics, prepcast_data, progress, flashcards_dir=FLASHCARDS_DIR)
            new_plan = preserve_completion_status(new_plan, old_plan)  # Preserve completed activities
            save_plan(new_plan, daily_plan_path)
            preserved = new_plan.get('_preservation_info', {}).get('preserved_count', 0)
            st.success(f"Study plan regenerated! ({preserved} completed activities preserved)")
            st.rerun()

    st.divider()

    # Exam info
    if config.exam_date:
        exam_date_formatted = format_swedish_date(config.exam_date)
        confirmed_text = " (Bokad)" if config.exam_date_confirmed else " (Mål)"
        st.caption(f"Tentamen: {exam_date_formatted}{confirmed_text} | {config.certification}")

    # Load or generate daily study plan
    daily_plan_path = SCHEDULE_DIR / "daily_plan.json"
    daily_plan = load_plan(daily_plan_path)

    # Check if daily plan needs regeneration
    needs_regen = (
        daily_plan is None or
        daily_plan.get('exam_date') != config.exam_date or
        daily_plan.get('version', 1) < 2
    )

    if needs_regen:
        if daily_plan is not None and daily_plan.get('version', 1) >= 2:
            st.warning("Your exam date has changed. Regenerate your study plan to update the schedule.")
            if st.button("Regenerate Plan", type="primary"):
                old_plan = daily_plan  # Preserve reference to old plan
                daily_plan = generate_daily_plan(config, topics, prepcast_data, progress, flashcards_dir=FLASHCARDS_DIR)
                daily_plan = preserve_completion_status(daily_plan, old_plan)  # Preserve completed activities
                save_plan(daily_plan, daily_plan_path)
                preserved = daily_plan.get('_preservation_info', {}).get('preserved_count', 0)
                st.success(f"Study plan regenerated! ({preserved} completed activities preserved)")
                st.rerun()
        else:
            # First time or upgrading from old format - auto-generate
            old_plan = daily_plan  # May be None for first time, that's OK
            daily_plan = generate_daily_plan(config, topics, prepcast_data, progress, flashcards_dir=FLASHCARDS_DIR)
            daily_plan = preserve_completion_status(daily_plan, old_plan)  # Preserve completed activities if any
            save_plan(daily_plan, daily_plan_path)
            st.rerun()

    # Migrate existing plan to fix flashcard naming and timing
    # This updates titles to match dropdown format, removes broken deck references,
    # and corrects durations to 1 minute per card
    # Version 5 = flashcard duration fix (1 min per card)
    if daily_plan and daily_plan.get('version', 1) < 5:
        daily_plan = migrate_daily_plan_flashcard_names(daily_plan, topics, FLASHCARDS_DIR)
        save_plan(daily_plan, daily_plan_path)

    # Day navigation state
    if 'schedule_day_offset' not in st.session_state:
        st.session_state.schedule_day_offset = 0

    # Get plan date range for navigation limits
    first_date, last_date = get_plan_date_range(daily_plan)

    # Day navigation header
    from datetime import date as date_type, timedelta as td
    current_view_date = date_type.today() + td(days=st.session_state.schedule_day_offset)

    # Check navigation limits
    can_go_prev = first_date and current_view_date > first_date
    can_go_next = last_date and current_view_date < last_date

    # Day Plan section with navigation
    nav_col1, nav_col2, nav_col3 = st.columns([1, 3, 1])

    with nav_col1:
        if st.button("◀ Previous", disabled=not can_go_prev, use_container_width=True):
            st.session_state.schedule_day_offset -= 1
            st.rerun()

    with nav_col2:
        # Show current day label
        if st.session_state.schedule_day_offset == 0:
            day_label = "Today's Plan"
        elif st.session_state.schedule_day_offset == -1:
            day_label = "Yesterday"
        elif st.session_state.schedule_day_offset == 1:
            day_label = "Tomorrow"
        else:
            day_label = format_swedish_date(current_view_date.isoformat())

        st.subheader(f"{day_label} (90 min)")

        # Quick jump back to today if viewing another day
        if st.session_state.schedule_day_offset != 0:
            if st.button("↩ Jump to Today", use_container_width=True):
                st.session_state.schedule_day_offset = 0
                st.rerun()

    with nav_col3:
        if st.button("Next ▶", disabled=not can_go_next, use_container_width=True):
            st.session_state.schedule_day_offset += 1
            st.rerun()

    # Show overdue items if viewing today
    if st.session_state.schedule_day_offset == 0:
        overdue_activities = get_overdue_daily_activities(daily_plan)
        if overdue_activities:
            with st.expander(f"⚠️ {len(overdue_activities)} Overdue Activities", expanded=True):
                st.caption("These activities from previous days are still pending")
                for activity in overdue_activities[:5]:  # Show max 5
                    original_date = activity.get('original_date', '')
                    icon = {"watch": "🎬", "read": "📖", "flashcards": "🎴", "quiz": "📝", "review": "🔄"}.get(
                        activity.get('activity_type', ''), "📌")
                    st.markdown(f"{icon} **{activity.get('title')}** *(from {format_swedish_date(original_date)})*")

                if len(overdue_activities) > 5:
                    st.caption(f"...and {len(overdue_activities) - 5} more")

                st.caption("Tip: Check off completed items by navigating to their original day")

    # Get the plan for the selected day
    selected_day_plan = get_day_plan_by_offset(daily_plan, st.session_state.schedule_day_offset)

    if selected_day_plan:
        show_today_activities(selected_day_plan, daily_plan, daily_plan_path, prepcast_data, prepcast_path)
    else:
        # Fallback to recommendations if no plan for selected day
        if st.session_state.schedule_day_offset == 0:
            recommendations = get_today_recommendations(config, topics, progress)
            if recommendations:
                for rec in recommendations[:3]:
                    icon = {"reading": "📖", "flashcards": "🎴", "quiz": "📝", "review": "🔄", "watch": "🎬"}.get(rec['type'], "📌")
                    st.markdown(f"{icon} **{rec['title']}**")
                    st.caption(rec['description'])
            else:
                st.success("No activities scheduled for today.")
        else:
            st.info(f"No activities scheduled for {format_swedish_date(current_view_date.isoformat())}")


def show_visual_progress(config: ScheduleConfig, topics: list, progress: dict, days_left: int):
    """Show visual progress indicators."""
    from datetime import date

    # Calculate progress percentages
    reading_progress = progress.get('reading_progress', {})
    reading_topics = [t for t in topics if t.study_guide]

    chapters_read = sum(1 for t in reading_topics
                        if reading_progress.get(t.id, {}).get('status') == 'completed')
    total_chapters = len(reading_topics)
    reading_pct = int((chapters_read / total_chapters) * 100) if total_chapters > 0 else 0

    # Time progress (days elapsed vs total)
    if config.exam_date and days_left is not None:
        exam_date = date.fromisoformat(config.exam_date)
        # Assume study started when config was created, or 8 weeks before exam
        if config.created:
            start_date = date.fromisoformat(config.created[:10])
        else:
            from datetime import timedelta
            start_date = exam_date - timedelta(weeks=config.target_weeks)

        total_days = (exam_date - start_date).days
        days_elapsed = (date.today() - start_date).days
        time_pct = int((days_elapsed / total_days) * 100) if total_days > 0 else 0
        time_pct = min(100, max(0, time_pct))  # Clamp to 0-100
    else:
        time_pct = 0
        days_elapsed = 0
        total_days = config.target_weeks * 7

    # Display progress bars
    col1, col2 = st.columns(2)

    with col1:
        st.caption("📚 Study Progress")
        st.progress(reading_pct / 100)
        st.caption(f"{reading_pct}% of chapters completed ({chapters_read}/{total_chapters})")

    with col2:
        st.caption("⏱️ Time Progress")
        st.progress(time_pct / 100)
        if days_left is not None and days_left > 0:
            st.caption(f"{time_pct}% of time elapsed ({days_elapsed} days used, {days_left} remaining)")
        elif days_left == 0:
            st.caption("Exam day!")
        else:
            st.caption(f"{days_elapsed} days of study")

    # Warning if behind schedule
    if reading_pct < time_pct - 10 and days_left is not None and days_left > 0:
        gap = time_pct - reading_pct
        st.warning(f"⚠️ Behind schedule by ~{gap}%. Consider increasing study time to catch up.")

    # ECO Domain Coverage (if plan has this data)
    daily_plan_path = SCHEDULE_DIR / "daily_plan.json"
    if daily_plan_path.exists():
        try:
            with open(daily_plan_path, 'r', encoding='utf-8') as f:
                daily_plan = json.load(f)
            eco_coverage = daily_plan.get('eco_domain_coverage', {})
            if eco_coverage:
                st.divider()
                st.caption("📊 ECO Domain Coverage (Planned)")
                eco_cols = st.columns(4)
                for i, (domain, data) in enumerate(sorted(eco_coverage.items(), key=lambda x: int(x[0]))):
                    if isinstance(data, dict):
                        with eco_cols[i]:
                            actual_pct = data.get('percentage', 0)
                            target_pct = data.get('target_percentage', 0)
                            delta = actual_pct - target_pct
                            delta_str = f"{delta:+.0f}%" if delta != 0 else "On target"
                            st.metric(
                                f"Domain {domain}",
                                f"{actual_pct:.0f}%",
                                delta=delta_str,
                                delta_color="normal" if abs(delta) <= 5 else ("off" if delta < 0 else "normal")
                            )
                            st.caption(data.get('name', '')[:20] + "..." if len(data.get('name', '')) > 20 else data.get('name', ''))
        except (json.JSONDecodeError, IOError):
            pass  # Silently skip if plan can't be read


def show_schedule_setup(config: ScheduleConfig):
    """Show schedule configuration UI."""
    st.subheader("Study Plan Setup")

    # Exam date
    from datetime import datetime, timedelta

    col1, col2 = st.columns(2)

    with col1:
        # Date input
        default_date = None
        if config.exam_date:
            default_date = datetime.fromisoformat(config.exam_date).date()
        else:
            default_date = (datetime.now() + timedelta(weeks=config.target_weeks)).date()

        exam_date = st.date_input(
            "Target Exam Date",
            value=default_date,
            min_value=datetime.now().date(),
            help="When do you plan to take the exam?"
        )

        confirmed = st.checkbox(
            "Exam is booked",
            value=config.exam_date_confirmed,
            help="Check if you've actually scheduled the exam"
        )

    with col2:
        daily_goal = st.number_input(
            "Daily study goal (minutes)",
            min_value=10,
            max_value=180,
            value=config.daily_goal_minutes,
            step=5
        )

        weekly_days = st.number_input(
            "Days per week",
            min_value=1,
            max_value=7,
            value=config.weekly_goal_days
        )

    # Save button
    if st.button("Save Settings", type="primary"):
        config.exam_date = exam_date.isoformat()
        config.exam_date_confirmed = confirmed
        config.daily_goal_minutes = daily_goal
        config.weekly_goal_days = weekly_days
        save_config(config, SCHEDULE_DIR / "config.json")
        st.success("Settings saved!")
        st.rerun()


def get_today_recommendations(config: ScheduleConfig, topics: list, progress: dict) -> list:
    """Get prioritized study recommendations for today."""
    recommendations = []

    # 1. Check for in-progress reading
    reading_progress = progress.get('reading_progress', {})
    for topic_id, rp in reading_progress.items():
        if rp.get('status') == 'in_progress':
            topic = next((t for t in topics if t.id == topic_id), None)
            if topic:
                recommendations.append({
                    'type': 'reading',
                    'topic_id': topic_id,
                    'title': f"Continue reading: {topic.name}",
                    'description': "You started this chapter - finish it!",
                    'priority': 1
                })

    # 2. Check for due flashcards - ONLY for topics where reading is completed
    # (You shouldn't do flashcards before reading the chapter)
    deck_files = list(FLASHCARDS_DIR.glob("*.json"))
    total_due = 0
    due_by_topic = {}

    # Build mapping of deck filename to topic_id
    topic_deck_map = {}
    for topic in topics:
        if topic.flashcard_deck:
            topic_deck_map[topic.flashcard_deck] = topic.id

    for deck_file in deck_files:
        # Check if this deck's topic has been read
        deck_filename = deck_file.name
        topic_id = topic_deck_map.get(deck_filename)

        # Only count flashcards for topics where reading is completed
        if topic_id:
            topic_reading_status = reading_progress.get(topic_id, {}).get('status', 'not_started')
            if topic_reading_status != 'completed':
                continue  # Skip - haven't read this chapter yet

        cards = load_deck(deck_file)
        due = get_due_cards(cards)
        if due:
            deck_name = deck_file.stem.replace("_domain", "").replace("_", " ").title()
            due_by_topic[deck_name] = len(due)
            total_due += len(due)

    if total_due > 0:
        topic_summary = ", ".join([f"{k} ({v})" for k, v in list(due_by_topic.items())[:3]])
        recommendations.append({
            'type': 'flashcards',
            'topic_id': None,
            'title': f"{total_due} flashcards due",
            'description': f"For chapters you've read. {topic_summary}",
            'priority': 2
        })

    # 3. Check weak areas from quiz results - recommend MORE retrieval practice (not re-reading!)
    results_file = QUIZZES_DIR / "results.json"
    weak = get_weak_areas(results_file)
    if weak:
        recommendations.append({
            'type': 'quiz',
            'topic_id': weak[0] if weak else None,
            'title': f"Weak area: {weak[0]}",
            'description': "More practice needed - flashcards & quizzes strengthen memory (re-reading doesn't)",
            'priority': 3
        })

    # 4. Quiz frequency based on days to exam
    days_left = get_days_until_exam(config) if config.exam_date else None
    if days_left is not None:
        # Determine recommended quiz frequency
        if days_left <= 14:
            quiz_interval_days = 1  # Daily
            freq_text = "daily"
        elif days_left <= 28:
            quiz_interval_days = 2  # Every 2 days
            freq_text = "every 2 days"
        elif days_left <= 56:
            quiz_interval_days = 3  # Twice a week
            freq_text = "twice a week"
        else:
            quiz_interval_days = 7  # Weekly
            freq_text = "weekly"

        # Check when last quiz was taken
        from datetime import datetime, date
        last_quiz_date = None
        if results_file.exists():
            try:
                with open(results_file, 'r', encoding='utf-8') as f:
                    quiz_data = json.load(f)
                results = quiz_data.get('results', [])
                if results:
                    last_timestamp = results[-1].get('timestamp', '')
                    if last_timestamp:
                        last_quiz_date = datetime.fromisoformat(last_timestamp).date()
            except (json.JSONDecodeError, IOError, ValueError):
                pass  # If results file is corrupted, treat as no quiz history

        days_since_quiz = None
        if last_quiz_date:
            days_since_quiz = (date.today() - last_quiz_date).days

        # Recommend quiz if overdue
        if days_since_quiz is None or days_since_quiz >= quiz_interval_days:
            overdue_text = f" (last quiz: {days_since_quiz} days ago)" if days_since_quiz else " (no quizzes yet)"
            recommendations.append({
                'type': 'quiz',
                'topic_id': None,
                'title': f"Time for a quiz",
                'description': f"Recommended: {freq_text} with {days_left} days to exam{overdue_text}",
                'priority': 4
            })

    # 5. Suggest next unread chapter
    for topic in sorted(topics, key=lambda t: t.order):
        if topic.study_guide:
            status = reading_progress.get(topic.id, {}).get('status', 'not_started')
            if status == 'not_started':
                recommendations.append({
                    'type': 'reading',
                    'topic_id': topic.id,
                    'title': f"Start reading: {topic.name}",
                    'description': f"~{topic.estimated_read_minutes} min | {topic.description}",
                    'priority': 7
                })
                break

    # Sort by priority
    recommendations.sort(key=lambda r: r.get('priority', 99))

    return recommendations


def show_today_activities(today_plan: dict, daily_plan: dict, plan_path: Path,
                          prepcast_data: dict = None, prepcast_path: Path = None):
    """Show today's scheduled activities with completion tracking."""
    from datetime import date

    day_progress = get_day_progress(today_plan)
    activities = today_plan.get('activities', [])

    # Progress header
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        today_str = today_plan.get('date', '')
        if today_str:
            st.caption(f"Day {today_plan.get('day_number', '?')} | {format_swedish_date(today_str)}")
    with col2:
        pct = day_progress.get('percent', 0)
        st.progress(pct / 100)
    with col3:
        done = day_progress.get('completed', 0)
        total = day_progress.get('total', 0)
        st.caption(f"{done}/{total} activities | {day_progress.get('completed_minutes', 0)}/{day_progress.get('total_minutes', 0)} min")

    if not activities:
        st.info("No activities scheduled for today.")
        return

    # Activity list with completion checkboxes
    for activity in activities:
        activity_id = activity.get('id')
        activity_type = activity.get('activity_type', 'review')
        title = activity.get('title', 'Activity')
        duration = activity.get('duration_minutes', 0)
        status = activity.get('status', 'pending')

        icon = {
            "watch": "🎬",
            "read": "📖",
            "flashcards": "🎴",
            "quiz": "📝",
            "review": "🔄"
        }.get(activity_type, "📌")

        col1, col2, col3 = st.columns([1, 5, 1])

        with col1:
            is_completed = status == 'completed'
            new_completed = st.checkbox(
                "Done",
                value=is_completed,
                key=f"daily_{activity_id}",
                label_visibility="collapsed"
            )

            if new_completed != is_completed:
                if new_completed:
                    daily_plan = mark_daily_activity_completed(daily_plan, activity_id)
                    save_plan(daily_plan, plan_path)

                    # Log the session
                    progress = load_progress(SCHEDULE_DIR / "progress.json")
                    progress = log_session(
                        progress,
                        session_type=activity_type,
                        topic_id=activity.get('topic_id'),
                        duration_minutes=duration,
                        details={"activity_id": activity_id, "title": title}
                    )
                    save_progress(progress, SCHEDULE_DIR / "progress.json")

                    # If it's a watch activity, also mark the lesson as watched
                    if activity_type == "watch" and prepcast_data and prepcast_path:
                        lesson_id = activity.get('lesson_id') or activity.get('details', {}).get('lesson_id')
                        if lesson_id:
                            prepcast_data = mark_lesson_watched(prepcast_data, lesson_id)
                            save_prepcast_lessons(prepcast_data, prepcast_path)

                    st.rerun()

        with col2:
            status_mark = "✓" if status == 'completed' else ""
            st.markdown(f"{icon} **{title}** {status_mark}")

        with col3:
            st.caption(f"{duration} min")

    # Quick action buttons
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        pending = [a for a in activities if a.get('status') == 'pending']
        if pending:
            if st.button("Mark All Done", use_container_width=True):
                for activity in pending:
                    daily_plan = mark_daily_activity_completed(daily_plan, activity.get('id'))
                save_plan(daily_plan, plan_path)

                # Log one session for all
                progress = load_progress(SCHEDULE_DIR / "progress.json")
                total_duration = sum(a.get('duration_minutes', 0) for a in pending)
                progress = log_session(
                    progress,
                    session_type="mixed",
                    topic_id=None,
                    duration_minutes=total_duration,
                    details={"activities_completed": len(pending)}
                )
                save_progress(progress, SCHEDULE_DIR / "progress.json")
                st.rerun()

    with col2:
        prepcast_stats = get_prepcast_stats(prepcast_data) if prepcast_data else {}
        next_video = prepcast_stats.get('next_lesson')
        if next_video:
            st.caption(f"Next video: {next_video['lesson_id']} ({next_video['duration_minutes']} min)")


def show_prepcast():
    """Show PM PrepCast video tracking page."""
    st.header("PM PrepCast Videos")
    st.caption("Track your 23h of mandatory CAPM preparation videos")

    # Load PrepCast data
    prepcast_path = PREPCAST_DIR / "lessons.json"
    if not prepcast_path.exists():
        st.error("PrepCast lessons data not found. Please check data/prepcast/lessons.json")
        return

    prepcast_data = load_prepcast_lessons(prepcast_path)
    stats = get_prepcast_stats(prepcast_data)

    # Top metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        core_pct = stats['core_percent']
        st.metric("Core Progress", f"{stats['core_watched']}/{stats['core_total']}", delta=f"{core_pct}%")

    with col2:
        core_hours = stats['core_minutes_watched'] // 60
        core_mins = stats['core_minutes_watched'] % 60
        total_hours = stats['core_minutes_total'] // 60
        st.metric("Core Time", f"{core_hours}h {core_mins}m", delta=f"of {total_hours}h")

    with col3:
        opt_watched = stats['optional_watched']
        opt_total = stats['optional_total']
        st.metric("Optional Videos", f"{opt_watched}/{opt_total}")

    with col4:
        next_lesson = stats.get('next_lesson')
        if next_lesson:
            st.metric("Next Up", next_lesson['lesson_id'])
        else:
            st.metric("Status", "All Done!")

    # Progress bar
    st.progress(core_pct / 100)

    st.divider()

    # ECO Domain breakdown
    st.subheader("Progress by ECO Domain")

    eco_domains = prepcast_data.get('eco_domains', {})
    lessons = prepcast_data.get('lessons', [])

    for domain_id, domain_info in eco_domains.items():
        domain_lessons = [l for l in lessons if l.get('eco_domain') == domain_id]
        watched = sum(1 for l in domain_lessons if l.get('status') == 'watched')
        total = len(domain_lessons)
        pct = int(watched / total * 100) if total > 0 else 0

        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{domain_info['name']}** ({domain_info['weight']}% of exam)")
            st.progress(pct / 100)
        with col2:
            st.caption(f"{watched}/{total} videos")

    st.divider()

    # Lesson list by module
    st.subheader("Video Lessons")

    # Group lessons by module
    modules = {}
    for lesson in lessons:
        module_id = lesson.get('module_id', 'Unknown')
        if module_id not in modules:
            modules[module_id] = {
                'title': lesson.get('module_title', module_id),
                'lessons': []
            }
        modules[module_id]['lessons'].append(lesson)

    # Show as expandable sections
    filter_option = st.radio(
        "Show",
        ["All", "Core Only", "Not Watched"],
        horizontal=True
    )

    for module_id in sorted(modules.keys()):
        module = modules[module_id]
        module_lessons = module['lessons']

        # Apply filter
        if filter_option == "Core Only":
            module_lessons = [l for l in module_lessons if l.get('is_core')]
        elif filter_option == "Not Watched":
            module_lessons = [l for l in module_lessons if l.get('status') == 'not_watched']

        if not module_lessons:
            continue

        watched_count = sum(1 for l in module_lessons if l.get('status') == 'watched')
        module_header = f"{module_id}: {module['title']} ({watched_count}/{len(module_lessons)})"

        with st.expander(module_header, expanded=False):
            for lesson in module_lessons:
                lesson_id = lesson.get('lesson_id')
                title = lesson.get('title', 'Unknown')
                duration = lesson.get('duration_minutes', 0)
                is_core = lesson.get('is_core', False)
                status = lesson.get('status', 'not_watched')

                col1, col2, col3 = st.columns([1, 4, 1])

                with col1:
                    is_watched = status == 'watched'
                    new_watched = st.checkbox(
                        "Watched",
                        value=is_watched,
                        key=f"lesson_{lesson_id}",
                        label_visibility="collapsed"
                    )

                    if new_watched != is_watched:
                        if new_watched:
                            prepcast_data = mark_lesson_watched(prepcast_data, lesson_id)
                            save_prepcast_lessons(prepcast_data, prepcast_path)

                            # Log the session
                            progress = load_progress(SCHEDULE_DIR / "progress.json")
                            progress = log_session(
                                progress,
                                session_type="watch",
                                topic_id=lesson.get('eco_domain'),
                                duration_minutes=duration,
                                details={"lesson_id": lesson_id, "title": title}
                            )
                            save_progress(progress, SCHEDULE_DIR / "progress.json")
                            st.rerun()

                with col2:
                    core_badge = "🔵" if is_core else "⚪"
                    status_icon = "✓" if status == 'watched' else ""
                    st.markdown(f"{core_badge} **{lesson_id}** - {title} {status_icon}")

                with col3:
                    st.caption(f"{duration} min")

    st.divider()

    # Next lesson to watch
    next_lesson = get_next_unwatched_lesson(prepcast_data, core_only=True)
    if next_lesson:
        st.info(
            f"**Next video:** {next_lesson['lesson_id']} - {next_lesson['title']} "
            f"({next_lesson['duration_minutes']} min)"
        )


def show_study_guides():
    st.header("Study Guides")
    st.caption("Reference material organized by topic - but remember: reading isn't learning!")

    # Load topics and progress for tracking
    topics = load_topics(SCHEDULE_DIR / "topics.json")
    progress = load_progress(SCHEDULE_DIR / "progress.json")

    # Create tabs for ECO domain guides vs other resources
    tab1, tab2 = st.tabs(["ECO Domain Guides", "Other Resources"])

    with tab1:
        show_pmbok_guides(topics, progress)

    with tab2:
        show_other_guides()


def show_pmbok_guides(topics: list, progress: dict):
    """Show PMBOK study guides with reading progress tracking."""
    pmbok_dir = STUDY_GUIDES_DIR / "pmbok"

    # Top anchor for navigation
    st.markdown('<div id="guide-top"></div>', unsafe_allow_html=True)

    # Check for comprehension prompt (guide just completed)
    if 'guide_just_completed' in st.session_state:
        completed_topic_id = st.session_state.pop('guide_just_completed')
        completed_topic = next((t for t in topics if t.id == completed_topic_id), None)
        if completed_topic:
            st.success(f"**{completed_topic.name}** marked as read!")
            st.info(
                "Now test your understanding with **Flashcards** or a **Quiz**. "
                "Testing yourself strengthens memory far more than re-reading."
            )
            st.divider()

    if not pmbok_dir.exists():
        st.warning("PMBOK study guides directory not found.")
        return

    # Get topics that have study guides, sorted by order
    reading_topics = [t for t in topics if t.study_guide]
    reading_topics.sort(key=lambda t: t.order)

    if not reading_topics:
        st.warning("No PMBOK topics configured.")
        return

    # Build options with status indicators
    def format_topic_option(topic):
        status = progress.get('reading_progress', {}).get(topic.id, {}).get('status', 'not_started')
        status_icon = {"completed": "✅", "in_progress": "📖", "not_started": "○"}.get(status, "○")
        return f"{status_icon} {topic.name}"

    selected_topic = st.selectbox(
        "Select chapter",
        reading_topics,
        format_func=format_topic_option
    )

    if selected_topic:
        # Show reading status for selected topic
        topic_status = progress.get('reading_progress', {}).get(selected_topic.id, {}).get('status', 'not_started')

        # Status and action row
        col1, col2, col3 = st.columns([2, 1, 1])

        with col1:
            est_time = f"~{selected_topic.estimated_read_minutes} min" if selected_topic.estimated_read_minutes > 0 else ""
            st.caption(f"{selected_topic.description} | {est_time}")

        with col2:
            status_text = {"completed": "✅ Read", "in_progress": "📖 In Progress", "not_started": "Not started"}.get(topic_status, "Not started")
            st.caption(f"Status: {status_text}")

        with col3:
            if topic_status != 'completed':
                if st.button("Mark as Read", key="mark_read_btn", type="primary"):
                    mark_guide_completed(selected_topic, progress)

        # Jump to bottom button
        st.markdown(
            '<a href="#guide-bottom" style="text-decoration:none;">'
            '<button style="background:#262730;color:#fafafa;border:1px solid #444;padding:4px 12px;border-radius:4px;cursor:pointer;">'
            '⬇ Jump to Bottom</button></a>',
            unsafe_allow_html=True
        )

        st.divider()

        # Load and display the guide content
        guide_path = pmbok_dir / selected_topic.study_guide
        if guide_path.exists():
            content = guide_path.read_text(encoding="utf-8")
            st.markdown(content)

            # Bottom anchor for navigation
            st.markdown('<div id="guide-bottom"></div>', unsafe_allow_html=True)

            # Jump to top button
            st.markdown(
                '<a href="#guide-top" style="text-decoration:none;">'
                '<button style="background:#262730;color:#fafafa;border:1px solid #444;padding:4px 12px;border-radius:4px;cursor:pointer;">'
                '⬆ Jump to Top</button></a>',
                unsafe_allow_html=True
            )

            # Bottom action area
            st.divider()

            if topic_status != 'completed':
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Mark Chapter as Read", key="mark_read_bottom", use_container_width=True):
                        mark_guide_completed(selected_topic, progress)
                with col2:
                    st.info("Testing yourself is more effective than re-reading")
            else:
                # Already read - nudge toward practice
                st.success("Chapter completed! Now reinforce with active recall:")
                col1, col2 = st.columns(2)
                with col1:
                    if selected_topic.flashcard_deck:
                        st.markdown("🎴 **Flashcards** available for this topic")
                with col2:
                    if selected_topic.quiz_bank:
                        st.markdown("📝 **Quiz** available for this topic")

            # Final jump to top at very bottom
            st.markdown(
                '<a href="#guide-top" style="text-decoration:none;">'
                '<button style="background:#262730;color:#fafafa;border:1px solid #444;padding:4px 12px;border-radius:4px;cursor:pointer;">'
                '⬆ Jump to Top</button></a>',
                unsafe_allow_html=True
            )
        else:
            st.error(f"Study guide file not found: {selected_topic.study_guide}")


def mark_guide_completed(topic, progress: dict):
    """Mark a guide as completed and log the session."""
    # Mark as completed
    progress = mark_reading_completed(progress, topic.id)

    # Log the reading session
    progress = log_session(
        progress,
        session_type="reading",
        topic_id=topic.id,
        duration_minutes=topic.estimated_read_minutes,
        details={"guide": topic.study_guide, "completed": True}
    )

    # Save progress
    save_progress(progress, SCHEDULE_DIR / "progress.json")

    # Show comprehension prompt
    st.session_state['guide_just_completed'] = topic.id
    st.rerun()


def show_other_guides():
    """Show non-PMBOK study guides (learning science, exam tips, etc.)."""
    guides = sorted(STUDY_GUIDES_DIR.glob("*.md"))

    if not guides:
        st.info("No additional study guides found.")
        return

    selected = st.selectbox(
        "Select a guide",
        guides,
        format_func=lambda x: x.stem.replace("-", " ").title()
    )

    if selected:
        content = selected.read_text(encoding="utf-8")
        st.markdown(content)


def show_flashcards():
    st.header("Flashcards")
    st.caption("Spaced repetition with active recall - the most effective way to retain information")

    # Initialize session state
    if 'fc_deck' not in st.session_state:
        st.session_state.fc_deck = None
        st.session_state.fc_cards = []
        st.session_state.fc_current = 0
        st.session_state.fc_show_answer = False
        st.session_state.fc_session_complete = False

    # Deck selection
    deck_files = list(FLASHCARDS_DIR.glob("*.json"))

    if not deck_files:
        st.warning("No flashcard decks found.")
        st.info("Flashcard decks will be created as we extract content from PMBOK.")

        # Show sample card structure
        with st.expander("Preview: How flashcards will work"):
            st.markdown("""
            **Question (front):**
            > What is the primary purpose of the Project Charter?

            *Think of your answer before clicking reveal...*

            **Answer (back):**
            > The Project Charter formally authorizes the project's existence and provides
            > the project manager with authority to apply organizational resources.

            **Why it matters:**
            > Without a charter, the project lacks formal authorization. The PM has no
            > official authority, making it difficult to secure resources or make decisions.

            **Related concepts:** Project Initiation, Sponsor Role, PM Authority
            """)
        return

    def format_deck_name(deck_path):
        """Format deck name with ECO domain indicator."""
        if deck_path == "ALL_MIXED":
            return "All Decks (Shuffled) - Interleaved Practice"
        name = deck_path.stem.replace("_", " ").title()
        domain = get_deck_eco_domain(deck_path.stem)
        return f"{name} (ECO {domain})"

    # Add "All Decks" option at the start
    deck_options = ["ALL_MIXED"] + deck_files

    selected_deck = st.selectbox(
        "Select deck",
        deck_options,
        format_func=format_deck_name
    )

    # Show info based on selection
    if selected_deck == "ALL_MIXED":
        st.caption("Interleaved practice across all domains - best for discrimination learning")
    elif selected_deck:
        domain = get_deck_eco_domain(selected_deck.stem)
        domain_name = ECO_DOMAIN_NAMES.get(domain, "Unknown")
        st.caption(f"ECO Domain {domain}: {domain_name} ({ECO_DOMAIN_WEIGHTS[domain]}% of exam)" if domain in ECO_DOMAIN_WEIGHTS else f"ECO Domain {domain}: {domain_name}")

    if st.button("Start Review Session") or st.session_state.fc_deck == selected_deck:
        st.session_state.fc_deck = selected_deck

        if not st.session_state.fc_cards:
            if selected_deck == "ALL_MIXED":
                # Load due cards from ALL decks and shuffle
                all_cards_by_deck = {}
                combined_due = []
                for deck_path in deck_files:
                    deck_cards = load_deck(deck_path)
                    all_cards_by_deck[deck_path.name] = deck_cards
                    due = get_due_cards(deck_cards)
                    # Tag each card with its source deck
                    for card in due:
                        card._source_deck = deck_path.name
                    combined_due.extend(due)
                # Shuffle for interleaving
                random.shuffle(combined_due)
                st.session_state.fc_cards = combined_due
                st.session_state.fc_all_cards_by_deck = all_cards_by_deck
                st.session_state.fc_is_mixed = True
            else:
                all_cards = load_deck(selected_deck)
                st.session_state.fc_cards = get_due_cards(all_cards)
                st.session_state.fc_all_cards = all_cards
                st.session_state.fc_is_mixed = False

        cards = st.session_state.fc_cards

        if not cards:
            st.success("No cards due for review! Come back later.")
            st.session_state.fc_deck = None
            return

        if st.session_state.fc_current >= len(cards):
            st.success(f"Session complete! Reviewed {len(cards)} cards.")

            # Save cards back to their decks
            if st.session_state.get('fc_is_mixed', False):
                # Save each deck separately
                for deck_name, deck_cards in st.session_state.fc_all_cards_by_deck.items():
                    deck_path = FLASHCARDS_DIR / deck_name
                    save_deck(deck_cards, deck_path)
            else:
                save_deck(st.session_state.fc_all_cards, selected_deck)

            # Log the flashcard session
            if 'fc_session_logged' not in st.session_state:
                progress = load_progress(SCHEDULE_DIR / "progress.json")
                if st.session_state.get('fc_is_mixed', False):
                    deck_name = "mixed"
                    deck_display = "All Decks (Mixed)"
                else:
                    deck_name = selected_deck.stem.replace("_domain", "")
                    deck_display = selected_deck.name
                progress = log_session(
                    progress,
                    session_type="flashcards",
                    topic_id=deck_name,
                    duration_minutes=len(cards) * 1,  # Estimate ~1 min per card
                    details={"cards_reviewed": len(cards), "deck": deck_display}
                )
                save_progress(progress, SCHEDULE_DIR / "progress.json")
                st.session_state.fc_session_logged = True

            if st.button("Start New Session"):
                st.session_state.fc_cards = []
                st.session_state.fc_current = 0
                st.session_state.pop('fc_session_logged', None)
                st.session_state.pop('fc_all_cards_by_deck', None)
                st.session_state.pop('fc_is_mixed', None)
                st.rerun()
            return

        card = cards[st.session_state.fc_current]

        # Progress indicator
        st.progress((st.session_state.fc_current) / len(cards))
        st.caption(f"Card {st.session_state.fc_current + 1} of {len(cards)} | {card.knowledge_area}")

        # Question
        st.subheader("Question")
        st.markdown(f"**{card.question}**")

        if card.card_type == "why":
            st.caption("(Think about WHY, not just WHAT)")

        # Answer reveal
        if not st.session_state.fc_show_answer:
            st.info("Think of your answer before revealing...")
            if st.button("Reveal Answer", type="primary"):
                st.session_state.fc_show_answer = True
                st.rerun()
        else:
            st.subheader("Answer")
            st.markdown(card.answer)

            if card.why_it_matters:
                st.markdown(f"**Why it matters:** {card.why_it_matters}")

            if card.related_concepts:
                st.caption(f"Related: {', '.join(card.related_concepts)}")

            st.divider()
            st.markdown("**How well did you recall this?**")

            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("Struggled (Again soon)", use_container_width=True):
                    rate_card(card, 2)
            with col2:
                if st.button("Got it (Some effort)", use_container_width=True):
                    rate_card(card, 4)
            with col3:
                if st.button("Easy (Perfect recall)", use_container_width=True):
                    rate_card(card, 5)


def rate_card(card: Card, quality: int):
    """Rate a card and move to next."""
    updated = sm2_update(card, quality)

    # Update in the full deck(s)
    if st.session_state.get('fc_is_mixed', False):
        # Mixed mode - find the card in its source deck
        source_deck = getattr(card, '_source_deck', None)
        if source_deck and source_deck in st.session_state.fc_all_cards_by_deck:
            deck_cards = st.session_state.fc_all_cards_by_deck[source_deck]
            for i, c in enumerate(deck_cards):
                if c.id == updated.id:
                    # Preserve source deck tag
                    updated._source_deck = source_deck
                    deck_cards[i] = updated
                    break
    else:
        # Single deck mode
        for i, c in enumerate(st.session_state.fc_all_cards):
            if c.id == updated.id:
                st.session_state.fc_all_cards[i] = updated
                break

    # Also update in the session cards list
    for i, c in enumerate(st.session_state.fc_cards):
        if c.id == updated.id:
            st.session_state.fc_cards[i] = updated
            break

    st.session_state.fc_current += 1
    st.session_state.fc_show_answer = False
    st.rerun()


def show_quiz():
    st.header("Practice Quiz")
    st.caption("Interleaved questions from multiple knowledge areas")

    # Initialize session state
    if 'quiz_questions' not in st.session_state:
        st.session_state.quiz_questions = []
        st.session_state.quiz_current = 0
        st.session_state.quiz_answers = []
        st.session_state.quiz_submitted = False
        st.session_state.quiz_show_explanation = False

    quiz_files = list(QUIZZES_DIR.glob("*.json"))
    quiz_files = [f for f in quiz_files if f.stem != "results"]

    if not quiz_files:
        st.warning("No quiz banks found.")
        st.info("Quiz questions will be created as we build out the study material.")

        with st.expander("Preview: How quizzes will work"):
            st.markdown("""
            **Scenario-based question (Apply level):**

            > A project manager discovers that a key stakeholder has been excluded from
            > important project communications. The stakeholder is now raising concerns
            > about project decisions. What should the PM do FIRST?

            - A) Update the communications management plan
            - B) Meet with the stakeholder to understand their concerns
            - C) Review the stakeholder register
            - D) Escalate to the sponsor

            *Select your answer, then see the explanation for WHY it's correct...*
            """)
        return

    if not st.session_state.quiz_questions:
        # Quiz setup
        st.subheader("Quiz Setup")

        num_questions = st.slider("Number of questions", 5, 50, 20)

        # Quiz mode selection
        quiz_mode = st.radio(
            "Quiz mode",
            ["ECO Weighted", "Focus on Weak Areas", "Random Interleaved"],
            help="ECO Weighted matches exam distribution. Weak Areas prioritizes topics you've struggled with."
        )

        # Show weak areas if that mode is selected
        results_file = QUIZZES_DIR / "results.json"
        weak_areas = get_weak_areas(results_file, threshold=0.75)
        if quiz_mode == "Focus on Weak Areas":
            if weak_areas:
                st.info(f"Will prioritize: {', '.join(weak_areas[:5])}")
            else:
                st.warning("No weak areas identified yet. Take some quizzes first, then this mode will target your trouble spots.")

        # Load all questions
        all_questions = []
        for qf in quiz_files:
            all_questions.extend(load_questions(qf))

        if st.button("Start Quiz", type="primary"):
            if quiz_mode == "ECO Weighted":
                st.session_state.quiz_questions = create_eco_weighted_quiz(all_questions, num_questions)
            elif quiz_mode == "Focus on Weak Areas" and weak_areas:
                # Prioritize questions from weak knowledge areas
                weak_questions = [q for q in all_questions if q.knowledge_area in weak_areas]
                other_questions = [q for q in all_questions if q.knowledge_area not in weak_areas]
                # Take 70% from weak areas, 30% from others (for interleaving)
                weak_count = min(int(num_questions * 0.7), len(weak_questions))
                other_count = num_questions - weak_count
                selected = random.sample(weak_questions, weak_count) if weak_count <= len(weak_questions) else weak_questions
                if other_count > 0 and other_questions:
                    selected.extend(random.sample(other_questions, min(other_count, len(other_questions))))
                random.shuffle(selected)
                st.session_state.quiz_questions = selected
            else:
                st.session_state.quiz_questions = create_interleaved_quiz(all_questions, num_questions)
            st.session_state.quiz_answers = [None] * len(st.session_state.quiz_questions)
            st.rerun()
    else:
        questions = st.session_state.quiz_questions
        current = st.session_state.quiz_current

        if not st.session_state.quiz_submitted:
            # Show current question
            q = questions[current]

            st.progress((current) / len(questions))
            st.caption(f"Question {current + 1} of {len(questions)} | {q.knowledge_area} | {q.difficulty.title()} | {q.question_type.title()}")

            st.markdown(f"**{q.question}**")

            # Options
            answer = st.radio(
                "Select your answer:",
                range(len(q.options)),
                format_func=lambda i: f"{chr(65+i)}. {q.options[i]}",
                key=f"q_{current}",
                index=st.session_state.quiz_answers[current] if st.session_state.quiz_answers[current] is not None else 0
            )
            st.session_state.quiz_answers[current] = answer

            # Navigation
            col1, col2, col3 = st.columns([1, 1, 1])

            with col1:
                if current > 0 and st.button("Previous"):
                    st.session_state.quiz_current -= 1
                    st.rerun()

            with col2:
                if current < len(questions) - 1:
                    if st.button("Next", type="primary"):
                        st.session_state.quiz_current += 1
                        st.rerun()

            with col3:
                if st.button("Submit Quiz"):
                    st.session_state.quiz_submitted = True
                    st.rerun()

        else:
            # Show results
            result = grade_quiz(questions, st.session_state.quiz_answers)

            score_pct = (result.correct / result.total_questions) * 100

            st.subheader("Quiz Results")

            col1, col2, col3 = st.columns(3)
            col1.metric("Score", f"{result.correct}/{result.total_questions}")
            col2.metric("Percentage", f"{score_pct:.0f}%")
            col3.metric("Target", "75-80%")

            if score_pct >= 80:
                st.success("Excellent! You're on track.")
            elif score_pct >= 70:
                st.warning("Good progress. Review the missed questions.")
            else:
                st.error("More practice needed. Focus on the explanations below.")

            # By knowledge area
            st.subheader("By Knowledge Area")
            for area, stats in result.by_knowledge_area.items():
                pct = (stats['correct'] / stats['total']) * 100 if stats['total'] > 0 else 0
                st.write(f"**{area}:** {stats['correct']}/{stats['total']} ({pct:.0f}%)")

            # Review missed questions
            if result.missed_questions:
                st.subheader("Review Missed Questions")
                st.caption("Understanding WHY you got it wrong is more valuable than just seeing the right answer")

                for i, q in enumerate(questions):
                    if q.id in result.missed_questions:
                        with st.expander(f"Q: {q.question[:80]}..."):
                            st.markdown(f"**Your answer:** {chr(65 + st.session_state.quiz_answers[i])}. {q.options[st.session_state.quiz_answers[i]]}")
                            st.markdown(f"**Correct answer:** {chr(65 + q.correct_answer)}. {q.options[q.correct_answer]}")
                            st.markdown(f"**Why:** {q.explanation}")

            # Save result and log session
            save_result(result, QUIZZES_DIR / "results.json")

            if 'quiz_session_logged' not in st.session_state:
                progress = load_progress(SCHEDULE_DIR / "progress.json")
                # Get topics covered in quiz
                quiz_topics = list(result.by_knowledge_area.keys())
                progress = log_session(
                    progress,
                    session_type="quiz",
                    topic_id=None,  # Mixed topics
                    duration_minutes=len(questions) * 2,  # Estimate ~2 min per question
                    details={
                        "questions": result.total_questions,
                        "correct": result.correct,
                        "score_pct": score_pct,
                        "topics": quiz_topics
                    }
                )
                save_progress(progress, SCHEDULE_DIR / "progress.json")
                st.session_state.quiz_session_logged = True

            if st.button("Start New Quiz"):
                st.session_state.quiz_questions = []
                st.session_state.quiz_current = 0
                st.session_state.quiz_answers = []
                st.session_state.quiz_submitted = False
                st.session_state.pop('quiz_session_logged', None)
                st.rerun()


def show_progress():
    st.header("Progress Tracking")

    # Load all progress data
    progress = load_progress(SCHEDULE_DIR / "progress.json")
    topics = load_topics(SCHEDULE_DIR / "topics.json")
    config = load_config(SCHEDULE_DIR / "config.json")
    stats = get_study_stats(progress)

    # Load daily plan for adherence stats
    daily_plan_path = SCHEDULE_DIR / "daily_plan.json"
    daily_plan = load_plan(daily_plan_path)
    plan_stats = get_plan_adherence_stats(daily_plan) if daily_plan else {}

    # Top metrics row - Overall Study Stats
    st.subheader("Overall Progress")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        streak = stats.get('current_streak', 0)
        longest = stats.get('longest_streak', 0)
        streak_emoji = "🔥" if streak >= 3 else ""
        st.metric(f"{streak_emoji} Current Streak", f"{streak} days", delta=f"Best: {longest}")

    with col2:
        total_min = stats.get('total_minutes', 0)
        hours = total_min // 60
        mins = total_min % 60
        st.metric("Total Study Time", f"{hours}h {mins}m")

    with col3:
        total_sessions = stats.get('total_sessions', 0)
        st.metric("Study Sessions", total_sessions)

    with col4:
        chapters_read = stats.get('chapters_read', 0)
        total_chapters = len([t for t in topics if t.study_guide])
        pct = int((chapters_read / total_chapters) * 100) if total_chapters > 0 else 0
        st.metric("Chapters Read", f"{chapters_read}/{total_chapters}", delta=f"{pct}%")

    # Plan Adherence section (if daily plan exists)
    if plan_stats and plan_stats.get('total_activities', 0) > 0:
        st.divider()
        st.subheader("Plan Adherence")

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            adherence = plan_stats.get('adherence_percent', 0)
            adherence_emoji = "✅" if adherence >= 80 else "⚠️" if adherence >= 50 else "📉"
            st.metric(
                f"{adherence_emoji} Overall Adherence",
                f"{adherence}%",
                delta=f"{plan_stats.get('completed_activities', 0)}/{plan_stats.get('total_activities', 0)} activities"
            )

        with col2:
            week_completed = plan_stats.get('this_week_completed', 0)
            week_total = plan_stats.get('this_week_total', 0)
            week_pct = plan_stats.get('this_week_percent', 0)
            st.metric(
                "This Week",
                f"{week_completed}/{week_total}",
                delta=f"{week_pct}%"
            )

        with col3:
            days_on_track = plan_stats.get('days_on_track', 0)
            days_total = plan_stats.get('days_total', 0)
            st.metric(
                "Days Completed",
                f"{days_on_track}/{days_total}",
                delta="all activities done"
            )

        with col4:
            overdue = plan_stats.get('overdue_count', 0)
            if overdue > 0:
                st.metric("⚠️ Overdue", overdue, delta="activities pending")
            else:
                today_done = plan_stats.get('current_day_complete', False)
                if today_done:
                    st.metric("✅ Today", "Complete!", delta="all done")
                else:
                    st.metric("📋 Today", "In Progress", delta="keep going!")

    st.divider()

    # Create tabs for different progress views
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "ECO Domains", "Reading", "Videos", "Flashcards", "Quizzes", "Activity Log"
    ])

    with tab1:
        show_eco_domain_progress()

    with tab2:
        show_reading_progress(topics, progress)

    with tab3:
        show_video_progress()

    with tab4:
        show_flashcard_progress()

    with tab5:
        show_quiz_progress()

    with tab6:
        show_activity_log(progress)

    # Export section
    st.divider()
    show_export_options(progress, config, stats)


def show_export_options(progress: dict, config, stats: dict):
    """Show export options for progress data."""
    st.subheader("Export Data")

    col1, col2 = st.columns(2)

    with col1:
        # Export progress data as JSON
        export_data = {
            "exported_at": datetime.now().isoformat() if 'datetime' in dir() else json.dumps(progress.get('updated', '')),
            "config": {
                "certification": config.certification,
                "exam_date": config.exam_date,
                "exam_date_confirmed": config.exam_date_confirmed
            },
            "stats": stats,
            "reading_progress": progress.get('reading_progress', {}),
            "sessions": progress.get('sessions', []),
            "streaks": progress.get('streaks', {})
        }

        # Need to import datetime for export timestamp
        from datetime import datetime as dt
        export_data["exported_at"] = dt.now().isoformat()

        export_json = json.dumps(export_data, indent=2, ensure_ascii=False)

        st.download_button(
            label="📥 Download Progress (JSON)",
            data=export_json,
            file_name=f"capm_progress_{dt.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

    with col2:
        # Export summary as text
        from datetime import datetime as dt

        summary_lines = [
            f"CAPM Study Progress Report",
            f"Generated: {dt.now().strftime('%Y-%m-%d %H:%M')}",
            f"",
            f"Exam Date: {config.exam_date or 'Not set'}",
            f"",
            f"=== Study Stats ===",
            f"Current Streak: {stats.get('current_streak', 0)} days",
            f"Longest Streak: {stats.get('longest_streak', 0)} days",
            f"Total Study Time: {stats.get('total_minutes', 0)} minutes",
            f"Total Sessions: {stats.get('total_sessions', 0)}",
            f"Chapters Read: {stats.get('chapters_read', 0)}",
            f"",
            f"=== Reading Progress ===",
        ]

        reading = progress.get('reading_progress', {})
        for topic_id, rp in reading.items():
            status = rp.get('status', 'not_started')
            completed_at = rp.get('completed_at', '')[:10] if rp.get('completed_at') else ''
            if status == 'completed':
                summary_lines.append(f"  ✓ {topic_id} (completed {completed_at})")
            elif status == 'in_progress':
                summary_lines.append(f"  → {topic_id} (in progress)")

        summary_text = "\n".join(summary_lines)

        st.download_button(
            label="📄 Download Summary (TXT)",
            data=summary_text,
            file_name=f"capm_summary_{dt.now().strftime('%Y%m%d')}.txt",
            mime="text/plain",
            use_container_width=True
        )


def show_eco_domain_progress():
    """Show detailed ECO domain breakdown with all components."""
    st.subheader("ECO Domain Analysis")

    # Get the calculated scores from the Home page function
    eco_scores = calculate_eco_domain_scores()

    # ECO Domain weights
    domain_weights = {1: 36, 2: 17, 3: 20, 4: 27}
    domain_full_names = {
        1: "PM Fundamentals & Core Concepts",
        2: "Predictive, Plan-Based Methodologies",
        3: "Agile Frameworks/Methodologies",
        4: "Business Analysis Frameworks"
    }

    # Overall readiness (weighted by exam weights)
    weighted_score = sum(
        eco_scores[d]["score"] * (domain_weights[d] / 100)
        for d in eco_scores
    )

    st.metric("Overall Exam Readiness", f"{weighted_score:.0f}%",
              delta="weighted by ECO domain importance")

    st.divider()

    # Detailed breakdown per domain
    for domain in sorted(eco_scores.keys()):
        data = eco_scores[domain]
        score = data["score"]

        # Color indicator
        if score >= 70:
            status = "🟢"
        elif score >= 40:
            status = "🟡"
        else:
            status = "🔴"

        with st.expander(f"{status} Domain {domain}: {domain_full_names[domain]} ({score:.0f}%)", expanded=False):
            st.caption(f"Exam weight: {domain_weights[domain]}%")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown(f"**Theoretical Base: {data['theoretical_avg']:.0f}%**")
                st.caption("Content consumption")
                for comp in data["theoretical"]:
                    pct = comp["value"]
                    bar = "█" * int(pct // 10) + "░" * (10 - int(pct // 10))
                    st.markdown(f"{comp['name']}: {bar} {pct:.0f}%")
                    st.caption(f"  {comp['detail']}")

            with col2:
                st.markdown(f"**Practical Application: {data['practical_avg']:.0f}%**")
                st.caption("Retrieval practice")
                for comp in data["practical"]:
                    pct = comp["value"]
                    bar = "█" * int(pct // 10) + "░" * (10 - int(pct // 10))
                    st.markdown(f"{comp['name']}: {bar} {pct:.0f}%")
                    st.caption(f"  {comp['detail']}")

            # Recommendation
            if data['theoretical_avg'] > data['practical_avg'] + 20:
                st.info("💡 You've consumed content but need more practice. Focus on flashcards and quizzes.")
            elif data['practical_avg'] > data['theoretical_avg'] + 20:
                st.info("💡 Good recall skills, but review the source material for deeper understanding.")
            elif score < 40:
                st.warning("⚠️ This domain needs attention. Start with reading/videos, then practice.")


def show_video_progress():
    """Show PrepCast video progress."""
    st.subheader("PrepCast Video Progress")

    prepcast_path = PREPCAST_DIR / "lessons.json"

    if not prepcast_path.exists():
        st.info("No PrepCast data found.")
        return

    try:
        with open(prepcast_path, 'r', encoding='utf-8') as f:
            prepcast_data = json.load(f)
    except (json.JSONDecodeError, IOError):
        st.error("Could not load PrepCast data.")
        return

    lessons = prepcast_data.get('lessons', [])
    eco_domains = prepcast_data.get('eco_domains', {})

    if not lessons:
        st.info("No lessons found.")
        return

    # Overall stats
    core_lessons = [l for l in lessons if l.get('is_core', False)]
    optional_lessons = [l for l in lessons if not l.get('is_core', False)]

    core_watched = sum(1 for l in core_lessons if l.get('status') == 'watched')
    optional_watched = sum(1 for l in optional_lessons if l.get('status') == 'watched')

    core_minutes = sum(l.get('duration_minutes', 0) for l in core_lessons if l.get('status') == 'watched')
    optional_minutes = sum(l.get('duration_minutes', 0) for l in optional_lessons if l.get('status') == 'watched')

    col1, col2, col3 = st.columns(3)

    with col1:
        core_pct = int((core_watched / len(core_lessons)) * 100) if core_lessons else 0
        st.metric("Core Lessons", f"{core_watched}/{len(core_lessons)}", delta=f"{core_pct}%")
        st.caption(f"{core_minutes} min watched")

    with col2:
        opt_pct = int((optional_watched / len(optional_lessons)) * 100) if optional_lessons else 0
        st.metric("Optional Lessons", f"{optional_watched}/{len(optional_lessons)}", delta=f"{opt_pct}%")
        st.caption(f"{optional_minutes} min watched")

    with col3:
        total_watched = core_watched + optional_watched
        total_lessons = len(lessons)
        total_pct = int((total_watched / total_lessons) * 100) if total_lessons else 0
        st.metric("Total Progress", f"{total_watched}/{total_lessons}", delta=f"{total_pct}%")

    st.divider()

    # Progress by ECO Domain
    st.markdown("**Progress by ECO Domain:**")

    domain_stats = {}
    for lesson in lessons:
        eco = lesson.get('eco_domain', 'other')
        if eco not in domain_stats:
            domain_stats[eco] = {'total': 0, 'watched': 0, 'minutes_total': 0, 'minutes_watched': 0}
        domain_stats[eco]['total'] += 1
        domain_stats[eco]['minutes_total'] += lesson.get('duration_minutes', 0)
        if lesson.get('status') == 'watched':
            domain_stats[eco]['watched'] += 1
            domain_stats[eco]['minutes_watched'] += lesson.get('duration_minutes', 0)

    # Map domain keys to names
    domain_names = {
        'domain1': 'Domain 1: PM Fundamentals',
        'domain2': 'Domain 2: Predictive',
        'domain3': 'Domain 3: Agile',
        'domain4': 'Domain 4: Business Analysis',
        'intro': 'Introduction/Overview',
        'other': 'Other'
    }

    for domain_key in ['domain1', 'domain2', 'domain3', 'domain4', 'intro', 'other']:
        if domain_key in domain_stats:
            stats = domain_stats[domain_key]
            pct = int((stats['watched'] / stats['total']) * 100) if stats['total'] > 0 else 0
            bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
            name = domain_names.get(domain_key, domain_key)
            st.markdown(f"**{name}**: {bar} {pct}% ({stats['watched']}/{stats['total']} lessons)")

    st.divider()

    # Module breakdown
    st.markdown("**Progress by Module:**")

    # Group by module
    modules = {}
    for lesson in lessons:
        module_id = lesson.get('module_id', 'Unknown')
        module_title = lesson.get('module_title', 'Unknown')
        if module_id not in modules:
            modules[module_id] = {'title': module_title, 'lessons': []}
        modules[module_id]['lessons'].append(lesson)

    for module_id in sorted(modules.keys()):
        module = modules[module_id]
        total = len(module['lessons'])
        watched = sum(1 for l in module['lessons'] if l.get('status') == 'watched')
        pct = int((watched / total) * 100) if total > 0 else 0

        if pct == 100:
            icon = "✅"
        elif pct > 0:
            icon = "📖"
        else:
            icon = "○"

        st.markdown(f"{icon} **{module_id}**: {module['title']} ({watched}/{total})")


def show_reading_progress(topics: list, progress: dict):
    """Show reading progress by chapter."""
    st.subheader("Reading Progress")

    reading_topics = [t for t in topics if t.study_guide]
    reading_progress = progress.get('reading_progress', {})

    completed = 0
    in_progress = 0
    not_started = 0

    for topic in reading_topics:
        status = reading_progress.get(topic.id, {}).get('status', 'not_started')
        if status == 'completed':
            completed += 1
        elif status == 'in_progress':
            in_progress += 1
        else:
            not_started += 1

    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Completed", completed, delta="✅")
    col2.metric("In Progress", in_progress, delta="📖")
    col3.metric("Not Started", not_started, delta="○")

    st.divider()

    # Chapter list
    for topic in sorted(reading_topics, key=lambda t: t.order):
        status = reading_progress.get(topic.id, {}).get('status', 'not_started')
        completed_at = reading_progress.get(topic.id, {}).get('completed_at')

        icon = {"completed": "✅", "in_progress": "📖", "not_started": "○"}.get(status, "○")

        if status == 'completed' and completed_at:
            date_str = completed_at[:10]
            st.markdown(f"{icon} **{topic.name}** - *completed {date_str}*")
        elif status == 'in_progress':
            st.markdown(f"{icon} **{topic.name}** - *in progress*")
        else:
            st.markdown(f"{icon} {topic.name}")


def show_flashcard_progress():
    """Show flashcard statistics."""
    st.subheader("Flashcard Progress")

    deck_files = list(FLASHCARDS_DIR.glob("*.json"))

    if not deck_files:
        st.info("No flashcard decks found.")
        return

    total_cards = 0
    total_due = 0
    total_mastered = 0  # Cards with interval > 21 days

    deck_stats = []

    for deck_file in deck_files:
        cards = load_deck(deck_file)
        due = get_due_cards(cards)
        stats = get_deck_stats(cards)

        deck_name = deck_file.stem.replace("_domain", "").replace("_", " ").title()
        total_cards += len(cards)
        total_due += len(due)
        total_mastered += stats.get('mastered', 0)

        deck_stats.append({
            'name': deck_name,
            'total': len(cards),
            'due': len(due),
            'mastered': stats.get('mastered', 0),
            'learning': stats.get('learning', 0)
        })

    # Summary
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Cards", total_cards)
    col2.metric("Due for Review", total_due)
    col3.metric("Mastered", total_mastered)

    st.divider()

    # By deck
    st.caption("Progress by deck:")
    for deck in sorted(deck_stats, key=lambda d: d['name']):
        mastery_pct = int((deck['mastered'] / deck['total']) * 100) if deck['total'] > 0 else 0
        bar = "█" * (mastery_pct // 10) + "░" * (10 - mastery_pct // 10)
        st.markdown(f"**{deck['name']}**: {bar} {mastery_pct}% mastered ({deck['due']} due)")


def show_quiz_progress():
    """Show quiz statistics."""
    st.subheader("Quiz Progress")

    results_file = QUIZZES_DIR / "results.json"

    if not results_file.exists():
        st.info("No quiz history yet. Take some quizzes to see your progress!")
        return

    try:
        with open(results_file, 'r') as f:
            data = json.load(f)
    except (json.JSONDecodeError, IOError):
        st.error("Quiz results file is corrupted. Starting fresh.")
        return

    results = data.get('results', [])

    if not results:
        st.info("No quiz history yet.")
        return

    # Overall stats
    total_questions = sum(r['total_questions'] for r in results)
    total_correct = sum(r['correct'] for r in results)
    overall_pct = (total_correct / total_questions) * 100 if total_questions > 0 else 0

    col1, col2, col3 = st.columns(3)
    col1.metric("Quizzes Taken", len(results))
    col2.metric("Total Questions", total_questions)
    col3.metric("Overall Accuracy", f"{overall_pct:.0f}%")

    st.divider()

    # Weak areas
    st.markdown("**Areas Needing Focus:**")
    weak = get_weak_areas(results_file, threshold=0.75)
    if weak:
        for area in weak:
            st.warning(f"Review needed: **{area}**")
    else:
        st.success("No weak areas identified. Keep practicing!")

    st.divider()

    # Recent quiz scores
    st.markdown("**Recent Quizzes:**")
    for r in reversed(results[-5:]):
        pct = (r['correct'] / r['total_questions']) * 100
        date_str = r['timestamp'][:10]
        emoji = "🎯" if pct >= 80 else "📈" if pct >= 70 else "📚"
        st.write(f"{emoji} {date_str}: {r['correct']}/{r['total_questions']} ({pct:.0f}%)")


def show_activity_log(progress: dict):
    """Show recent activity log."""
    st.subheader("Activity Log")

    sessions = progress.get('sessions', [])

    if not sessions:
        st.info("No activity recorded yet. Start studying to see your activity here!")
        return

    # Show most recent 20 sessions
    recent = sessions[-20:][::-1]  # Reverse to show newest first

    for session in recent:
        session_type = session.get('type', 'unknown')
        timestamp = session.get('timestamp', '')[:16].replace('T', ' ')
        duration = session.get('duration_minutes', 0)
        topic_id = session.get('topic_id', '')
        details = session.get('details', {})

        icon = {"reading": "📖", "flashcards": "🎴", "quiz": "📝"}.get(session_type, "📌")

        if session_type == 'reading':
            st.markdown(f"{icon} **{timestamp}** - Read: {topic_id} ({duration} min)")
        elif session_type == 'flashcards':
            cards = details.get('cards_reviewed', 0)
            st.markdown(f"{icon} **{timestamp}** - Flashcards: {topic_id} ({cards} cards)")
        elif session_type == 'quiz':
            score = details.get('score_pct', 0)
            questions = details.get('questions', 0)
            st.markdown(f"{icon} **{timestamp}** - Quiz: {questions} questions ({score:.0f}%)")
        else:
            st.markdown(f"{icon} **{timestamp}** - {session_type}")


if __name__ == "__main__":
    main()
