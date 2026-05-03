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
    if flag_emoji in COMMON_COUNTRIES:
        return COMMON_COUNTRIES[flag_emoji]
    try:
        codepoints = [ord(c) - 0x1F1E6 for c in flag_emoji]
        code = "".join([chr(c + ord('A')) for c in codepoints])
        return code
    except:
        return "Proxy"

def get_flag_emoji(text):
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
    return flags[0] if flags else None

def parse():
    # Используем словарь {конфиг: ссылка_источника}
    unique_configs = {}
    
    for url in SOURCES:
        try:
            print(f"Загрузка из: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                content = response.text
                configs = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
                for cfg in configs:
                    clean_cfg = cfg.strip().replace('\r', '').replace('`', '').replace('"', '')
                    if clean_cfg not in unique_configs:
                        unique_configs[clean_cfg] = url
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

    if unique_configs:
        # Сортировка: VLESS в начале
        sorted_items = sorted(
            unique_configs.items(), 
            key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0])
        )
        
        final_configs = []
        bypass_counter = 1 

        for cfg, source_url in sorted_items:
            parts = cfg.split('#', 1)
            base_link = parts[0]
            old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""
            
            # --- ОПРЕДЕЛЯЕМ ПОДПИСЬ АВТОРА ---
            author_tag = ""
            if "etoneya" in source_url:
                author_tag = "EtoNeYa 🏳"
            elif "igareck" in source_url:
                author_tag = "igareck"
            elif "RKP" in source_url:
                author_tag = "#RKP"
            elif "Ilyacom4ik" in source_url:
                author_tag = "FCH"

            # --- ФОРМИРУЕМ НАЗВАНИЕ ---
            flag = get_flag_emoji(old_name)
            if "anycast" in old_name.lower():
                new_name = "🌐 Anycast"
            elif flag:
                new_name = f"{flag} {get_country_name(flag)}"
            else:
                new_name = f"Обход {bypass_counter}"
                bypass_counter += 1
            
            # Сборка: [Имя] | [Автор] | Ваш котенок ❤
            if author_tag:
                full_label = f"{new_name} | {author_tag} | Ваш котенок ❤"
            else:
                full_label = f"{new_name} | Ваш котенок ❤"
                
            final_configs.append(f"{base_link}#{full_label}")

        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
            
        print(f"Готово! Собрано: {len(final_configs)}")
    else:
        print("Новых конфигов не найдено.")

if __name__ == "__main__":
    parse()
