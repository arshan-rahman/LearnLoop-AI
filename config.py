import os
from dotenv import load_dotenv
load_dotenv()
APP_NAME="LearnLoop AI"
APP_TAGLINE="Learn Smarter. Adapt Faster. Master Every Concept."
SUBJECT="Class 10 Physics"
CHAPTER="Electricity"
DB_PATH=os.getenv("LEARNLOOP_DB","learnloop.db")
MASTERY_THRESHOLDS={"critical":30,"weak":50,"developing":70,"strong":85}

