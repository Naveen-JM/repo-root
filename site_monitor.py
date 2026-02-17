import smtplib
import requests
from email.message import EmailMessage
from datetime import datetime
import pytz
import logging
import os

# =========================================================
# EMAIL CONFIG
# =========================================================

SENDER_EMAIL = "multi.countries.automation@gmail.com"

RECEIVER_EMAILS = [
    "naveenjanardhananm@hexaware.com"
]

EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

TIMEZONE = pytz.timezone("Asia/Kolkata")


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)


# =========================================================
# EMAIL FUNCTION
# =========================================================

def send_email(site_name, url, status):
    now = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)
    msg["Subject"] = f"🚨 Website Down Alert: {site_name}"

    msg.set_content(
        f"""
Time   : {now}
Site   : {site_name}
URL    : {url}
Status : {status}

Action needed.
"""
    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.warning(f"ALERT SENT → {site_name}")

    except Exception as e:
        logging.error(f"Email failed: {e}")


# =========================================================
# SITES TO MONITOR (UPDATED)
# =========================================================

websites = {
    "Korea": "https://korea.progress.im/",
    "Australia": "https://australia.progress.im/",
    "Brazil": "https://brazil.progress.im/",
    "Canada": "https://canada.progress.im/",
    "Japan": "https://japan.progress.im/",

    # test site
    "TEST-DOWN": "https://httpstat.us/500"
}


# =========================================================
# CHECK LOGIC (STRICT 200 ONLY)
# =========================================================

def check_websites():
    for name, url in websites.items():

        try:
            response = requests.get(url, timeout=10)
            status = response.status_code

            if status == 200:
                logging.info(f"{name} OK (200)")
            else:
                logging.error(f"{name} DOWN ({status})")
                send_email(name, url, status)

        except requests.RequestException as e:
            logging.error(f"{name} unreachable: {e}")
            send_email(name, url, "No response")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    check_websites()


