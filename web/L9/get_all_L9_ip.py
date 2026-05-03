import socket
import psutil
from ipaddress import IPv4Network, IPv4Address
from typing import List, Tuple, Optional
import concurrent.futures
import threading

print_lock = threading.Lock()


def get_wired_ip_segment() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    智能获取有线网卡的 IP 和正确网段（支持 /24 /23 /22 /21 /20 等）
    返回: (本机IP, 子网掩码, 网段)
    """
    wired_keywords = ['ethernet', '以太网', 'eth', 'enp', 'ens', 'eno', 'Ethernet', 'lan']
    exclude_keywords = ['wireless', 'wi-fi', 'wlan', 'wifi', 'virtual', 'vmware', 'vbox', 'docker', 'vpn', 'bluetooth']

    print("正在检测有线网卡和真实网段...\n")

    for interface, addrs in psutil.net_if_addrs().items():
        iface_lower = interface.lower()

        # 排除无线和虚拟网卡
        if any(kw in iface_lower for kw in exclude_keywords):
            continue
        if not any(kw in iface_lower for kw in wired_keywords) and "eth" not in iface_lower and "en" not in iface_lower:
            continue

        for addr in addrs:
            if addr.family == socket.AF_INET and addr.netmask:  # 有子网掩码
                ip = addr.address
                netmask = addr.netmask

                try:
                    # 自动计算正确网段
                    network = IPv4Network(f"{ip}/{netmask}", strict=False)
                    network_str = str(network)

                    print(f"✅ 找到有线网卡: {interface}")
                    print(f"   IP地址   : {ip}")
                    print(f"   子网掩码 : {netmask}")
                    print(f"   网段     : {network_str}   ({network.prefixlen}位)\n")

                    return ip, netmask, network_str
                except:
                    continue

    # 如果 psutil 没找到，退回到简单方法
    print("⚠️  未找到完整网卡信息，使用备用模式...")
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        network = IPv4Network(f"{ip}/24", strict=False)  # 最后保底用/24
        print(f"✅ 本机IP: {ip}")
        print(f"✅ 网段: {network}  (保底 /24)")
        return ip, "255.255.255.0", str(network)
    except:
        return None, None, None


def scan_antminer_l9(ip_range: str, timeout: float = 0.8, max_workers: int = 80) -> List[dict]:
    """扫描 L9（已优化打印整齐）"""
    found_miners = []
    network = IPv4Network(ip_range)

    print(f"开始扫描网段 {ip_range}  ({network.num_addresses} 个地址)...\n")

    def check_ip(ip: str):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((str(ip), 4028)) == 0:
                    s.sendall(b'{"command":"version"}\n')
                    data = s.recv(2048).decode('utf-8', errors='ignore')

                    if "L9" in data.upper() or "Antminer L9" in data or "BMMiner" in data:
                        with print_lock:
                            print(f"✅ 发现 L9: {ip}")
                        return {"ip": str(ip), "status": "在线", "type": "Antminer L9"}
        except:
            pass
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_ip, ip) for ip in network.hosts()]
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                found_miners.append(result)

    # 排序并整齐打印
    found_miners.sort(key=lambda x: tuple(map(int, x["ip"].split('.'))))

    print("\n" + "=" * 65)
    print(f"扫描完成！共发现 {len(found_miners)} 台 Antminer L9\n")
    for m in found_miners:
        print(f"   {m['ip']:18} →  Antminer L9")

    return found_miners


def scan_local_network_l9() -> List[dict]:
    """一键扫描（推荐直接调用这个）"""
    _, _, segment = get_wired_ip_segment()
    if not segment:
        print("❌ 无法获取网段")
        return []
    return scan_antminer_l9(segment)


# ====================== 测试 ======================
if __name__ == "__main__":
    miners = scan_local_network_l9()
    for i in miners:
        print(i["ip"])