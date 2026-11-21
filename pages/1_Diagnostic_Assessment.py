import streamlit as st
import pandas as pd
from core.concept_graph import CONCEPTS
from core.question_bank import QUESTIONS
from core.assessment import evaluate_answer
from database.db import initialize_database,seed_concepts,create_student,initialize_student_mastery,get_student_mastery,start_assessment,finish_assessment
initialize_database(); seed_concepts(CONCEPTS); sid=create_student("Demo Student","student@learnloop.demo"); initialize_student_mastery(sid,CONCEPTS)
st.set_page_config(page_title="Diagnostic | LearnLoop AI",layout="wide")
st.title("📝 Diagnostic assessment"); st.caption("Ten questions covering seven Electricity concepts. Results are saved for each attempt.")
for key,val in [("diag_index",0),("diag_results",[]),("diag_done",False),("diag_session_id",None),("diag_session_saved",False)]:
    if key not in st.session_state: st.session_state[key]=val
if st.session_state.diag_done:
    res=st.session_state.diag_results; pct=100*sum(x["is_correct"] for x in res)/max(1,len(res))
    st.success(f"Assessment complete · {pct:.0f}%")
    if not st.session_state.diag_session_saved:
        finish_assessment(st.session_state.diag_session_id,pct,len(res)); st.session_state.diag_session_saved=True
    current=get_student_mastery(sid)
    chart=pd.DataFrame([{"Concept":CONCEPTS[cid]["name"],"Mastery":current.get(cid,0),"Status":"Critical" if current.get(cid,0)<30 else "Weak" if current.get(cid,0)<50 else "Developing" if current.get(cid,0)<70 else "Strong"} for cid in CONCEPTS]); st.dataframe(chart,use_container_width=True)
    for n,r in enumerate(res,1):
        with st.expander(f"Question {n}: {r['concept']}"):
            st.write("Your answer:",r["student_answer"],"· Correct:",r["is_correct"]); st.write("Correct answer:",r["correct_answer"]); st.info(r["explanation"])
    if st.button("Retake assessment"):
        st.session_state.diag_index=0; st.session_state.diag_results=[]; st.session_state.diag_done=False; st.session_state.diag_session_saved=False; st.session_state.diag_session_id=None; st.rerun()
else:
    if st.session_state.diag_session_id is None: st.session_state.diag_session_id=start_assessment(sid)
    i=st.session_state.diag_index; q=QUESTIONS[i]
    st.progress((i+1)/len(QUESTIONS)); st.caption(f"Question {i+1}/{len(QUESTIONS)} · {q['concept']} · {q['difficulty']}")
    st.subheader(q["question"]); answer=st.radio("Choose an answer",q["options"],key=f"diag_{i}_{len(st.session_state.diag_results)}"); reasoning=st.text_input("How did you work it out? (optional)",key=f"reason_{i}")
    if st.button("Submit answer",type="primary"):
        result=evaluate_answer(sid,q,answer,reasoning,st.session_state.diag_session_id); result["student_answer"]=answer; st.session_state.diag_results.append(result)
        if i+1==len(QUESTIONS): st.session_state.diag_done=True
        else: st.session_state.diag_index+=1
        st.rerun()


