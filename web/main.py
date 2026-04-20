import scapy.all as scapy
import ipaddress
import socket
import requests
import sys


def get_hostname(ip):
    """尝试通过反向 DNS 查询获取主机名"""
    try:
        return socket.gethostbyaddr(ip)[0]
    except socket.herror:
        return "未知"


def get_vendor(mac):
    """通过 MAC 地址查询厂商（使用在线 API）"""
    try:
        url = f"https://api.macvendors.com/{mac}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return response.text
        return "未知"
    except requests.RequestException:
        return "未知"


def scan_network(ip_range):
    # 创建 ARP 请求
    arp = scapy.ARP(pdst=str(ip_range))
    ether = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    # 发送 ARP 请求并接收响应
    result = scapy.srp(packet, timeout=2, verbose=False)[0]

    # 存储发现的设备
    devices = []
    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc
        hostname = get_hostname(ip)
        vendor = get_vendor(mac)
        devices.append({'ip': ip, 'mac': mac, 'hostname': hostname, 'vendor': vendor})

    return devices


def print_devices(devices):
    print("\n发现的设备:")
    print("IP地址" + " " * 15 + "MAC地址" + " " * 15 + "主机名" + " " * 15 + "厂商")
    print("-" * 80)
    for device in devices:
        print(f"{device['ip']:<20} {device['mac']:<20} {device['hostname']:<20} {device['vendor']}")


def main():
    # 设置IP范围变量
    IP_RANGE = "192.168.3.0/24"  # 可修改为你的局域网IP范围

    try:
        # 验证IP范围格式
        ipaddress.ip_network(IP_RANGE, strict=False)
        print(f"正在扫描网络: {IP_RANGE}...")
        devices = scan_network(IP_RANGE)

        if devices:
            print_devices(devices)
        else:
            print("未发现任何设备")

    except ValueError:
        print("无效的IP范围格式！请检查 IP_RANGE 变量的格式")
    except KeyboardInterrupt:
        print("\n扫描被用户中断")
    except Exception as e:
        print(f"发生错误: {str(e)}")


if __name__ == "__main__":
    main()