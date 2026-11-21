
from core.concept_graph import CONCEPTS
from database.db import (
    initialize_database,
    seed_concepts,
    create_student,
    save_mastery
)

print("Initializing LearnLoop AI database...")

# Create all database tables
initialize_database()

# Insert syllabus concepts and dependencies
seed_concepts(CONCEPTS)

# Create a demo student
student_id = create_student(
    name="Rahul",
    email="rahul@learnloop.demo"
)

# Initialize mastery for every concept
initial_mastery = {
    "C1": 85,
    "C2": 85,
    "C3": 65,
    "C4": 40,
    "C5": 25,
    "C6": 35,
    "C7": 55
}

for concept_id, score in initial_mastery.items():
    save_mastery(student_id, concept_id, score)

print("\nDatabase initialized successfully!")
print("Student ID:", student_id)
print("Concepts inserted:", len(CONCEPTS))
print("Initial mastery records:", len(initial_mastery))
