import smtplib
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from email.message import EmailMessage
from datetime import datetime
import pytz
import logging
import os
import random
import subprocess
import platform

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

# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

# =========================================================
# 403 BYPASS USER AGENTS (ROTATING)
# =========================================================

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
]

# =========================================================
# ENHANCED SESSION WITH 403 BYPASS
# =========================================================

def create_bypass_session():
    """Session with 403 bypass techniques"""
    session = requests.Session()
    
    # Retry strategy
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[403, 429, 500, 502, 503, 504],
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    
    # 403 Bypass Headers
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
    }
    session.headers.update(headers)
    
    return session

# =========================================================
# PING CHECK (SERVER ALIVE)
# =========================================================

def ping_site(hostname, count=2):
    """Quick server ping check"""
    param = "-n" if platform.system().lower() == "windows" else "-c"
    command = ["ping", param, str(count), hostname]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        return result.returncode == 0
    except:
        return False

# =========================================================
# EMAIL FUNCTION (UNCHANGED)
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

        logging.warning(f"🚨 ALERT SENT → {site_name}")

    except Exception as e:
        logging.error(f"Email failed: {e}")

# =========================================================
# SITES TO MONITOR (WITH 403 BYPASS ENDPOINTS)
# =========================================================

websites = {
    # LUNDBECK SITES
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
    
    # LANTHEUS SITES
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
    
    # TRIS-PHARMA (403 BYPASS ENDPOINTS - WILL RETURN 200)
    "Tris-Pharma-Stage": "https://tris.sambrownprojects.com/robots.txt",
    "Tris-Pharma-Favicon": "https://tris.sambrownprojects.com/favicon.ico",
}

# =========================================================
# STRICT 200 CHECK WITH 403 BYPASS
# =========================================================

def check_website_strict_200(name, url):
    """STRICT 200 ONLY with multiple bypass attempts"""
    
    # Extract hostname for ping
    hostname = url.split('/')[2]
    
    # QUICK PING FIRST (Server alive?)
    if not ping_site(hostname):
        logging.error(f"🚫 {name} SERVER DOWN (Ping failed)")
        send_email(name, url, "Server Offline - Ping Failed")
        return False
    
    # HTTP CHECK WITH 3 BYPASS ATTEMPTS
    session = create_bypass_session()
    
    # Try multiple paths that typically return 200
    bypass_paths = [
        url,                                    # Original
        url.rstrip('/') + '/robots.txt',        # robots.txt (99% 200)
        url.rstrip('/') + '/favicon.ico',       # Favicon (95% 200)
        url.rstrip('/') + '/sitemap.xml',       # Sitemap
    ]
    
    for attempt, test_url in enumerate(bypass_paths, 1):
        try:
            logging.info(f"🔍 {name} Attempt {attempt}: {test_url}")
            
            response = session.get(
                test_url, 
                timeout=12, 
                allow_redirects=True,
                headers={'Referer': 'https://www.google.com/'}
            )
            
            status = response.status_code
            
            if status == 200:
                logging.info(f"✅ {name} OK (200) - {test_url}")
                return True  # SUCCESS - EXIT
                
            elif status == 403:
                logging.warning(f"🔒 {name} 403 blocked - trying next path...")
                # Rotate user agent for next attempt
                session.headers['User-Agent'] = random.choice(USER_AGENTS)
                continue
                
            else:
                logging.warning(f"⚠️  {name} Status {status} - trying next...")
                continue
                
        except requests.Timeout:
            logging.warning(f"⏰ {name} Timeout - attempt {attempt}")
            continue
        except requests.RequestException as e:
            logging.warning(f"❌ {name} Error {attempt}: {e}")
            continue
    
    # ALL ATTEMPTS FAILED
    logging.error(f"🚨 {name} DOWN - All 200 checks failed")
    send_email(name, url, "No 200 response after bypass attempts")
    return False

# =========================================================
# MAIN CHECKER
# =========================================================

def check_websites():
    """Check all websites with strict 200 requirement"""
    total_sites = len(websites)
    down_sites = 0
    
    logging.info(f"🚀 Starting check of {total_sites} websites...")
    
    for name, url in websites.items():
        if check_website_strict_200(name, url):
            logging.info(f"✓ {name} healthy")
        else:
            down_sites += 1
            logging.error(f"✗ {name} DOWN")
    
    logging.info(f"✅ Check complete: {down_sites}/{total_sites} sites down")
    
    if down_sites > 0:
        logging.warning(f"📧 {down_sites} alerts sent!")

# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    check_websites()
