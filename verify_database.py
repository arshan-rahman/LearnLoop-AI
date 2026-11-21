
import sqlite3

conn = sqlite3.connect("learnloop.db")

tables = conn.execute("""
SELECT name
FROM sqlite_master
WHERE type='table'
ORDER BY name
""").fetchall()

print("\n===== DATABASE TABLES =====")

for table in tables:
    print("✓", table[0])

print("\n===== CONCEPT RECORDS =====")

concepts = conn.execute("""
SELECT id, name, difficulty
FROM concepts
""").fetchall()

for concept in concepts:
    print(concept)

print("\n===== PREREQUISITE RELATIONSHIPS =====")

relationships = conn.execute("""
SELECT c.name, p.name
FROM concept_dependencies d
JOIN concepts c ON c.id = d.concept_id
JOIN concepts p ON p.id = d.prerequisite_id
""").fetchall()

for relationship in relationships:
    print(relationship[1], "->", relationship[0])

conn.close()
