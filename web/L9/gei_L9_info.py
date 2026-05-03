import socket
import json
from typing import Dict, Any


def get_antminer_l9_info(ip: str = "172.16.25.94", port: int = 4028) -> Dict[str, Any]:
    """
    获取 Antminer L9 基本信息并返回结构化数据

    返回值是一个字典，包含所有关键信息，方便后续使用或显示
    """
    TIMEOUT = 8

    def clean_and_parse_json(raw_data: str) -> Dict:
        """清理蚂蚁矿机返回的不标准 JSON"""
        try:
            raw = raw_data.strip()
            if raw.startswith('['):
                raw = raw[1:]
            if raw.endswith(']'):
                raw = raw[:-1]
            if ',"id":' in raw:
                raw = raw.split(',"id":')[0]
            if not raw.endswith('}'):
                last_brace = raw.rfind('}')
                if last_brace != -1:
                    raw = raw[:last_brace + 1]
            return json.loads(raw)
        except:
            return {"error": "JSON解析失败", "raw": raw_data}

    def send_command(command: str) -> Dict:
        """发送API命令"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(TIMEOUT)
                s.connect((ip, port))
                cmd = json.dumps({"command": command}) + "\n"
                s.sendall(cmd.encode('utf-8'))

                data = b''
                while True:
                    chunk = s.recv(8192)
                    if not chunk:
                        break
                    data += chunk
                    if b'}\n' in chunk or len(data) > 16384:
                        break

                response = data.decode('utf-8', errors='ignore').strip()
                if not response:
                    return {"error": "空响应"}
                return clean_and_parse_json(response)
        except socket.timeout:
            return {"error": "连接超时"}
        except ConnectionRefusedError:
            return {"error": "连接被拒绝，请检查IP和4028端口"}
        except Exception as e:
            return {"error": str(e)}

    # ==================== 获取数据 ====================
    info = {
        "ip": ip,
        "success": True,
        "version": {},
        "summary": {},
        "stats": {},
        "pools": {},
        "error": None
    }

    # Version
    info["version"] = send_command("version")
    # Summary
    info["summary"] = send_command("summary")
    # Stats（最重要）
    info["stats"] = send_command("stats")
    # Pools
    info["pools"] = send_command("pools")

    # 检查是否有错误
    if any("error" in str(v) for v in [info["version"], info["summary"], info["stats"], info["pools"]]):
        info["success"] = False

    return info


# ====================== 示例使用 ======================
if __name__ == "__main__":
    result = get_antminer_l9_info("172.16.25.94")

    if result["success"]:
        summary = result["summary"].get("SUMMARY", [{}])[0]
        stats = result["stats"].get("STATS", [{}])[-1]  # 最后一条是详细数据

        print("✅ Antminer L9 状态摘要")
        print(f"IP地址       : {result['ip']}")
        print(f"运行时间     : {summary.get('Elapsed', 0)} 秒")
        print(f"实时算力     : {summary.get('GHS 5s', 0)} GH/s")
        print(f"平均算力     : {summary.get('GHS av', 0)} GH/s")
        print(f"最高温度     : {stats.get('temp_max', 0)}°C")
        print(f"总硬件错误   : {summary.get('Hardware Errors', 0)}")
        print(f"接受份额     : {summary.get('Accepted', 0)} / 拒绝: {summary.get('Rejected', 0)}")

        # 显示三条链算力
        print("\n三条链算力:")
        for i in range(1, 4):
            print(f"  链路{i}: {stats.get(f'chain_rate{i}', 0):.2f} GH/s   "
                  f"硬件错误: {stats.get(f'chain_hw{i}', 0)}")
    else:
        print("❌ 获取信息失败:", result.get("error"))