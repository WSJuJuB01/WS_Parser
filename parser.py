import requests
import re
import urllib.parse
import base64
import concurrent.futures
from datetime import datetime

# ТВОИ SOURCES 🐾
SOURCES = [
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://githubusercontent.com",
    "https://vercel.app"
]

# Словарь стран (ищем ключи в названии)
COUNTRY_MAP = {
    "russia": "🇷🇺 Russia", "germany": "🇩🇪 Germany", "netherlands": "🇳🇱 Netherlands",
    "usa": "🇺🇸 USA", "united states": "🇺🇸 USA", "uk": "🇬🇧 UK", 
    "finland": "🇫🇮 Finland", "poland": "🇵🇱 Poland", "turkey": "🇹🇷 Turkey",
    "france": "🇫🇷 France", "kazakhstan": "🇰🇿 Kazakhstan", "ukraine": "🇺🇦 Ukraine",
    "singapore": "🇸🇬 Singapore", "japan": "🇯🇵 Japan", "sweden": "🇸🇪 Sweden",
    "austria": "🇦🇹 Austria"
}

class FinalCorrectParser:
    def __init__(self):
        self.raw_data = []
        self.headers = {'User-Agent': 'Mozilla/5.0'}

    def get_author(self, url):
        if "etoneya" in url: return "EtoNeYa"
        if "igareck" in url: return "igareck"
        if "RKP" in url: return "RKP"
        if "Ilyacom4ik" in url: return "FCH"
        return "Dev"

    def get_pretty_country(self, old_name):
        low_name = old_name.lower()
        for key, formatted in COUNTRY_MAP.items():
            if key in low_name:
                return formatted
        # Если текста нет, ищем флаги-эмодзи
        flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', old_name)
        return "".join(flags) if flags else None

    def fetch(self, url):
        try:
            res = requests.get(url, headers=self.headers, timeout=20)
            if res.status_code == 200:
                return res.text, url
        except: return None, url

    def process(self):
        # 1. Скачиваем всё
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            results = list(executor.map(self.fetch, SOURCES))

        for content, url in results:
            if not content: continue
            author = self.get_author(url)
            found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
            
            for cfg in found:
                cfg = cfg.strip().replace('`', '').replace('"', '').replace('\r', '')
                if '#' in cfg:
                    link, raw_n = cfg.rsplit('#', 1)
                    old_name = urllib.parse.unquote(raw_n)
                else:
                    link, old_name = cfg, ""
                
                self.raw_data.append({"link": link, "old_name": old_name, "author": author})

        # 2. Сортировка (VLESS в начало)
        self.raw_data.sort(key=lambda x: 0 if x["link"].startswith('vless') else 1)

        # 3. Финальная сборка с раздельными счетчиками
        final_list = []
        rkp_counter = 1
        other_counter = 1

        for item in self.raw_data:
            country = self.get_pretty_country(item["old_name"])
            
            if item["author"] == "RKP":
                # Считаем ТОЛЬКО RKP
                name = f"🛡 RKP #{rkp_counter}"
                rkp_counter += 1
            elif country:
                name = country
            else:
                # Если страну не нашли, ставим номер для "прочих"
                name = f"Node #{other_counter}"
                other_counter += 1

            final_list.append(f"{item['link']}#{name} | {item['author']} | Ваш котенок ❤")

        # 4. Шапка
        now = datetime.now().strftime('%d.%m %H:%M')
        final_list.insert(0, f"vless://00000000-0000-0000-0000-000000000000@0.0.0.0:443?encryption=none&type=tcp#REMARK=🐈 Собрано: {len(final_list)} | {now}")

        # 5. Сохранение
        output = "\n".join(final_list)
        with open("subscription.txt", "w", encoding="utf-8") as f: f.write(output)
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(output.encode()).decode())
        
        print(f"✅ Готово! RKP пронумерованы отдельно.")

if __name__ == "__main__":
    FinalCorrectParser().process()
