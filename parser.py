import requests, re, urllib.parse, base64

# ТВОИ SOURCES — ВСЕГДА ТУТ 💖
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

# Карта частых стран для красивых названий
COUNTRY_DATA = {
    "Russia": "🇷🇺 Russia", "Germany": "🇩🇪 Germany", "Netherlands": "🇳🇱 Netherlands",
    "USA": "🇺🇸 USA", "United States": "🇺🇸 USA", "United Kingdom": "🇬🇧 UK",
    "Czechia": "🇨🇿 Czechia", "Finland": "🇫🇮 Finland", "Poland": "🇵🇱 Poland",
    "Turkey": "🇹🇷 Turkey", "France": "🇫🇷 France", "Kazakhstan": "🇰🇿 Kazakhstan",
    "Sweden": "🇸🇪 Sweden", "Ukraine": "🇺🇦 Ukraine", "Austria": "🇦🇹 Austria",
    "Canada": "🇨🇦 Canada", "Hong Kong": "🇭🇰 Hong Kong", "Japan": "🇯🇵 Japan",
    "Singapore": "🇸🇬 Singapore", "Italy": "🇮🇹 Italy", "Spain": "🇪🇸 Spain"
}

def get_clean_name(old_name):
    # 1. ПРИОРИТЕТ: Если уже есть эмодзи-флаг
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    if flags: return flags[0]

    # 2. Ищем по нашему списку COUNTRY_DATA
    for english_name, formatted in COUNTRY_DATA.items():
        if english_name.lower() in old_name.lower():
            return formatted
    
    # 3. МАГИЯ ДЛЯ РЕДКИХ СТРАН: Ищем текстовые коды (типа RU, LU, US)
    # и превращаем их в эмодзи-флаги
    clean_text = re.sub(r'[^a-zA-Z\s]', ' ', old_name).strip().split()
    for word in clean_text:
        if len(word) == 2 and word.isupper():
            # Превращаем буквы в эмодзи-флаг
            flag = "".join(chr(ord(c) + 127397) for c in word)
            return f"{flag} {word}"
            
    # 4. Если нашли просто латиницу (название страны без кода)
    clean_final = re.sub(r'[^a-zA-Z\s]', '', old_name).strip()
    if len(clean_final) > 2:
        return f"🌍 {clean_final.capitalize()}"
    
    return None

def parse():
    unique_cfgs = {}
    print("🐾 Начинаю сборку подписки...")
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', res.text)
                for c in found:
                    clean = c.strip().replace('\r', '').replace('`', '').replace('"', '')
                    if clean not in unique_cfgs: unique_cfgs[clean] = url
        except: pass

    if unique_cfgs:
        # Сортировка: VLESS в начало
        items = sorted(unique_cfgs.items(), key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
        
        final_list = []
        counts = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

        for cfg, src in items:
            parts = cfg.split('#', 1)
            base = parts[0]
            old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""

            if "etoneya" in src: auth = "EtoNeYa"
            elif "igareck" in src: auth = "igareck"
            elif "RKP" in src: auth = "RKP"
            elif "Ilyacom4ik" in src: auth = "FCH"
            else: auth = "Other"

            display_name = get_clean_name(old_name)
            
            if "anycast" in old_name.lower(): 
                name = "🌐 Anycast"
            elif display_name:
                name = display_name
            else:
                name = f"Обход {counts.get(auth, 1)}"
                counts[auth] = counts.get(auth, 1) + 1

            final_list.append(f"{base}#{name} | {auth} | Ваш котенок ❤")

        res_text = "\n".join(final_list)
        with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(res_text.encode()).decode())
        print(f"✅ Готово! Собрано: {len(final_list)}")

if __name__ == "__main__":
    parse()
