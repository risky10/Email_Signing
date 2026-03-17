import json, os

DB_FILE = "database.json"

def load_db():
    if not os.path.exists(DB_FILE):
        return {}
    with open(DB_FILE, "r") as f:
        return json.load(f)

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=4)

def save_document(doc_id, path, sender, original_filename):
    db = load_db()

    db[doc_id] = {
        "path": path,
        "filename": original_filename,
        "sender": sender,
        "signed": False
    }
    save_db(db)

def mark_signed(doc_id):
    db = load_db()
    if doc_id in db:
        db[doc_id]["signed"] = True
        save_db(db)


def get_document(doc_id=None, list_all=False):
    db = load_db()

    if list_all:
        return db  # return all documents

    return db.get(doc_id)
