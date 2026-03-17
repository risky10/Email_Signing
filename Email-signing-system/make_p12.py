from cryptography.hazmat.primitives.serialization import pkcs12, Encoding, NoEncryption
from cryptography.hazmat.primitives import serialization

# Load key
with open("signer_key.pem", "rb") as f:
    key = serialization.load_pem_private_key(f.read(), password=None)

# Load certificate
with open("signer_cert.pem", "rb") as f:
    cert_data = f.read()

from cryptography import x509
cert = x509.load_pem_x509_certificate(cert_data)

# Create PKCS#12 bundle
p12 = pkcs12.serialize_key_and_certificates(
    name=b"joze-signer",
    key=key,
    cert=cert,
    cas=None,
    encryption_algorithm=NoEncryption()
)

with open("signer.p12", "wb") as f:
    f.write(p12)

print("Created signer.p12")
