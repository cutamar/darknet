import smtplib
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
from twilio.rest import TwilioRestClient

gmail_user = ''  
gmail_password = ''

account_sid = ''
auth_token = ''
number = ''
call_url = 'http://demo.twilio.com/docs/voice.xml' 

def send_mail(send_to, subject, text, files=[]):
  if not isinstance(send_to, list):
    send_to_buffer = send_to
    send_to = []
    send_to.append(send_to_buffer)
  if not isinstance(files, list):
    files_buffer = files
    files = []
    files.append(files_buffer)
  msg = MIMEMultipart()
  msg['From'] = gmail_user
  msg['To'] = COMMASPACE.join(send_to)
  msg['Date'] = formatdate(localtime=True)
  msg['Subject'] = subject
  msg.attach( MIMEText(text) )
  for f in files:
    part = MIMEBase('application', "octet-stream")
    part.set_payload( open(f,"rb").read() )
    Encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
    msg.attach(part)
  smtp = smtplib.SMTP_SSL('smtp.gmail.com', 465)
  smtp.login(gmail_user, gmail_password)
  smtp.sendmail(gmail_user, send_to, msg.as_string())
  smtp.close()

def call_number(send_to):
    client = TwilioRestClient(account_sid, auth_token)
    if isinstance(send_to, list):
        for number in send_to:
            message = client.calls.create(to=number, from_=number, url=call_url)
    else:
        message = client.calls.create(to=send_to, from_=number, url=call_url)
