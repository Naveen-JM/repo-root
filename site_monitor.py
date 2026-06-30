import smtplib
import subprocess
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
# WEBSITE DOWN EMAIL
# =========================================================
def send_email(site_name, url, status):
    now = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    subject = f"🚨 Website Down: {site_name} - {status}"

    body = f"""
Time: {now}

Site: {site_name}
URL: {url}

Status: {status}

Action needed.
"""

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(
                SENDER_EMAIL,
                RECEIVER_EMAILS,
                msg.as_string()
            )

        logging.warning(f"Website alert sent → {site_name}")

    except Exception as e:
        logging.error(f"Email failed: {e}")


# =========================================================
# SSL EXPIRY EMAIL
# =========================================================
def send_ssl_email(site_name, url, expiry_date, days_left):

    now = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    subject = f"⚠ SSL Expiry Alert: {site_name} ({days_left} days left)"

    body = f"""
Time: {now}

SSL Certificate Expiry Warning

Site:
{site_name}

URL:
{url}

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

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(
                SENDER_EMAIL,
                RECEIVER_EMAILS,
                msg.as_string()
            )

        logging.warning(f"SSL alert sent → {site_name}")

    except Exception as e:
        logging.error(f"SSL Email failed: {e}")


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
# WEBSITE CHECKER
# =========================================================
def check_websites():

    for name, url in websites.items():

        try:

            result = subprocess.run(
                [
                    "curl",
                    "-L",
                    "--connect-timeout", "15",
                    "--max-time", "30",
                    "-A",
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
                    "-o", "/dev/null",
                    "-s",
                    "-w", "%{http_code}",
                    url,
                ],
                capture_output=True,
                text=True,
                timeout=35,
            )

            status = result.stdout.strip()

            if (
                status.startswith("2")
                or status.startswith("3")
                or status == "403"
            ):
                logging.info(f"{name} OK ({status})")

            else:
                logging.error(f"{name} DOWN ({status})")
                send_email(name, url, status)

        except subprocess.TimeoutExpired:

            logging.error(f"{name} TIMEOUT")
            send_email(name, url, "TIMEOUT")

        except Exception as e:

            logging.error(f"{name} ERROR: {e}")
            send_email(name, url, f"ERROR: {e}")


# =========================================================
# SSL CHECKER
# =========================================================
def get_ssl_expiry(hostname):

    context = ssl.create_default_context()

    with socket.create_connection((hostname, 443), timeout=15) as sock:
        with context.wrap_socket(sock, server_hostname=hostname) as ssock:
            cert = ssock.getpeercert()

    expiry = cert["notAfter"]

    return datetime.strptime(
        expiry,
        "%b %d %H:%M:%S %Y %Z"
    ).replace(tzinfo=timezone.utc)


def check_ssl_expiry():

    now = datetime.now(timezone.utc)

    for name, url in websites.items():

        try:

            hostname = urlparse(url).hostname

            expiry_date = get_ssl_expiry(hostname)

            days_left = (expiry_date - now).days

            logging.info(
                f"{name} SSL expires in {days_left} days"
            )

            # Send email only during the last 15 days
            if 0 <= days_left <= 15:

                send_ssl_email(
                    name,
                    url,
                    expiry_date,
                    days_left
                )

        except Exception as e:

            logging.error(f"{name} SSL check failed: {e}")


# =========================================================
# MAIN
# =========================================================
if __name__ == "__main__":

    logging.info("Starting website monitoring...")

    check_websites()

    logging.info("Checking SSL certificates...")

    check_ssl_expiry()

    logging.info("Website monitoring completed.")
