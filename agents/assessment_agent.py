from core.assessment import evaluate_answer
def assess(student_id,question,answer,reasoning="",session_id=None):
    return evaluate_answer(student_id,question,answer,reasoning,session_id)

