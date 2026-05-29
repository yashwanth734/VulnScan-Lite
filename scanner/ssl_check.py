import ssl
import socket
import datetime

def check_ssl(domain):
    """
    Connects to the domain over port 443 and inspects the SSL certificate.
    Returns issuer, expiry date, and whether it's valid.
    """
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(5)
            s.connect((domain, 443))
            cert = s.getpeercert()

            # Expiry check
            expiry = datetime.datetime.strptime(cert['notAfter'], "%b %d %H:%M:%S %Y %Z")
            valid = expiry > datetime.datetime.utcnow()

            return {
                "issuer": cert.get("issuer"),
                "expires": expiry.strftime("%Y-%m-%d"),
                "valid": valid
            }

    except Exception as e:
        return {"error": str(e)}
