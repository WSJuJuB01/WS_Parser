import requests, re, urllib.parse, base64

# ТВОЙ АКТУАЛЬНЫЙ СПИСОК ИСТОЧНИКОВ
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

# Карта стран для поиска в расшифрованном тексте
COUNTRY_MAP = {
    "russia": "🇷🇺 Russia", "germany": "🇩🇪 Germany", "netherlands": "🇳🇱 Netherlands",
    "usa": "🇺🇸 USA", "unitedstates": "🇺🇸 USA", "unitedkingdom": "🇬🇧 UK",
    "ukraine": "🇺🇦 Ukraine", "finland": "🇫🇮 Finland", "poland": "🇵🇱 Poland",
    "turkey": "🇹🇷 Turkey", "france": "🇫🇷 France", "kazakhstan": "🇰🇿 Kazakhstan",
    "japan": "🇯🇵 Japan", "singapore": "🇸🇬 Singapore", "austria": "🇦🇹 Austria",
    "canada": "🇨🇦 Canada", "hongkong": "🇭🇰 Hong Kong", "sweden": "🇸🇪 Sweden"
}

def universal_decode(text):
    """Превращает греческие и мат. символы EtoNeYa в обычную латиницу"""
    table = {
        'α': 'a', 'β': 'b', 'γ': 'g', 'δ': 'd', 'ε': 'a', 'ζ': 'z', 'η': 'n', 'θ': 'h',
        'ι': 'i', 'κ': 'k', 'λ': 'l', 'μ': 'm', 'ν': 'n', 'ξ': 'x', 'ο': 'o', 'π': 'p',
        'ρ': 'r', 'σ': 's', 'τ': 't', 'υ': 'u', 'φ': 'f', 'χ': 'x', 'ψ': 'u', 'ω': 'w',
        '†': 'i', '‡': 's', '·': '', ' ': ''
    }
    decoded = "".join(table.get(c, c) for c in text.lower())
    # Убираем всё, кроме чистых букв a-z для точного поиска страны
    return re.sub(r'[^a-z]', '', decoded)

def get_name(old_name):
    # 1. Если в названии уже есть реальный эмодзи-флаг
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    if flags: 
        return f"{flags[0]} Location"
    
    # 2. Декодируем и ищем название страны по ключам
    clean = universal_decode(old_name)
    for key, val in COUNTRY_MAP.items():
        if key in clean: return val
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
        except: print(f"❌ Ошибка загрузки: {url[:40]}...")

    if not unique_cfgs: return print("😿 Новых конфигов не найдено.")

    # Сортировка: VLESS всегда в топе
    sorted_items = sorted(unique_cfgs.items(), key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
    final_list = []
    counts = {"EtoNeYa 🏳": 1, "igareck": 1, "#RKP": 1, "FCH": 1, "Other": 1}

    for cfg, src in sorted_items:
        parts = cfg.split('#', 1)
        base = parts[0]
        old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""

        # Определяем автора
        if "etoneya" in src: auth = "EtoNeYa 🏳"
        elif "igareck" in src: auth = "igareck"
        elif "RKP" in src: auth = "#RKP"
        elif "Ilyacom4ik" in src: auth = "FCH"
        else: auth = "Other"

        # Формируем красивое название
        country = get_name(old_name)
        if "anycast" in old_name.lower(): 
            name = "🌐 Anycast"
        elif country:
            name = country
        else:
            # Если страну не узнали — ставим номер обхода
            name = f"Обход {counts.get(auth, 1)}"
            counts[auth] += 1

        final_list.append(f"{base}#{name} | {auth} | Ваш котенок ❤")

    res_text = "\n".join(final_list)
    # Сохраняем текстовый вариант
    with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
    # Сохраняем Base64 вариант (для v2rayNG и др.)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(res_text.encode()).decode())
    
    print(f"✅ Готово! Собрано: {len(final_list)} конфигов.")

if __name__ == "__main__":
    parse()
