# LearnLoop AI
Learn Smarter. Adapt Faster. Master Every Concept.

A Streamlit adaptive learning MVP for Class 10 Physics, Electricity. It records learner answers in SQLite, updates concept mastery, detects common misconceptions, chooses prerequisite-aware practice, schedules reviews, and provides an AI tutor fallback.

## Features
- Ten-question diagnostic with MCQ/numerical items, per-concept report, and persistent retakes.
- Seven-node Electricity concept graph and prerequisite-aware recommendations.
- Learner mastery, attempts, uncertainty, last-practice date, and mastery history.
- Adaptive question selection and rule-based misconception explanations.
- Gemini tutor integration when configured; local teaching content remains available offline.
- Spaced review dates, student dashboard, live teacher metrics and misconception history.
- SQLite access layer with schema migration for existing data.

## Architecture
Streamlit pages call database-backed services. Assessment evaluates and records an answer, detects likely misconception, updates learner evidence, schedules a review, and supports recommendation and practice selection. Tutor uses Gemini through the GEMINI_API_KEY setting with a local fallback.

## Setup
    py -m venv .venv
    .\.venv\Scripts\Activate.ps1
    pip install -r requirements.txt
    Copy-Item .env.example .env
    streamlit run app.py

Optionally configure GEMINI_API_KEY in .env. No key is needed for local tutor responses. Set LEARNLOOP_DB to change the database location. Demo learner selection is not production authentication.

## Judge demo workflow
Take the diagnostic, inspect concept mastery, answer an adaptive question and include reasoning for a mistake, ask the tutor for a worked example, then switch to Teacher for class insights.

## Limitations
Question generation uses the curated question bank; Gemini currently powers tutor responses only. Authentication, account creation, question breadth, and numeric answer tolerance should be expanded before production.

