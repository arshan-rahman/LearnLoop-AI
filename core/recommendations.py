from core.concept_graph import CONCEPTS
def next_learning(mastery):
    ordered=sorted(CONCEPTS,key=lambda cid:mastery.get(cid,0))
    for cid in ordered:
        prereqs=CONCEPTS[cid]["prerequisites"]
        if mastery.get(cid,0)<70 and all(mastery.get(p,0)>=45 for p in prereqs):
            return {"concept_id":cid,"concept":CONCEPTS[cid]["name"],"activity":"Review the key idea, then complete an adaptive practice question."}
    cid=ordered[0]
    return {"concept_id":cid,"concept":CONCEPTS[cid]["name"],"activity":"Strengthen foundations with a short review and practice."}

