#!/usr/bin/env python3
"""
Скачивает изображения юнитов на локальный диск
"""

import csv
import os
import requests
import re
from urllib.parse import unquote

IMAGES_DIR = "images"
CSV_FILE = "empire_units.csv"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
    "Referer": "https://disciples.fandom.com/"
}


def sanitize_filename(name):
    """Очистить имя файла от недопустимых символов"""
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    name = name.replace(' ', '_')
    return name


def download_image(url, filename):
    """Скачать изображение"""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        
        filepath = os.path.join(IMAGES_DIR, filename)
        with open(filepath, 'wb') as f:
            f.write(resp.content)
        
        return True
    except Exception as e:
        print(f"    Ошибка: {e}")
        return False


def main():
    # Создаём папку для изображений
    os.makedirs(IMAGES_DIR, exist_ok=True)
    
    # Читаем CSV
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        units = list(reader)
        fieldnames = reader.fieldnames
    
    print(f"Найдено юнитов: {len(units)}")
    print(f"Скачиваем изображения в папку '{IMAGES_DIR}'...\n")
    
    updated_units = []
    
    for i, unit in enumerate(units, 1):
        name = unit.get('name', f'unit_{i}')
        image_url = unit.get('image_url', '')
        
        print(f"[{i}/{len(units)}] {name}...", end=" ")
        
        if not image_url:
            print("нет URL")
            updated_units.append(unit)
            continue
        
        # Определяем расширение
        if '.png' in image_url.lower():
            ext = 'png'
        elif '.gif' in image_url.lower():
            ext = 'gif'
        else:
            ext = 'png'
        
        # Имя файла
        filename = f"{sanitize_filename(name)}.{ext}"
        
        # Скачиваем
        if download_image(image_url, filename):
            print(f"✓ {filename}")
            unit['image_url'] = f"{IMAGES_DIR}/{filename}"
        else:
            print("✗ не удалось")
        
        updated_units.append(unit)
    
    # Сохраняем обновлённый CSV
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(updated_units)
    
    print(f"\n✓ CSV обновлён: {CSV_FILE}")
    print(f"✓ Изображения сохранены в: {IMAGES_DIR}/")


if __name__ == "__main__":
    main()

