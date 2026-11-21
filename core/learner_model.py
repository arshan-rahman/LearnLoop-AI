LEARNING_RATE=.22
def update_mastery(old_mastery,is_correct):
    # Bayesian-like incremental update: evidence moves mastery gradually, never instantly.
    target=100.0 if is_correct else 0.0
    rate=LEARNING_RATE if is_correct else LEARNING_RATE*.72
    return round(max(0,min(100,old_mastery+rate*(target-old_mastery))),2)
def get_mastery_status(value):
    return "Critical" if value<30 else "Weak" if value<50 else "Developing" if value<70 else "Strong" if value<85 else "Excellent"

