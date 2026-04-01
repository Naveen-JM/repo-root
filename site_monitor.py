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
    "naveenjanardhananm@hexaware.com",
    "DileepkumarT@hexaware.com",
    "AwanishK@hexaware.com",
    "AnuN@hexaware.com",
    "SandipC@hexaware.com",
    "GeorgeC@hexaware.com",
    "JulianneB@hexaware.com"
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
    #LUNDBECK SITES
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
    "Switzerland":"https://switzerland.progress.im/",
    "Switzerland-Stage":"https://switzerland-qa9.progress.im/",
    #LANTHEUS SITES
    "Pylarify" : "https://pylarify.com/",
    "Pylarify-Dev" : "https://pylarifydev.prod.acquia-sites.com/",
    "Pylarify-Stg" : "https://pylarifystg.prod.acquia-sites.com/",
    "Definity" : "https://www.definityimaging.com/",
    "Definity-Dev" : "https://definitydev.prod.acquia-sites.com/",
    "Definity-Stg" : "https://definitystg.prod.acquia-sites.com/",
    "Time2See" : "https://www.time2see.com/",
    #'Lantheusspect' : 'https://www.lantheusspect.com/',
    "LantheusLink" : "https://www.lantheuslink.com/",
    "Neuraceq" : "https://neuraceq.com/",
    "Neuraceq-Dev" : "https://neuraceqdev.prod.acquia-sites.com/",
    "Neuraceq-Stage" : "https://neuraceqstage.prod.acquia-sites.com/",
    #TRIS-PHARMA SITES
    "Tris-Pharma" : "https://www.trispharma.com",
    "Tris-Pharma-Stage" : "https://tris.sambrownprojects.com/"
    # test site
    #"TEST-DOWN": "https://httpstat.us/500"
}


# =========================================================
# CHECK LOGIC (STRICT 200 ONLY)
# =========================================================

def check_websites():
    for name, url in websites.items():

        try:
            response = requests.get(url, timeout=15)
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







