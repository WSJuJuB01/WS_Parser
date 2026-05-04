import requests
import re
import urllib.parse
import base64
import concurrent.futures
import os

SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/1",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/whitelist"
]

class UltraParser:
    def __init__(self, sources):
        self.sources = sources
        self.buckets = {
            "EtoNeYa": [],
            "RKP": [],
            "igarek": [],
            "FCH": [],
            "Other": []
        }
        self.etoneya_counter = 0
        self.rkp_counter = 0

    def get_author_label(self, url):
        url_lower = url.lower()
        if "etoneya" in url_lower: return "EtoNeYa"
        if "igareck" in url_lower: return "igarek"
        if "rkp" in url_lower: return "RKP"
        if "ilyacom4ik" in url_lower: return "FCH"
        return "Other"

    def decode_display_name(self, raw_name, link, author, url=""):
        full_text = f"{raw_name} {link}".lower()

        if author == "EtoNeYa":
            if url and "whitelist" in url:
                self.etoneya_counter += 1
                return f"🏳 White lists #{self.etoneya_counter} | EtoNeYa", "котенок"

            if url and url.endswith("/1"):
                if "youtube" in full_text:
                    return "📺 YouTube🔴 | EtoNeYa", "котенок"
                if "cloudflare" in full_text:
                    return "☁️ Cloudflare | EtoNeYa", "котенок"
                if any(x in full_text for x in ["gemini", "bard", "google ai", "ai"]):
                    return "🤖✨ Gemini | EtoNeYa", "котенок"
                return None, None

            self.etoneya_counter += 1
            return f"💎 Config #{self.etoneya_counter} | EtoNeYa", "котенок"

        if author == "RKP":
            self.rkp_counter += 1
            return f"🛡️ RKP #{self.rkp_counter}", "котенок"

        return raw_name, "котенок"

    def fetch_and_parse(self, url):
        try:
            response = requests.get(url, timeout=15)
            if response.status_code != 200: return
            
            author = self.get_author_label(url)
            # Ищем ссылки целиком (без групп в регулярке, чтобы findall вернул строку)
            pattern = r'(?:vless|vmess|ss|trojan)://[^\s,|<]+'
            found_links = re.findall(pattern, response.text)

            for full_link in found_links:
                name = ""
                clean_link = full_link
                if "#" in full_link:
                    parts = full_link.split("#", 1)
                    clean_link = parts[0]
                    name = urllib.parse.unquote(parts[1])
                
                if clean_link:
                    self.buckets[author].append({
                        "name": name,
                        "link": clean_link,
                        "url": url
                    })
        except Exception as e:
            print(f"Ошибка при загрузке {url}: {e}")

    def run(self):
        print("🚀 Нарезаем торт...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
            executor.map(self.fetch_and_parse, self.sources)

        authors_order = ["EtoNeYa", "RKP", "igarek", "FCH", "Other"]
        final_list = []

        while any(len(b) > 0 for b in self.buckets.values()):
            for author in authors_order:
                chunk = self.buckets[author][:10]
                self.buckets[author] = self.buckets[author][10:]

                for item in chunk:
                    res = self.decode_display_name(
                        item["name"], 
                        item["link"], 
                        author, 
                        url=item["url"]
                    )
                    
                    if res is None:
                        continue
                    
                    display_name, cat_type = res
                    # Сборка: полная ссылка + # + наше имя + приписка
                    final_list.append(f"{item['link']}#{display_name} | Ваш {cat_type} ❤️")

                if final_list:
            # 1. Обычный список (для чтения)
            combined_string = "\n".join(final_list)
            with open("subscription.txt", "w", encoding="utf-8") as f:
                f.write(combined_string)

            # 2. Base64 версия (для программ)
            encoded_content = base64.b64encode(combined_string.encode('utf-8')).decode('utf-8')
            with open("subscription_b64.txt", "w", encoding="utf-8") as f:
                f.write(encoded_content)
            
            print(f"✅ Файлы обновлены: {len(final_list)} конфигов")
        else:
            print("❌ Список пуст, файлы не перезаписаны")
