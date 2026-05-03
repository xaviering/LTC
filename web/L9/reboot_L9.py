import requests
from requests.auth import HTTPDigestAuth
import time
import os

def reboot_antminer_l9(ip, username="root", password="root", timeout=5):
    url = f"http://{ip}/cgi-bin/reboot.cgi"
    try:
        response = requests.get(
            url,
            auth=HTTPDigestAuth(username, password),
            timeout=timeout
        )

        if response.status_code == 200:
            print(f"[{ip}] Reboot command sent successfully.")
            return True
        else:
            print(f"[{ip}] Failed: {response.status_code}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"[{ip}] Error: {e}")
        return False

def wait_until_online(ip, timeout=120):
    start = time.time()
    while time.time() - start < timeout:
        if os.system(f"ping -c 1 {ip} > /dev/null 2>&1") == 0:
            return True
        time.sleep(5)
    return False




def batch_reboot(ips):
    for ip in ips:
        reboot_antminer_l9(ip)
        wait_until_online(ip)



if __name__ == '__main__':
    ip = ["172.16.25.198","172.16.25.25"]