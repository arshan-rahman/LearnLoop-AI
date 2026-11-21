import json,os,random
from core.question_bank import QUESTIONS
from core.concept_graph import CONCEPTS
def generate_question(concept_id,mastery):
    level="Easy" if mastery<30 else "Medium" if mastery<65 else "Hard"
    key=os.getenv("GEMINI_API_KEY")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model=genai.GenerativeModel(os.getenv("GEMINI_MODEL","gemini-1.5-flash"))
            prompt="Return only valid JSON with keys question, options (exactly four strings), answer (one exact option), explanation. Make one Class 10 Electricity "+level+" question for "+CONCEPTS[concept_id]["name"]+"."
            data=json.loads(model.generate_content(prompt).text.strip().removeprefix("```json").removesuffix("```").strip())
            if len(data["options"])==4 and data["answer"] in data["options"]:
                return {"id":100000+random.randrange(900000),"concept_id":concept_id,"concept":CONCEPTS[concept_id]["name"],"difficulty":level,"question":data["question"],"options":data["options"],"answer":data["answer"],"explanation":data["explanation"]}
        except Exception: pass
    pool=[q for q in QUESTIONS if q["concept_id"]==concept_id and q["difficulty"]==level] or [q for q in QUESTIONS if q["concept_id"]==concept_id]
    return dict(random.choice(pool)) if pool else None

