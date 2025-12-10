#!/usr/bin/env python3
"""
Парсер юнитов Империи из Disciples II Wiki (English)
Собирает данные о 29 существах, переводит на русский и сохраняет в CSV
"""

import csv
import time
import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

BASE_URL = "https://disciples.fandom.com"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"
}

# Список юнитов Империи (29 штук) - английские названия и URL (формат /D2)
EMPIRE_UNITS = [
    ("Angel", "Angel/D2"),
    ("Apprentice", "Apprentice/D2"),
    ("Archer", "Archer/D2"),
    ("Cleric", "Cleric/D2"),
    ("Defender of Faith", "Defender_of_Faith"),
    ("Grand Inquisitor", "Grand_Inquisitor/D2"),
    ("Hierophant", "Hierophant/D2"),
    ("Holy Avenger", "Holy_Avenger/D2"),
    ("Imperial Assassin", "Imperial_Assassin/D2"),
    ("Imperial Knight", "Imperial_Knight/D2"),
    ("Imperial Priest", "Imperial_Priest/D2"),
    ("Inquisitor", "Inquisitor/D2"),
    ("Knight", "Knight/D2"),
    ("Mage", "Mage/D2"),
    ("Marksman", "Marksman/D2"),
    ("Matriarch", "Matriarch/D2"),
    ("Myzrael", "Myzrael"),
    ("Paladin", "Paladin/D2"),
    ("Acolyte", "Acolyte/D2"),
    ("Prophetess", "Prophetess/D2"),
    ("Priest", "Priest/D2"),
    ("Squire", "Squire/D2"),
    ("Titan", "Titan/D2"),
    ("Witch Hunter", "Witch_Hunter/D2"),
    ("White Wizard", "White_Wizard/D2"),
    ("Wizard", "Wizard/D2"),
    ("Golem", "Golem/D2"),
    ("Living Armor", "Living_Armor/D2"),
    ("Elementalist", "Elementalist/D2"),
]

# Перевод названий и терминов
TRANSLATIONS = {
    # Названия юнитов
    "Angel": "Ангел",
    "Archmage": "Белый волшебник",
    "Apprentice": "Ученик",
    "Archer": "Лучник",
    "Cleric": "Клирик",
    "Defender of Faith": "Защитник Веры",
    "Grand Inquisitor": "Великий инквизитор",
    "Hierophant": "Иерофант",
    "Holy Avenger": "Святой мститель",
    "Imperial Assassin": "Имперский ассасин",
    "Imperial Knight": "Имперский рыцарь",
    "Imperial Priest": "Имперский жрец",
    "Inquisitor": "Инквизитор",
    "Knight": "Рыцарь",
    "Mage": "Маг",
    "Marksman": "Стрелок",
    "Matriarch": "Матриарх",
    "Myzrael": "Мизраэль",
    "Paladin": "Паладин",
    "Pilgrim": "Послушник",
    "Prophetess": "Прорицательница",
    "Priest": "Жрец",
    "Squire": "Сквайр",
    "Titan": "Титан",
    "Witch Hunter": "Охотник на ведьм",
    "White Wizard": "Белый волшебник",
    "Wizard": "Волшебник",
    "Golem": "Голем",
    "Imperial Golem": "Голем",
    "Living Armor": "Оживший доспех",
    "Elementalist": "Элементалист",
    "Acolyte": "Послушник",
    
    # Размеры
    "Small": "Малый",
    "Medium": "Обычный",
    "Large": "Большой",
    
    # Источники урона
    "Weapon": "Оружие",
    "Fire": "Огонь",
    "Water": "Вода",
    "Air": "Воздух",
    "Earth": "Земля",
    "Mind": "Разум",
    "Death": "Смерть",
    "Life": "Жизнь",
    
    # Защита/Иммунитет
    "None": "Нет",
    "Poison": "Яд",
    "Frostbite": "Обморожение",
    "Blister": "Волдыри",
    "Paralyze": "Паралич",
    "Petrify": "Окаменение",
    "Lower Initiative": "Снижение инициативы",
    "Lower Damage": "Снижение урона",
    "Drain Life": "Похищение жизни",
    "Fear": "Страх",
    "Curse": "Проклятие",
    
    # Цели / Дальность
    "Any": "Любой",
    "Adjacent": "Ближайший",
    "All": "Все",
    "6 Adjacent": "6 ближайших",
    "Any unit": "Любой юнит",
    "Adjacent units": "Ближние юниты",
    
    # Атаки / Оружие
    "Holy Lance": "Святое копьё",
    "Lightning": "Молния",
    "Arrow": "Стрела",
    "Healing": "Исцеление",
    "Healing / Cure": "Исцеление / Снятие эффектов",
    "Healing / Revive": "Исцеление / Воскрешение",
    "Long Sword": "Длинный меч",
    "(2x) Long Sword": "(2x) Длинный меч",
    "Sword": "Меч",
    "Great Sword": "Двуручный меч",
    "Mace": "Булава",
    "Holy Mace": "Святая булава",
    "Dagger / Poison": "Кинжал / Яд",
    "Dagger": "Кинжал",
    "Lance": "Копьё",
    "Holy Wrath": "Святой гнев",
    "Smash": "Удар",
    "Earthquake": "Землетрясение",
    "Summon (Air Elemental)": "Призыв (Элементаль воздуха)",
    
    # Класс атаки
    "Damage": "Урон",
    "Damage / Poison": "Урон / Яд",
    "Heal": "Лечение",
    "Heal / Cure": "Лечение / Снятие эффектов",
    "Heal / Revive": "Лечение / Воскрешение",
    "Summon": "Призыв",
    
    # Прочее
    "Yes": "Да",
    "No": "Нет",
}


def get_soup(url: str) -> BeautifulSoup:
    """Получить BeautifulSoup объект для URL"""
    response = requests.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def translate(text: str) -> str:
    """Перевести текст на русский"""
    if not text:
        return ""
    text = text.strip()
    
    # Прямой перевод
    if text in TRANSLATIONS:
        return TRANSLATIONS[text]
    
    # Попробуем перевести составные значения (например "Fire, Mind")
    if "," in text:
        parts = [p.strip() for p in text.split(",")]
        translated = [TRANSLATIONS.get(p, p) for p in parts]
        return ", ".join(translated)
    
    return text


def clean_text(text: str) -> str:
    """Очистить текст от лишних пробелов и символов"""
    if not text:
        return ""
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\[.*?\]', '', text)  # Убираем ссылки типа [1]
    return text.strip()


def parse_unit_page(url: str, en_name: str) -> dict:
    """Парсить страницу юнита и извлечь характеристики"""
    soup = get_soup(url)
    data = {
        "url": url,
        "name_en": en_name,
        "name": translate(en_name)
    }
    
    # Ищем изображение юнита
    image_url = ""
    infobox = soup.find("aside", class_="portable-infobox")
    
    if infobox:
        # Ищем все img теги в инфобоксе
        for img in infobox.find_all("img"):
            src = img.get("data-src") or img.get("src") or ""
            if src and "static.wikia.nocookie.net" in src:
                if ".gif" in src.lower() or ".png" in src.lower():
                    image_url = src
                    break
    
    # Метод 2: Первое изображение в контенте
    if not image_url:
        content = soup.find("div", class_="mw-parser-output")
        if content:
            for img in content.find_all("img"):
                src = img.get("data-src") or img.get("src") or ""
                if src and "static.wikia.nocookie.net" in src:
                    if ".gif" in src.lower() or ".png" in src.lower():
                        image_url = src
                        break
    
    # Очищаем URL изображения
    if image_url:
        image_url = re.sub(r'/scale-to-width-down/\d+', '', image_url)
        image_url = re.sub(r'/scale-to-width/\d+', '', image_url)
    
    data["image_url"] = image_url
    
    # Парсим инфобокс для характеристик
    if infobox:
        items = infobox.find_all("div", class_="pi-item")
        for item in items:
            label = item.find("h3", class_="pi-data-label")
            value = item.find("div", class_="pi-data-value")
            
            if label and value:
                key = clean_text(label.get_text())
                val = clean_text(value.get_text())
                
                # Пропускаем мусор
                if len(val) > 150 or "•" in val:
                    continue
                
                # Маппинг английских полей на русские
                field_map = {
                    # Основные
                    "Level": "Уровень",
                    "Size": "Размер",
                    "Hit Points": "Здоровье",
                    "Hit points": "Здоровье",
                    "HP": "Здоровье",
                    "Armor": "Броня",
                    
                    # Атака
                    "Attack": "Атака",
                    "Attack name": "Атака",
                    "Damage": "Урон",
                    "Initiative": "Инициатива",
                    "Source": "Источник",
                    "Class": "Класс атаки",
                    "Chances to hit": "Шанс попадания",
                    
                    # Защита
                    "Ward": "Защита",
                    "Wards": "Защита",
                    "Immunity": "Иммунитет",
                    "Immunities": "Иммунитет",
                    
                    # Цели
                    "Reach": "Дальность",
                    "Target": "Цель",
                    "Targets": "Кол-во целей",
                    
                    # Опыт и стоимость
                    "Cost": "Цена",
                    "Gold cost": "Цена",
                    "XP": "Опыт",
                    "Experience": "Опыт",
                    "XP next": "Опыт до апгрейда",
                    "XP Killed": "Опыт за убийство",
                    "XP killed": "Опыт за убийство",
                    
                    # Прочее
                    "Leadership": "Лидерство",
                    "Movement": "Перемещение",
                    "Scouting Range": "Обзор",
                    "Scouting range": "Обзор",
                    "Regeneration": "Регенерация",
                    "Accuracy": "Точность",
                    "Healing": "Лечение",
                    "Effect": "Эффект",
                }
                
                if key in field_map:
                    ru_key = field_map[key]
                    # Переводим значение если нужно
                    ru_val = translate(val)
                    data[ru_key] = ru_val
    
    # Парсим таблицы с характеристиками (если есть)
    content = soup.find("div", class_="mw-parser-output")
    if content:
        tables = content.find_all("table", class_="article-table")
        for table in tables:
            rows = table.find_all("tr")
            for row in rows:
                cells = row.find_all(["th", "td"])
                if len(cells) >= 2:
                    key = clean_text(cells[0].get_text())
                    val = clean_text(cells[1].get_text())
                    
                    if key and val and len(val) < 100:
                        # Пробуем добавить если ещё нет
                        field_map = {
                            "Level": "Уровень",
                            "Hit Points": "Здоровье",
                            "Armor": "Броня",
                            "Damage": "Урон",
                            "Source": "Источник",
                            "Initiative": "Инициатива",
                            "Reach": "Цель",
                            "XP Killed": "Опыт за убийство",
                        }
                        if key in field_map and field_map[key] not in data:
                            data[field_map[key]] = translate(val)
    
    return data


def get_unit_links() -> list[dict]:
    """Получить список ссылок на страницы юнитов"""
    units = []
    
    for name, slug in EMPIRE_UNITS:
        url = f"{BASE_URL}/wiki/{slug}"
        units.append({
            "name": name,
            "url": url
        })
    
    return units


def normalize_data(units_data: list[dict]) -> tuple[list[str], list[dict]]:
    """Нормализовать данные"""
    
    # Порядок колонок
    priority_fields = [
        "name", "name_en", "image_url", "url",
        "Уровень", "Размер", "Здоровье", "Броня", 
        "Атака", "Урон", "Инициатива", "Источник",
        "Защита", "Иммунитет", "Цель", "Точность",
        "Лечение", "Эффект",
        "Цена", "Опыт", "Опыт за убийство",
        "Перемещение", "Обзор", "Лидерство", "Регенерация"
    ]
    
    # Собираем все ключи
    all_keys = set()
    for unit in units_data:
        all_keys.update(unit.keys())
    
    # Сортируем
    sorted_keys = []
    for f in priority_fields:
        if f in all_keys:
            sorted_keys.append(f)
            all_keys.discard(f)
    
    for key in sorted(all_keys):
        if len(key) <= 30:
            sorted_keys.append(key)
    
    # Нормализуем
    normalized = []
    for unit in units_data:
        norm_unit = {key: unit.get(key, "") for key in sorted_keys}
        normalized.append(norm_unit)
    
    return sorted_keys, normalized


def save_to_csv(units_data: list[dict], filename: str = "empire_units.csv"):
    """Сохранить данные в CSV файл"""
    if not units_data:
        print("Нет данных для сохранения!")
        return
    
    keys, normalized = normalize_data(units_data)
    
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(normalized)
    
    print(f"Данные сохранены в {filename}")
    print(f"Колонок: {len(keys)}")


def main():
    print("=" * 60)
    print("Парсер юнитов Империи - Disciples II (English Wiki)")
    print("=" * 60)
    
    # Получаем список юнитов
    print("\n[1/3] Список юнитов Империи...")
    units = get_unit_links()
    print(f"Всего юнитов: {len(units)}")
    
    # Парсим каждого юнита
    print("\n[2/3] Парсим страницы юнитов...")
    units_data = []
    
    for i, unit in enumerate(units, 1):
        print(f"  [{i}/{len(units)}] {unit['name']}...")
        try:
            data = parse_unit_page(unit["url"], unit["name"])
            units_data.append(data)
            
            img_status = "✓" if data.get("image_url") else "✗"
            hp = data.get("Здоровье", "?")
            dmg = data.get("Урон", "?")
            print(f"    → {data['name']} | HP:{hp} DMG:{dmg} IMG:{img_status}")
            
            time.sleep(0.3)
        except Exception as e:
            print(f"    Ошибка: {e}")
    
    # Сохраняем в CSV
    print("\n[3/3] Сохраняем данные...")
    save_to_csv(units_data)
    
    print("\n" + "=" * 60)
    print(f"Готово! Обработано юнитов: {len(units_data)}")
    print("=" * 60)


if __name__ == "__main__":
    main()
