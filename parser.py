import requests, re, urllib.parse, base64
from datetime import datetime

# ТВОИ SOURCES — ВСЕГДА В КОДЕ 🐾
SOURCES = [
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://vercel.app"
]

# Карта для EtoNeYa: ищем английское слово -> ставим флаг
COUNTRY_DATA = {
    "Russia": "🇷🇺 Russia", "Germany": "🇩🇪 Germany", "Netherlands": "🇳🇱 Netherlands",
    "USA": "🇺🇸 USA", "United States": "🇺🇸 USA", "UK": "🇬🇧 UK", "Czechia": "🇨🇿 Czechia",
    "Finland": "🇫🇮 Finland", "Poland": "🇵🇱 Poland", "Turkey": "🇹🇷 Turkey",
    "France": "🇫🇷 France", "Kazakhstan": "🇰🇿 Kazakhstan", "Sweden": "🇸🇪 Sweden",
    "Ukraine": "🇺🇦 Ukraine", "Austria": "🇦🇹 Austria", "Canada": "🇨🇦 Canada"
}

def get_name(old_name, auth):
    if auth == "RKP": return None
    
    # 1. ПРИОРИТЕТ ДЛЯ ИГОРЯ: Если уже есть эмодзи-флаг — берем его!
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    if flags: 
        return "".join(flags)

    # 2. ДЛЯ ETONEYA: Ищем английское слово в названии
    for english_name, formatted in COUNTRY_DATA.items():
        if english_name.lower() in old_name.lower():
            return formatted
            
    return None

def parse():
    all_data = [] 
    print("🐾 Собираю конфиги из твоих источников...")
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=20)
            if res.status_code == 200:
                found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', res.text)
                for c in found:
                    clean = c.strip().replace('\r', '').replace('`', '').replace('"', '')
                    all_data.append((clean, url))
        except: pass

    if all_data:
        # Исправленная сортировка для GitHub Actions
        sorted_data = sorted(all_data, key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
        
        final_list = []
        counts = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

        # Инфо-строка
        now_str = datetime.now().strftime('%d.%m %H:%M')
        info_tag = f"REMARK=🐈 Всего: {len(sorted_data)} | Обновлено: {now_str}"
        final_list.append(f"vless://00000000-0000-0000-0000-000000000000@0.0.0.0:443?encryption=none&type=tcp#{info_tag}")

        for cfg_full, src in sorted_data:
            if '#' in cfg_full:
                base_link, old_name_raw = cfg_full.rsplit('#', 1)
                old_name = urllib.parse.unquote(old_name_raw)
            else:
                base_link, old_name = cfg_full, ""

            if "etoneya" in src: auth = "EtoNeYa"
            elif "igareck" in src: auth = "igareck"
            elif "RKP" in src: auth = "RKP"
            elif "Ilyacom4ik" in src: auth = "FCH"
            else: auth = "Other"

            display_name = get_name(old_name, auth)
            
            if "anycast" in old_name.lower(): 
                name = "🌐 Anycast"
            elif auth == "RKP":
                name = f"🛡#RKP {counts[auth]}"
                counts[auth] += 1
            elif display_name:
                name = display_name
            else:
                name = f"Обход {counts[auth]}"
                counts[auth] += 1

            final_list.append(f"{base_link}#{name} | {auth} | Ваш котенок ❤")

        res_text = "\n".join(final_list)
        with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(res_text.encode()).decode())
        print(f"✅ Готово! Собрано: {len(final_list)}")
    else:
        print("😿 Ссылок не нашли.")

if __name__ == "__main__":
    parse()
