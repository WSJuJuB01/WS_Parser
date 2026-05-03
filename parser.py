import requests, re, urllib.parse, base64

# ТВОИ АКТУАЛЬНЫЙ СПИСОК ИСТОЧНИКОВ
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

COUNTRY_MAP = {
    "russia": "🇷🇺 Russia", "germany": "🇩🇪 Germany", "netherlands": "🇳🇱 Netherlands",
    "usa": "🇺🇸 USA", "unitedstates": "🇺🇸 USA", "ukraine": "🇺🇦 Ukraine", 
    "finland": "🇫🇮 Finland", "poland": "🇵🇱 Poland", "turkey": "🇹🇷 Turkey", 
    "france": "🇫🇷 France", "kazakhstan": "🇰🇿 Kazakhstan"
}

def universal_decode(text):
    """Дешифрует греческие символы в обычную латиницу для EtoNeYa"""
    table = {
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'a', 'ζ': 'z', 'η': 'n', 'θ': 'h',
        'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
        'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'u', 'φ': 'f', 'χ': 'x', 'ψ': 'u', 'ω': 'w',
        '†': 'i', '‡': 's', '·': '', ' ': ''
    }
    decoded = "".join(table.get(c, c) for c in text.lower())
    return re.sub(r'[^a-z]', '', decoded)

def get_name(old_name):
    # 1. ПРИОРИТЕТ: Ищем готовый эмодзи-флаг
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    if flags:
        return flags[0] # Возвращаем СТРОКУ, а не список
    
    # 2. Если флага нет, дешифруем абракадабру (для EtoNeYa)
    clean = universal_decode(old_name)
    for key, val in COUNTRY_MAP.items():
        if key in clean: return val
    return None

def parse():
    unique_cfgs = {}
    print("🐾 Собираю конфиги из 6 источников...")
    
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
        # Сортировка: VLESS (приоритет 0) всегда в топе
        sorted_items = sorted(unique_cfgs.items(), key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
        
        final_list = []
        counts = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

        for cfg, src in sorted_items:
            parts = cfg.split('#', 1)
            base = parts[0]
            old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""

            # Определяем автора
            if "etoneya" in src: auth = "EtoNeYa"
            elif "igareck" in src: auth = "igareck"
            elif "RKP" in src: auth = "RKP"
            elif "Ilyacom4ik" in src: auth = "FCH"
            else: auth = "Other"

            # Получаем имя
            country = get_name(old_name)
            if "anycast" in old_name.lower(): 
                name = "🌐 Anycast"
            elif country:
                name = country
            else:
                name = f"Обход {counts[auth]}"
                counts[auth] += 1

            final_list.append(f"{base}#{name} | {auth} | Ваш котенок ❤")

        res_text = "\n".join(final_list)
        with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(res_text.encode()).decode())
        print(f"✅ Успех! Собрано: {len(final_list)}")
    else:
        print("😿 Новых конфигов не нашли.")

if __name__ == "__main__":
    parse()
