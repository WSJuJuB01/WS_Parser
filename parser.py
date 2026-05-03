import requests
import re
import urllib.parse
import base64
from datetime import datetime

# ТВОИ SOURCES — НАВЕКИ В КОДЕ 💖
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

# Карта стран для поиска
COUNTRY_MAP = {
    "russia": "🇷🇺 Russia", "germany": "🇩🇪 Germany", "netherlands": "🇳🇱 Netherlands",
    "usa": "🇺🇸 USA", "unitedstates": "🇺🇸 USA", "ukraine": "🇺🇦 Ukraine", 
    "finland": "🇫🇮 Finland", "poland": "🇵🇱 Poland", "turkey": "🇹🇷 Turkey", 
    "france": "🇫🇷 France", "kazakhstan": "🇰🇿 Kazakhstan", "sweden": "🇸🇪 Sweden"
}

def get_name(old_name, auth):
    # Для RKP принудительно возвращаем None для нумерации
    if auth == "RKP": return None

    # 1. Ищем готовый эмодзи-флаг
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
    if flags: return "".join(flags)

    # 2. Ищем название страны (игнорируя кракозябры)
    clean = re.sub(r'[^a-zA-Z]', '', old_name).lower()
    for key, val in COUNTRY_MAP.items():
        if key in clean: return val
    return None

def parse():
    unique_cfgs = {}
    print(f"🐾 Начинаю сборку... ({datetime.now().strftime('%H:%M:%S')})")
    
    for url in SOURCES:
        try:
            res = requests.get(url, timeout=20)
            if res.status_code == 200:
                found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', res.text)
                for c in found:
                    clean = c.strip().replace('\r', '').replace('`', '').replace('"', '')
                    # Проверка на дубликаты по ссылке
                    base_link = clean.split('#')[0]
                    if base_link not in unique_cfgs:
                        unique_cfgs[base_link] = (clean, url)
        except: pass

    if not unique_cfgs: return print("😿 Источники пусты.")

    # Сортировка VLESS в начало
    sorted_items = sorted(unique_cfgs.values(), key=lambda x: (0 if x[0].startswith('vless://') else 1, x[0]))
    
    final_list = []
    counts = {"EtoNeYa": 1, "igareck": 1, "RKP": 1, "FCH": 1, "Other": 1}

    # Инфо-строка
    now_str = datetime.now().strftime('%d.%m %H:%M')
    info_tag = f"REMARK=🐈 Всего: {len(sorted_items)} | Обновлено: {now_str}"
    final_list.append(f"vless://00000000-0000-0000-0000-000000000000@0.0.0.0:443?encryption=none&type=tcp#{info_tag}")

    for cfg, src in sorted_items:
        if '#' in cfg:
            base, old_name_raw = cfg.rsplit('#', 1)
            old_name = urllib.parse.unquote(old_name_raw)
        else:
            base, old_name = cfg, ""

        if "etoneya" in src: auth = "EtoNeYa"
        elif "igareck" in src: auth = "igareck"
        elif "RKP" in src: auth = "RKP"
        elif "Ilyacom4ik" in src: auth = "FCH"
        else: auth = "Other"

        display_name = get_name(old_name, auth)
        
        if "anycast" in old_name.lower(): 
            name = "🌐 Anycast"
        elif auth == "RKP":
            name = f"🛡#RKP {counts[auth]}"
            counts[auth] += 1
        elif display_name:
            name = display_name
        else:
            name = f"Обход {counts[auth]}"
            counts[auth] += 1

        final_list.append(f"{base}#{name} | {auth} | Ваш котенок ❤")

    res_text = "\n".join(final_list)
    with open("subscription.txt", "w", encoding="utf-8") as f: f.write(res_text)
    with open("subscription_b64.txt", "w", encoding="utf-8") as f:
        f.write(base64.b64encode(res_text.encode()).decode())
    
    print(f"✅ Готово! Собрано: {len(final_list)}")

if __name__ == "__main__":
    parse()
