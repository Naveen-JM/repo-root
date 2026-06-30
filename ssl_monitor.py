import smtplib
import socket
import ssl
from urllib.parse import urlparse
from email.mime.text import MIMEText
from datetime import datetime, timezone
import pytz
import logging
import os

# =========================================================
# EMAIL CONFIG
# =========================================================
SENDER_EMAIL = "multi.countries.automation@gmail.com"

RECEIVER_EMAILS = [
    "naveenjanardhananm@hexaware.com",
    "DileepkumarT@hexaware.com",
    "AwanishK@hexaware.com",
    "AnuN@hexaware.com",
]

EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
TIMEZONE = pytz.timezone("Asia/Kolkata")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================================================
# SSL ALERT EMAIL
# =========================================================
def send_ssl_email(site_name, url, expiry_date, days_left):

    now = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    subject = f"⚠ SSL Expiry Alert: {site_name} ({days_left} days left)"

    body = f"""
Time: {now}

SSL Certificate Expiry Warning

Site: {site_name}
URL: {url}

Expiry Date:
{expiry_date.strftime("%Y-%m-%d %H:%M UTC")}

Days Remaining:
{days_left}

Please renew the SSL certificate before expiry.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SENDER_EMAIL, EMAIL_PASSWORD)
        server.sendmail(
            SENDER_EMAIL,
            RECEIVER_EMAILS,
            msg.as_string()
        )

    logging.warning(f"SSL Alert Sent → {site_name}")


# =========================================================
# WEBSITES
# =========================================================
websites = {
    "Korea": "https://korea.progress.im/",
    "Korea-Stage": "https://korea-qa9.progress.im/",
    "Australia": "https://australia.progress.im/",
    "Australia-Stage": "https://australia-qa9.progress.im/",
    "Brazil": "https://brazil.progress.im/",
    "Brazil-Stage": "https://brazil-qa9.progress.im/",
    "Canada": "https://canada.progress.im/",
    "Canada-Stage": "https://canada-qa9.progress.im/",
    "Japan": "https://japan.progress.im/",
    "Japan-Stage": "https://japan-qa9.progress.im/",
    "Switzerland": "https://switzerland.progress.im/",
    "Switzerland-Stage": "https://switzerland-qa9.progress.im/",
    "Pylarify": "https://pylarify.com/",
    "Pylarify-Dev": "https://pylarifydev.prod.acquia-sites.com/",
    "Pylarify-Stg": "https://pylarifystg.prod.acquia-sites.com/",
    "Definity": "https://www.definityimaging.com/",
    "Definity-Dev": "https://definitydev.prod.acquia-sites.com/",
    "Definity-Stg": "https://definitystg.prod.acquia-sites.com/",
    "Time2See": "https://www.time2see.com/",
    "LantheusLink": "https://www.lantheuslink.com/",
    "Neuraceq": "https://neuraceq.com/",
    "Neuraceq-Dev": "https://neuraceqdev.prod.acquia-sites.com/",
    "Neuraceq-Stage": "https://neuraceqstage.prod.acquia-sites.com/",
    "Tris-Pharma": "https://trispharma.com/",
    "Tris-Pharma-Stage": "https://tris.sambrownprojects.com/",
    "Novartis-Dev": "https://dev.fabhalta-locator.com/",
    "Novartis-Stage": "https://uat.fabhalta-locator.com/",
    "Novartis-Prod": "https://fabhalta-locator.com/"
}

# =========================================================
# SSL CHECKER
# =========================================================
def get_ssl_expiry(hostname):
    context = ssl.create_default_context()

    with socket.create_connection((hostname, 443), timeout=15) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()

    return datetime.strptime(
        cert["notAfter"],
        "%b %d %H:%M:%S %Y %Z"
    ).replace(tzinfo=timezone.utc)


def check_ssl_expiry():
    now = datetime.now(timezone.utc)

    for name, url in websites.items():
        try:
            hostname = urlparse(url).hostname
            expiry = get_ssl_expiry(hostname)

            days_left = (expiry - now).days

            logging.info(f"{name}: {days_left} days remaining")

            if 0 <= days_left <= 15:
                send_ssl_email(name, url, expiry, days_left)

        except Exception as e:
            logging.error(f"{name}: SSL check failed - {e}")


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":
    logging.info("Starting SSL monitoring...")
    check_ssl_expiry()
    logging.info("SSL monitoring completed.")
