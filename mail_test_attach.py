import imaplib
import os
import shutil
import smtplib
import ssl
import time
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


class Mail:
    def __init__(self):
        load_dotenv()
        self.username = os.getenv("USERNAME")
        self.password = os.getenv("PASSWORD")
        self.smtp_host = os.getenv("SMTP_SERVER")
        self.smtp_port = os.getenv("SMTP_PORT")
        self.imap_host = os.getenv("IMAP_SERVER")
        self.imap_port = os.getenv("IMAP_PORT")

    def send_email(self, to, subject, attach=None):
        path = "./to_send/"
        destination = "./sent/"

        # Build mail
        message = MIMEMultipart()
        message["From"] = self.username
        message["To"] = to
        message["Subject"] = subject
        message.attach(MIMEText(body + signature, "html"))

        # Attachment
        if attach:
            with open(path + attach, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
            encoders.encode_base64(part)

            part.add_header(
                "Content-Disposition",
                'attachment; filename= "' + attach + '"',
            )

            message.attach(part)

        text = message.as_string()
        context = ssl.create_default_context()

        # Login and send mail
        with smtplib.SMTP_SSL(
            self.smtp_host, self.smtp_port, context=context
        ) as server:
            server.login(self.username, self.password)
            server.sendmail(self.username, to, text)

        # Save to sent
        imap = imaplib.IMAP4_SSL(self.imap_host, self.imap_port)
        imap.login(self.username, self.password)
        imap.append(
            "INBOX.Sent",
            "\\Seen",
            imaplib.Time2Internaldate(time.time()),
            text.encode("utf8"),
        )
        imap.logout()

        # Move files
        if attach:
            src_path = os.path.join(path, attach)
            dst_path = os.path.join(destination, attach)
            shutil.move(src_path, dst_path)


if __name__ == "__main__":
    # Find all filenames
    allfiles = os.listdir("./to_send/")
    if allfiles:
        mail = Mail()
        signature = open("signature.txt", "r", encoding="utf-8").read()
        body = open("message.txt", "r", encoding="utf-8").read()
        for file in allfiles:
            mail.send_email("dzokas@cognitera.gr", "Support")  # , file)
