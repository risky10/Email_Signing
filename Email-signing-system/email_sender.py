import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from config import SMTP_SERVER, EMAIL_USER, EMAIL_PASS, BASE_URL

def send_signing_link(to_email, doc_id):
    link = f"{BASE_URL}/sign/{doc_id}"
    msg = MIMEText(f"Click here to sign your document:\n{link}")
    msg["Subject"] = "Sign Your Document"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email

    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)

def send_signed_pdf(to_email, pdf_path):
    msg = MIMEMultipart()
    msg["Subject"] = "Signed Document"
    msg["From"] = EMAIL_USER
    msg["To"] = to_email
    msg.attach(MIMEText("Here is your signed PDF."))

    with open(pdf_path, "rb") as f:
        attachment = MIMEApplication(f.read(), _subtype="pdf")
        attachment.add_header("Content-Disposition", "attachment", filename="signed.pdf")
        msg.attach(attachment)

    with smtplib.SMTP_SSL(SMTP_SERVER, 465) as server:
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)