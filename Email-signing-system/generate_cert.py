from datetime import datetime, timedelta

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID

# 1. Generate private key
key = rsa.generate_private_key(public_exponent=65537, key_size=2048)

with open("signer_key.pem", "wb") as f:
    f.write(
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption(),
        )
    )

# 2. Build self-signed certificate
subject = issuer = x509.Name(
    [
        x509.NameAttribute(NameOID.COUNTRY_NAME, "SI"),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, "Slovenia"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, "Logatec"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Email Signing System"),
        x509.NameAttribute(NameOID.COMMON_NAME, "Joze Test Signer"),
    ]
)

cert = (
    x509.CertificateBuilder()
    .subject_name(subject)
    .issuer_name(issuer)
    .public_key(key.public_key())
    .serial_number(x509.random_serial_number())
    .not_valid_before(datetime.utcnow() - timedelta(days=1))
    .not_valid_after(datetime.utcnow() + timedelta(days=365 * 5))
    .add_extension(
        x509.BasicConstraints(ca=False, path_length=None),
        critical=True,
    )
    .sign(private_key=key, algorithm=hashes.SHA256())
)

with open("signer_cert.pem", "wb") as f:
    f.write(cert.public_bytes(serialization.Encoding.PEM))

print("Created signer_key.pem and signer_cert.pem")
