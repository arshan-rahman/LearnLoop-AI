
from core.concept_graph import (
    get_all_concepts,
    get_learning_path,
    get_weak_concepts
)

print("\n===== LEARNLOOP CONCEPT GRAPH =====")

concepts = get_all_concepts()

for cid, concept in concepts.items():
    print(f"\n{cid}: {concept['name']}")
    print("Prerequisites:", concept["prerequisites"])

print("\n===== LEARNING PATH FOR OHM'S LAW =====")

path = get_learning_path("C5")

for cid in path:
    print("->", concepts[cid]["name"])

print("\n===== WEAK CONCEPTS =====")

mastery = {
    "C1": 85,
    "C2": 85,
    "C3": 65,
    "C4": 40,
    "C5": 25,
    "C6": 35,
    "C7": 55
}

weak = get_weak_concepts(mastery)

for concept in weak:
    print(
        concept["name"],
        "-",
        concept["mastery"],
        "%"
    )
