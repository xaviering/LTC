import socket
import threading
import time
from ipaddress import IPv4Network
from typing import List, Tuple, Optional
import concurrent.futures


def get_wired_ip_segment() -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    获取有线网卡的 IP 和网段（跨平台）
    返回: (本机IP, 子网掩码, 网段如 192.168.1.0/24)
    """
    try:
        # 方法1：最可靠的方式（推荐）
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))  # 不需要真正连接
        local_ip = s.getsockname()[0]
        s.close()

        # 假设常见家用/公司网络为 /24（255.255.255.0）
        # 你可以根据实际情况改成 /23 或 /22
        network = IPv4Network(f"{local_ip}/24", strict=False)

        print(f"✅ 检测到本机IP: {local_ip}")
        print(f"✅ 当前网段: {network}")

        return local_ip, "255.255.255.0", str(network)

    except Exception as e:
        print(f"获取IP失败: {e}")
        return None, None, None


def scan_antminer_l9(ip_range: str, timeout: float = 0.8, max_workers: int = 100) -> List[dict]:
    """
    扫描指定网段内的 Antminer L9 矿机

    参数：
        ip_range: 网段，例如 "192.168.1.0/24"
        timeout: 单个IP超时时间（秒）
        max_workers: 并发线程数

    返回：发现的 L9 列表，每个元素是一个字典
    """
    found_miners = []
    network = IPv4Network(ip_range)

    print(f"开始扫描网段 {ip_range}，共 {network.num_addresses} 个地址...\n")

    def check_ip(ip: str):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                if s.connect_ex((str(ip), 4028)) == 0:  # 4028 是 CGMiner API 端口
                    # 尝试获取版本信息确认是否为 L9
                    s.sendall(b'{"command":"version"}\n')
                    data = s.recv(4096).decode('utf-8', errors='ignore')

                    if "Antminer L9" in data or "L9" in data or "BMMiner" in data:
                        miner_info = {
                            "ip": str(ip),
                            "status": "在线",
                            "type": "Antminer L9"
                        }
                        found_miners.append(miner_info)
                        print(f"✅ 发现 L9: {ip}")
                        return miner_info
        except:
            pass
        return None

    # 使用线程池并发扫描
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(check_ip, ip) for ip in network.hosts()]

        # 实时显示进度
        for future in concurrent.futures.as_completed(futures):
            pass  # 可以在这里加进度条，但为了简洁省略

    print(f"\n扫描完成！共发现 {len(found_miners)} 台 Antminer L9")
    return found_miners


# ====================== 组合使用方法 ======================
def scan_local_network_l9() -> List[dict]:
    """
    一键扫描：自动获取网段并扫描 L9
    """
    _, _, segment = get_wired_ip_segment()
    if not segment:
        print("❌ 无法获取本地网段")
        return []

    return scan_antminer_l9(segment)


# ====================== 示例运行 ======================
if __name__ == "__main__":
    print("=== 开始扫描局域网 Antminer L9 ===\n")
    miners = scan_local_network_l9()

    if miners:
        print("\n" + "=" * 60)
        print("发现的 Antminer L9 列表：")
        for m in miners:
            print(f"   {m['ip']}  →  Antminer L9")
    else:
        print("未发现 L9 矿机，请确认矿机已开机且与电脑在同一网段")