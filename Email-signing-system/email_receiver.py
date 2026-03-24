import imaplib, email, os, uuid, time
from email.header import decode_header
from storage import save_document
from email_sender import send_signing_link
from datetime import datetime
from config import IMAP_SERVER, EMAIL_USER, EMAIL_PASS
first_time = True

def fetch_incoming_pdfs():
    global first_time

    if(first_time):
        print("Connecting to IMAP...")

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    if(first_time):
        print("Logged in.")

    mail.select("inbox")
    if(first_time):
        print("Inbox selected.")
        first_time = False

    today = datetime.now().strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'(UNSEEN SENTSINCE {today})')

    msg_ids = messages[0].split()

    if not msg_ids:
        return
    
    print(f"Found {len(msg_ids)} new unread email(s).")

    for num in messages[0].split():
        print("Processing email ID:", num)

        status, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

        subject = msg["Subject"] or ""
        if subject.startswith("New document for signing from"):
            sender = subject.replace("New document for signing from", "").strip()
        else:
            sender = msg["From"]


        print("Email from:", sender)

        for part in msg.walk():
            print("Part:", part.get_content_type())

            if part.get_content_type() == "application/pdf":
                original_filename = part.get_filename()
                print("Found PDF:", original_filename)

                doc_id = str(uuid.uuid4())
                filepath = os.path.join("incoming_docs", f"{doc_id}.pdf")

                with open(filepath, "wb") as f:
                    f.write(part.get_payload(decode=True))

                save_document(doc_id, filepath, sender, original_filename)

                send_signing_link(sender, doc_id)

                print("Saved and sent signing link.")

if __name__ == "__main__":
    while True:
        fetch_incoming_pdfs()
        time.sleep(10)
