import requests
import re
import urllib.parse

# ТВОЙ АКТУАЛЬНЫЙ СПИСОК ИСТОЧНИКОВ
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

COMMON_COUNTRIES = {
    "🇺🇸": "USA", "🇬🇧": "United Kingdom", "🇷🇺": "Russia", "🇩🇪": "Germany",
    "🇳🇱": "Netherlands", "🇫🇷": "France", "🇰🇿": "Kazakhstan", "🇹🇷": "Turkey",
    "🇯🇵": "Japan", "🇫🇮": "Finland", "🇵🇱": "Poland", "🇸🇬": "Singapore",
    "🇺🇦": "Ukraine", "🇦🇹": "Austria", "🇨🇦": "Canada", "🇭🇰": "Hong Kong"
}

def get_country_name(flag_emoji):
    if flag_emoji in COMMON_COUNTRIES: return COMMON_COUNTRIES[flag_emoji]
    try:
        codepoints = [ord(c) - 0x1F1E6 for c in flag_emoji]
        return "".join([chr(c + ord('A')) for c in codepoints])
    except: return "Proxy"

def get_flag_emoji(text):
    # Ищем все флаги-эмодзи в тексте. Берем первый найденный, где бы он ни был.
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
    return flags[0] if flags else None

def parse():
    unique_configs = {}
    for url in SOURCES:
        try:
            print(f"Загрузка: {url}")
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                configs = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', res.text)
                for cfg in configs:
                    clean = cfg.strip().replace('\r', '').replace('`', '').replace('"', '')
                    if clean not in unique_configs:
                        unique_configs[clean] = url
        except: print(f"Ошибка в источнике: {url}")

    if unique_configs:
        # Сортировка: VLESS (приоритет 0) всегда первым
        sorted_items = sorted(
            unique_configs.items(), 
            key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0])
        )
        
        final_configs = []
        counter = 1

        for cfg, source_url in sorted_items:
            parts = cfg.split('#', 1)
            base = parts[0]
            old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""
            
            # Определяем автора по URL
            tag = ""
            if "etoneya" in source_url: tag = "EtoNeYa 🏳"
            elif "igareck" in source_url: tag = "igareck"
            elif "RKP" in source_url: tag = "#RKP"
            elif "Ilyacom4ik" in source_url: tag = "FCH"

            # Вытаскиваем флаг (даже если он после цифр)
            flag = get_flag_emoji(old_name)
            if "anycast" in old_name.lower(): 
                name = "🌐 Anycast"
            elif flag: 
                name = f"{flag} {get_country_name(flag)}"
            else:
                name = f"Обход {counter}"
                counter += 1
            
            # Сборка финального названия
            full_label = f"{name} | {tag}" if tag else name
            final_configs.append(f"{base}#{full_label} | Ваш котенок ❤")

        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
        print(f"Готово! Собрано: {len(final_configs)}")
    else:
        print("Конфиги не найдены.")

if __name__ == "__main__":
    parse()
