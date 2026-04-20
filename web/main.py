import httpx
from httpx import DigestAuth
import json


def set_antminer_l9_pool(ip, pool_url, worker, password="x"):
    url = f"http://{ip}/cgi-bin/set_miner_conf.cgi"
    auth = DigestAuth("root", "root")

    data = {
        "pools": [
            {
                "url": pool_url,  # 这里建议用 tcp
                "user": worker,
                "pass": password
            },
            {"url": "", "user": "", "pass": ""},
            {"url": "", "user": "", "pass": ""}
        ]
    }

    try:
        with httpx.Client(auth=auth, timeout=15) as client:
            resp = client.post(url, json=data)
            print(f"状态码: {resp.status_code}")
            print(f"返回: {resp.text.strip()[:600]}")

            if resp.status_code == 200 and "success" in resp.text.lower():
                return "✅ 修改成功！建议重启矿机后观察"
            else:
                return f"⚠️ 可能失败，返回内容：{resp.text.strip()}"
    except Exception as e:
        return f"❌ 请求异常：{str(e)}"


# ====================== 你改这里 ======================
ip = "172.16.25.94"
new_pool = "stratum+tcp://43.160.206.50:42371"  # 改成 tcp
new_worker = "owenhclz2.s05105"
# ====================================================

print(set_antminer_l9_pool(ip, new_pool, new_worker))