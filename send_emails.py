import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os
import time 

smtp_server = 'smtp.gmail.com'
smtp_port = 587
smtp_user = 'example_email@gmail.com'
smtp_password = 'Enter Here'

# Email content
subject = "Research Opportunity Request"
body = """
Greetings Dr. {name},

Write message here

Thank you, Name
Westfield High School

"""

def send_email(to_email, to_name, attachments=None):
    # Create message
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body.format(name=to_name), 'plain'))
    
    # Attach files
    if attachments:
        for filepath in attachments:
            with open(filepath, 'rb') as file:
                part = MIMEApplication(file.read(), Name=os.path.basename(filepath))
                part['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(filepath)
                msg.attach(part)
    
    # Connect to SMTP server and send email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)
        print(f"Email sent to {to_name} ({to_email})")

#examples

email_list = [
    {'name': 'Harry Potter', 'email': 'harry.potter@gmail.com', 'attachments': [r"Resume Filepath", r"Transcript Filepath"]},
    {'name': 'Marry Poppins', 'email': 'marry.poppins@gmail.com', 'attachments': [r"Resume Filepath", r"Transcript Filepath"]},
    {'name': 'Patrick Star', 'email': 'patrick.star@gmail.com', 'attachments': [r"Resume Filepath", r"Transcript Filepath"]}
]


count=0
for participant in email_list:
    send_email(participant['email'], participant['name'], participant.get('attachments', None))
    count+=1
    time.sleep(5)
    
print(count)






