from flask import Flask, render_template, request, session, redirect
from storage import get_document
from pdf_signer import apply_signature
from email_sender import send_signed_pdf
from flask import send_from_directory
from storage import save_document
from email_sender import send_signing_link
import uuid
import subprocess
import sys
import os, base64

app = Flask(__name__)
app.secret_key = os.urandom(24)  # needed for sessions

@app.route("/set_email", methods=["POST"])
def set_email():
    session["email"] = request.form["email"]
    return redirect("/")

@app.route("/")
def home():
    user_email = session.get("email")
    
    if not user_email:
        return redirect("/login")

    docs = get_document(list_all=True)

    for doc in docs.values():
        if "filename" not in doc:
            doc["filename"] = os.path.basename(doc["path"])

    filtered_docs = {
        doc_id: doc
        for doc_id, doc in docs.items()
        if doc["sender"] == user_email
        and not doc["signed"]
        and os.path.exists(doc["path"])
    }

    return render_template("home.html", docs=filtered_docs, user_email=user_email)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("email", None)
    return redirect("/login")

@app.route("/upload", methods=["POST"])
def upload():
    user_email = session.get("email")  # signer’s email from login
    file = request.files["pdf"]

    if not file or file.filename == "":
        return "No file uploaded."

    original_filename = file.filename

    # Save temporarily
    temp_id = str(uuid.uuid4())
    temp_path = os.path.join("incoming_docs", f"{temp_id}.pdf")
    file.save(temp_path)

    # Send email to your signing inbox
    from email_sender import send_pdf_to_signing_inbox
    send_pdf_to_signing_inbox(temp_path, user_email, original_filename)

    return render_template("upload_success.html", filename=original_filename)

@app.route("/signed/<filename>")
def serve_signed(filename):
    return send_from_directory("signed_docs", filename)


@app.route("/preview/<filename>")
def preview_pdf(filename):
    return send_from_directory("incoming_docs", filename)

@app.route("/sign/<doc_id>")
def sign_page(doc_id):
    doc = get_document(doc_id)

    if doc is None:
        return "Error: Document not found. Did you run email_receiver.py first?"
    
    pdf_filename = os.path.basename(doc["path"])
    return render_template("sign.html", doc_id=doc_id, pdf_filename=pdf_filename)

@app.route("/submit_signature", methods=["POST"])
def submit_signature():
    doc_id = request.form["doc_id"]
    doc = get_document(doc_id)

    if doc is None:
        return "Error: Document not found. Did you run email_receiver.py first?"

    signature_data = request.form["signature"]

    signature_path = f"signatures/{doc_id}.png"
    pdf_path = doc["path"]
    output_path = f"signed_docs/{doc_id}.pdf"


    # Decode base64 PNG
    signature_data = signature_data.replace("data:image/png;base64,", "")
    with open(signature_path, "wb") as f:
        f.write(base64.b64decode(signature_data))

    from PIL import Image
    img = Image.open(signature_path).convert("RGBA")
    white_bg = Image.new("RGB", img.size, (255, 255, 255))
    white_bg.paste(img, mask=img.split()[3])  # use alpha channel

    flat_signature_path = f"signatures/{doc_id}_flat.png"
    white_bg.save(flat_signature_path, "PNG")

    apply_signature(pdf_path, flat_signature_path, output_path)

    sender = get_document(doc_id)["sender"]
    send_signed_pdf(sender, output_path)
    from storage import mark_signed
    mark_signed(doc_id)


    signed_filename = os.path.basename(output_path)
    return render_template("signed_success.html", doc_id=doc_id, signed_filename=signed_filename)

if __name__ == "__main__":
    subprocess.Popen([sys.executable, "email_receiver.py"])

    app.run(debug=True, use_reloader=False)