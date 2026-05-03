import requests, re, urllib.parse, base64

# ТВОИ SOURCES — ТЕПЕРЬ ТОЧНО ТУТ И НАВСЕГДА! 💖
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

COUNTRY_FLAGS = {
    "Russia": "🇷🇺", "Germany": "🇩🇪", "Netherlands": "🇳🇱", "USA": "🇺🇸", 
    "United States": "🇺🇸", "UK": "🇬🇧", "Czechia": "🇨🇿", "Finland": "🇫🇮", 
    "Poland": "🇵🇱", "Turkey": "🇹🇷", "France": "🇫🇷", "Kazakhstan": "🇰🇿", 
    "Sweden": "🇸🇪", "Ukraine": "🇺🇦", "Austria": "🇦🇹", "Canada": "🇨🇦"
}

def get_clean_name(old_name, auth):
    # Если это RKP — сразу в игнор их тех. названия, будем нумеровать красиво
    if auth == "RKP":
        return None 

    # 1. ПРИОРИТЕТ: Ищем готовый эмодзи-флаг
    existing_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    
    # 2. Очищаем текст от мусора
    words = re.findall(r'[a-zA-Z]{3,}', old_name)
    clean_text = " ".join(words).strip()

    # 3. Ищем страну для флага
    emoji = ""
    for name, flag in COUNTRY_FLAGS.items():
        if name.lower() in clean_text.lower():
            emoji = flag
            break
    
    if emoji:
        return f"{emoji} {clean_text}"
    if existing_flags:
        # Если нашли флаг, возвращаем первый найденный
        return f"{existing_flags[0]} Server"
    
    return None

def parse():
    unique_cfgs = {}
    print("🐾 СРОЧНО ЧИНЮ ВСЁ...")
    
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
        # Сортировка по ссылке (vless вперед)
        sorted_items = sorted(unique_cfgs.items(), key=lambda x: (0 if x.startswith('vless://') else 1, x))
        
        final_list = []
        counts = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

        for cfg, src in sorted_items:
            if '#' in cfg:
                base, old_name_raw = cfg.rsplit('#', 1)
                old_name = urllib.parse.unquote(old_name_raw)
            else:
                base = cfg
                old_name = ""

            # Кто автор?
            if "etoneya" in src: auth = "EtoNeYa"
            elif "igareck" in src: auth = "igareck"
            elif "RKP" in src: auth = "RKP"
            elif "Ilyacom4ik" in src: auth = "FCH"
            else: auth = "Other"

            # Чистим имя
            display_name = get_clean_name(old_name, auth)
            
            if "anycast" in old_name.lower(): 
                name = "🌐 Anycast"
            elif display_name:
                name = display_name
            else:
                # Настройка префикса
                prefix = "🛡 Server" if auth == "RKP" else "Обход"
                name = f"{prefix} {counts[auth]}"
                counts[auth] += 1

            final_list.append(f"{base}#{name} | {auth} | Ваш котенок ❤")

        res_text = "\n".join(final_list)
        with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(res_text.encode()).decode())
        print(f"✅ Готово! Исправлено и собрано: {len(final_list)}")

if __name__ == "__main__":
    parse()
