import requests
from requests.auth import HTTPDigestAuth

class AntminerL9:
    def __init__(self, ip, username="root", password="root"):
        self.url = f"http://{ip}/cgi-bin/blink.cgi"
        self.auth = HTTPDigestAuth(username, password)

    def led_on(self):
        payloads = [
            {"blink": True},
            {"blink": 1},
            {"led": True},
            {"cmd": "blink", "param": "on"},
            {"command": "blink", "parameter": "on"},
        ]

        for p in payloads:
            try:
                r = requests.post(self.url, json=p, auth=self.auth, timeout=5)
                print("尝试 JSON:", p, "->", r.text)
                if "B001" not in r.text:
                    return r.text
            except Exception as e:
                print("错误:", e)

        return "全部失败"

    def led_off(self):
        payloads = [
            {"blink": False},
            {"blink": 0},
            {"led": False},
            {"cmd": "blink", "param": "off"},
            {"command": "blink", "parameter": "off"},
        ]

        for p in payloads:
            try:
                r = requests.post(self.url, json=p, auth=self.auth, timeout=5)
                print("尝试 JSON:", p, "->", r.text)
                if "B001" not in r.text:
                    return r.text
            except Exception as e:
                print("错误:", e)

        return "全部失败"


if __name__ == "__main__":
    miner = AntminerL9("10.10.3.2")

    print("开灯:", miner.led_on())
    input("回车关闭...")
    print("关灯:", miner.led_off())
