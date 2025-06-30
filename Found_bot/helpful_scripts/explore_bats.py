import subprocess
import time
import json

# Константы
EXPLORE_URL = "https://ruby-king.ru/api/farm/farm-mob-one?name=1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec"
BATS_URL = "https://ruby-king.ru/api/user/vesna?name=1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec"
REFERER = "https://ruby-king.ru/city?name=1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec&timeEnd=1751300208114"
HEADERS = [
    "-H", "Accept: application/json, text/plain, */*",
    "-H", "Accept-Language: ru,en;q=0.9,en-US;q=0.8,de;q=0.7",
    "-H", "Connection: keep-alive",
    "-H", "Content-Type: application/json",
    "-H", "Origin: https://ruby-king.ru",
    "-H", f"Referer: {REFERER}",
    "-H", "Sec-Fetch-Dest: empty",
    "-H", "Sec-Fetch-Mode: cors",
    "-H", "Sec-Fetch-Site: same-origin",
    "-H", "User-Agent: Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
]

def curl_post(url):
    cmd = ["curl", "-s", "-X", "POST", url] + HEADERS + ["--data-raw", "{}"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout

def explore():
    resp = curl_post(EXPLORE_URL)
    try:
        data = json.loads(resp)
    except Exception:
        data = resp
    return data

def main():
    print("[1] Исследование...")
    data = explore()
    print("Ответ на исследование:", data)
    if isinstance(data, dict) and data.get("action") == "SPEC_BATS":
        print("[1] Найдены летучие мыши! Отправляю обход...")
        bats1 = curl_post(BATS_URL)
        print("Ответ сервера на обход 1:", bats1)
        time.sleep(3)
        print("[2] Повторное исследование...")
        data2 = explore()
        print("Ответ на исследование 2:", data2)
        if isinstance(data2, dict) and data2.get("action") == "SPEC_BATS":
            print("[2] Снова летучие мыши! Отправляю обход...")
            bats2 = curl_post(BATS_URL)
            print("Ответ сервера на обход 2:", bats2)
        else:
            print("[2] Мыши не встретились повторно.")
    else:
        print("[1] Мыши не встретились.")

if __name__ == "__main__":
    main() 