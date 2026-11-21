from database.db import schedule_revision, get_revisions, complete_revision
def schedule(student_id,concept_id,mastery): schedule_revision(student_id,concept_id,mastery)
def due_revisions(student_id): return get_revisions(student_id)
def complete(student_id,concept_id,mastery): complete_revision(student_id,concept_id,mastery)

