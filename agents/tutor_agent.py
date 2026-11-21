import os
def answer_question(prompt,weak_concepts=None):
    weak_concepts=weak_concepts or []
    key=os.getenv("GEMINI_API_KEY")
    if key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=key)
            model=genai.GenerativeModel(os.getenv("GEMINI_MODEL","gemini-1.5-flash"))
            context=", ".join(weak_concepts) or "none identified yet"
            return model.generate_content("You are a friendly Class 10 Electricity tutor. Explain simply, step by step, with a real example. Mention weak concepts when relevant: "+context+". Student asks: "+prompt).text
        except Exception: pass
    q=prompt.lower()
    if "ohm" in q or "voltage" in q: return "Ohm's law connects voltage (V), current (I), and resistance (R): V = I × R. Example: a 2 A current through 5 Ω gives V = 2 × 5 = 10 V. Check units and rearrange the equation when solving for another quantity."
    if "current" in q or "charge" in q: return "Electric current is how quickly charge flows: I = Q/t. If 12 coulombs pass a point in 3 seconds, I = 12/3 = 4 amperes. Current is measured in amperes (A)."
    if "power" in q: return "Electric power is the rate of energy transfer. Use P = V × I; a 10 V device drawing 2 A uses 20 W. Power is measured in watts."
    if "series" in q or "parallel" in q: return "In series, resistances add and the same current passes through each component. In parallel, each branch has the same voltage and total resistance decreases."
    focus=(" Your current focus includes "+", ".join(weak_concepts)+".") if weak_concepts else ""
    return "Electricity describes charge and how it moves. Start with the known quantities, choose the matching relationship (I=Q/t, V=W/Q, V=IR, P=VI), substitute values with units, and check whether the result is reasonable. Try asking about a specific formula or example."+focus



