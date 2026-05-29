import requests
import time
import random
from datetime import datetime

accounts = [
    {
        "token": "ghp_xxx1",
        "codespace": "codespace-name-1"
    },
    {
        "token": "ghp_xxx2",
        "codespace": "codespace-name-2"
    },
    {
        "token": "ghp_xxx3",
        "codespace": "codespace-name-3"
    },
    {
        "token": "ghp_xxx4",
        "codespace": "codespace-name-4"
    },
    {
        "token": "ghp_xxx5",
        "codespace": "codespace-name-5"
    },
    {
        "token": "ghp_xxx6",
        "codespace": "codespace-name-6"
    },
    {
        "token": "ghp_xxx7",
        "codespace": "codespace-name-7"
    }
]

index = 0

while True:

    account = accounts[index]

    token = account["token"]
    codespace = account["codespace"]

    print("=" * 60)
    print(f"[{datetime.now()}]")

    print(f"正在启动 Codespace:")
    print(codespace)

    url = f"https://api.github.com/user/codespaces/{codespace}/start"

    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json"
    }

    try:

        response = requests.post(
            url,
            headers=headers
        )

        print("状态码:", response.status_code)
        print(response.text)

    except Exception as e:

        print("启动失败:")
        print(e)

    index = (index + 1) % len(accounts)

    # 3小时55分钟 ~ 3小时58分钟随机
    sleep_time = random.randint(
        3 * 60 * 60 + 55 * 60,
        3 * 60 * 60 + 58 * 60
    )

    hours = sleep_time / 3600

    print(f"等待 {hours:.2f} 小时")
    print("准备启动下一个账号")

    time.sleep(sleep_time)
