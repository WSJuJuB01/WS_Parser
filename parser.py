import requests
import re
import urllib.parse
import base64
import concurrent.futures
from datetime import datetime

# ==========================================
# SOURCES 🛰️
# ==========================================
SOURCES = {
    "EtoNeYa": ["https://etoneya.best/whitelist"],
    "BYWARM": ["https://gitverse.ru/api/repos/bywarm/rser/raw/branch/master/selected.txt"],
    "ByeWhite": ["https://raw.githubusercontent.com/ByeWhiteLists/ByeWhiteLists2/refs/heads/main/ByeWhiteLists2.txt"],
    "Temnuk": ["https://raw.githubusercontent.com/Temnuk/naabuzil/refs/heads/main/whitelist_full"],
    "Igareck": [
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/Vless-Reality-White-Lists-Rus-Mobile.txt",
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
        "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS-all_RUS.txt"
    ]
}

# --- ПОЛНЫЙ WHITE SNI LIST ---
WHITE_SNI_LIST = [
    "gosuslugi.ru", "gu-st.ru", "gov.ru", "nalog.ru", "mos.ru", "pfr.ru", "zakupki.gov.ru", "kremlin.ru", "customs.ru", "fssp.gov.ru", "mvd.ru", "mil.ru", "nalog.gov.ru", "lkfl2.nalog.ru", "fss.ru", "moex.com", "cbr.ru", "fsvps.gov.ru", "minfin.gov.ru",
    "yandex.ru", "ya.ru", "dzen.ru", "yandex.net", "zen.yandex.ru", "yastatic.net", "smartcaptcha.yandexcloud.net", "yandexcloud.net", "yandex.maps", "static-maps.yandex.ru", "yandex-team.ru", "yandex.kz", "yandex.by", "alice.yandex.net", "disk.yandex.ru",
    "vk.com", "vkvideo.ru", "ok.ru", "my.games", "mail.ru", "tamtam.chat", "vk-portal.ru", "ok.me", "m.vk.com", "userapi.com", "vk-cdn.net", "vkuseraudio.net", "vk-me.com", "vkmessenger.com", "vk-bridge.ru", "vks.ru",
    "sberbank.ru", "sber.ru", "vtb.ru", "tinkoff.ru", "alfa-bank.ru", "raiffeisen.ru", "rshb.ru", "gazprombank.ru", "nspk.ru", "mir-vsem.ru", "platezh.ru", "qiwi.com", "yoomoney.ru", "sberpay.ru", "sbp.nspk.ru", "vtb24.ru", "open.ru", "mkb.ru", "sovkombank.ru", "psbank.ru", "unicredit.ru", "pochtabank.ru",
    "ozon.ru", "wildberries.ru", "avito.ru", "market.yandex.ru", "lamoda.ru", "aliexpress.ru", "magnit.ru", "lenta.com", "dostavista.ru", "mvideo.ru", "eldorado.ru", "dns-shop.ru", "x5.ru", "ads.x5.ru", "fivepost.ru", "perekrestok.ru", "delivery-club.ru", "samokat.ru", "cdek.ru", "pochta.ru", "vprok.ru", "auchan.ru", "metro-cc.ru", "detmir.ru", "citilink.ru",
    "rutube.ru", "itv.ru", "vgtrk.ru", "smotrim.ru", "ntv.ru", "russia.tv", "max.ru", "1tv.ru", "ivi.ru", "kinopoisk.ru", "music.yandex.ru", "tnt-online.ru", "ctc.ru", "more.tv", "okko.tv", "premier.one", "kion.ru", "wink.ru", "matchtv.ru",
    "hh.ru", "superjob.ru", "stepik.org", "skyeng.ru", "ucheba.ru", "dnevnik.ru", "mesh.mos.ru", "giga-chat.ru", "kandinsky.ru", "sberdevices.ru", "salute.ru", "gosobr.ru", "foxford.ru", "netology.ru", "geekbrains.ru",
    "rzd.ru", "tutu.ru", "city-mobil.ru", "ya-taxi.ru", "aeroflot.ru", "s7.ru", "uralairlines.ru", "2gis.ru", "2gis.com", "maps.me",
    "cian.ru", "rbc.ru", "tass.ru", "gismeteo.ru", "rambler.ru", "consultant.ru", "garant.ru", "lenta.ru", "rg.ru", "ria.ru", "iz.ru", "kommersant.ru", "bfm.ru", "mk.ru", "vedomosti.ru", "interfax.ru"
]

# --- FLAG DATABASE (ДОБАВЛЕН ЕВРОСОЮЗ 🇪🇺) ---
FLAG_DB = {
    "🇪🇺": "Europe", "🇦🇫": "Afghanistan", "🇦🇱": "Albania", "🇩🇿": "Algeria", "🇦🇸": "American Samoa", "🇦🇩": "Andorra", "🇦🇴": "Angola", "🇦🇮": "Anguilla", "🇦🇶": "Antarctica", "🇦🇬": "Antigua", "🇦🇷": "Argentina", "🇦🇲": "Armenia", "🇦🇼": "Aruba", "🇦🇺": "Australia", "🇦🇹": "Austria", "🇦🇿": "Azerbaijan", "🇧🇸": "Bahamas", "🇧🇭": "Bahrain", "🇧🇩": "Bangladesh", "🇧🇧": "Barbados",
    "🇧🇾": "Belarus", "🇧🇪": "Belgium", "🇧🇿": "Belize", "🇧🇳": "Benin", "🇧🇲": "Bermuda", "🇧🇹": "Bhutan", "🇧🇴": "Bolivia", "🇧🇦": "Bosnia", "🇧🇼": "Botswana", "🇧🇷": "Brazil", "🇻🇬": "British Virgin Islands", "🇧🇳": "Brunei", "🇧🇬": "Bulgaria", "🇧🇫": "Burkina Faso", "🇧🇮": "Burundi", "🇰🇭": "Cambodia", "🇨🇲": "Cameroon", "🇨🇦": "Canada", "🇨🇻": "Cape Verde", "🇰🇾": "Cayman Islands",
    "🇨🇫": "Central African Republic", "🇹🇩": "Chad", "🇨🇱": "Chile", "🇨🇳": "China", "🇨🇴": "Colombia", "🇰🇲": "Comoros", "🇨🇬": "Congo", "🇨🇰": "Cook Islands", "🇨🇷": "Costa Rica", "🇭🇷": "Croatia", "🇨🇺": "Cuba", "🇨🇾": "Cyprus", "🇨🇿": "Czechia", "🇩🇰": "Denmark", "🇩🇯": "Djibouti", "🇩🇲": "Dominica", "🇩🇴": "Dominican Republic", "🇪🇨": "Ecuador", "🇪🇬": "Egypt", "🇸🇻": "El Salvador",
    "🇬🇶": "Equatorial Guinea", "🇪🇷": "Eritrea", "🇪🇪": "Estonia", "🇪🇹": "Ethiopia", "🇫🇯": "Fiji", "🇫🇮": "Finland", "🇫🇷": "France", "🇬🇦": "Gabon", "🇬🇲": "Gambia", "🇬🇪": "Georgia", "🇩🇪": "Germany", "🇬🇭": "Ghana", "🇬🇮": "Gibraltar", "🇬🇷": "Greece", "🇬🇱": "Greenland", "🇬🇩": "Grenada", "🇬🇵": "Guadeloupe", "🇬🇺": "Guam", "🇬🇹": "Guatemala", "🇬🇳": "Guinea",
    "🇬🇼": "Guinea-Bissau", "🇬🇾": "Guyana", "🇭🇹": "Haiti", "🇭🇳": "Honduras", "🇭🇰": "Hong Kong", "🇭🇺": "Hungary", "🇮🇸": "Iceland", "🇮🇳": "India", "🇮🇩": "Indonesia", "🇮🇷": "Iran", "🇮🇶": "Iraq", "🇮🇪": "Ireland", "🇮🇲": "Isle of Man", "🇮🇱": "Israel", "🇮🇹": "Italy", "🇯🇲": "Jamaica", "🇯🇵": "Japan", "🇯🇪": "Jersey", "🇯🇴": "Jordan", "🇰🇿": "Kazakhstan",
    "🇰🇪": "Kenya", "🇰🇮": "Kiribati", "🇰🇼": "Kuwait", "🇰🇬": "Kyrgyzstan", "🇱🇦": "Laos", "🇱🇻": "Latvia", "🇱🇧": "Lebanon", "🇱🇸": "Lesotho", "🇱🇷": "Liberia", "🇱🇾": "Libya", "🇱🇮": "Liechtenstein", "🇱🇹": "Lithuania", "🇱🇺": "Luxembourg", "🇲🇴": "Macau", "🇲🇰": "Macedonia", "🇲🇬": "Madagascar", "🇲🇼": "Malawi", "🇲🇾": "Malaysia", "🇲🇻": "Maldives", "🇲🇱": "Mali",
    "🇲🇹": "Malta", "🇲🇭": "Marshall Islands", "🇲🇶": "Martinique", "🇲🇷": "Mauritania", "🇲🇺": "Mauritius", "🇲🇽": "Mexico", "🇫🇲": "Micronesia", "🇲🇩": "Moldova", "🇲🇨": "Monaco", "🇲🇳": "Mongolia", "🇲🇪": "Montenegro", "🇲🇸": "Montserrat", "🇲🇦": "Morocco", "🇲🇿": "Mozambique", "🇲🇲": "Myanmar", "🇳🇦": "Namibia", "🇳🇷": "Nauru", "🇳🇵": "Nepal", "🇳🇱": "Netherlands", "🇳🇨": "New Caledonia",
    "🇳🇿": "New Zealand", "🇳🇮": "Nicaragua", "🇳🇪": "Niger", "🇳🇬": "Nigeria", "🇳🇺": "Niue", "🇳🇫": "Norfolk Island", "🇲🇵": "Northern Mariana Islands", "🇰🇵": "North Korea", "🇳🇴": "Norway", "🇴🇲": "Oman", "🇵🇰": "Pakistan", "🇵🇼": "Palau", "🇵🇸": "Palestine", "🇵🇦": "Panama", "🇵🇬": "Papua New Guinea", "🇵🇾": "Paraguay", "🇵🇪": "Peru", "🇵🇭": "Philippines", "🇵🇳": "Pitcairn Islands",
    "🇵🇱": "Poland", "🇵🇹": "Portugal", "🇵🇷": "Puerto Rico", "🇶🇦": "Qatar", "🇷🇪": "Reunion", "🇷🇴": "Romania", "🇷🇺": "Russia", "🇷🇼": "Rwanda", "🇼🇸": "Samoa", "🇸🇲": "San Marino", "🇸🇹": "Sao Tome", "🇸🇦": "Saudi Arabia", "🇸🇳": "Senegal", "🇷🇸": "Serbia", "🇸🇨": "Seychelles", "🇸🇱": "Sierra Leone", "🇸🇬": "Singapore", "🇸🇽": "Sint Maarten", "🇸🇰": "Slovakia", "🇸🇮": "Slovenia",
    "🇸🇧": "Solomon Islands", "🇸🇴": "Somalia", "🇿🇦": "South Africa", "🇰🇷": "South Korea", "🇸🇸": "South Sudan", "🇪🇸": "Spain", "🇱🇰": "Sri Lanka", "🇸🇩": "Sudan", "🇸🇷": "Suriname", "🇸🇿": "Swaziland", "🇸🇪": "Sweden", "🇨🇭": "Switzerland", "🇸🇾": "Syria", "🇹🇼": "Taiwan", "🇹🇯": "Tajikistan", "🇹🇿": "Tanzania", "🇹🇭": "Thailand", "🇹🇱": "Timor-Leste", "🇹🇬": "Togo",
    "🇹🇰": "Tokelau", "🇹🇴": "Tonga", "🇹🇹": "Trinidad", "🇹🇳": "Tunisia", "🇹🇷": "Turkey", "🇹🇲": "Turkmenistan", "🇹🇨": "Turks and Caicos", "🇹🇻": "Tuvalu", "🇺🇬": "Uganda", "🇺🇦": "Ukraine", "🇦🇪": "UAE", "🇬🇧": "UK", "🇺🇸": "USA", "🇺🇾": "Uruguay", "🇺🇿": "Uzbekistan", "🇻🇺": "Vanuatu", "🇻🇦": "Vatican City", "🇻🇪": "Venezuela", "🇻🇳": "Vietnam", "🇼🇫": "Wallis and Futuna",
    "🇪🇭": "Western Sahara", "🇾🇪": "Yemen", "🇿🇲": "Zambia", "🇿🇼": "Zimbabwe"
}

class UltraParser:
    def __init__(self, sources_dict):
        self.sources_dict = sources_dict
        self.buckets = {auth: [] for auth in sources_dict.keys()}
        self.counters = {auth: 1 for auth in sources_dict.keys()}

    def decode_display_name(self, raw_name, link, author):
        if author == "EtoNeYa":
            name = f"🏳️ White lists {self.counters[author]}"
            self.counters[author] += 1
            return name

        is_white = any(sni in (link + raw_name).lower() for sni in WHITE_SNI_LIST)
        white_tag = " 🏳️ White list" if is_white else ""
        
        found_flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', raw_name)
        if found_flags:
            flag = found_flags[0]
            country = FLAG_DB.get(flag, "Location")
            label = f"{flag} {country}"
        elif "anycast" in raw_name.lower():
            label = "🌐 Anycast"
        else:
            label = "🌐 Unknown"

        name = f"{label} | {author} #{self.counters[author]}{white_tag}"
        self.counters[author] += 1
        return name

    def fetch_and_parse(self, author, urls):
        for url in urls:
            try:
                res = requests.get(url, timeout=15, headers={'User-Agent': 'Mozilla/5.0'})
                if res.status_code != 200: continue
                content = res.text
                if not any(p in content for p in ["vless://", "ss://", "vmess://", "trojan://"]):
                    try: content = base64.b64decode(content).decode('utf-8')
                    except: pass
                links = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2)://[^\r\n\t\s]+', content)
                for l in links:
                    l = l.strip()
                    clean_link, raw_name = (l.split("#", 1) if "#" in l else (l, ""))
                    if clean_link:
                        self.buckets[author].append({"link": clean_link, "name": urllib.parse.unquote(raw_name)})
            except Exception as e:
                print(f"❌ Error {author}: {e}")

    def run(self):
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 🥪 Добавляем Европу в бутерброд...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as ex:
            futures = [ex.submit(self.fetch_and_parse, auth, urls) for auth, urls in self.sources_dict.items()]
            concurrent.futures.wait(futures)

        final_list = []
        authors = list(self.buckets.keys())
        global_count = 0

        while any(self.buckets[a] for a in authors):
            for a in authors:
                chunk = self.buckets[a][:10]
                self.buckets[a] = self.buckets[a][10:]
                for item in chunk:
                    display = self.decode_display_name(item["name"], item["link"], a)
                    safe_display = urllib.parse.quote(f"{display} | WSVPN 🐈‍⬛")
                    final_list.append(f"{item['link']}#{safe_display}")
                    global_count += 1
                    
                    if global_count % 20 == 0:
                        final_list.append("") 

        if final_list:
            content = "\n".join(final_list)
            with open("subscription.txt", "w", encoding="utf-8") as f:
                f.write(content)
            b64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")
            with open("subscription_b64.txt", "w", encoding="utf-8") as f:
                f.write(b64_content)
            print(f"✅ Готово! Найдено {global_count} конфигов.")

if __name__ == "__main__":
    parser = UltraParser(SOURCES)
    parser.run()
