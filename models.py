from datetime import datetime
from app import db

class EmailTask(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    location = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), default='Pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Analytics(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    total_emails_sent = db.Column(db.Integer, default=0)
    emails_pending = db.Column(db.Integer, default=0)
    emails_failed = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
