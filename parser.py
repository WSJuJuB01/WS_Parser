import requests
import re
import urllib.parse

# Список источников
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt"
    "https://etoneya.vercel.app/whitelist"
]

# Словарь для самых популярных стран (чтобы названия были красивыми)
COMMON_COUNTRIES = {
    "🇺🇸": "USA", "🇬🇧": "United Kingdom", "🇷🇺": "Russia", "🇩🇪": "Germany",
    "🇳🇱": "Netherlands", "🇫🇷": "France", "🇰🇿": "Kazakhstan", "🇹🇷": "Turkey",
    "🇯🇵": "Japan", "🇫🇮": "Finland", "🇵🇱": "Poland", "🇸🇬": "Singapore",
    "🇺🇦": "Ukraine", "🇦🇹": "Austria", "🇨🇦": "Canada", "🇭🇰": "Hong Kong"
}

def get_country_name(flag_emoji):
    """Преобразует любой флаг-эмодзи в текстовое название страны"""
    if flag_emoji in COMMON_COUNTRIES:
        return COMMON_COUNTRIES[flag_emoji]
    
    # Магия декодирования любого флага в ISO-код (напр. 🇧🇿 -> BZ)
    try:
        codepoints = [ord(c) - 0x1F1E6 for c in flag_emoji]
        code = "".join([chr(c + ord('A')) for c in codepoints])
        return code # Возвращает код страны (US, NL, JP), если её нет в списке COMMON
    except:
        return "Proxy"

def get_flag_emoji(text):
    # Находим все флаги-эмодзи в тексте и возвращаем первый найденный
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
    return flags[0] if flags else None

def parse():
    unique_configs = set()
    
    for url in SOURCES:
        try:
            print(f"Загрузка из: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                content = response.text
                configs = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
                for cfg in configs:
                    clean_cfg = cfg.strip().replace('\r', '').replace('`', '').replace('"', '')
                    unique_configs.add(clean_cfg)
            else:
                print(f"Ошибка {response.status_code} для {url}")
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

    if unique_configs:
        # 1. Сортировка: VLESS (приоритет 0) всегда идет первым
        sorted_raw = sorted(
            list(unique_configs), 
            key=lambda x: (0 if x.startswith('vless://') else 1, x)
        )
        
        final_configs = []
        bypass_counter = 1 

        for cfg in sorted_raw:
            parts = cfg.split('#', 1)
            base_link = parts[0]
            # Определяем протокол (VLESS, SS, etc.)
            proto = base_link.split('://')[0].upper() 
            old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""
            
            # 2. Формируем новое красивое название
            flag = get_flag_emoji(old_name)
            
            if "anycast" in old_name.lower():
                new_name = "🌐 Anycast"
            elif flag:
                # Получаем название страны по флагу
                country_label = get_country_name(flag)
                new_name = f"{flag} {country_label}"
            else:
                # Если флага и Anycast нет — ставим порядковый номер
                new_name = f"Обход {bypass_counter}"
                bypass_counter += 1
            
            # 3. Собираем всё вместе с твоей подписью
            final_configs.append(f"{base_link}#{new_name} | Ваш котенок ❤")

        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
            
        print(f"Готово! Собрано: {len(final_configs)}")
        print("VLESS в топе, флаги с названиями стран и котенок на месте! 🐾")
    else:
        print("Новых конфигов не найдено.")

if __name__ == "__main__":
    parse()
