import socket
import json
from concurrent.futures import ThreadPoolExecutor

# 1. 扫描内网开放 4028 端口的蚂蚁矿机
def scan_miner_ip(network_prefix="192.168.1."):
    print(f"开始扫描内网: {network_prefix}1 ~ {network_prefix}254")
    ips = [network_prefix + str(i) for i in range(1, 255)]
    miners = []

    def check(ip):
        try:
            with socket.socket() as s:
                s.settimeout(0.2)
                if s.connect_ex((ip, 4028)) == 0:
                    return ip
        except:
            return None

    with ThreadPoolExecutor(100) as executor:
        res = executor.map(check, ips)

    for ip in res:
        if ip:
            miners.append(ip)
            print(f"✅ 发现矿机: {ip}")

    if not miners:
        print("未找到矿机")
    return miners


# 2. 根据 IP 获取精确信息：算力、矿池、钱包、温度、风扇
def get_miner_detail(ip):
    try:
        with socket.socket() as s:
            s.settimeout(2)
            s.connect((ip, 4028))

            # 获取 summary（算力）
            s.sendall(b'{"command":"summary"}\n')
            sum_data = s.recv(8192).decode(errors="ignore")
            summary = json.loads(sum_data)

            # 获取 pools（矿池、钱包）
            s.sendall(b'{"command":"pools"}\n')
            pool_data = s.recv(8192).decode(errors="ignore")
            pools = json.loads(pool_data)

            # 获取 stats（温度、风扇）
            s.sendall(b'{"command":"stats"}\n')
            stats_data = s.recav(16384).decode(errors="ignore")
            stats = json.loads(stats_data)

        # 解析算力
        hs = summary.get("SUMMARY", [{}])[0]
        realtime_hash = hs.get("MHS 5s", "0")
        avg_hash = hs.get("MHS av", "0")

        # 解析矿池与钱包
        pool_info = pools.get("POOLS", [])
        pool_url = pool_info[0].get("URL", "") if pool_info else ""
        worker = pool_info[0].get("User", "") if pool_info else ""
        wallet = worker.split(".")[0] if "." in worker else worker

        # 解析温度、风扇
        fan = temp = "-"
        if stats.get("STATS"):
            st = stats["STATS"][1] if len(stats["STATS"]) > 1 else stats["STATS"][0]
            fan = st.get("fan", st.get("Fan Speed", "-"))
            temp = st.get("temp", st.get("Chip Temp", "-"))

        # 运行时间
        uptime = hs.get("Elapsed", "0")
        uptime_str = f"{int(uptime)//3600}h {int(uptime)%3600//60}m {int(uptime)%60}s"

        return {
            "ip": ip,
            "实时算力 GH/s": round(float(realtime_hash), 2),
            "平均算力 GH/s": round(float(avg_hash), 2),
            "矿池": pool_url,
            "钱包地址": wallet,
            "矿工名": worker,
            "温度": temp,
            "风扇": fan,
            "运行时间": uptime_str
        }
    except Exception as e:
        return {"ip": ip, "error": str(e)}


# 3. 主流程：扫描 → 逐个获取详情
if __name__ == "__main__":
    # 改成你自己的网段，例如 192.168.0.
    miner_ips = scan_miner_ip("172.16.25.")

    print("\n" + "="*60)
    print("开始获取矿机详细信息...\n")

    for ip in miner_ips:
        info = get_miner_detail(ip)
        for k, v in info.items():
            print(f"{k}: {v}")
        print("-"*60)