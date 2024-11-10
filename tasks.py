from celery import Celery
from email_utils import send_email, generate_email_content
from app import db
from models import EmailTask

app = Celery('tasks', broker='redis://localhost:6379/0')

@app.task
def schedule_email_task():
    emails = EmailTask.query.filter_by(status='Pending').all()
    for email in emails:
        prompt = f"Generate a custom email for {email.company_name} located at {email.location}"
        email_content = generate_email_content(prompt)
        send_email(email.email, email_content)
        email.status = 'Sent'
        db.session.commit()
