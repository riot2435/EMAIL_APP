from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from email_utils import send_email, generate_email_content
from tasks import schedule_email_task
import openai
import pandas as pd
from google.oauth2 import service_account
from googleapiclient.discovery import build

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///email_sender.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'BLACKOUTAI_TECH'

db = SQLAlchemy(app)
openai.api_key = ''

from models import EmailTask, Analytics

SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
SERVICE_ACCOUNT_FILE = 'credentials/google_credentials.json'

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})
    
    if file and file.filename.endswith('.csv'):
        data = pd.read_csv(file)
     
        for index, row in data.iterrows():
            new_email_task = EmailTask(email=row['email'], company_name=row['company_name'], location=row['location'])
            db.session.add(new_email_task)
        db.session.commit()
        return jsonify({'message': 'File processed successfully'})

    return jsonify({'error': 'Invalid file format'})

@app.route('/upload_google_sheet', methods=['POST'])
def upload_google_sheet():
    sheet_id = request.json.get('sheet_id')
    sheet_range = request.json.get('range')
    service = build('sheets', 'v4', credentials=credentials)
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=sheet_id, range=sheet_range).execute()
    values = result.get('values', [])

    if not values:
        return jsonify({'error': 'No data found in the Google Sheet'})

    
    for row in values[1:]:  
        new_email_task = EmailTask(email=row[0], company_name=row[1], location=row[2])
        db.session.add(new_email_task)
    db.session.commit()
    return jsonify({'message': 'Google Sheet data processed successfully'})

@app.route('/customize_prompt', methods=['POST'])
def customize_prompt():
    custom_prompt = request.json.get('prompt')
    email_tasks = EmailTask.query.filter_by(status='Pending').all()

    for email in email_tasks:
        prompt = custom_prompt.format(company_name=email.company_name, location=email.location)
        email_content = generate_email_content(prompt)
        send_email(email.email, email_content)
        email.status = 'Sent'
        db.session.commit()

    return jsonify({'message': 'Emails sent successfully'})

@app.route('/send_emails', methods=['POST'])
def send_emails():
    schedule_email_task.apply_async()
    return jsonify({'message': 'Emails scheduled for sending'})

if __name__ == '__main__':
    app.run(debug=True)

