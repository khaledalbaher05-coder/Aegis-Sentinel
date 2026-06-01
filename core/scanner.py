import subprocess
import datetime
import os
from dotenv import load_dotenv

load_dotenv()
WHITELIST = ["127.0.0.1", os.getenv('MY_PUBLIC_IP')]

def log_action(action, ip):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open("security_audit.log", "a") as f:
        f.write(f"[{timestamp}] ACTION: {action} | IP: {ip}\n")

def scan_and_block():
    threats_found = []
    # ملاحظة: استبدل المسار بـ test.log للتجربة في WSL
    log_file = "/var/log/auth.log"
    if not os.path.exists(log_file): return []
    
    cmd = f"grep 'Failed password' {log_file} | awk '{{print $(NF-3)}}' | sort | uniq -c | awk '$1 > 5 {{print $2}}'"
    try:
        output = subprocess.check_output(cmd, shell=True).decode().splitlines()
        for ip in output:
            if ip and ip not in WHITELIST:
                check = subprocess.run(["sudo", "iptables", "-C", "INPUT", "-s", ip, "-j", "DROP"], stderr=subprocess.DEVNULL)
                if check.returncode != 0:
                    subprocess.run(["sudo", "iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
                    log_action("BLOCK", ip)
                    threats_found.append(f"IP مشبوه: {ip}")
    except: pass
    return threats_found
