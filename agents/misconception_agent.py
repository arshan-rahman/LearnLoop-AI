def detect_misconception(question,student_answer,reasoning=""):
    a=str(student_answer).lower().replace(" ",""); cid=question.get("concept_id")
    result={"detected":False,"type":"Uncertain","description":"There is not enough evidence to infer the reasoning. Explain how you approached this answer.","correction":question.get("explanation",""),"confidence":.2}
    rules={
      "C5":(("2.5v","2.5"),"Divided current by resistance","You may have divided I by R. For voltage use V = I × R.",.96),
      "C2":(("20a","5a"),"Confused charge and current","Current is charge divided by time: I = Q/t.",.8),
      "C3":(("36v","0.25v"),"Multiplied work and charge","Potential difference is work per unit charge: V = W/Q.",.8),
      "C6":(("1.2ω","1.2ohm"),"Applied the parallel rule to a series circuit","Series resistances add: Rtotal = R1 + R2.",.88),
      "C7":(("110w","110"),"Divided voltage by current","Power is P = V × I.",.87),
      "C4":(("increasingitsarea",),"Reversed the effect of conductor area","Resistance is inversely proportional to area: R = ρL/A.",.85),
    }
    rule=rules.get(cid)
    if rule and a in rule[0]: result.update(detected=True,type=rule[1],description=rule[2],correction=rule[2],confidence=rule[3])
    elif reasoning and len(reasoning)>12:
        result.update(description="Your reasoning needs a closer look. Compare each step with the worked explanation, then try a similar question.",confidence=.42)
    return result
def generate_feedback(misconception):
    return misconception.get("description","Let's revisit the concept.")

