import requests, re, urllib.parse, base64, concurrent.futures
from datetime import datetime

# ТВОИ SOURCES 🐾
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

# МАКСИМАЛЬНАЯ БАЗА СТРАН ДЛЯ 100% РЕЗУЛЬТАТА 🌍
COUNTRY_MAP = {
    "russia": "🇷🇺 Russia", " rus": "🇷🇺 Russia", "germany": "🇩🇪 Germany", " ger": "🇩🇪 Germany",
    "netherlands": "🇳🇱 Netherlands", " nl": "🇳🇱 Netherlands", "usa": "🇺🇸 USA", "united states": "🇺🇸 USA",
    "uk ": "🇬🇧 UK", "united kingdom": "🇬🇧 UK", "finland": "🇫🇮 Finland", " fi": "🇫🇮 Finland",
    "poland": "🇵🇱 Poland", " pl": "🇵🇱 Poland", "turkey": "🇹🇷 Turkey", " tr": "🇹🇷 Turkey",
    "france": "🇫🇷 France", " fr": "🇫🇷 France", "kazakhstan": "🇰🇿 Kazakhstan", " kz": "🇰🇿 Kazakhstan",
    "ukraine": "🇺🇦 Ukraine", " ua": "🇺🇦 Ukraine", "sweden": "🇸🇪 Sweden", " se": "🇸🇪 Sweden",
    "austria": "🇦🇹 Austria", " at": "🇦🇹 Austria", "singapore": "🇸🇬 Singapore", " sg": "🇸🇬 Singapore",
    "japan": "🇯🇵 Japan", " jp": "🇯🇵 Japan", "hong kong": "🇭🇰 Hong Kong", " hk": "🇭🇰 Hong Kong",
    "canada": "🇨🇦 Canada", " ca": "🇨🇦 Canada", "australia": "🇦🇺 Australia", " au": "🇦🇺 Australia",
    "italy": "🇮🇹 Italy", " it": "🇮🇹 Italy", "spain": "🇪🇸 Spain", " es": "🇪🇸 Spain",
    "switzerland": "🇨🇭 Switzerland", " ch": "🇨🇭 Switzerland", "brazil": "🇧🇷 Brazil", " br": "🇧🇷 Brazil",
    "india": "🇮🇳 India", " in": "🇮🇳 India", "korea": "🇰🇷 Korea", " kr": "🇰🇷 Korea"
}

def get_author(url):
    if "etoneya" in url: return "EtoNeYa"
    if "igareck" in url: return "igareck"
    if "RKP" in url: return "RKP"
    if "Ilyacom4ik" in url: return "FCH"
    return "Other"

def get_pretty_country(old_name):
    low_name = old_name.lower()
    # 1. Сначала ищем полное совпадение или код из базы
    for key, formatted in COUNTRY_MAP.items():
        if key in low_name:
            return formatted
    # 2. Если не нашли, вытаскиваем эмодзи-флаги, если они есть в кракозябрах
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    if flags:
        return "".join(flags)
    # 3. Если совсем глухо
    return "🌐 Unknown"

def fetch(url):
    try:
        res = requests.get(url, timeout=15)
        return res.text if res.status_code == 200 else None, url
    except: return None, url

def run():
    # Группировка
    buckets = {"EtoNeYa": [], "RKP": [], "igareck": [], "FCH": [], "Other": []}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(fetch, SOURCES))

    for content, url in results:
        if not content: continue
        author = get_author(url)
        # Находим все ссылки
        found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
        
        for cfg in found:
            cfg = cfg.strip().replace('`', '').replace('"', '').replace('\r', '')
            if '#' in cfg:
                link, old_name = cfg.rsplit('#', 1)
                name_decoded = urllib.parse.unquote(old_name)
            else:
                link, name_decoded = cfg, ""
            buckets[author].append({"link": link, "old_name": name_decoded})

    final_list = []
    rkp_counter = 1
    authors_order = ["EtoNeYa", "RKP", "igareck", "FCH", "Other"]
    
    # ПЕРЕМЕШИВАНИЕ СЛОЯМИ ПО 10
    while any(buckets.values()):
        for author in authors_order:
            chunk = buckets[author][:10]
            buckets[author] = buckets[author][10:]
            
            for item in chunk:
                # Название: для RKP свой счетчик, для остальных — страна
                if author == "RKP":
                    name = f"🛡 RKP #{rkp_counter}"
                    rkp_counter += 1
                else:
                    name = get_pretty_country(item["old_name"])

                final_list.append(f"{item['link']}#{name} | {author} | Ваш котенок ❤")

    # Шапка сабки
    now = datetime.now().strftime('%d.%m %H:%M')
    final_list.insert(0, f"vless://00000000-0000-0000-0000-000000000000@0.0.0.0:443?encryption=none&type=tcp#REMARK=🐈 Super Mix | {now} | {len(final_list)} шт.")

    # Сохранение (TXT и Base64)
    content = "\n".join(final_list)
    with open("subscription.txt", "w", encoding="utf-8") as f: f.write(content)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(content.encode()).decode())
        
    print(f"✅ Готово на 100%! Теперь все страны и авторы перемешаны идеально.")

if __name__ == "__main__":
    run()
