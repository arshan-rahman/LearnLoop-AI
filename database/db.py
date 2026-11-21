import os, sqlite3
from contextlib import contextmanager
from pathlib import Path
from config import DB_PATH

@contextmanager
def get_connection():
    path = Path(DB_PATH)
    path.parent.mkdir(parents=True, exist_ok=True)
    c=sqlite3.connect(str(path), timeout=15)
    c.row_factory=sqlite3.Row
    c.execute("PRAGMA foreign_keys=ON")
    try:
        yield c
        c.commit()
    except Exception:
        c.rollback()
        raise
    finally:
        c.close()

def initialize_database():
    with get_connection() as c:
        c.executescript("""
        CREATE TABLE IF NOT EXISTS students(id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE, role TEXT NOT NULL DEFAULT 'student', created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS concepts(id TEXT PRIMARY KEY,name TEXT NOT NULL,description TEXT,difficulty TEXT);
        CREATE TABLE IF NOT EXISTS concept_dependencies(concept_id TEXT,prerequisite_id TEXT,PRIMARY KEY(concept_id,prerequisite_id));
        CREATE TABLE IF NOT EXISTS questions(id INTEGER PRIMARY KEY, concept_id TEXT, question TEXT NOT NULL, answer TEXT NOT NULL, difficulty TEXT, question_type TEXT, options TEXT, explanation TEXT);
        CREATE TABLE IF NOT EXISTS learner_mastery(student_id INTEGER,concept_id TEXT,mastery REAL DEFAULT 0,attempts INTEGER DEFAULT 0,correct INTEGER DEFAULT 0,uncertainty REAL DEFAULT 1,last_practice TEXT,PRIMARY KEY(student_id,concept_id));
        CREATE TABLE IF NOT EXISTS mastery_history(id INTEGER PRIMARY KEY,student_id INTEGER,concept_id TEXT,old_mastery REAL,new_mastery REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS assessment_sessions(id INTEGER PRIMARY KEY,student_id INTEGER,score REAL,total INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS attempts(id INTEGER PRIMARY KEY,student_id INTEGER,question_id INTEGER,concept_id TEXT,student_answer TEXT,reasoning TEXT,is_correct INTEGER,score REAL,session_id INTEGER,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS misconceptions(id INTEGER PRIMARY KEY,student_id INTEGER,concept_id TEXT,misconception TEXT,reasoning_error TEXT,confidence REAL,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        CREATE TABLE IF NOT EXISTS revision_schedule(id INTEGER PRIMARY KEY,student_id INTEGER,concept_id TEXT,next_review TEXT,interval_days INTEGER DEFAULT 1,review_count INTEGER DEFAULT 0,completed_at TEXT,UNIQUE(student_id,concept_id));
        CREATE TABLE IF NOT EXISTS tutor_history(id INTEGER PRIMARY KEY,student_id INTEGER,role TEXT,message TEXT,created_at TEXT DEFAULT CURRENT_TIMESTAMP);
        """)
        student_cols={x["name"] for x in c.execute("PRAGMA table_info(students)")}
        if "role" not in student_cols: c.execute("ALTER TABLE students ADD COLUMN role TEXT NOT NULL DEFAULT 'student'")
        # Migrate earlier databases safely.
        cols={x["name"] for x in c.execute("PRAGMA table_info(attempts)")}
        for name, typ in [("reasoning","TEXT"),("session_id","INTEGER")]:
            if name not in cols: c.execute(f"ALTER TABLE attempts ADD COLUMN {name} {typ}")
        cols={x["name"] for x in c.execute("PRAGMA table_info(learner_mastery)")}
        for name, typ in [("attempts","INTEGER DEFAULT 0"),("correct","INTEGER DEFAULT 0"),("uncertainty","REAL DEFAULT 1"),("last_practice","TEXT")]:
            if name not in cols: c.execute(f"ALTER TABLE learner_mastery ADD COLUMN {name} {typ}")

def seed_concepts(concepts):
    with get_connection() as c:
        for cid,x in concepts.items():
            c.execute("INSERT OR IGNORE INTO concepts(id,name,description,difficulty) VALUES(?,?,?,?)",(cid,x["name"],x["description"],x["difficulty"]))
        for cid,x in concepts.items():
            for p in x["prerequisites"]: c.execute("INSERT OR IGNORE INTO concept_dependencies VALUES(?,?)",(cid,p))

def create_student(name,email=None,role="student"):
    with get_connection() as c:
        if email:
            c.execute("INSERT OR IGNORE INTO students(name,email,role) VALUES(?,?,?)",(name,email,role))
            row=c.execute("SELECT id FROM students WHERE email=?",(email,)).fetchone()
            return row["id"]
        cur=c.execute("INSERT INTO students(name,role) VALUES(?,?)",(name,role)); return cur.lastrowid

def initialize_student_mastery(student_id, concepts):
    with get_connection() as c:
        c.executemany("INSERT OR IGNORE INTO learner_mastery(student_id,concept_id) VALUES(?,?)",[(student_id,x) for x in concepts])

def get_student_mastery(student_id):
    with get_connection() as c: return {r["concept_id"]:r["mastery"] for r in c.execute("SELECT concept_id,mastery FROM learner_mastery WHERE student_id=?",(student_id,))}

def save_mastery(student_id,concept_id,mastery):
    with get_connection() as c: c.execute("INSERT INTO learner_mastery(student_id,concept_id,mastery) VALUES(?,?,?) ON CONFLICT(student_id,concept_id) DO UPDATE SET mastery=excluded.mastery",(student_id,concept_id,mastery))

def save_attempt(student_id,question_id,concept_id,student_answer,is_correct,score,reasoning="",session_id=None):
    with get_connection() as c:
        cur=c.execute("INSERT INTO attempts(student_id,question_id,concept_id,student_answer,reasoning,is_correct,score,session_id) VALUES(?,?,?,?,?,?,?,?)",(student_id,question_id,concept_id,student_answer,reasoning,int(is_correct),score,session_id)); return cur.lastrowid

def record_learning(student_id,concept_id,old,new,correct):
    with get_connection() as c:
        c.execute("INSERT INTO mastery_history(student_id,concept_id,old_mastery,new_mastery) VALUES(?,?,?,?)",(student_id,concept_id,old,new))
        c.execute("UPDATE learner_mastery SET mastery=?,attempts=attempts+1,correct=correct+?,uncertainty=MAX(.08,uncertainty*.88),last_practice=CURRENT_TIMESTAMP WHERE student_id=? AND concept_id=?",(new,int(correct),student_id,concept_id))

def save_misconception(student_id,concept_id,misconception,reasoning_error,confidence):
    with get_connection() as c: c.execute("INSERT INTO misconceptions(student_id,concept_id,misconception,reasoning_error,confidence) VALUES(?,?,?,?,?)",(student_id,concept_id,misconception,reasoning_error,confidence))

def get_student_misconceptions(student_id):
    with get_connection() as c: return [dict(r) for r in c.execute("SELECT * FROM misconceptions WHERE student_id=? ORDER BY created_at DESC",(student_id,))]

def get_attempt_history(student_id):
    with get_connection() as c: return [dict(r) for r in c.execute("SELECT * FROM attempts WHERE student_id=? ORDER BY created_at DESC",(student_id,))]

def schedule_revision(student_id,concept_id,mastery):
    from datetime import datetime,timedelta
    interval=1 if mastery<30 else 2 if mastery<50 else 4 if mastery<70 else 8 if mastery<85 else 16
    due=(datetime.now()+timedelta(days=interval)).date().isoformat()
    with get_connection() as c:
        c.execute("INSERT INTO revision_schedule(student_id,concept_id,next_review,interval_days) VALUES(?,?,?,?) ON CONFLICT(student_id,concept_id) DO UPDATE SET next_review=excluded.next_review,interval_days=excluded.interval_days,completed_at=NULL",(student_id,concept_id,due,interval))

def get_revisions(student_id):
    from datetime import date
    with get_connection() as c: return [dict(r) for r in c.execute("SELECT r.*,c.name FROM revision_schedule r JOIN concepts c ON c.id=r.concept_id WHERE student_id=? ORDER BY next_review",(student_id,))]

def complete_revision(student_id,concept_id,mastery):
    with get_connection() as c: c.execute("UPDATE revision_schedule SET review_count=review_count+1,completed_at=CURRENT_TIMESTAMP WHERE student_id=? AND concept_id=?",(student_id,concept_id))
    schedule_revision(student_id,concept_id,mastery)


def start_assessment(student_id):
    with get_connection() as c:
        cur=c.execute("INSERT INTO assessment_sessions(student_id,score,total) VALUES(?,0,0)",(student_id,))
        return cur.lastrowid

def finish_assessment(session_id,score,total):
    with get_connection() as c:
        c.execute("UPDATE assessment_sessions SET score=?,total=? WHERE id=?",(score,total,session_id))



