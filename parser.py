import requests
import re
import urllib.parse
import base64
import concurrent.futures
from datetime import datetime

# ==========================================
# 🌐 ТВОИ SOURCES
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://etoneya.vercel.app/whitelist"
]

# ==========================================
# 💎 ПОЛНАЯ БАЗА ФЛАГОВ МИРА
# ==========================================
FLAG_DB = {
    "🇦🇫": "Afghanistan", "🇦🇱": "Albania", "🇩🇿": "Algeria", "🇦🇸": "American Samoa", "🇦🇩": "Andorra", "🇦🇴": "Angola", "🇦🇮": "Anguilla",
    "🇦🇶": "Antarctica", "🇦🇬": "Antigua", "🇦🇷": "Argentina", "🇦🇲": "Armenia", "🇦🇼": "Aruba", "🇦🇺": "Australia", "🇦🇹": "Austria",
    "🇦🇿": "Azerbaijan", "🇧🇸": "Bahamas", "🇧🇭": "Bahrain", "🇧🇩": "Bangladesh", "🇧🇧": "Barbados", "🇧🇾": "Belarus", "🇧🇪": "Belgium",
    "🇧🇿": "Belize", "🇧🇯": "Benin", "🇧🇲": "Bermuda", "🇧🇹": "Bhutan", "🇧🇴": "Bolivia", "🇧🇦": "Bosnia", "🇧🇼": "Botswana", "🇧🇷": "Brazil",
    "🇻🇬": "British Virgin Islands", "🇧🇳": "Brunei", "🇧🇬": "Bulgaria", "🇧🇫": "Burkina Faso", "🇧🇮": "Burundi", "🇰🇭": "Cambodia",
    "🇨🇲": "Cameroon", "🇨🇦": "Canada", "🇨🇻": "Cape Verde", "🇰🇾": "Cayman Islands", "🇨🇫": "Central African Republic", "🇹🇩": "Chad",
    "🇨🇱": "Chile", "🇨🇳": "China", "🇨🇴": "Colombia", "🇰🇲": "Comoros", "🇨🇬": "Congo", "🇨🇰": "Cook Islands", "🇨🇷": "Costa Rica",
    "🇭🇷": "Croatia", "🇨🇺": "Cuba", "🇨🇾": "Cyprus", "🇨🇿": "Czechia", "🇩🇰": "Denmark", "🇩🇯": "Djibouti", "🇩🇲": "Dominica",
    "🇩🇴": "Dominican Republic", "🇪🇨": "Ecuador", "🇪🇬": "Egypt", "🇸🇻": "El Salvador", "🇬🇶": "Equatorial Guinea", "🇪🇷": "Eritrea",
    "🇪🇪": "Estonia", "🇪🇹": "Ethiopia", "🇫🇯": "Fiji", "🇫🇮": "Finland", "🇫🇷": "France", "🇬🇦": "Gabon", "🇬🇲": "Gambia", "🇬🇪": "Georgia",
    "🇩🇪": "Germany", "🇬🇭": "Ghana", "🇬🇮": "Gibraltar", "🇬🇷": "Greece", "🇬🇱": "Greenland", "🇬🇩": "Grenada", "🇬🇵": "Guadeloupe",
    "🇬🇺": "Guam", "🇬🇹": "Guatemala", "🇬🇬": "Guernsey", "🇬🇳": "Guinea", "🇬🇼": "Guinea-Bissau", "🇬🇾": "Guyana", "🇭🇹": "Haiti",
    "🇭🇳": "Honduras", "🇭🇰": "Hong Kong", "🇭🇺": "Hungary", "🇮🇸": "Iceland", "🇮🇳": "India", "🇮🇩": "Indonesia", "🇮🇷": "Iran",
    "🇮🇶": "Iraq", "🇮🇪": "Ireland", "🇮🇲": "Isle of Man", "🇮🇱": "Israel", "🇮🇹": "Italy", "🇯🇲": "Jamaica", "🇯🇵": "Japan", "🇯🇪": "Jersey",
    "🇯🇴": "Jordan", "🇰🇿": "Kazakhstan", "🇰🇪": "Kenya", "🇰🇮": "Kiribati", "🇰🇼": "Kuwait", "🇰🇬": "Kyrgyzstan", "🇱🇦": "Laos",
    "🇱🇻": "Latvia", "🇱🇧": "Lebanon", "🇱🇸": "Lesotho", "🇱🇷": "Liberia", "🇱🇾": "Libya", "🇱🇮": "Liechtenstein", "🇱🇹": "Lithuania",
    "🇱🇺": "Luxembourg", "🇲🇴": "Macao", "🇲🇰": "Macedonia", "🇲🇬": "Madagascar", "🇲🇼": "Malawi", "🇲🇾": "Malaysia", "🇲🇻": "Maldives",
    "🇲🇱": "Mali", "🇲🇹": "Malta", "🇲🇭": "Marshall Islands", "🇲🇶": "Martinique", "🇲🇷": "Mauritania", "🇲🇺": "Mauritius", "🇲🇽": "Mexico",
    "🇫🇲": "Micronesia", "🇲🇩": "Moldova", "🇲🇨": "Monaco", "🇲🇳": "Mongolia", "🇲🇪": "Montenegro", "🇲🇸": "Montserrat", "🇲🇦": "Morocco",
    "🇲🇿": "Mozambique", "🇲🇲": "Myanmar", "🇳🇦": "Namibia", "🇳🇷": "Nauru", "🇳🇵": "Nepal", "🇳🇱": "Netherlands", "🇳🇨": "New Caledonia",
    "🇳🇿": "New Zealand", "🇳🇮": "Nicaragua", "🇳🇪": "Niger", "🇳🇬": "Nigeria", "🇳🇺": "Niue", "🇳🇫": "Norfolk Island", "🇰🇵": "North Korea",
    "🇲🇵": "Northern Mariana Islands", "🇳🇴": "Norway", "🇴🇲": "Oman", "🇵🇰": "Pakistan", "🇵🇼": "Palau", "🇵🇸": "Palestine", "🇵🇦": "Panama",
    "🇵🇬": "Papua New Guinea", "🇵🇾": "Paraguay", "🇵🇪": "Peru", "🇵🇭": "Philippines", "🇵🇳": "Pitcairn Islands", "🇵🇱": "Poland",
    "🇵🇹": "Portugal", "🇵🇷": "Puerto Rico", "🇶🇦": "Qatar", "🇷🇪": "Reunion", "🇷🇴": "Romania", "🇷🇺": "Russia", "🇷🇼": "Rwanda",
    "🇼🇸": "Samoa", "🇸🇲": "San Marino", "🇸🇹": "Sao Tome", "🇸🇦": "Saudi Arabia", "🇸🇳": "Senegal", "🇷🇸": "Serbia", "🇸🇨": "Seychelles",
    "🇸🇱": "Sierra Leone", "🇸🇬": "Singapore", "🇸🇽": "Sint Maarten", "🇸🇰": "Slovakia", "🇸🇮": "Slovenia", "🇸🇧": "Solomon Islands",
    "🇸🇴": "Somalia", "🇿🇦": "South Africa", "🇰🇷": "South Korea", "🇸🇸": "South Sudan", "🇪🇸": "Spain", "🇱🇰": "Sri Lanka", "🇸🇩": "Sudan",
    "🇸🇷": "Suriname", "🇸🇿": "Swaziland", "🇸🇪": "Sweden", "🇨🇭": "Switzerland", "🇸🇾": "Syria", "🇹🇼": "Taiwan", "🇹🇯": "Tajikistan",
    "🇹🇿": "Tanzania", "🇹🇭": "Thailand", "🇹🇱": "Timor-Leste", "🇹🇬": "Togo", "🇹🇰": "Tokelau", "🇹🇴": "Tonga", "🇹🇹": "Trinidad",
    "🇹🇳": "Tunisia", "🇹🇷": "Turkey", "🇹🇲": "Turkmenistan", "🇹🇨": "Turks and Caicos", "🇹🇻": "Tuvalu", "🇺🇬": "Uganda", "🇺🇦": "Ukraine",
    "🇦🇪": "UAE", "🇬🇧": "UK", "🇺🇸": "USA", "🇺🇾": "Uruguay", "🇺🇿": "Uzbekistan", "🇻🇺": "Vanuatu", "🇻🇦": "Vatican City", "🇻🇪": "Venezuela",
    "🇻🇳": "Vietnam", "🇼🇫": "Wallis and Futuna", "🇪🇭": "Western Sahara", "🇾🇪": "Yemen", "🇿🇲": "Zambia", "🇿🇼": "Zimbabwe"
}

# ==========================================
# 🛡️ ТОТАЛЬНЫЙ БЕЛЫЙ СПИСОК SNI
# ==========================================
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
        if "igareck" in u: return "igarek"
        if "rkp" in u: return "RKP"
        if "ilyacom4ik" in u: return "FCH"
        return "Other"

    def decode_display_name(self, raw_name, link, author, source_url):
        # 1. ПРАВИЛО: Все от EtoNeYa — это White lists
        if author == "EtoNeYa":
            name = f"🏳 White lists #{self.etoneya_counter}"
            self.etoneya_counter += 1
            return name

        # 2. ПРАВИЛО: Проверка на Белый Список по SNI
        is_white_sni = any(sni in (link + raw_name).lower() for sni in WHITE_SNI_LIST)
        
        # 3. Кастомная логика для RKP
        if author == "RKP":
            base_name = f"🛡️ RKP #{self.rkp_counter}"
            self.rkp_counter += 1
            return f"{base_name} 🏳" if is_white_sni else base_name

        # 4. Логика стран (Игорек, FCH и др.)
        found_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', raw_name)
        if found_flags:
            flag = found_flags[0]
            country = FLAG_DB.get(flag, "Location")
            # Белый флаг СЗАДИ флага страны
            if is_white_sni:
                return f"{flag} 🏳 {country}"
            return f"{flag} {country}"
        else:
            return "🌐 🏳 Unknown" if is_white_sni else "🌐 Unknown"

    def fetch_and_parse(self, url):
        try:
            res = requests.get(url, timeout=15)
            if res.status_code != 200: return
            author = self.get_author_label(url)
            links = re.findall(r'(?:vless|vmess|ss|trojan)://[^\s,|<]+', res.text)
            for l in links:
                clean_link = l.split("#")[0]
                raw_name = urllib.parse.unquote(l.split("#")[1]) if "#" in l else ""
                self.buckets[author].append({"link": clean_link, "name": raw_name, "source": url})
        except: pass

    def run(self):
        print("🚀 Старт ремейка с флагом сзади...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=20) as ex:
            ex.map(self.fetch_and_parse, self.sources)

        final_list = []
        auth_order = ["EtoNeYa", "RKP", "igarek", "FCH", "Other"]
        
        while any(self.buckets[a] for a in auth_order):
            for a in auth_order:
                chunk = self.buckets[a][:10]
                self.buckets[a] = self.buckets[a][10:]
                for item in chunk:
                    display = self.decode_display_name(item["name"], item["link"], a, item["source"])
                    final_list.append(f"{item['link']}#{display} | {a} | Ваш котенок ❤️")

        if final_list:
            content = "\n".join(final_list)
            with open("subscription.txt", "w", encoding="utf-8") as f: f.write(content)
            with open("subscription_b64.txt", "w", encoding="utf-8") as f:
                f.write(base64.b64encode(content.encode()).decode())
            print(f"✅ Готово: {len(final_list)}")

if __name__ == "__main__":
    UltraParser(SOURCES).run()
