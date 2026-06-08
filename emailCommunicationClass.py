import email
import smtplib
import imaplib
import threading
import time
from email.message import EmailMessage 
from datetime import datetime, timedelta

class emailCommunication:
    def __init__(self, onMessage, onShowWarning):
        self.onMessage = onMessage
        self.onShowWarning = onShowWarning
        self.isReceiving = False

    def sendEmail(self, userNamem, userPassword,  receiverEmail, messageText):
        senderEmail = userNamem
        senderPassword = userPassword
        msg = EmailMessage()
        msg['Subject'] = f"Messege from {senderEmail}"
        msg['From'] = senderEmail
        msg['To'] = receiverEmail
        msg.set_content(messageText)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(senderEmail, senderPassword)
            smtp.send_message(msg)

    def startReceivingEmail(self, userName, userPassword, receiverEmail):
        if self.isReceiving: 
            return
        self.isReceiving = True
        thread = threading.Thread(target=self.receiveEmailLoop, args=(userName, userPassword, receiverEmail), daemon=True)
        thread.start()

    def receiveEmailLoop(self, userName, userPassword, receiverEmail):
        while self.isReceiving:
            try: 
                self.checkUnreadEmail(userName, userPassword, receiverEmail)

            except Exception as e:
                self.isReceiving = False
                if self.onShowWarning:
                    self.onShowWarning("Email recive error", str(e))
                break
            time.sleep(10)

    def checkUnreadEmail(self, userName, userPassword, receiverEmail):
        mail = imaplib.IMAP4_SSL("imap.gmail.com")
        mail.login(userName, userPassword)
        mail.select("inbox")
        key = 'From'
        value = receiverEmail
        dayAgo = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
        result, data = mail.search(None, key, value, "SINCE", dayAgo)
        
        if result != "OK":
            mail.logout()
            return
        for num in data[0].split():
            result, msg_data = mail.fetch(num, "(RFC822)")
            if result != "OK":
                continue
            msg = email.message_from_bytes(msg_data[0][1])

            sender = msg["From"]
            subject  =msg["Subject"]

            body = ""

            if msg.is_multipart():
                for part in msg.walk():
                    if part.get_content_type() == "text/plain":
                        payload = part.get_payload(decode=True)

                        if payload:
                            body = payload.decode(errors="ignore")

                        break
            else:
                payload = msg.get_payload(decode=True)

                if payload:
                    body = payload.decode(errors="ignore")

            if self.onMessage:
                self.onMessage(
                    f"EMAIL from {sender}\n"
                    f"Subject: {subject}\n"
                    f"{body}"
                )
        
        mail.logout()


    def stopReceivingEmail(self):
        self.isReceiving = False
