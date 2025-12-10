#!/usr/bin/env python3
"""
Переводит оставшиеся английские значения в CSV на русский
"""

import csv

CSV_FILE = "empire_units.csv"

# Словарь переводов
TRANSLATIONS = {
    # Атаки
    "Holy Lance": "Святое копьё",
    "Lightning": "Молния",
    "Arrow": "Стрела",
    "Healing": "Лечение",
    "Sword": "Меч",
    "Mace": "Булава",
    "Staff": "Посох",
    "Longsword": "Длинный меч",
    "Greatsword": "Двуручный меч",
    "Dagger": "Кинжал",
    "Crossbow": "Арбалет",
    "Holy Staff": "Святой посох",
    "Sacred Staff": "Священный посох",
    "Resurrection": "Воскрешение",
    "Heal": "Лечение",
    "Mass Heal": "Массовое лечение",
    "Revive": "Воскрешение",
    "Fire Ball": "Огненный шар",
    "Fire": "Огонь",
    "Ice": "Лёд",
    "Fist": "Кулак",
    "Claw": "Коготь",
    "Summon": "Призыв",
    "Air Elemental": "Элементаль воздуха",
    "Poison Dagger": "Отравленный кинжал",
    "Parasitic Attack": "Паразитическая атака",
    "Holy Avenger": "Святое возмездие",
    "Divine Avenger": "Божественное возмездие",
    "Smite": "Кара",
    "Holy Smite": "Святая кара",
    "Earthquake": "Землетрясение",
    "Stomp": "Топот",
    "Slash": "Рубящий удар",
    
    # Дальность
    "Adjacent units": "Соседние",
    "Adjacent unit": "Соседний",
    "Any unit": "Любой",
    "Any": "Любой",
    "All": "Все",
    "6 adjacent": "6 соседних",
    "All adjacent": "Все соседние",
    
    # Класс атаки
    "Damage": "Урон",
    "Heal": "Лечение",
    "Paralyze": "Паралич",
    "Poison": "Яд",
    "Petrify": "Окаменение",
    "Fear": "Страх",
    "Drain Life": "Похищение жизни",
    "Lower Initiative": "Снижение инициативы",
    "Lower Damage": "Снижение урона",
    "Summon": "Призыв",
    "Cure": "Исцеление",
    "Revive": "Воскрешение",
    
    # Защита/Иммунитет
    "None": "Нет",
    "Poison": "Яд",
    "Mind": "Разум",
    "Death": "Смерть",
    "Fire": "Огонь",
    "Water": "Вода",
    "Air": "Воздух",
    "Earth": "Земля",
    
    # Источник
    "Weapon": "Оружие",
    "Life": "Жизнь",
    "Death": "Смерть",
    "Fire": "Огонь",
    "Water": "Вода",
    "Air": "Воздух",
    "Earth": "Земля",
    "Mind": "Разум",
}


def translate(value):
    """Перевести значение"""
    if not value or value == '—':
        return value
    
    # Прямой перевод
    if value in TRANSLATIONS:
        return TRANSLATIONS[value]
    
    # Перевод с учётом регистра
    if value.strip() in TRANSLATIONS:
        return TRANSLATIONS[value.strip()]
    
    # Попробуем перевести части (через запятую или /)
    if ',' in value:
        parts = [p.strip() for p in value.split(',')]
        translated = [TRANSLATIONS.get(p, p) for p in parts]
        return ', '.join(translated)
    
    if ' / ' in value:
        parts = [p.strip() for p in value.split(' / ')]
        translated = [TRANSLATIONS.get(p, p) for p in parts]
        return ' / '.join(translated)
    
    return value


def main():
    # Читаем CSV
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        units = list(reader)
    
    print(f"Обрабатываем {len(units)} юнитов...\n")
    
    # Поля для перевода
    fields_to_translate = ['Атака', 'Дальность', 'Класс атаки', 'Защита', 'Иммунитет', 'Источник']
    
    for unit in units:
        name = unit.get('name', '?')
        changes = []
        
        for field in fields_to_translate:
            old_val = unit.get(field, '')
            new_val = translate(old_val)
            if old_val != new_val:
                unit[field] = new_val
                changes.append(f"{field}: {old_val} → {new_val}")
        
        if changes:
            print(f"{name}:")
            for c in changes:
                print(f"  • {c}")
    
    # Сохраняем
    with open(CSV_FILE, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(units)
    
    print(f"\n✓ CSV обновлён: {CSV_FILE}")


if __name__ == "__main__":
    main()

