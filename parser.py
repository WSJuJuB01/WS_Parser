import requests
import re
import urllib.parse
import base64
import concurrent.futures
from datetime import datetime

# ==========================================
# ТВОИ SOURCES 🛰️ (Добавил новые протоколы в проверку)
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS-all_RUS.txt",
    "https://raw.githubusercontent.com/RKPChannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/ilyacom41k/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.a9fm.site/whitelist"
]

FLAG_DB = {
    "🇦🇫": "Afghanistan", "🇦🇱": "Albania", "🇩🇿": "Algeria", "🇦🇸": "American Samoa", "🇦🇩": "Andorra", "🇦🇴": "Angola", "🇦🇮": "Anguilla", "🇦🇶": "Antarctica", "🇦🇬": "Antigua", "🇦🇷": "Argentina", "🇦🇲": "Armenia", "🇦🇼": "Aruba", "🇦🇺": "Australia", "🇦🇹": "Austria", "🇦🇿": "Azerbaijan", "🇧🇸": "Bahamas", "🇧🇭": "Bahrain", "🇧🇩": "Bangladesh", "🇧🇧": "Barbados", "🇧🇾": "Belarus", "🇧🇪": "Belgium", "🇧🇿": "Belize", "🇧🇳": "Benin", "🇧🇲": "Bermuda", "🇧🇹": "Bhutan", "🇧🇴": "Bolivia", "🇧🇦": "Bosnia", "🇧🇼": "Botswana", "🇧🇷": "Brazil", "🇻🇬": "British Virgin Islands", "🇧🇳": "Brunei", "🇧🇬": "Bulgaria", "🇧🇫": "Burkina Faso", "🇧🇮": "Burundi", "🇰🇭": "Cambodia", "🇨🇲": "Cameroon", "🇨🇦": "Canada", "🇨🇻": "Cape Verde", "🇰🇾": "Cayman Islands", "🇨🇫": "Central African Republic", "🇹🇩": "Chad", "🇨🇱": "Chile", "🇨🇳": "China", "🇨🇴": "Colombia", "🇰🇲": "Comoros", "🇨🇬": "Congo", "🇨🇰": "Cook Islands", "🇨🇷": "Costa Rica", "🇭🇷": "Croatia", "🇨🇺": "Cuba", "🇨🇾": "Cyprus", "🇨🇿": "Czechia", "🇩🇰": "Denmark", "🇩🇯": "Djibouti", "🇩🇲": "Dominica", "🇩🇴": "Dominican Republic", "🇪🇨": "Ecuador", "🇪🇬": "Egypt", "🇸🇻": "El Salvador", "🇬🇶": "Equatorial Guinea", "🇪🇷": "Eritrea", "🇪🇪": "Estonia", "🇪🇹": "Ethiopia", "🇫🇯": "Fiji", "🇫🇮": "Finland", "🇫🇷": "France", "🇬🇦": "Gabon", "🇬🇲": "Gambia", "🇬🇪": "Georgia", "🇩🇪": "Germany", "🇬🇭": "Ghana", "🇬🇮": "Gibraltar", "🇬🇷": "Greece", "🇬🇱": "Greenland", "🇬🇩": "Grenada", "🇬🇵": "Guadeloupe", "🇬🇺": "Guam", "🇬🇹": "Guatemala", "🇬🇳": "Guinea", "🇬🇼": "Guinea-Bissau", "🇬🇾": "Guyana", "🇭🇹": "Haiti", "🇭🇳": "Honduras", "🇭🇰": "Hong Kong", "🇭🇺": "Hungary", "🇮🇸": "Iceland", "🇮🇳": "India", "🇮🇩": "Indonesia", "🇮🇷": "Iran", "🇮🇶": "Iraq", "🇮🇪": "Ireland", "🇮🇲": "Isle of Man", "🇮🇱": "Israel", "🇮🇹": "Italy", "🇯🇲": "Jamaica", "🇯🇵": "Japan", "🇯🇪": "Jersey", "🇯🇴": "Jordan", "🇰🇿": "Kazakhstan", "🇰🇪": "Kenya", "🇰🇮": "Kiribati", "🇰🇼": "Kuwait", "🇰🇬": "Kyrgyzstan", "🇱🇦": "Laos", "🇱🇻": "Latvia", "🇱🇧": "Lebanon", "🇱🇸": "Lesotho", "🇱🇷": "Liberia", "🇱🇾": "Libya", "🇱🇮": "Liechtenstein", "🇱🇹": "Lithuania", "🇱🇺": "Luxembourg", "🇲🇴": "Macau", "🇲🇰": "Macedonia", "🇲🇬": "Madagascar", "🇲🇼": "Malawi", "🇲🇾": "Malaysia", "🇲🇻": "Maldives", "🇲🇱": "Mali", "🇲🇹": "Malta", "🇲🇭": "Marshall Islands", "🇲🇶": "Martinique", "🇲🇷": "Mauritania", "🇲🇺": "Mauritius", "🇲🇽": "Mexico", "🇫🇲": "Micronesia", "🇲🇩": "Moldova", "🇲🇨": "Monaco", "🇲🇳": "Mongolia", "🇲🇪": "Montenegro", "🇲🇸": "Montserrat", "🇲🇦": "Morocco", "🇲🇿": "Mozambique", "🇲🇲": "Myanmar", "🇳🇦": "Namibia", "🇳🇷": "Nauru", "🇳🇵": "Nepal", "🇳🇱": "Netherlands", "🇳🇨": "New Caledonia", "🇳🇿": "New Zealand", "🇳🇮": "Nicaragua", "🇳🇪": "Niger", "🇳🇬": "Nigeria", "🇳🇺": "Niue", "🇳🇫": "Norfolk Island", "🇲🇵": "Northern Mariana Islands", "🇰🇵": "North Korea", "🇳🇴": "Norway", "🇴🇲": "Oman", "🇵🇰": "Pakistan", "🇵🇼": "Palau", "🇵🇸": "Palestine", "🇵🇦": "Panama", "🇵🇬": "Papua New Guinea", "🇵🇾": "Paraguay", "🇵🇪": "Peru", "🇵🇭": "Philippines", "🇵🇳": "Pitcairn Islands", "🇵🇱": "Poland", "🇵🇹": "Portugal", "🇵🇷": "Puerto Rico", "🇶🇦": "Qatar", "🇷🇪": "Reunion", "🇷🇴": "Romania", "🇷🇺": "Russia", "🇷🇼": "Rwanda", "🇼🇸": "Samoa", "🇸🇲": "San Marino", "🇸🇹": "Sao Tome", "🇸🇦": "Saudi Arabia", "🇸🇳": "Senegal", "🇷🇸": "Serbia", "🇸🇨": "Seychelles", "🇸🇱": "Sierra Leone", "🇸🇬": "Singapore", "🇸🇽": "Sint Maarten", "🇸🇰": "Slovakia", "🇸🇮": "Slovenia", "🇸🇧": "Solomon Islands", "🇸🇴": "Somalia", "🇿🇦": "South Africa", "🇰🇷": "South Korea", "🇸🇸": "South Sudan", "🇪🇸": "Spain", "🇱🇰": "Sri Lanka", "🇸🇩": "Sudan", "🇸🇷": "Suriname", "🇸🇿": "Swaziland", "🇸🇪": "Sweden", "🇨🇭": "Switzerland", "🇸🇾": "Syria", "🇹🇼": "Taiwan", "🇹🇯": "Tajikistan", "🇹🇿": "Tanzania", "🇹🇭": "Thailand", "🇹🇱": "Timor-Leste", "🇹🇬": "Togo", "🇹🇰": "Tokelau", "🇹🇴": "Tonga", "🇹🇹": "Trinidad", "🇹🇳": "Tunisia", "🇹🇷": "Turkey", "🇹🇲": "Turkmenistan", "🇹🇨": "Turks and Caicos", "🇹🇻": "Tuvalu", "🇺🇬": "Uganda", "🇺🇦": "Ukraine", "🇦🇪": "UAE", "🇬🇧": "UK", "🇺🇸": "USA", "🇺🇾": "Uruguay", "🇺🇿": "Uzbekistan", "🇻🇺": "Vanuatu", "🇻🇦": "Vatican City", "🇻🇪": "Venezuela", "🇻🇳": "Vietnam", "🇼🇫": "Wallis and Futuna", "🇪🇭": "Western Sahara", "🇾🇪": "Yemen", "🇿🇲": "Zambia", "🇿🇼": "Zimbabwe"
}

WHITE_SNI_LIST = [
    "gosuslugi.ru", "gu-st.ru", "gov.ru", "nalog.ru", "mos.ru", "pfr.ru", "zakupki.gov.ru", "kremlin.ru",
    "vk.com", "vkvideo.ru", "ok.ru", "my.games", "mail.ru", "tamtam.chat", "vk-portal.ru",
    "yandex.ru", "ya.ru", "dzen.ru", "kinopoisk.ru", "music.yandex.ru", "yandex.net", "zen.yandex.ru",
    "sberbank.ru", "sber.ru", "vtb.ru", "tinkoff.ru", "alfa-bank.ru", "raiffeisen.ru", "rshb.ru", "gazprombank.ru",
    "ozon.ru", "wildberries.ru", "avito.ru", "market.yandex.ru", "lamoda.ru", "aliexpress.ru", "magnit.ru",
    "rutube.ru", "itv.ru", "vgtrk.ru", "smotrim.ru", "ntv.ru", "russia.tv", "max.ru", "vmp-vless.ru",
    "ads.x5.ru", "x5.ru", "rzd.ru", "tutu.ru", "yandex.st", "yastatic.net", "delivery-club.ru", "yandex.maps"
]

class UltraParser:
    def __init__(self, sources):
        self.sources = sources
        self.buckets = {"EtoNeYa": [], "RKP": [], "igareck": [], "FCH": [], "Other": []}
        self.rkp_counter = 1
        self.etoneya_counter = 1

    def get_author_label(self, url):
        u = url.lower()
        if "etoneya" in u: return "EtoNeYa"
        if "igareck" in u: return "igareck"
        if "rkp" in u: return "RKP"
        if "ilyacom41k" in u: return "FCH"
        return "Other"

    def decode_display_name(self, raw_name, link, author):
        if author == "EtoNeYa":
            name = f"🏳️ White lists {self.etoneya_counter}"
            self.etoneya_counter += 1
            return name

        is_white_sni = any(sni in (link + raw_name).lower() for sni in WHITE_SNI_LIST)

        if author == "RKP":
            base_name = f"🛡️ RKP #{self.rkp_counter}"
            self.rkp_counter += 1
            return f"🏳️ {base_name}" if is_white_sni else base_name

        found_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', raw_name)
        if found_flags:
            flag = found_flags[0]
            country = FLAG_DB.get(flag, "Location")
            res = f"{flag} {country}"
        elif "anycast" in raw_name.lower():
            res = "🌐 Anycast"
        else:
            res = "🌐 Unknown"

        return f"{res} 🏳️" if is_white_sni else res

    def fetch_and_parse(self, url):
        try:
            res = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
            if res.status_code != 200: return
            
            content = res.text
            # Проверка на Base64 (если весь файл зашифрован)
            if not any(proto in content for proto in ["vless://", "ss://", "vmess://", "trojan://"]):
                try:
                    content = base64.b64decode(content).decode('utf-8')
                except: pass

            author = self.get_author_label(url)
            # Жадная регулярка: забирает всё до конца строки, включая новые протоколы
            links = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2)://[^\r\n\t\s]+', content)
            
            for l in links:
                l = l.strip()
                if "#" in l:
                    parts = l.split("#", 1)
                    clean_link = parts[0]
                    raw_name = urllib.parse.unquote(parts[1])
                else:
                    clean_link = l
                    raw_name = ""
                
                if clean_link:
                    self.buckets[author].append({"link": clean_link, "name": raw_name})
        except Exception as e:
            print(f"❌ Ошибка на {url}: {e}")

    def run(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🚀 Поиск потерянных конфигов Игорька...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            ex.map(self.fetch_and_parse, self.sources)

        final_list = []
        auth_order = ["EtoNeYa", "RKP", "igareck", "FCH", "Other"]

        while any(self.buckets[a] for a in auth_order):
            for a in auth_order:
                chunk = self.buckets[a][:10]
                self.buckets[a] = self.buckets[a][10:]
                for item in chunk:
                    display = self.decode_display_name(item["name"], item["link"], a)
                    safe_display = urllib.parse.quote(f"{display} | WSVPN 🐈‍⬛")
                    final_list.append(f"{item['link']}#{safe_display}")

        if final_list:
            content = "\n".join(final_list)
            with open("subscription.txt", "w", encoding="utf-8") as f:
                f.write(content)
            
            b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            with open("subscription_b64.txt", "w", encoding="utf-8") as f:
                f.write(b64_content)
            print(f"✅ Успех! Собрано: {len(final_list)} конфигов.")
        else:
            print("🛑 Пусто! Проверь источники вручную.")

if __name__ == "__main__":
    parser = UltraParser(SOURCES)
    parser.run()
)
    parser.run()
