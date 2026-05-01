import requests
import re
import urllib.parse

# Список источников
SOURCES = [
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/WHITE-CIDR-RU-all.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_VLESS_RUS.txt",
    "https://raw.githubusercontent.com/igareck/vpn-configs-for-russia/refs/heads/main/BLACK_SS+All_RUS.txt",
    "https://raw.githubusercontent.com/RKPchannel/RKP_bypass_configs/refs/heads/main/configs/url_work.txt",
    "https://raw.githubusercontent.com/Ilyacom4ik/free-v2ray-2026/refs/heads/main/subscriptions/FreeCFGHub1.txt"
]

def get_flag_emoji(text):
    # Находим все флаги-эмодзи в тексте и возвращаем первый найденный
    flags = re.findall(r'[\U0001F1E6-\U0001F1FF]{2}', text)
    return flags[0] if flags else None

def parse():
    unique_configs = set()
    
    for url in SOURCES:
        try:
            print(f"Загрузка из: {url}")
            response = requests.get(url, timeout=15)
            if response.status_code == 200:
                content = response.text
                # Поиск всех поддерживаемых протоколов
                configs = re.findall(r'(?:vless|vmess|ss|trojan|tuic|hysteria2?)://[^\s]+', content)
                
                for cfg in configs:
                    # Базовая очистка строки
                    clean_cfg = cfg.strip().replace('\r', '').replace('`', '').replace('"', '')
                    unique_configs.add(clean_cfg)
            else:
                print(f"Ошибка {response.status_code} для {url}")
        except Exception as e:
            print(f"Ошибка при обработке {url}: {e}")

    if unique_configs:
        # 1. Сортировка: VLESS (приоритет 0) всегда идет первым в списке
        sorted_raw = sorted(
            list(unique_configs), 
            key=lambda x: (0 if x.startswith('vless://') else 1, x)
        )
        
        final_configs = []
        for i, cfg in enumerate(sorted_raw, 1):
            # Разделяем саму ссылку и название (всё, что после знака #)
            parts = cfg.split('#', 1)
            base_link = parts[0]
            # Декодируем имя (убираем %20 и прочие символы)
            old_name = urllib.parse.unquote(parts[1]) if len(parts) > 1 else ""
            
            # 2. Формируем новое красивое название
            flag = get_flag_emoji(old_name)
            
            if "anycast" in old_name.lower():
                new_name = "🌐 Anycast"
            elif flag:
                # Убираем найденный флаг из старого имени, чтобы он не дублировался
                clean_old_name = old_name.replace(flag, '').strip()
                # Убираем технический мусор (палки, подчеркивания), если они остались
                clean_old_name = re.sub(r'[|_-]', '', clean_old_name).strip()
                new_name = f"{flag} {clean_old_name if clean_old_name else 'Server'}"
            else:
                # Если флага и Anycast нет — ставим порядковый номер
                new_name = f"Обход {i}"
            
            # 3. Собираем итоговую строку: Ссылка + Новое имя + Твоя подпись
            final_configs.append(f"{base_link}#{new_name} | Ваш котенок ❤")

        # Записываем результат в файл
        with open("subscription.txt", "w", encoding="utf-8") as f:
            f.write("\n".join(final_configs))
            
        print(f"Готово! Собрано: {len(final_configs)}")
        print("VLESS сверху, флаги на месте, котенок доволен. 🐈‍⬛")
    else:
        print("Новых конфигов не найдено.")

if __name__ == "__main__":
    parse()
