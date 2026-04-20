import socket
from concurrent.futures import ThreadPoolExecutor


def check_miner(ip):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.2)
            if s.connect_ex((ip, 4028)) == 0:
                return ip
    except:
        pass
    return None


def scan_antminer(network_prefix="192.168.1."):
    print(f"正在扫描内网 {network_prefix}1 ~ {network_prefix}254...")

    ips = [network_prefix + str(i) for i in range(1, 255)]
    miners = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        results = executor.map(check_miner, ips)

    for res in results:
        if res:
            miners.append(res)
            print(f"✅ 发现蚂蚁矿机: {res}")

    if not miners:
        print("未扫描到蚂蚁矿机")
    return miners


if __name__ == "__main__":
    # 这里改成你自己的网段前缀，比如 192.168.0.
    scan_antminer("192.168.1.")