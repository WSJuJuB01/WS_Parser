import requests, re, urllib.parse, base64

# ТВОИ SOURCES — ВСЕГДА В ЦЕНТРЕ ВНИМАНИЯ 🐾
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

# Карта для красивых флагов
COUNTRY_FLAGS = {
    "Russia": "🇷🇺", "Germany": "🇩🇪", "Netherlands": "🇳🇱", "USA": "🇺🇸", 
    "United States": "🇺🇸", "UK": "🇬🇧", "Czechia": "🇨🇿", "Finland": "🇫🇮", 
    "Poland": "🇵🇱", "Turkey": "🇹🇷", "France": "🇫🇷", "Kazakhstan": "🇰🇿", 
    "Sweden": "🇸🇪", "Ukraine": "🇺🇦", "Austria": "🇦🇹", "Canada": "🇨🇦"
}

def get_clean_name(old_name):
    # 1. Сначала ищем уже готовый эмодзи-флаг
    existing_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    
    # 2. Оставляем только английские слова (страны), игнорируем кракозябры
    words = re.findall(r'[a-zA-Z]{3,}', old_name)
    clean_text = " ".join(words).strip()

    # 3. Подбираем флаг по названию страны
    emoji = ""
    for name, flag in COUNTRY_FLAGS.items():
        if name.lower() in clean_text.lower():
            emoji = flag
            break
    
    # Если название страны не узнали, но флаг был — оставляем старый флаг
    if not emoji and existing_flags:
        emoji = existing_flags[0]

    if clean_text:
        return f"{emoji} {clean_text}".strip()
    elif existing_flags:
        return existing_flags[0]
    
    return None

def parse():
    unique_cfgs = {}
    print("🐾 Начинаю сборку подписки...")
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                # Ищем все ссылки на конфиги
                found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', res.text)
                for c in found:
                    clean = c.strip().replace('\r', '').replace('`', '').replace('"', '')
                    if clean not in unique_cfgs: unique_cfgs[clean] = url
        except: print(f"❌ Ошибка загрузки: {url[:40]}...")

    if unique_cfgs:
        # Сортировка: VLESS в начало
        items = sorted(unique_cfgs.items(), key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
        
        final_list = []
        counts = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

        for cfg, src in items:
            # Делим ссылку и старое название по решетке (берем только последнюю решетку для имени)
            if '#' in cfg:
                base, old_name_raw = cfg.rsplit('#', 1)
                old_name = urllib.parse.unquote(old_name_raw)
            else:
                base = cfg
                old_name = ""

            # Определяем автора по источнику
            if "etoneya" in src: auth = "EtoNeYa"
            elif "igareck" in src: auth = "igareck"
            elif "RKP" in src: auth = "RKP"
            elif "Ilyacom4ik" in src: auth = "FCH"
            else: auth = "Other"

            # Чистим название
            display_name = get_clean_name(old_name)
            
            if "anycast" in old_name.lower(): 
                name = "🌐 Anycast"
            elif display_name:
                name = display_name
            else:
                name = f"Обход {counts.get(auth, 1)}"
                counts[auth] = counts.get(auth, 1) + 1

            final_list.append(f"{base}#{name} | {auth} | Ваш котенок ❤")

        # Сохраняем файлы
        res_text = "\n".join(final_list)
        with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(res_text.encode()).decode())
        
        print(f"✅ Готово! Собрано: {len(final_list)} конфигов.")
    else:
        print("😿 Ничего не найдено.")

if __name__ == "__main__":
    parse()
