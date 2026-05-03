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
# Реальный Белый Список РФ 🇷🇺
WHITE_SNI = [
    "gosuslugi.ru", "gu-st.ru", "vk.com", "vkvideo.ru", "ok.ru", "mail.ru", 
    "max.ru", "yandex.ru", "ya.ru", "dzen.ru", "ozon.ru", "wildberries.ru", 
    "avito.ru", "vtb.ru", "alfa-bank.ru", "sberbank.ru", "nspk.ru", "mir.ru",
    "kinopoisk.ru", "mos.ru", "tinkoff.ru", "moex.com", "mvideo.ru"
]

def get_pretty_country(old_name, full_link):
    # 1. Сначала ищем живой эмодзи-флаг (для Игоря)
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    country_part = "".join(flags) if flags else ""

    # 2. Если флага нет, ищем текст (Эстония, Латвия и т.д.)
    if not country_part:
        n_low = old_name.lower()
        if any(x in n_low for x in ["russia", " rus", " ru"]): country_part = "🇷🇺"
        elif "estonia" in n_low or " ee" in n_low: country_part = "🇪🇪"
        elif "latvia" in n_low or " lv" in n_low: country_part = "🇱🇻"
        elif "germany" in n_low or " de" in n_low: country_part = "🇩🇪"
        elif "netherlands" in n_low or " nl" in n_low: country_part = "🇳🇱"
        elif "usa" in n_low or " us" in n_low: country_part = "🇺🇸"
        elif "finland" in n_low or " fi" in n_low: country_part = "🇫🇮"

    # 3. Проверка на Белый Список (SNI)
    is_white = False
    check_text = (old_name + full_link).lower()
    for sni in WHITE_SNI:
        if sni in check_text:
            is_white = True
            break

    # Итоговая сборка
    if country_part:
        return f"{country_part} 🏳" if is_white else country_part
    
    return "🌐 Unknown"

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
        author = "EtoNeYa" if "etoneya" in url else \
                 "igareck" if "igareck" in url else \
                 "RKP" if "RKP" in url else \
                 "FCH" if "Ilyacom4ik" in url else "Other"
        
        found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
        for cfg in found:
            cfg = cfg.strip().replace('`', '').replace('"', '').replace('\r', '')
            link, old_name = cfg.rsplit('#', 1) if '#' in cfg else (cfg, "")
            buckets[author].append({"link": link, "old_name": urllib.parse.unquote(old_name)})

    final_list = []
    counters = {"RKP": 1, "EtoNeYa": 1}
    authors_order = ["EtoNeYa", "RKP", "igareck", "FCH", "Other"]
    
    # Перемешивание слоями по 10 штук
    while any(buckets.values()):
        for author in authors_order:
            chunk = buckets[author][:10]
            buckets[author] = buckets[author][10:]
            
            for item in chunk:
                if author == "EtoNeYa":
                    name = f"🏳 White lists {counters['EtoNeYa']}"
                    counters["EtoNeYa"] += 1
                elif author == "RKP":
                    name = f"🛡 RKP #{counters['RKP']}"
                    counters["RKP"] += 1
                else:
                    # Логика флагов + белых SNI
                    name = get_pretty_country(item["old_name"], item["link"])

                cat = "котик" if author == "EtoNeYa" else "котенок"
                final_list.append(f"{item['link']}#{name} | {author} | Ваш {cat} ❤")

    # Шапка
    now = datetime.now().strftime('%d.%m %H:%M')
    final_list.insert(0, f"vless://00000000-0000-0000-0000-000000000000@0.0.0.0:443?encryption=none&type=tcp#REMARK=🐈 Global Mix 🏳 | {now} | {len(final_list)} шт.")

    # Сохранение (TXT и Base64)
    res_text = "\n".join(final_list)
    with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(res_text.encode()).decode())
    
    print(f"✅ Успех! Сабка готова, белые списки помечены 🏳.")

if __name__ == "__main__":
    run()
