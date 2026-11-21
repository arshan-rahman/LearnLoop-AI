import streamlit as st
from core.concept_graph import CONCEPTS
from core.adaptive_engine import get_adaptive_question,get_learning_recommendation
from core.assessment import evaluate_answer
from database.db import initialize_database,seed_concepts,create_student,initialize_student_mastery,get_student_mastery
initialize_database(); seed_concepts(CONCEPTS); sid=create_student("Demo Student","student@learnloop.demo"); initialize_student_mastery(sid,CONCEPTS)
st.set_page_config(page_title="Practice | LearnLoop AI",layout="wide"); st.title("🎯 Adaptive practice"); mastery=get_student_mastery(sid)
for item in get_learning_recommendation(mastery): st.write(f"**{item['concept']}** · {item['mastery']:.0f}%")
for key,val in [("practice_q",None),("practice_result",None)]:
    if key not in st.session_state: st.session_state[key]=val
if st.session_state.practice_q is None:
    data=get_adaptive_question(mastery,[]); st.session_state.practice_q=data["question"] if data else None
q=st.session_state.practice_q
if q:
    st.caption(f"{q['concept']} · {q['difficulty']}"); st.subheader(q["question"])
    if st.session_state.practice_result is None:
        answer=st.radio("Your answer",q["options"],key=f"prac_{q['id']}_{len(get_student_mastery(sid))}"); reasoning=st.text_area("Explain your reasoning (helps detect misconceptions)")
        if st.button("Check answer",type="primary"):
            st.session_state.practice_result=evaluate_answer(sid,q,answer,reasoning); st.rerun()
    else:
        r=st.session_state.practice_result; st.success("Correct!" if r["is_correct"] else "Let's learn from this answer.")
        if not r["is_correct"] and r.get("misconception"): st.warning(r["misconception"]["description"])
        st.write("Correct answer:",r["correct_answer"]); st.info(r["explanation"]); st.caption(f"Mastery: {r['old_mastery']:.1f}% → {r['new_mastery']:.1f}%")
        if st.button("Next question",type="primary"): st.session_state.practice_q=None; st.session_state.practice_result=None; st.rerun()
else: st.success("Question bank complete. Ask the tutor for another worked example.")

