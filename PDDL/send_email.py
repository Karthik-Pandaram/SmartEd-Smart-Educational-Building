import smtplib, ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "writer.banu11@gmail.com"  # Enter your address
receiver_email = "karthikp0712@gmail.com"  # Enter receiver address
password = "Dreambig@1"
message = """ """

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
