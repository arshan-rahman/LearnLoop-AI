import streamlit as st
from agents.tutor_agent import answer_question
from core.concept_graph import CONCEPTS
from database.db import initialize_database,seed_concepts,create_student,initialize_student_mastery,get_student_mastery,get_connection
initialize_database(); seed_concepts(CONCEPTS); sid=create_student("Demo Student","student@learnloop.demo"); initialize_student_mastery(sid,CONCEPTS)
st.set_page_config(page_title="AI Tutor | LearnLoop AI",layout="wide"); st.title("💬 Electricity tutor"); st.caption("Ask about a concept or share a numerical problem.")
with get_connection() as c: history=[dict(r) for r in c.execute("SELECT role,message FROM tutor_history WHERE student_id=? ORDER BY id",(sid,))]
for row in history: st.chat_message(row["role"]).write(row["message"])
prompt=st.chat_input("Ask a question about Electricity")
if prompt:
    weak=[CONCEPTS[k]["name"] for k,v in get_student_mastery(sid).items() if v<50]
    with get_connection() as c: c.execute("INSERT INTO tutor_history(student_id,role,message) VALUES(?,?,?)",(sid,"user",prompt))
    reply=answer_question(prompt,weak)
    with get_connection() as c: c.execute("INSERT INTO tutor_history(student_id,role,message) VALUES(?,?,?)",(sid,"assistant",reply))
    st.rerun()

