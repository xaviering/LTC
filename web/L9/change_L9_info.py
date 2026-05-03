import httpx
from httpx import DigestAuth
from typing import Optional


def set_antminer_pool(
        ip: str,
        pool_url: str,
        worker: str,
        password: str = "x",
        username: str = "root",
        auth_password: str = "root"
) -> str:
    """
    修改 Antminer L9 的矿池配置（推荐使用此版本）

    参数：
        ip          : 矿机IP地址（如 "172.16.25.94"）
        pool_url    : 矿池地址（如 "stratum+ssl://43.160.206.50:42371"）
        worker      : 矿工号/钱包.子账号（如 "owenhclz2.s05105"）
        password    : 矿池密码，默认 "x"
        username    : 矿机登录用户名，默认 root
        auth_password : 矿机登录密码，默认 root
    """
    url = f"http://{ip}/cgi-bin/set_miner_conf.cgi"
    auth = DigestAuth(username, auth_password)

    # 构造标准的 pools 数组格式
    data = {
        "pools": [
            {
                "url": pool_url,
                "user": worker,
                "pass": password
            },
            {"url": "", "user": "", "pass": ""},  # pool 2
            {"url": "", "user": "", "pass": ""}  # pool 3
        ]
    }

    try:
        with httpx.Client(auth=auth, timeout=15) as client:
            resp = client.post(url, json=data)

            print(f"状态码: {resp.status_code}")
            print(f"返回内容: {resp.text.strip()[:300]}...")

            if resp.status_code == 200 and ("success" in resp.text.lower() or "ok" in resp.text.lower()):
                return "✅ 矿池修改成功！"
            elif resp.status_code == 200:
                return "⚠️ 已提交，但返回结果未知，请手动检查矿机是否切换成功"
            else:
                return f"❌ 修改失败，状态码: {resp.status_code}\n返回: {resp.text.strip()[:200]}"

    except httpx.TimeoutException:
        return "❌ 请求超时，请检查矿机是否在线"
    except httpx.ConnectError:
        return "❌ 无法连接到矿机，请检查IP地址和网络"
    except Exception as e:
        return f"❌ 请求异常: {str(e)}"


# ====================== 示例使用 ======================
if __name__ == "__main__":
    result = set_antminer_pool(
        ip="172.16.25.94",
        pool_url="stratum+ssl://43.160.206.50:42371",
        worker="owenhclz2.s05105",
        password="x"
    )
    print(result)