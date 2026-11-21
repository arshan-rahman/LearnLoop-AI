import os
import tempfile
import unittest
from pathlib import Path
import database.db as db
from core.concept_graph import CONCEPTS
from core.question_bank import QUESTIONS
from core.assessment import evaluate_answer
from core.adaptive_engine import get_adaptive_question
from agents.tutor_agent import answer_question
from agents.question_agent import generate_question

class LearnLoopWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.api_key=os.environ.pop("GEMINI_API_KEY",None)
        self.tmp=tempfile.TemporaryDirectory()
        db.DB_PATH=Path(self.tmp.name)/"test.db"
        db.initialize_database(); db.seed_concepts(CONCEPTS)
        self.student=db.create_student("Test learner","test@example.invalid")
        db.initialize_student_mastery(self.student,CONCEPTS)
    def tearDown(self):
        self.tmp.cleanup()
        if self.api_key is not None: os.environ["GEMINI_API_KEY"]=self.api_key
    def test_answer_updates_mastery_and_records_misconception(self):
        q=next(q for q in QUESTIONS if q["id"]==7)
        result=evaluate_answer(self.student,q,"2.5 V","I divided current by resistance")
        self.assertFalse(result["is_correct"])
        self.assertTrue(result["misconception"]["detected"])
        self.assertEqual(result["new_mastery"],0)
        with db.get_connection() as c:
            row=c.execute("SELECT uncertainty FROM learner_mastery WHERE student_id=? AND concept_id=?",(self.student,"C5")).fetchone()
            self.assertLess(row["uncertainty"],1)
        self.assertEqual(len(db.get_attempt_history(self.student)),1)
        self.assertEqual(len(db.get_student_misconceptions(self.student)),1)
        self.assertEqual(len(db.get_revisions(self.student)),1)
    def test_correct_answer_does_not_create_instant_mastery(self):
        q=next(q for q in QUESTIONS if q["id"]==7)
        result=evaluate_answer(self.student,q,"10 V")
        self.assertTrue(result["is_correct"])
        self.assertLess(result["new_mastery"],100)
    def test_adaptive_question_and_question_bank_fallback(self):
        q=get_adaptive_question(db.get_student_mastery(self.student))
        self.assertIsNotNone(q); self.assertIn(q["question"]["concept_id"],CONCEPTS)
        generated=generate_question("C5",20)
        self.assertEqual(generated["concept_id"],"C5")
        self.assertEqual(len(generated["options"]),4)
    def test_local_tutor_fallback(self):
        os.environ.pop("GEMINI_API_KEY",None)
        self.assertIn("V = I",answer_question("Explain Ohm's law"))
    def test_assessment_history_is_separate(self):
        session=db.start_assessment(self.student); db.finish_assessment(session,70,10)
        with db.get_connection() as c:
            row=c.execute("SELECT score,total FROM assessment_sessions WHERE id=?",(session,)).fetchone()
        self.assertEqual((row["score"],row["total"]),(70,10))

if __name__=="__main__": unittest.main()






