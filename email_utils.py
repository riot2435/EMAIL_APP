import openai
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def generate_email_content(prompt):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=200
    )
    return response.choices[0].text.strip()

def send_email(to_email, content):
    message = Mail(
        from_email='from@example.com',
        to_emails=to_email,
        subject='Customized Email',
        html_content=content
    )
    try:
        sg = SendGridAPIClient(os.getenv(''))
        sg.send(message)
    except Exception as e:
        print(e)
