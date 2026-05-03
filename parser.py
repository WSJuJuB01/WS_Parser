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

# База стран (для всех, кроме EtoNeYa и RKP) 🌍
COUNTRY_MAP = {
    "russia": "🇷🇺 Russia", "germany": "🇩🇪 Germany", "netherlands": "🇳🇱 Netherlands",
    "usa": "🇺🇸 USA", "united states": "🇺🇸 USA", "uk": "🇬🇧 UK", "finland": "🇫🇮 Finland",
    "poland": "🇵🇱 Poland", "turkey": "🇹🇷 Turkey", "france": "🇫🇷 France", 
    "kazakhstan": "🇰🇿 Kazakhstan", "ukraine": "🇺🇦 Ukraine", "sweden": "🇸🇪 Sweden", 
    "austria": "🇦🇹 Austria", "singapore": "🇸🇬 Singapore", "japan": "🇯🇵 Japan"
}

def get_author(url):
    if "etoneya" in url: return "EtoNeYa"
    if "igareck" in url: return "igareck"
    if "RKP" in url: return "RKP"
    if "Ilyacom4ik" in url: return "FCH"
    return "Other"

def get_pretty_country(old_name):
    low_name = old_name.lower()
    for key, formatted in COUNTRY_MAP.items():
        if key in low_name: return formatted
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    return "".join(flags) if flags else "🌐 Unknown"

def fetch(url):
    try:
        res = requests.get(url, timeout=15)
        return res.text if res.status_code == 200 else None, url
    except: return None, url

def run():
    buckets = {"EtoNeYa": [], "RKP": [], "igareck": [], "FCH": [], "Other": []}
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
        results = list(ex.map(fetch, SOURCES))

    for content, url in results:
        if not content: continue
        author = get_author(url)
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
    etoneya_counter = 1
    
    authors_order = ["EtoNeYa", "RKP", "igareck", "FCH", "Other"]
    
    while any(buckets.values()):
        for author in authors_order:
            chunk = buckets[author][:10]
            buckets[author] = buckets[author][10:]
            
            for item in chunk:
                # СПЕЦ-ЛОГИКА ДЛЯ АВТОРОВ
                if author == "EtoNeYa":
                    # Тот самый кастомный формат 🏳
                    name = f"🏳 White lists {etoneya_counter}"
                    etoneya_counter += 1
                elif author == "RKP":
                    name = f"🛡 RKP #{rkp_counter}"
                    rkp_counter += 1
                else:
                    # Для остальных — страны и флаги
                    name = get_pretty_country(item["old_name"])

                # Собираем строку (у EtoNeYa подпись "котик", у остальных "котенок")
                cat_tag = "котик" if author == "EtoNeYa" else "котенок"
                final_list.append(f"{item['link']}#{name} | {author} | Ваш {cat_tag} ❤")

    # Шапка
    now = datetime.now().strftime('%d.%m %H:%M')
    final_list.insert(0, f"vless://00000000-0000-0000-0000-000000000000@0.0.0.0:443?encryption=none&type=tcp#REMARK=🐈 Custom Mix | {now} | {len(final_list)} шт.")

    # Сохранение
    content = "\n".join(final_list)
    with open("subscription.txt", "w", encoding="utf-8") as f: f.write(content)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(content.encode()).decode())
        
    print(f"✅ Готово! EtoNeYa теперь особенная 🏳")

if __name__ == "__main__":
    run()
