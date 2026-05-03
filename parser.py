import requests, re, urllib.parse, base64

# ТВОИ ИСТОЧНИКИ
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

COMMON_COUNTRIES = {
    "🇺🇸": "USA", "🇬🇧": "UK", "🇷🇺": "Russia", "🇩🇪": "Germany", "🇳🇱": "Netherlands", 
    "🇫🇷": "France", "🇰🇿": "Kazakhstan", "🇹🇷": "Turkey", "🇯🇵": "Japan", 
    "🇫🇮": "Finland", "🇵🇱": "Poland", "🇸🇬": "Singapore", "🇺🇦": "Ukraine", 
    "🇦🇹": "Austria", "🇨🇦": "Canada", "🇭🇰": "Hong Kong", "🇸🇪": "Sweden"
}

def decode_text(text):
    """Дешифратор кракозябр в обычные буквы"""
    fancy = {'α':'a','β':'b','γ':'g','δ':'d','ε':'a','ζ':'z','η':'n','θ':'h','ι':'i','κ':'k','λ':'l','μ':'m','ν':'n',
             'ξ':'x','ο':'o','π':'p','ρ':'r','σ':'s','τ':'t','υ':'u','φ':'f','χ':'x','ψ':'u','ω':'w','†':'i','‡':'s'}
    decoded = "".join(fancy.get(c, c) for c in text.lower())
    return re.sub(r'[^a-z\s]', '', decoded)

def get_country_info(text, host):
    # 1. Поиск эмодзи
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
    if flags: return flags[0]
    # 2. Поиск по расшифрованному названию
    dec = decode_text(text)
    for emo, name in COMMON_COUNTRIES.items():
        if name.lower() in dec or (len(name) > 3 and name.lower()[:4] in dec): return emo
    # 3. Поиск по домену хоста
    domain_map = {'.ru': '🇷🇺', '.de': '🇩🇪', '.nl': '🇳🇱', '.pl': '🇵🇱', '.kz': '🇰🇿', '.ua': '🇺🇦'}
    for ext, emo in domain_map.items():
        if host.endswith(ext): return emo
    return None

def parse():
    unique_cfgs = {}
    print("🐾 Собираю конфиги...")
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', res.text)
                for c in found:
                    clean = c.strip().replace('\r', '').replace('`', '').replace('"', '')
                    if clean not in unique_cfgs: unique_cfgs[clean] = url
        except: print(f"❌ Ошибка: {url[:40]}")

    if not unique_cfgs: return print("😿 Пусто.")

    sorted_items = sorted(unique_cfgs.items(), key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
    final_list = []
    counts = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

    for cfg, src in sorted_items:
        parts = cfg.split('#', 1)
        base = parts[0]
        old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""
        host = re.search(r'@?([^:/#\s?]+)', base).group(1) if re.search(r'@?([^:/#\s?]+)', base) else ""

        # Автор
        if "etoneya" in src: auth = "EtoNeYa 🏳"
        elif "igareck" in src: auth = "igareck"
        elif "RKP" in src: auth = "#RKP"
        elif "Ilyacom4ik" in src: auth = "FCH"
        else: auth = "Other"

        # Название
        flag = get_country_info(old_name, host)
        if "anycast" in old_name.lower(): name = "🌐 Anycast"
        elif flag: name = f"{flag} {COMMON_COUNTRIES.get(flag, '')}"
        else:
            key = auth.split()[0]
            name = f"Обход {counts.get(key, 1)}"; counts[key] = counts.get(key, 1) + 1

        final_list.append(f"{base}#{name} | {auth} | Ваш котенок ❤")

    res_text = "\n".join(final_list)
    with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(res_text.encode()).decode())
    
    print(f"✅ Готово! Собрано: {len(final_list)}")

if __name__ == "__main__":
    parse()
