import requests
import re
import urllib.parse
import base64
import concurrent.futures

# ==========================================
# ТВОИ SOURCES — СЕРДЦЕ ПРОЕКТА 🐾
# ==========================================
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/1",
    "https://raw.githubusercontent.com/EtoNeYaProject/etoneyaproject.github.io/refs/heads/main/whitelist"
]
# ==========================================
# ПОЛНАЯ БАЗА ФЛАГОВ МИРА (250+ записей) 🌍
# ==========================================
FLAG_DB = {
    "🇦🇫": "Afghanistan", "🇦🇱": "Albania", "🇩🇿": "Algeria", "🇦🇸": "American Samoa", "🇦🇩": "Andorra", "🇦🇴": "Angola", "🇦🇮": "Anguilla", "🇦🇶": "Antarctica", "🇦🇬": "Antigua", "🇦🇷": "Argentina",
    "🇦🇲": "Armenia", "🇦🇼": "Aruba", "🇦🇺": "Australia", "🇦🇹": "Austria", "🇦🇿": "Azerbaijan", "🇧🇸": "Bahamas", "🇧🇭": "Bahrain", "🇧🇩": "Bangladesh", "🇧🇧": "Barbados", "🇧🇾": "Belarus",
    "🇧🇪": "Belgium", "🇧🇿": "Belize", "🇧🇯": "Benin", "🇧🇲": "Bermuda", "🇧🇹": "Bhutan", "🇧🇴": "Bolivia", "🇧🇦": "Bosnia", "🇧🇼": "Botswana", "🇧🇷": "Brazil", "🇻🇬": "British Virgin Islands",
    "🇧🇳": "Brunei", "🇧🇬": "Bulgaria", "🇧🇫": "Burkina Faso", "🇧🇮": "Burundi", "🇰🇭": "Cambodia", "🇨🇲": "Cameroon", "🇨🇦": "Canada", "🇨🇻": "Cape Verde", "🇰🇾": "Cayman Islands", "🇨🇫": "Central African Republic",
    "🇹🇩": "Chad", "🇨🇱": "Chile", "🇨🇳": "China", "🇨🇴": "Colombia", "🇰🇲": "Comoros", "🇨🇬": "Congo", "🇨🇰": "Cook Islands", "🇨🇷": "Costa Rica", "🇭🇷": "Croatia", "🇨🇺": "Cuba",
    "🇨🇾": "Cyprus", "🇨🇿": "Czechia", "🇩🇰": "Denmark", "🇩🇯": "Djibouti", "🇩🇲": "Dominica", "🇩🇴": "Dominican Republic", "🇪🇨": "Ecuador", "🇪🇬": "Egypt", "🇸🇻": "El Salvador", "🇬🇶": "Equatorial Guinea",
    "🇪🇷": "Eritrea", "🇪🇪": "Estonia", "🇪🇹": "Ethiopia", "🇫🇯": "Fiji", "🇫🇮": "Finland", "🇫🇷": "France", "🇬🇦": "Gabon", "🇬🇲": "Gambia", "🇬🇪": "Georgia", "🇩🇪": "Germany",
    "🇬🇭": "Ghana", "🇬🇮": "Gibraltar", "🇬🇷": "Greece", "🇬🇱": "Greenland", "🇬🇩": "Grenada", "🇬🇵": "Guadeloupe", "🇬🇺": "Guam", "🇬🇹": "Guatemala", "🇬🇳": "Guinea", "🇬🇼": "Guinea-Bissau",
    "🇬🇾": "Guyana", "🇭🇹": "Haiti", "🇭🇳": "Honduras", "🇭🇰": "Hong Kong", "🇭🇺": "Hungary", "🇮🇸": "Iceland", "🇮🇳": "India", "🇮🇩": "Indonesia", "🇮🇷": "Iran", "🇮🇶": "Iraq",
    "🇮🇪": "Ireland", "🇮🇲": "Isle of Man", "🇮🇱": "Israel", "🇮🇹": "Italy", "🇯🇲": "Jamaica", "🇯🇵": "Japan", "🇯🇪": "Jersey", "🇯🇴": "Jordan", "🇰🇿": "Kazakhstan", "🇰🇪": "Kenya",
    "🇰🇮": "Kiribati", "🇰🇼": "Kuwait", "🇰🇬": "Kyrgyzstan", "🇱🇦": "Laos", "🇱🇻": "Latvia", "🇱🇧": "Lebanon", "🇱🇸": "Lesotho", "🇱🇷": "Liberia", "🇱🇾": "Libya", "🇱🇮": "Liechtenstein",
    "🇱🇹": "Lithuania", "🇱🇺": "Luxembourg", "🇲🇴": "Macao", "🇲🇰": "Macedonia", "🇲🇬": "Madagascar", "🇲🇼": "Malawi", "🇲🇾": "Malaysia", "🇲🇻": "Maldives", "🇲🇱": "Mali", "🇲🇹": "Malta",
    "🇲🇭": "Marshall Islands", "🇲🇶": "Martinique", "🇲🇷": "Mauritania", "🇲🇺": "Mauritius", "🇲🇽": "Mexico", "🇫🇲": "Micronesia", "🇲🇩": "Moldova", "🇲🇨": "Monaco", "🇲🇳": "Mongolia", "🇲🇪": "Montenegro",
    "🇲🇦": "Morocco", "🇲🇿": "Mozambique", "🇲🇲": "Myanmar", "🇳🇦": "Namibia", "🇳🇷": "Nauru", "🇳🇵": "Nepal", "🇳🇱": "Netherlands", "🇳🇨": "New Caledonia", "🇳🇿": "New Zealand", "🇳🇮": "Nicaragua",
    "🇳🇪": "Niger", "🇳🇬": "Nigeria", "🇳🇺": "Niue", "🇰🇵": "North Korea", "🇲🇵": "Northern Mariana Islands", "🇳🇴": "Norway", "🇴🇲": "Oman", "🇵🇰": "Pakistan", "🇵🇼": "Palau", "🇵🇸": "Palestine",
    "🇵🇦": "Panama", "🇵🇬": "Papua New Guinea", "🇵🇾": "Paraguay", "🇵🇪": "Peru", "🇵🇭": "Philippines", "🇵🇳": "Pitcairn Islands", "🇵🇱": "Poland", "🇵🇹": "Portugal", "🇵🇷": "Puerto Rico", "🇶🇦": "Qatar",
    "🇷🇪": "Reunion", "🇷🇴": "Romania", "🇷🇺": "Russia", "🇷🇼": "Rwanda", "🇼🇸": "Samoa", "🇸🇲": "San Marino", "🇸🇹": "Sao Tome", "🇸🇦": "Saudi Arabia", "🇸🇳": "Senegal", "🇷🇸": "Serbia",
    "🇸🇨": "Seychelles", "🇸🇱": "Sierra Leone", "🇸🇬": "Singapore", "🇸🇽": "Sint Maarten", "🇸🇰": "Slovakia", "🇸🇮": "Slovenia", "🇸🇧": "Solomon Islands", "🇸🇴": "Somalia", "🇿🇦": "South Africa", "🇰🇷": "South Korea",
    "🇸🇸": "South Sudan", "🇪🇸": "Spain", "🇱🇰": "Sri Lanka", "🇸🇩": "Sudan", "🇸🇷": "Suriname", "🇸🇿": "Swaziland", "🇸🇪": "Sweden", "🇨🇭": "Switzerland", "🇸🇾": "Syria", "🇹🇼": "Taiwan",
    "🇹🇯": "Tajikistan", "🇹🇿": "Tanzania", "🇹🇭": "Thailand", "🇹🇱": "Timor-Leste", "🇹🇬": "Togo", "🇹🇰": "Tokelau", "🇹🇴": "Tonga", "🇹🇹": "Trinidad", "🇹🇳": "Tunisia", "🇹🇷": "Turkey",
    "🇹🇲": "Turkmenistan", "🇹🇨": "Turks and Caicos", "🇹🇻": "Tuvalu", "🇺🇬": "Uganda", "🇺🇦": "Ukraine", "🇦🇪": "UAE", "🇬🇧": "UK", "🇺🇸": "USA", "🇺🇾": "Uruguay", "🇺🇿": "Uzbekistan",
    "🇻🇺": "Vanuatu", "🇻🇦": "Vatican City", "🇻🇪": "Venezuela", "🇻🇳": "Vietnam", "🇼🇫": "Wallis and Futuna", "🇪🇭": "Western Sahara", "🇾🇪": "Yemen", "🇿🇲": "Zambia", "🇿🇼": "Zimbabwe"
}

# ==========================================
# ТОТАЛЬНЫЙ БЕЛЫЙ СПИСОК SNI РФ 🏳️
# ==========================================
WHITE_SNI_LIST = [
    # Государственные
    "gosuslugi.ru", "gu-st.ru", "gov.ru", "nalog.ru", "mos.ru", "pfr.ru", "zakupki.gov.ru", "kremlin.ru",
    # Соцсети и Мессенджеры
    "vk.com", "vkvideo.ru", "ok.ru", "my.games", "mail.ru", "tamtam.chat", "://vk.com", "vk-portal.ru",
    # Поисковики и медиа
    "yandex.ru", "ya.ru", "dzen.ru", "kinopoisk.ru", "music.yandex.ru", "yandex.net", "zen.yandex.ru",
    # Банки
    "sberbank.ru", "sber.ru", "vtb.ru", "tinkoff.ru", "alfa-bank.ru", "raiffeisen.ru", "rshb.ru", "gazprombank.ru",
    # Маркетплейсы
    "ozon.ru", "wildberries.ru", "avito.ru", "market.yandex.ru", "lamoda.ru", "aliexpress.ru", "magnit.ru",
    # Разное и Техническое
    "rutube.ru", "1tv.ru", "vgtrk.ru", "smotrim.ru", "ntv.ru", "russia.tv", "max.ru", "vmp-vless.ru",
    "ads.x5.ru", "x5.ru", "rzd.ru", "tutu.ru", "yandex.st", "yastatic.net", "delivery-club.ru", "yandex.maps"
]

class UltraParser:
    def __init__(self, sources):
        self.sources = sources
        self.buckets = {"EtoNeYa": [], "RKP": [], "igareck": [], "FCH": [], "Other": []}
        self.rkp_counter = 1
        self.etoneya_counter = 1

    def get_author_label(self, url):
        if "etoneya" in url: return "EtoNeYa"
        if "igareck" in url: return "igareck"
        if "RKP" in url: return "RKP"
        if "Ilyacom4ik" in url: return "FCH"
        return "Other"
       
        if author == "EtoNeYa":
            # --- 1. ПРИОРИТЕТ: WHITELIST (берем всё с БЕЛЫМ ФЛАГОМ) ---
            if "whitelist" in url:
                self.etoneya_counter += 1
                name = f"🏳 White lists #{self.etoneya_counter} | EtoNeYa"
                return name, "котенок"

            # --- 2. ФАЙЛ "1" (фильтрация и твои спец-эмодзи) ---
            if url.endswith("/1"):
                # YouTube
                if "youtube" in full_text:
                    return "📺 YouTube🔴", "котенок"
                
                # Cloudflare
                if "cloudflare" in full_text:
                    return "☁️ Cloudflare", "котенок"
                
                # Gemini
                if any(x in full_text for x in ["gemini", "bard", "google ai", "ai"]):
                    return "🤖✨ Gemini", "котенок"
                
                # Если в файле "1" нет ключевых слов — пропускаем
                return None, None

            # --- 3. ОСТАЛЬНОЕ (дефолтные конфиги EtoNeYa) ---
            self.etoneya_counter += 1
            name = f"💎 Config #{self.etoneya_counter} | EtoNeYa"
            return name, "котенок"



        if author == "RKP":
            name = f"🛡 RKP #{self.rkp_counter}"
            self.rkp_counter += 1
            return name, "котенок" # Приписку оставил как была

        # Логика для Игоря и FCH (приписка тоже "котенок")
        found_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', raw_name)
        country_info = "🌐 Unknown"
        
        if found_flags:
            flag = found_flags[0]
            country_name = FLAG_DB.get(flag, "Location")
            country_info = f"{flag} {country_name}"

        is_white = any(sni in (link + raw_name).lower() for sni in WHITE_SNI_LIST)
        final_name = f"{country_info} 🏳" if is_white else country_info
        
        return final_name, "котенок" # Приписку оставил как была

        # Проверка на белый список
        is_white = any(sni in (link + raw_name).lower() for sni in WHITE_SNI_LIST)
        final_name = f"{country_info} 🏳" if is_white else country_info
        
        return final_name, "котенок"

    def fetch_url(self, url):
        try:
            res = requests.get(url, timeout=20, headers={'User-Agent': 'Mozilla/5.0'})
            if res.status_code == 200:
                return res.text, url
        except:
            pass
        return None, url

    def run(self):
        print("🚀 Запуск Мега-Парсера...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
            results = list(executor.map(self.fetch_url, self.sources))

        for content, url in results:
            if not content: continue
            author = self.get_author_label(url)
            # Извлекаем ссылки
            found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
            for cfg in found:
                cfg = cfg.strip().replace('`', '').replace('"', '').replace('\r', '')
                link, name = cfg.rsplit('#', 1) if '#' in cfg else (cfg, "")
                self.buckets[author].append({"link": link, "name": urllib.parse.unquote(name)})

        final_list = []
        authors_order = ["EtoNeYa", "RKP", "igareck", "FCH", "Other"]

        # Перемешивание слоями по 10
        while any(self.buckets.values()):
            for author in authors_order:
                chunk = self.buckets[author][:10]
                self.buckets[author] = self.buckets[author][10:]
                
                for item in chunk:
                    display_name, cat_type = self.decode_display_name(item["name"], item["link"], author)
                    final_list.append(f"{item['link']}#{display_name} | {author} | Ваш {cat_type} ❤")


        # Сохранение
        output_text = "\n".join(final_list)
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write(output_text)
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            f.write(base64.b64encode(output_text.encode()).decode())

        print(f"✨ Готово! Собрано {len(final_list)-1} конфигов. GitHub будет в восторге!")

if __name__ == "__main__":
    UltraParser(SOURCES).run()
