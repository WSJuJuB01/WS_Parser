import requests
from bs4 import BeautifulSoup
import re

def parse_all_configs():
    url = "https://t.me/s/free_vless_whitelist"
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            return []
            
        soup = BeautifulSoup(response.text, 'html.parser')
        message_blocks = soup.find_all('div', class_='tgme_widget_message_text')
        
        new_links = []
        for block in message_blocks:
            text = block.get_text()
            
            # Регулярка ищет любые протоколы: vless://, vmess://, ss://, trojan://, hy2:// и т.д.
            # [a-zA-O0-9]+:// находит текст перед ://, а [^\s]+ забирает всю ссылку до пробела
            found = re.findall(r'([a-zA-Z0-9]+://[^\s]+)', text)
            if found:
                for link in found:
                    new_links.append(link.strip())
        return new_links
    except:
        return []

if __name__ == "__main__":
    file_name = "sub.txt"
    
    # Собираем абсолютно все типы ссылок, которые сейчас есть на странице
    fresh_configs = parse_all_configs()
    
    # Полностью перезаписываем файл свежими данными
    with open(file_name, "w", encoding="utf-8") as f:
        if fresh_configs:
            for link in fresh_configs:
                f.write(link + "\n")
            print(f"Файл перезаписан. Успешно сохранено {len(fresh_configs)} конфигов.")
        else:
            print("Конфиги не найдены. Файл очищен.")
