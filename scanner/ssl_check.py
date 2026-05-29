import ssl
import socket
from datetime import datetime
import urllib.parse

def check_ssl(url_host):
    # parse hostname from url_host (strip scheme)
    host = urllib.parse.urlparse(url_host).hostname or url_host
    
    cert = None
    cipher = None
    cert_valid = True
    err_msg = None
    
    # 1. Try standard secure verification
    try:
        ctx = ssl.create_default_context()
        with socket.create_connection((host, 443), timeout=8) as sock:
            with ctx.wrap_socket(sock, server_hostname=host) as ssock:
                cert = ssock.getpeercert()
                cipher = ssock.cipher()
    except Exception as ver_err:
        cert_valid = False
        err_msg = str(ver_err)
        
        # 2. Try unverified connection to at least inspect the cipher suite and extract details
        try:
            unverified_ctx = ssl._create_unverified_context()
            with socket.create_connection((host, 443), timeout=8) as sock:
                with unverified_ctx.wrap_socket(sock, server_hostname=host) as ssock:
                    cipher = ssock.cipher()
        except Exception as unver_err:
            return {
                "ok": False,
                "error": f"Connection failed: {err_msg} (Fallback also failed: {str(unver_err)})",
                "score_delta": -30
            }
            
    days_left = 0
    valid = False
    
    if cert and 'notAfter' in cert:
        try:
            not_after = datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            days_left = (not_after - datetime.utcnow()).days
            valid = days_left > 0 and cert_valid
        except Exception:
            valid = cert_valid
    else:
        valid = cert_valid

    cipher_name, ssl_version, secret_bits = cipher if cipher else (None, None, 0)
    
    # Grading logic
    # Base: if valid and expires in > 30 days: +20. Else if expired/invalid: -20
    score_delta = 20 if valid and days_left > 30 else -20
    if not cert_valid:
        score_delta = -30
        
    is_weak_cipher = secret_bits < 128
    is_weak_proto = (ssl_version or "").upper() in ["SSLV2", "SSLV3", "TLSV1", "TLSV1.0", "TLSV1.1"]
    
    if is_weak_cipher or is_weak_proto:
        score_delta -= 10
        
    cipher_str = f"{cipher_name} ({ssl_version}, {secret_bits} bits)" if cipher_name else "None"
    
    return {
        "ok": True,
        "valid": valid,
        "days_left": days_left if cert_valid else 0,
        "cipher_strength": "Weak" if (is_weak_cipher or is_weak_proto) else "Strong",
        "cipher": cipher_str,
        "score_delta": score_delta,
        "error": err_msg
    }
