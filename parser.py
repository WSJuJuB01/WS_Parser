import requests
import re
import urllib.parse
import base64
import concurrent.futures
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

# База данных для распознавания локаций
COUNTRY_DATA = {
    "russia": "🇷🇺 Russia", " rus": "🇷🇺 Russia", "_ru": "🇷🇺 Russia",
    "germany": "🇩🇪 Germany", " ger": "🇩🇪 Germany", "_de": "🇩🇪 Germany", "frankfurt": "🇩🇪 Germany",
    "netherlands": "🇳🇱 Netherlands", " nl": "🇳🇱 Netherlands", "holland": "🇳🇱 Netherlands", "amsterdam": "🇳🇱 Netherlands",
    "usa": "🇺🇸 USA", " us": "🇺🇸 USA", "united states": "🇺🇸 USA", "america": "🇺🇸 USA",
    "finland": "🇫🇮 Finland", " fi": "🇫🇮 Finland", "helsinki": "🇫🇮 Finland",
    "poland": "🇵🇱 Poland", " pl": "🇵🇱 Poland", "warsaw": "🇵🇱 Poland",
    "france": "🇫🇷 France", " fr": "🇫🇷 France", "paris": "🇫🇷 France",
    "turkey": "🇹🇷 Turkey", " tr": "🇹🇷 Turkey", "istanbul": "🇹🇷 Turkey",
    "ukraine": "🇺🇦 Ukraine", " ua": "🇺🇦 Ukraine", "kyiv": "🇺🇦 Ukraine",
    "kazakhstan": "🇰🇿 Kazakhstan", " kz": "🇰🇿 Kazakhstan", "astana": "🇰🇿 Kazakhstan",
    "austria": "🇦🇹 Austria", " at": "🇦🇹 Austria", "vienna": "🇦🇹 Austria",
    "sweden": "🇸🇪 Sweden", " se": "🇸🇪 Sweden", "stockholm": "🇸🇪 Sweden",
    "singapore": "🇸🇬 Singapore", " sg": "🇸🇬 Singapore",
    "japan": "🇯🇵 Japan", " jp": "🇯🇵 Japan", "tokyo": "🇯🇵 Japan",
    "united kingdom": "🇬🇧 UK", " uk": "🇬🇧 UK", " gb": "🇬🇧 UK", "london": "🇬🇧 UK"
}

class FullSubscriptionGenerator:
    def __init__(self):
        self.all_configs = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }

    def identify_author(self, url):
        """Определяет владельца источника"""
        mapping = {
            "etoneya": "EtoNeYa",
            "igareck": "igareck",
            "RKP": "RKP",
            "Ilyacom4ik": "FCH"
        }
        for key, name in mapping.items():
            if key in url:
                return name
        return "Dev"

    def detect_location(self, text):
        """Ищет страну в названии конфига"""
        t_low = text.lower()
        for key, label in COUNTRY_DATA.items():
            if key in t_low:
                return label
        # Если текста нет, пробуем найти встроенные флаги
        flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
        return "".join(flags) if flags else None

    def fetch_data(self, url):
        """Загружает данные из интернета"""
        try:
            print(f"🔄 Запрашиваю: {url}")
            res = requests.get(url, headers=self.headers, timeout=30)
            if res.status_code == 200:
                return res.text, url
        except Exception as e:
            print(f"⚠️ Проблема с {url}: {e}")
        return None, url

    def run_parser(self):
        """Основной цикл парсинга (многопоточный)"""
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(SOURCES)) as executor:
            downloaded = list(executor.map(self.fetch_data, SOURCES))

        for content, source_url in downloaded:
            if not content:
                continue

            author = self.identify_author(source_url)
            # Извлекаем все ссылки на прокси
            raw_found = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
            
            for item in raw_found:
                # Глубокая очистка строки
                item = item.strip().replace('`', '').replace('"', '').replace('\r', '').replace('\n', '')
                
                # Парсинг имени и линка
                if '#' in item:
                    link_part, raw_name = item.rsplit('#', 1)
                    old_name = urllib.parse.unquote(raw_name)
                else:
                    link_part, old_name = item, ""

                # Определяем локацию
                location = self.detect_location(old_name)
                
                # Формирование финального Remark
                if author == "RKP":
                    display_name = f"🛡 RKP #{len(self.all_configs) + 1}"
                elif location:
                    display_name = location
                else:
                    # Если ничего не нашли, сохраняем остатки оригинального имени или даем номер
                    clean_orig = old_name.split('|')[0].strip()
                    display_name = clean_orig if len(clean_orig) > 1 else f"Node {len(self.all_configs) + 1}"

                # Добавляем в общий список (ДУБЛИКАТЫ РАЗРЕШЕНЫ)
                self.all_configs.append(f"{link_part}#{display_name} | {author} | Ваш котенок ❤")

    def generate_files(self):
        """Сортировка и сохранение в файлы"""
        if not self.all_configs:
            print("❌ Сбор завершен, но ничего не найдено.")
            return

        # Сортировка: VLESS сначала, остальное потом
        self.all_configs.sort(key=lambda x: 0 if x.startswith('vless') else 1)

        # Создание информационной шапки
        update_time = datetime.now().strftime('%d.%m %H:%M')
        header = f"vless://00000000-0000-0000-0000-000000000000@0.0.0.0:443?encryption=none&type=tcp#REMARK=🐾 Обновлено: {update_time} | Всего: {len(self.all_configs)}"
        self.all_configs.insert(0, header)

        final_output = "\n".join(self.all_configs)
        
        # Запись в обычный текст
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write(final_output)
            
        # Запись в Base64 для клиентов
        with open("subscription_b64.txt", "w", encoding="utf-8") as f:
            b64_str = base64.b64encode(final_output.encode('utf-8')).decode('utf-8')
            f.write(b64_str)

        print(f"✨ Готово! Файлы обновлены. Собрано конфигов: {len(self.all_configs) - 1}")

if __name__ == "__main__":
    generator = FullSubscriptionGenerator()
    generator.run_parser()
    generator.generate_files()
