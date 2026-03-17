import imaplib, email, os, uuid
from email.header import decode_header
from storage import save_document
from email_sender import send_signing_link
from datetime import datetime
from config import IMAP_SERVER, EMAIL_USER, EMAIL_PASS

def fetch_incoming_pdfs():
    print("Connecting to IMAP...")

    mail = imaplib.IMAP4_SSL(IMAP_SERVER)
    mail.login(EMAIL_USER, EMAIL_PASS)
    print("Logged in.")

    mail.select("inbox")
    print("Inbox selected.")

    today = datetime.now().strftime("%d-%b-%Y")
    status, messages = mail.search(None, f'(UNSEEN SENTSINCE {today})')

    print("Search result:", status, messages)

    if messages == [b''] or messages == []:
        print("No unread emails found.")
        return

    for num in messages[0].split():
        print("Processing email ID:", num)

        status, msg_data = mail.fetch(num, "(RFC822)")
        msg = email.message_from_bytes(msg_data[0][1])

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
    fetch_incoming_pdfs()

