import base64
import hashlib
import io
import secrets

import qrcode

def generar_token():
    return secrets.token_urlsafe(32)

def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def generar_qr_data_url(claim_url: str) -> str:
    img = qrcode.make(claim_url)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("ascii")
    return f"data:image/png;base64,{b64}"
