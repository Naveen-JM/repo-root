import smtplib
import subprocess
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
    format="%(asctime)s | %(levelname)s | %(message)s",
    handlers=[
        logging.FileHandler('website_monitor.log'),
        logging.StreamHandler()
    ]
)


# =========================================================
# EMAIL FUNCTION (Enhanced)
# =========================================================

def send_email(site_name, url, status):
    now = datetime.now(TIMEZONE).strftime("%Y-%m-%d %H:%M:%S")

    msg = EmailMessage()
    msg["From"] = SENDER_EMAIL
    msg["To"] = ", ".join(RECEIVER_EMAILS)
    msg["Subject"] = f"🚨 Website Alert: {site_name} - {status}"
    
    # HTML Email (Better formatting)
    html_content = f"""
    <h2>🚨 Website Monitoring Alert</h2>
    <table border="1" cellpadding="10" style="border-collapse: collapse;">
        <tr><td><b>Time</b></td><td>{now}</td></tr>
        <tr><td><b>Site</b></td><td>{site_name}</td></tr>
        <tr><td><b>URL</b></td><td><a href="{url}">{url}</a></td></tr>
        <tr><td><b>Status</b></td><td style="color: #d32f2f; font-weight: bold;">{status}</td></tr>
    </table>
    <p><b>Action Required:</b> Check server logs and hosting dashboard.</p>
    <hr>
    <small>Automated alert from Website Monitor</small>
    """
    
    msg.add_alternative(html_content, subtype="html")
    msg.set_content(
        f"Time: {now}\nSite: {site_name}\nURL: {url}\nStatus: {status}\n\nAction needed."
    )

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, EMAIL_PASSWORD)
            server.send_message(msg)

        logging.warning(f"📧 ALERT SENT → {site_name} ({status})")

    except Exception as e:
        logging.error(f"📧 Email failed for {site_name}: {e}")


# =========================================================
# SITES TO MONITOR
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
# SMART CHECK LOGIC (Handles 307/301/302 correctly)
# =========================================================

def check_websites():
    """
    Production-ready monitoring:
    ✅ Handles redirects (301/302/307)
    ✅ Response time monitoring
    ✅ Real browser headers
    ✅ No spam alerts
    """
    
    total_sites = len(websites)
    ok_count = 0
    alert_count = 0
    
    logging.info(f"🔍 Starting check for {total_sites} websites...")
    
    for name, url in websites.items():
        try:
            # Production curl command with real browser simulation
            cmd = [
                "curl", 
                "-L",                          # Follow redirects
                "-o", "/dev/null",             # Discard body
                "-s",                          # Silent
                "-w", "%{http_code}\n%{time_total}\n%{num_redirects}\n%{url_effective}",  # Metrics
                "--max-time", "30",            # 30s timeout
                "--connect-timeout", "10",     # 10s connect timeout
                "-H", "Cache-Control: no-cache, no-store, must-revalidate",  # Fresh content
                "-H", "Pragma: no-cache",
                "-H", "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                "-H", "Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                url
            ]
            
            result = subprocess.run(
                cmd, 
                capture_output=True, 
                text=True,
                timeout=35  # Extra buffer
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.decode().strip()[:200]
                logging.error(f"❌ {name}: CURL_ERROR - {error_msg}")
                send_email(name, url, f"CURL_ERROR: {error_msg}")
                alert_count += 1
                continue
            
            # Parse curl output
            lines = [line.strip() for line in result.stdout.strip().split('\n')]
            if len(lines) < 3:
                logging.error(f"❌ {name}: INVALID_RESPONSE")
                send_email(name, url, "INVALID_RESPONSE")
                alert_count += 1
                continue
                
            status = lines[0]
            response_time = float(lines[1])
            redirects = int(lines[2])
            final_url = lines[3] if len(lines) > 3 else url
            
            # ✅ SAFE CONDITIONS (No alert)
            SAFE_STATUSES = ["200", "301", "302", "307"]
            is_safe_status = status in SAFE_STATUSES
            is_fast = response_time < 15
            is_reasonable_redirects = redirects <= 5
            
            if is_safe_status and is_fast and is_reasonable_redirects:
                logging.info(f"✅ {name} OK | {status} | {response_time:.1f}s | {redirects}r | {final_url[:60]}...")
                ok_count += 1
            else:
                # 🚨 REAL PROBLEM - Send alert
                reasons = []
                if status not in SAFE_STATUSES:
                    reasons.append(f"Status={status}")
                if response_time >= 15:
                    reasons.append(f"Slow={response_time:.1f}s")
                if redirects > 5:
                    reasons.append(f"Redirects={redirects}")
                if final_url != url:
                    reasons.append(f"Redirected→{final_url[-50:]}")
                    
                error_msg = " | ".join(reasons)
                logging.error(f"🚨 {name} DOWN | {error_msg}")
                send_email(name, url, error_msg)
                alert_count += 1

        except subprocess.TimeoutExpired:
            logging.error(f"⏰ {name} TIMEOUT (>30s)")
            send_email(name, url, "TIMEOUT_30s")
            alert_count += 1
        except ValueError as ve:
            logging.error(f"❌ {name} PARSE_ERROR: {ve}")
            send_email(name, url, f"PARSE_ERROR: {ve}")
            alert_count += 1
        except Exception as e:
            logging.error(f"💥 {name} UNEXPECTED: {str(e)[:100]}")
            send_email(name, url, f"ERROR: {str(e)[:50]}")
            alert_count += 1
    
    # Summary
    logging.info(f"📊 SUMMARY: {ok_count}/{total_sites} OK | {alert_count} alerts | {datetime.now(TIMEZONE).strftime('%H:%M:%S')}")


# =========================================================
# ENTRY POINT
# =========================================================

if __name__ == "__main__":
    print("🚀 Website Monitor Starting...")
    check_websites()
    print("✅ Check complete. Check logs for details.")
