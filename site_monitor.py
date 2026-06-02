import smtplib
import subprocess
from email.mime.text import MIMEText
from datetime import datetime
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
# EMAIL ALERT
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

        logging.warning(f"ALERT SENT → {site_name}")

    except Exception as e:
        logging.error(f"Email failed: {e}")


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
    "Tris-Pharma-Stage": "https://tris.sambrownprojects.com/"
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
                    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/125.0.0.0 Safari/537.36",
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

            # Consider site UP if reachable
            if (
                status.startswith("2")
                or status.startswith("3")
                or status == "403"
            ):
                logging.info(f"{name} OK ({status})")

            # Alert only for real failures
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
# MAIN
# =========================================================
if __name__ == "__main__":
    logging.info("Starting website monitoring...")
    check_websites()
    logging.info("Website monitoring completed.")
