import requests, re, urllib.parse, base64

SOURCES = [
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://vercel.app"
]

COMMON_COUNTRIES = {
    "🇺🇸": "USA", "🇬🇧": "United Kingdom", "🇷🇺": "Russia", "🇩🇪": "Germany",
    "🇳🇱": "Netherlands", "🇫🇷": "France", "🇰🇿": "Kazakhstan", "🇹🇷": "Turkey",
    "🇯🇵": "Japan", "🇫🇮": "Finland", "🇵🇱": "Poland", "🇸🇬": "Singapore",
    "🇺🇦": "Ukraine", "🇦🇹": "Austria", "🇨🇦": "Canada", "🇭🇰": "Hong Kong", "🇸🇪": "Sweden"
}

# Расширенный дешифратор для EtoNeYa и других
def decode_text(text):
    fancy = {'α':'a','β':'b','γ':'g','δ':'d','ε':'a','ζ':'z','η':'n','θ':'h','ι':'i','κ':'k','λ':'l','μ':'m','ν':'n',
             'ξ':'x','ο':'o','π':'p','ρ':'r','σ':'s','τ':'t','υ':'u','φ':'f','χ':'x','ψ':'u','ω':'w','†':'i','‡':'s'}
    decoded = "".join(fancy.get(c, c) for c in text.lower())
    return re.sub(r'[^a-z\s]', '', decoded)

def get_country_info(text, host):
    # 1. Ищем готовый эмодзи
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
    if flags: return flags[0]
    
    # 2. Ищем по названию в дешифрованном тексте
    decoded = decode_text(text)
    for emoji, name in COMMON_COUNTRIES.items():
        if name.lower() in decoded or (len(name) > 3 and name.lower()[:4] in decoded):
            return emoji
            
    # 3. Магия: пытаемся понять страну по домену (адресу)
    domain_map = {'.ru': '🇷🇺', '.de': '🇩🇪', '.nl': '🇳🇱', '.pl': '🇵🇱', '.kz': '🇰🇿', '.ua': '🇺🇦', '.fr': '🇫🇷'}
    for ext, emoji in domain_map.items():
        if host.endswith(ext): return emoji
    return None

def parse():
    unique_configs = {}
    print("🐾 Начинаю сбор конфигов...")
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=15)
            if res.status_code == 200:
                # Находим все ссылки на протоколы
                found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', res.text)
                for cfg in found:
                    clean = cfg.strip().replace('\r', '').replace('`', '').replace('"', '')
                    if clean not in unique_configs: unique_configs[clean] = url
        except: print(f"❌ Ошибка в источнике: {url[:30]}...")

    if not unique_configs: return print("😿 Ничего не найдено.")

    # Сортировка (VLESS в начало)
    items = sorted(unique_configs.items(), key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
    final_list = []
    counters = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

    for cfg, src in items:
        parts = cfg.split('#', 1)
        base_link = parts[0]
        # Извлекаем хост для определения страны
        host_match = re.search(r'@?([^:/#\s?]+)', base_link)
        host = host_match.group(1) if host_match else ""
        old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""

        # Определяем автора
        author = "Other"
        if "etoneya" in src: author = "EtoNeYa 🏳"
        elif "igareck" in src: author = "igareck"
        elif "RKP" in src: author = "#RKP"
        elif "Ilyacom4ik" in src: author = "FCH"

        # Формируем имя
        flag = get_country_info(old_name, host)
        if "anycast" in old_name.lower(): 
            name = "🌐 Anycast"
        elif flag:
            country_name = COMMON_COUNTRIES.get(flag, "Location")
            name = f"{flag} {country_name}"
        else:
            name = f"Обход {counters.get(author.split()[0], 1)}"
            counters[author.split()[0]] = counters.get(author.split()[0], 1) + 1

        final_list.append(f"{base_link}#{name} | {author} | Ваш котенок ❤")

    # Сохраняем текстовый файл
    content = "\n".join(final_list)
    with open("subscription.txt", "w", encoding="utf-8") as f:
        f.write(content)
        
    # Создаем Base64 версию для приложений (v2rayNG и др.)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(content.encode('utf-8')).decode('utf-8'))

    print(f"✅ Готово! Собрано {len(final_list)} конфигов.")
    print("🐾 Файлы subscription.txt и subscription_b64.txt обновлены.")

if __name__ == "__main__":
    parse()
