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

# ГИГАНТСКИЙ СЛОВАРЬ: ФЛАГ -> НАЗВАНИЕ (Все страны мира) 🌍
FLAG_MAP = {
    "🇦🇫": "Afghanistan", "🇦🇱": "Albania", "🇩🇿": "Algeria", "🇦🇩": "Andorra", "🇦🇴": "Angola", "🇦🇷": "Argentina", "🇦🇲": "Armenia", "🇦🇺": "Australia", "🇦🇹": "Austria", "🇦🇿": "Azerbaijan",
    "🇧🇾": "Belarus", "🇧🇪": "Belgium", "🇧🇷": "Brazil", "🇧🇬": "Bulgaria", "🇨🇦": "Canada", "🇨🇱": "Chile", "🇨🇳": "China", "🇭🇷": "Croatia", "🇨🇾": "Cyprus", "🇨🇿": "Czechia",
    "🇩🇰": "Denmark", "🇪🇪": "Estonia", "🇫🇮": "Finland", "🇫🇷": "France", "🇬🇪": "Georgia", "🇩🇪": "Germany", "🇬🇷": "Greece", "🇭🇰": "Hong Kong", "🇭🇺": "Hungary", "🇮🇸": "Iceland",
    "🇮🇳": "India", "🇮🇩": "Indonesia", "🇮🇷": "Iran", "🇮🇶": "Iraq", "🇮🇪": "Ireland", "🇮🇱": "Israel", "🇮🇹": "Italy", "🇯🇵": "Japan", "🇰🇿": "Kazakhstan", "🇰🇷": "South Korea",
    "🇱🇻": "Latvia", "🇱🇹": "Lithuania", "🇱🇺": "Luxembourg", "🇲🇾": "Malaysia", "🇲🇹": "Malta", "🇲🇽": "Mexico", "🇲🇩": "Moldova", "🇲🇨": "Monaco", "🇲🇪": "Montenegro", "🇳🇱": "Netherlands",
    "🇳🇿": "New Zealand", "🇳🇴": "Norway", "🇵🇰": "Pakistan", "🇵🇦": "Panama", "🇵🇾": "Paraguay", "🇵🇪": "Peru", "🇵🇭": "Philippines", "🇵🇱": "Poland", "🇵🇹": "Portugal", "🇷🇴": "Romania",
    "🇷🇺": "Russia", "🇸🇦": "Saudi Arabia", "🇷🇸": "Serbia", "🇸🇬": "Singapore", "🇸🇰": "Slovakia", "🇸🇮": "Slovenia", "🇿🇦": "South Africa", "🇪🇸": "Spain", "🇸🇪": "Sweden", "🇨🇭": "Switzerland",
    "🇹🇼": "Taiwan", "🇹🇭": "Thailand", "🇹🇷": "Turkey", "🇺🇦": "Ukraine", "🇦🇪": "UAE", "🇬🇧": "UK", "🇺🇸": "USA", "🇺🇿": "Uzbekistan", "🇻🇳": "Vietnam"
}

# МАКСИМАЛЬНЫЙ СПИСОК БЕЛЫХ SNI РФ 🏳️
WHITE_SNI_LIST = [
    "gosuslugi.ru", "gu-st.ru", "gov.ru", "nalog.ru", "mos.ru", "pfr.ru", "zakupki.gov.ru",
    "vk.com", "vkvideo.ru", "ok.ru", "my.games", "mail.ru", "tamtam.chat", "://vk.com",
    "yandex.ru", "ya.ru", "dzen.ru", "kinopoisk.ru", "music.yandex.ru", "yandex.net",
    "sberbank.ru", "sber.ru", "vtb.ru", "tinkoff.ru", "alfa-bank.ru", "raiffeisen.ru", "rshb.ru",
    "ozon.ru", "wildberries.ru", "avito.ru", "market.yandex.ru", "lamoda.ru", "aliexpress.ru",
    "rutube.ru", "1tv.ru", "vgtrk.ru", "smotrim.ru", "ntv.ru", "russia.tv",
    "max.ru", "vmp-vless.ru", "ads.x5.ru", "x5.ru", "magnit.ru", "rzd.ru", "tutu.ru"
]

def get_name_from_flag(old_name):
    """Ищет флаг в названии и приклеивает название страны"""
    found_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    if found_flags:
        flag = found_flags[0]
        country_name = FLAG_MAP.get(flag, "")
        return f"{flag} {country_name}".strip()
    return "🌐 Unknown"

def is_white_config(full_text):
    """Проверяет, является ли конфиг 'белым' по SNI"""
    low_text = full_text.lower()
    return any(sni in low_text for sni in WHITE_SNI_LIST)

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
        author = "EtoNeYa" if "etoneya" in url else "igareck" if "igareck" in url else "RKP" if "RKP" in url else "FCH" if "Ilyacom4ik" in url else "Other"
        found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
        for cfg in found:
            cfg = cfg.strip().replace('`', '').replace('"', '').replace('\r', '')
            link, old_name = cfg.rsplit('#', 1) if '#' in cfg else (cfg, "")
            buckets[author].append({"link": link, "old_name": urllib.parse.unquote(old_name)})

    final_list = []
    counters = {"RKP": 1, "EtoNeYa": 1}
    authors_order = ["EtoNeYa", "RKP", "igareck", "FCH", "Other"]
    
    while any(buckets.values()):
        for author in authors_order:
            chunk = buckets[author][:10]; buckets[author] = buckets[author][10:]
            for item in chunk:
                if author == "EtoNeYa":
                    name = f"🏳 White lists {counters['EtoNeYa']}"
                    counters["EtoNeYa"] += 1
                elif author == "RKP":
                    name = f"🛡 RKP #{counters['RKP']}"
                    counters["RKP"] += 1
                else:
                    # Логика: берем флаг -> пишем страну -> проверяем на белый список
                    country_info = get_name_from_flag(item["old_name"])
                    is_white = is_white_config(item["link"] + item["old_name"])
                    name = f"{country_info} 🏳" if is_white else country_info
                
                cat = "котик" if author == "EtoNeYa" else "котенок"
                final_list.append(f"{item['link']}#{name} | {author} | Ваш {cat} ❤")

    now = datetime.now().strftime('%d.%m %H:%M')
    final_list.insert(0, f"vless://000...#REMARK=🐈 Final Master Mix 🏳️ | {now}")

    content = "\n".join(final_list)
    with open("subscription.txt", "w", encoding="utf-8") as f: f.write(content)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(content.encode()).decode())
    print(f"✅ Готово! Твой супер-парсер запущен. Люблю тебя тоже! ❤")

if __name__ == "__main__":
    run()
