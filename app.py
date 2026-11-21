import streamlit as st
import pandas as pd
import plotly.express as px
from config import APP_NAME,APP_TAGLINE
from core.concept_graph import CONCEPTS
from core.recommendations import next_learning
from database.db import initialize_database,seed_concepts,create_student,initialize_student_mastery,get_student_mastery,get_revisions,get_attempt_history,get_connection
st.set_page_config(page_title=APP_NAME,page_icon="🧠",layout="wide")
initialize_database(); seed_concepts(CONCEPTS)
demo_id=create_student("Demo Student","student@learnloop.demo"); initialize_student_mastery(demo_id,CONCEPTS)
st.markdown("""<style>.stApp{background:#f5f7fb;color:#172033}.block-container{max-width:1200px;padding-top:2rem}.hero{padding:26px;border-radius:18px;background:linear-gradient(120deg,#172554,#4338ca);color:white}.hero h1{color:white}.hero p{color:#dbeafe}.stMarkdown,.stCaption,.stMetric label,.stMetric [data-testid=stMetricValue]{color:#172033!important}.stMetric{background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:14px}.stDataFrame,.stPlotlyChart{background:#fff;border-radius:14px}</style>""",unsafe_allow_html=True)
st.sidebar.title("🧠 LearnLoop AI"); role=st.sidebar.radio("Workspace",["Student","Teacher"])
with get_connection() as c: students=[dict(r) for r in c.execute("SELECT id,name FROM students WHERE role='student' ORDER BY id")]
if not students: students=[{"id":demo_id,"name":"Demo Student"}]
if role=="Student":
    selected=st.sidebar.selectbox("Learner",students,format_func=lambda x:x["name"]); sid=selected["id"]; mastery=get_student_mastery(sid)
    st.markdown(f'<div class="hero"><h1>Welcome, {selected["name"]} 👋</h1><p>{APP_TAGLINE}<br>Class 10 Physics · Electricity</p></div>',unsafe_allow_html=True)
    avg=sum(mastery.values())/max(1,len(mastery)); weak=sum(v<50 for v in mastery.values())
    a,b,c=st.columns(3); a.metric("Chapter mastery",f"{avg:.0f}%"); b.metric("Concepts in syllabus",len(CONCEPTS)); c.metric("Concepts to strengthen",weak)
    chart=pd.DataFrame([{"Concept":CONCEPTS[k]["name"],"Mastery":mastery.get(k,0)} for k in CONCEPTS])
    st.subheader("Your concept mastery"); fig=px.bar(chart,x="Concept",y="Mastery",range_y=[0,100],color="Mastery",color_continuous_scale=["#f97316","#6366f1"],template="plotly_white"); fig.update_layout(paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",font_color="#172033"); st.plotly_chart(fig,use_container_width=True)
    rec=next_learning(mastery); st.subheader("Recommended next step"); st.info(f"**{rec['concept']}** — {rec['activity']}")
    st.subheader("Revision schedule"); revisions=get_revisions(sid)
    if revisions:
        for rev in revisions:
            col1,col2=st.columns([4,1]); col1.write(f"{rev['name']} · due {rev['next_review']}")
            if col2.button("Review",key=f"rev_{rev['concept_id']}"):
                from database.db import complete_revision
                complete_revision(sid,rev["concept_id"],mastery.get(rev["concept_id"],0)); st.rerun()
    else: st.caption("Revision sessions are scheduled after practice answers.")
    st.metric("Recorded answers",len(get_attempt_history(sid)))
    st.page_link("pages/1_Diagnostic_Assessment.py",label="Take diagnostic assessment",icon="📝"); st.page_link("pages/2_Adaptive_Practice.py",label="Start adaptive practice",icon="🎯"); st.page_link("pages/3_AI_Tutor.py",label="Ask the AI tutor",icon="💬")
else:
    st.title("👩‍🏫 Teacher dashboard"); st.caption("Live class insight from saved learner records.")
    with get_connection() as c:
        roster=[dict(r) for r in c.execute("SELECT id,name FROM students WHERE role='student' ORDER BY name")]
        rows=[dict(r) for r in c.execute("SELECT s.name,c.name concept,m.mastery,m.attempts FROM learner_mastery m JOIN students s ON s.id=m.student_id JOIN concepts c ON c.id=m.concept_id WHERE s.role='student'")]
        misconceptions=[dict(r) for r in c.execute("SELECT c.name concept,x.misconception,x.confidence,x.created_at FROM misconceptions x JOIN concepts c ON c.id=x.concept_id ORDER BY x.created_at DESC LIMIT 30")]
        assessments=[dict(r) for r in c.execute("SELECT s.name,a.score,a.total,a.created_at FROM assessment_sessions a JOIN students s ON s.id=a.student_id ORDER BY a.created_at DESC LIMIT 20")]
    x,y,z=st.columns(3); x.metric("Students",len(roster)); y.metric("Average mastery",f"{sum(r['mastery'] for r in rows)/len(rows):.1f}%" if rows else "—"); z.metric("Recorded answers",sum(r["attempts"] for r in rows))
    if rows:
        df=pd.DataFrame(rows); st.subheader("Concept mastery by student"); heat=px.imshow(df.pivot_table(index="name",columns="concept",values="mastery",aggfunc="mean").fillna(0),text_auto=".0f",zmin=0,zmax=100,color_continuous_scale="RdYlGn",template="plotly_white"); heat.update_layout(paper_bgcolor="#ffffff",plot_bgcolor="#ffffff",font_color="#172033"); st.plotly_chart(heat,use_container_width=True)
        st.subheader("Class concept averages"); st.dataframe(df.groupby("concept",as_index=False).mastery.mean().sort_values("mastery"),use_container_width=True)
        st.subheader("Students needing attention"); st.dataframe(df.groupby("name",as_index=False).mastery.mean().query("mastery < 50"),use_container_width=True)
    else: st.info("No learner activity recorded yet. Ask a student to complete the diagnostic.")
    st.subheader("Recent assessment history"); st.dataframe(assessments,use_container_width=True); st.subheader("Common misconceptions"); st.dataframe(misconceptions,use_container_width=True)


