from database.db import get_student_mastery,save_attempt,record_learning,save_misconception,schedule_revision
from core.learner_model import update_mastery
from agents.misconception_agent import detect_misconception
def evaluate_answer(student_id,question,student_answer,reasoning="",session_id=None):
    expected=str(question["answer"]).strip().lower()
    given=str(student_answer).strip().lower()
    is_correct=given==expected or (expected in {"10 v","5 Ω","4 a","4 v","440 w"} and given.replace(" ","")==expected.replace(" ",""))
    cid=question["concept_id"]; mastery=get_student_mastery(student_id); old=float(mastery.get(cid,0)); new=update_mastery(old,is_correct)
    save_attempt(student_id,question["id"],cid,str(student_answer),is_correct,100 if is_correct else 0,reasoning,session_id)
    record_learning(student_id,cid,old,new,is_correct); schedule_revision(student_id,cid,new)
    misconception=None
    if not is_correct:
        misconception=detect_misconception(question,student_answer,reasoning)
        if misconception["detected"]: save_misconception(student_id,cid,misconception["type"],misconception["description"],misconception["confidence"])
    return {"is_correct":is_correct,"correct_answer":question["answer"],"explanation":question["explanation"],"old_mastery":old,"new_mastery":new,"concept":question["concept"],"misconception":misconception}

