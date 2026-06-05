import smtplib
import subprocess
from email.mime.text import MIMEText  # ← SIMPLIFIED EMAIL
from datetime import datetime
import pytz
import logging
import os

# =========================================================
# EMAIL CONFIG (UNCHANGED)
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

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")

# =========================================================
# FIXED EMAIL (SIMPLE - NO BUGS)
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
    
    msg = MIMEText(body)  # ← SIMPLE FIX
    msg['Subject'] = subject
    msg['From'] = SENDER_EMAIL
    msg['To'] = ", ".join(RECEIVER_EMAILS)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAILS, msg.as_string())  # ← SIMPLE
        logging.warning(f"ALERT SENT → {site_name}")
    except Exception as e:
        logging.error(f"Email failed: {e}")

# =========================================================
# YOUR SITES (UNCHANGED)
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
    "Tris-Pharma-Stage": "https://tris.sambrownprojects.com/"
}

# =========================================================
# FIXED CHECK (2 LINES CHANGED)
# =========================================================
def check_websites():
    for name, url in websites.items():
        try:
            result = subprocess.run(
                ["curl", "-L", "-o", "/dev/null", "-s", "-w", "%{http_code}", url],
                capture_output=True,
                text=True,
                timeout=30  # ← ADDED: Prevent hanging
            )

            status = result.stdout.strip()

            # ✅ FIXED: Allow redirects (301,302,307) + only alert 5xx/4xx
            if status in ["200", "301", "302", "307"]:  # ← 1 LINE CHANGE
                logging.info(f"{name} OK ({status})")
            else:
                logging.error(f"{name} DOWN ({status})")
                send_email(name, url, status)

        except Exception as e:
            logging.error(f"{name} unreachable: {e}")
            send_email(name, url, "TIMEOUT/ERROR")

# =========================================================
# RUN
# =========================================================
if __name__ == "__main__":
    check_websites()
