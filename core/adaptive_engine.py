import os,random
from core.question_bank import QUESTIONS
from core.concept_graph import CONCEPTS
def get_recommended_difficulty(mastery): return "Easy" if mastery<30 else "Medium" if mastery<60 else "Hard"
def get_weakest_concept(mastery):
    eligible=[cid for cid,c in CONCEPTS.items() if all(mastery.get(p,0)>=35 for p in c["prerequisites"])]
    return min(eligible or list(CONCEPTS),key=lambda cid:mastery.get(cid,0))
def get_adaptive_question(mastery,answered_ids=None):
    answered_ids=set(answered_ids or []); cid=get_weakest_concept(mastery); level=get_recommended_difficulty(mastery.get(cid,0))
    if os.getenv("GEMINI_API_KEY"):
        from agents.question_agent import generate_question
        generated=generate_question(cid,mastery.get(cid,0))
        if generated and generated["id"]>=100000: return {"question":generated,"concept_id":cid,"difficulty":generated["difficulty"]}
    candidates=[q for q in QUESTIONS if q["concept_id"]==cid and q["id"] not in answered_ids]
    if not candidates: candidates=[q for q in QUESTIONS if q["id"] not in answered_ids]
    if not candidates: return None
    q=random.choice([x for x in candidates if x["difficulty"]==level] or candidates)
    return {"question":q,"concept_id":q["concept_id"],"difficulty":q["difficulty"]}
def get_learning_recommendation(mastery):
    return [{"concept":c["name"],"mastery":mastery.get(cid,0),"recommended_action":"Review prerequisites and solve targeted practice."} for cid,c in CONCEPTS.items() if mastery.get(cid,0)<70]

