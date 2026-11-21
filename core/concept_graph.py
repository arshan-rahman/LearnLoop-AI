
# =====================================
# LEARNLOOP AI - CONCEPT KNOWLEDGE GRAPH
# =====================================

CONCEPTS = {
    "C1": {
        "name": "Electric Charge",
        "description": "Basic property of matter responsible for electrical interactions.",
        "difficulty": "Easy",
        "prerequisites": []
    },

    "C2": {
        "name": "Electric Current",
        "description": "Rate of flow of electric charge.",
        "difficulty": "Easy",
        "prerequisites": ["C1"]
    },

    "C3": {
        "name": "Potential Difference",
        "description": "Work done per unit charge between two points.",
        "difficulty": "Medium",
        "prerequisites": ["C1"]
    },

    "C4": {
        "name": "Resistance",
        "description": "Opposition offered to the flow of electric current.",
        "difficulty": "Medium",
        "prerequisites": ["C2", "C3"]
    },

    "C5": {
        "name": "Ohm's Law",
        "description": "Relationship between voltage, current and resistance.",
        "difficulty": "Medium",
        "prerequisites": ["C2", "C3", "C4"]
    },

    "C6": {
        "name": "Series and Parallel Circuits",
        "description": "Different ways of connecting electrical components.",
        "difficulty": "Hard",
        "prerequisites": ["C2", "C4", "C5"]
    },

    "C7": {
        "name": "Electric Power",
        "description": "Rate at which electrical energy is consumed or transferred.",
        "difficulty": "Medium",
        "prerequisites": ["C2", "C3", "C5"]
    }
}


def get_all_concepts():
    return CONCEPTS


def get_concept(concept_id):
    return CONCEPTS.get(concept_id)


def get_prerequisites(concept_id):
    concept = get_concept(concept_id)

    if concept:
        return concept["prerequisites"]

    return []


def get_weak_concepts(mastery, threshold=50):
    weak = []

    for concept_id, concept in CONCEPTS.items():

        score = mastery.get(concept_id, 0)

        if score < threshold:
            weak.append({
                "id": concept_id,
                "name": concept["name"],
                "mastery": score
            })

    return weak


def get_learning_path(concept_id):
    """
    Returns prerequisite concepts followed by
    the requested concept.
    """

    visited = set()
    result = []

    def visit(cid):

        if cid in visited:
            return

        visited.add(cid)

        for prerequisite in get_prerequisites(cid):
            visit(prerequisite)

        result.append(cid)

    visit(concept_id)

    return result
