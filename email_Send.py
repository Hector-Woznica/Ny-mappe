import smtplib
from email.message import EmailMessage

# 1. Construct the email
msg = EmailMessage()
msg.set_content("This is the body of the email sent from a Python script.")
msg['Subject'] = "Automated Python Email"
msg['From'] = "your_email@gmail.com"
msg['To'] = "hector@woznica.com"

# 2. Send the email
try:
    # Connect to Gmail's SMTP server using SSL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login("eeumairali@gmail.com", "eqfr jywe opki apqy")
        server.send_message(msg)
    print("Email sent successfully!")
except Exception as e:
    print(f"Error: {e}")