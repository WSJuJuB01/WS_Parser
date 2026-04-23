import requests
import re

# Список ваших источников
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt"
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt"
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt"
]

def parse():
    unique_configs = set()
    
    for url in SOURCES:
        try:
            print(f"Загрузка из: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                # Извлекаем строки, похожие на конфиги (vless, vmess, ss, trojan и т.д.)
                content = response.text
                configs = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
                
                for cfg in configs:
                    # Убираем возможный мусор в конце строки
                    clean_cfg = cfg.strip().replace('\r', '')
                    unique_configs.add(clean_cfg)
            else:
                print(f"Ошибка {response.status_code} для {url}")
        except Exception as e:
            print(f"Ошибка: {e}")

    # Сохраняем результат
    if unique_configs:
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(sorted(list(unique_configs))))
        print(f"Успешно! Собрано уникальных конфигов: {len(unique_configs)}")
    else:
        print("Конфиги не найдены.")

if __name__ == "__main__":
    parse()
