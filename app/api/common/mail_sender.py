import os
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def otp_sender(receiver_email, name, otp, subject):
    sender_email = os.getenv('EMAIL')
    password = os.getenv('PASSWORD')
    message = MIMEMultipart("alternative")
    text = """

        Hello {}

        Your Account Verification OTP  :  {}

    """.format(name, str(otp), receiver_email, str(otp))
    print(text)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email
    part1 = MIMEText(text, "plain")
    message.attach(part1)
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
            server.login(sender_email, password)
            server.sendmail(
                sender_email, receiver_email, message.as_string()
            )
            return True
    except Exception as e:
        print(e)
        return False