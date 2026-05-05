import requests
import re
import urllib.parse
import base64
import concurrent.futures
from datetime import datetime

# ==========================================
# 🌐 ТВОИ ИСТОЧНИКИ (SOURCES)
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+ALL_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/ilyacom41k/free-v2ray-2025/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

# ==========================================
# 🚩 ПОЛНАЯ БАЗА ФЛАГОВ (чтобы не было "Location")
# ==========================================
FLAG_DB = {
    "🇦🇫": "Afghanistan", "🇦🇱": "Albania", "🇩🇿": "Algeria", "🇦🇸": "American Samoa", "🇦🇩": "Andorra", "🇦🇴": "Angola", "🇦🇮": "Anguilla",
    "🇦🇶": "Antarctica", "🇦🇬": "Antigua", "🇦🇷": "Argentina", "🇦🇲": "Armenia", "🇦🇼": "Aruba", "🇦🇺": "Australia", "🇦🇹": "Austria",
    "🇦🇿": "Azerbaijan", "🇧🇸": "Bahamas", "🇧🇭": "Bahrain", "🇧🇩": "Bangladesh", "🇧🇧": "Barbados", "🇧🇾": "Belarus", "🇧🇪": "Belgium",
    "🇧🇿": "Belize", "🇧🇯": "Benin", "🇧🇲": "Bermuda", "🇧🇹": "Bhutan", "🇧🇴": "Bolivia", "🇧🇦": "Bosnia", "🇧🇼": "Botswana",
    "🇧🇷": "Brazil", "🇻🇬": "British Virgin Islands", "🇧🇳": "Brunei", "🇧🇬": "Bulgaria", "🇧🇫": "Burkina Faso", "🇧🇮": "Burundi",
    "🇰🇭": "Cambodia", "🇨🇲": "Cameroon", "🇨🇦": "Canada", "🇨🇻": "Cape Verde", "🇰🇾": "Cayman Islands", "🇨🇫": "Central African Republic",
    "🇹🇩": "Chad", "🇨🇱": "Chile", "🇨🇳": "China", "🇷🇺": "Russia", "🇩🇪": "Germany", "🇺🇸": "USA", "🇫🇷": "France", "🇬🇧": "UK",
    "🇳🇱": "Netherlands", "🇰🇿": "Kazakhstan", "🇹🇷": "Turkey", "🇵🇱": "Poland", "🇪🇸": "Spain", "🇮🇹": "Italy", "🇯🇵": "Japan"
}

WHITE_SNI_LIST = [
    "gosuslugi.ru", "gu-st.ru", "gov.ru", "nalog.ru", "mos.ru", "vk.com", "ok.ru", "mail.ru",
    "yandex.ru", "ya.ru", "dzen.ru", "kinopoisk.ru", "sberbank.ru", "sber.ru", "vtb.ru",
    "tinkoff.ru", "tbank.ru", "ozon.ru", "wildberries.ru", "avito.ru", "rutube.ru"
]

class UltraParser:
    def __init__(self, sources):
        self.sources = sources
        self.buckets = {"EtoNeYa": [], "RKP": [], "igarek": [], "FCH": [], "Other": []}
        self.rkp_counter = 1
        self.etoneya_counter = 1

    def get_author_label(self, url):
        u = url.lower()
        if "etoneya" in u: return "EtoNeYa"
        if "igareck" in u or "igarek" in u: return "igarek" # Починил игорька
        if "rkp" in u: return "RKP"
        if "ilyacom41k" in u: return "FCH"
        return "Other"

    def decode_display_name(self, raw_name, link, author):
        # 1. EtoNeYa: White Lists БЕЗ решетки
        if author == "EtoNeYa":
            name = f"🏳️ White Lists {self.etoneya_counter}"
            self.etoneya_counter += 1
            return name

        is_white_sni = any(sni in (link + raw_name).lower() for sni in WHITE_SNI_LIST)

        # 2. RKP: Щит в начале + Спутник
        if author == "RKP":
            base_name = f"🛡️ RKP #{self.rkp_counter} 🛰️"
            self.rkp_counter += 1
            return f"{base_name} 🏳️" if is_white_sni else base_name

        # 3. Остальные (Игорек, FCH и др.): Флаг + Страна
        found_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', raw_name)
        if found_flags:
            flag = found_flags[0]
            country = FLAG_DB.get(flag, "Location")
            return f"{flag} {country} 🏳️" if is_white_sni else f"{flag} {country}"
        
        return "🌐 Unknown 🏳️" if is_white_sni else "🌐 Unknown"

    def fetch_and_parse(self, url):
        try:
            res = requests.get(url, timeout=15)
            if res.status_code != 200: return
            author = self.get_author_label(url)
            links = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s<>]+', res.text)
            for l in links:
                clean_link = l.split("#")[0] # Чистим старые названия
                raw_name = urllib.parse.unquote(l.split("#")[1]) if "#" in l else ""
                self.buckets[author].append({"link": clean_link, "name": raw_name})
        except:
            pass

    def run(self):
        print("🚀 Генерация подписки для Nekobox (с правками для RKP и Игорька)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            ex.map(self.fetch_and_parse, self.sources)

        final_list = []
        auth_order = ["EtoNeYa", "RKP", "igarek", "FCH", "Other"]

        while any(self.buckets[a] for a in auth_order):
            for a in auth_order:
                chunk = self.buckets[a][:10]
                self.buckets[a] = self.buckets[a][10:]
                for item in chunk:
                    display = self.decode_display_name(item["name"], item["link"], a)
                    # Формат: [флаг] [страна] | [автор] | [приписка]
                    full_name = f"{display} | {a} | Ваш котенок ❤️"
                    safe_name = urllib.parse.quote(full_name)
                    final_list.append(f"{item['link']}#{safe_name}")

        if final_list:
            content = "\n".join(final_list)
            with open("subscription.txt", "w", encoding="utf-8") as f:
                f.write(content)
            with open("subscription_b64.txt", "w", encoding="utf-8") as f:
                f.write(base64.b64encode(content.encode()).decode())
            print(f"✅ Успешно собрано {len(final_list)} конфигов!")

if __name__ == "__main__":
    UltraParser(SOURCES).run()
