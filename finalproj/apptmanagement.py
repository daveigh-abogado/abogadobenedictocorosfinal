import database as db
from flask import session
from datetime import datetime

def create_appt_from_session(day, time):
    appt = {}
    appt.setdefault("username",session["user"]["username"])
    appt.setdefault("appt_made",datetime.utcnow())
    appt.setdefault("appt_day",day)
    appt.setdefault("appt_time",time)
    
    db.create_appt(appt)
