import socket
import psutil
from ipaddress import IPv4Network, IPv4Address
from typing import Optional, Tuple


def get_wired_ip_segment() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    获取有线网卡（Ethernet）的 IP 地址和 IP 段

    返回: (IP地址, 子网掩码, IP段如 192.168.1.0/24)
    """
    # 常见的有线网卡名称（Windows + Linux + macOS）
    wired_keywords = ['ethernet', '以太网', 'eth', 'enp', 'ens', 'eno', 'Ethernet']

    print("正在扫描有线网卡...\n")

    for interface, addrs in psutil.net_if_addrs().items():
        interface_lower = interface.lower()

        # 过滤虚拟网卡和无线网卡
        if any(kw in interface_lower for kw in
               ['wireless', 'wi-fi', 'wlan', 'wifi', 'virtual', 'vmware', 'vbox', 'docker', 'vpn']):
            continue

        # 只检查可能是有线的网卡
        if any(kw in interface_lower for kw in wired_keywords) or "ethernet" in interface_lower:
            for addr in addrs:
                if addr.family == socket.AF_INET:  # IPv4
                    ip = addr.address
                    netmask = addr.netmask

                    if ip and netmask:
                        try:
                            # 计算网段
                            network = IPv4Network(f"{ip}/{netmask}", strict=False)
                            network_str = str(network)  # 如 192.168.1.0/24

                            print(f"✅ 找到有线网卡: {interface}")
                            print(f"   IP地址   : {ip}")
                            print(f"   子网掩码 : {netmask}")
                            print(f"   IP网段   : {network_str}")

                            return ip, netmask, network_str
                        except Exception:
                            continue

    print("❌ 未找到有效的有线网卡IP")
    return None, None, None


# ====================== 简化版（只返回网段） ======================
def get_current_ip_segment() -> Optional[str]:
    """只返回当前有线网卡的 IP 网段（如 192.168.1.0/24）"""
    _, _, segment = get_wired_ip_segment()
    return segment


# ====================== 示例使用 ======================
if __name__ == "__main__":
    ip, mask, segment = get_wired_ip_segment()

    if segment:
        print(f"\n当前有线网络网段为：{segment}")
        # 可以用来扫描同一网段的矿机
        print(f"建议扫描范围：{segment.replace('/24', '.1')}-{segment.replace('/24', '.255')}")
    else:
        print("无法获取有线网卡IP，请检查网线是否连接")