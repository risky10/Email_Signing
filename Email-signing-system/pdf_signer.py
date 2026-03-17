from reportlab.pdfgen import canvas
from PyPDF2 import PdfReader, PdfWriter

from pyhanko.sign.fields import SigFieldSpec
from pyhanko.sign import fields as sigfields
from pyhanko.sign.signers import SimpleSigner
from pyhanko.sign.signers.pdf_signer import PdfSigner
from pyhanko.sign import PdfSignatureMetadata
from pyhanko.pdf_utils.incremental_writer import IncrementalPdfFileWriter

import os


def apply_signature(pdf_path, signature_path, output_path):
    # STEP 1 — Create visual signature overlay
    temp_overlay = "temp_overlay.pdf"
    c = canvas.Canvas(temp_overlay)
    c.drawImage(signature_path, 50, 155, width=135, height=35)
    c.save()

    # STEP 2 — Merge overlay onto original PDF
    temp_visual = "temp_visual.pdf"

    reader = PdfReader(pdf_path)
    writer = PdfWriter()

    sig_reader = PdfReader(temp_overlay)
    sig_page = sig_reader.pages[0]

    page = reader.pages[0]
    page.merge_page(sig_page)
    writer.add_page(page)

    with open(temp_visual, "wb") as f:
        writer.write(f)

    # STEP 3 — Load PKCS#12 signer (PyHanko 0.18.0 API)
    signer = SimpleSigner.load_pkcs12(
        pfx_file="signer.p12",
        passphrase=None  # or b"password" if you set one
    )

    # STEP 4 — Add signature field using IncrementalPdfFileWriter
    field_spec = SigFieldSpec(
        sig_field_name="Signature1",
        box=(50, 150, 250, 250),
        on_page=0
    )

    temp_with_field = "temp_with_field.pdf"

    with open(temp_visual, "rb") as inf:
        writer2 = IncrementalPdfFileWriter(inf)
        sigfields.append_signature_field(writer2, field_spec)

        with open(temp_with_field, "wb") as outf:
            writer2.write(outf)

    # STEP 5 — Apply cryptographic signature
    with open(temp_with_field, "rb") as inf:
        writer3 = IncrementalPdfFileWriter(inf)
        meta = PdfSignatureMetadata(field_name="Signature1")
        pdf_signer = PdfSigner(meta, signer=signer)

        with open(output_path, "wb") as outf:
            pdf_signer.sign_pdf(writer3, output=outf)

    # Cleanup
    os.remove(temp_overlay)
    os.remove(temp_visual)
    os.remove(temp_with_field)