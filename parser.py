import requests
import re

# Список источников
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt"
]

def parse():
    unique_configs = set()
    
    for url in SOURCES:
        try:
            print(f"Загрузка из: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                content = response.text
                # Ищем все протоколы: vless, vmess, ss, trojan, tuic, hysteria
                configs = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
                
                for cfg in configs:
                    # Очистка строки от мусора
                    clean_cfg = cfg.strip().replace('\r', '').replace('`', '').replace('"', '')
                    unique_configs.add(clean_cfg)
            else:
                print(f"Ошибка {response.status_code} для {url}")
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

    # Запись в файл (режим 'w' полностью стирает старое содержимое)
    if unique_configs:
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(list(unique_configs))))
        print(f"Готово! Собрано свежих конфигов: {len(unique_configs)}")
    else:
        print("Новых конфигов не найдено. Файл не будет обновлен.")

if __name__ == "__main__":
    parse()
