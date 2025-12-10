#!/usr/bin/env python3
"""
Веб-интерфейс для просмотра юнитов Империи Disciples II
Данные и изображения хранятся локально
"""

import csv
import os
import json
from flask import Flask, render_template_string, send_from_directory

app = Flask(__name__)

# Папка с изображениями
IMAGES_DIR = os.path.join(os.path.dirname(__file__), 'images')


@app.route("/images/<path:filename>")
def serve_image(filename):
    """Отдаём локальные изображения"""
    return send_from_directory(IMAGES_DIR, filename)


def load_csv_data(filename="empire_units.csv"):
    """Загружаем данные из локального CSV"""
    filepath = os.path.join(os.path.dirname(__file__), filename)
    if not os.path.exists(filepath):
        return [], []
    with open(filepath, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        units = list(reader)
    # Пути к изображениям уже локальные (images/filename.png)
    # Добавляем / в начало для корректного URL
    for unit in units:
        if unit.get('image_url') and not unit['image_url'].startswith('/'):
            unit['image_url'] = '/' + unit['image_url']
    return columns, units


CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #fff;
    color: #1a1a1a;
    line-height: 1.5;
}

nav {
    position: fixed;
    top: 0; left: 0; right: 0;
    height: 52px;
    background: #fff;
    border-bottom: 1px solid #e5e5e5;
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 16px;
    z-index: 100;
}

.logo { font-size: 14px; font-weight: 600; }
.nav-links { display: flex; gap: 16px; }
.nav-links a { font-size: 13px; color: #666; text-decoration: none; }
.nav-links a:hover, .nav-links a.active { color: #000; }

main {
    max-width: 1600px;
    margin: 0 auto;
    padding: 68px 16px 48px;
}

h1 { font-size: 20px; font-weight: 600; margin-bottom: 4px; }
.sub { font-size: 12px; color: #666; margin-bottom: 20px; }

.controls {
    display: flex;
    gap: 12px;
    margin-bottom: 16px;
    flex-wrap: wrap;
    align-items: center;
}

.search input {
    width: 200px;
    padding: 8px 12px;
    font-size: 13px;
    border: 1px solid #ddd;
    border-radius: 4px;
    background: #fafafa;
}

.search input:focus {
    outline: none;
    border-color: #999;
    background: #fff;
}

.sort-info {
    font-size: 11px;
    color: #999;
}

/* TABLE */
.tbl-wrap {
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
    min-width: 1200px;
}

th {
    text-align: left;
    padding: 10px 8px;
    font-weight: 600;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #666;
    background: #fafafa;
    border-bottom: 1px solid #e5e5e5;
    white-space: nowrap;
    cursor: pointer;
    user-select: none;
    position: relative;
}

th:hover { background: #f0f0f0; }

th.sorted { color: #000; }
th.sorted::after {
    content: '';
    position: absolute;
    right: 4px;
    top: 50%;
    transform: translateY(-50%);
    border: 4px solid transparent;
}
th.asc::after { border-bottom-color: #000; margin-top: -4px; }
th.desc::after { border-top-color: #000; margin-top: 4px; }

th:first-child { cursor: default; }
th:first-child:hover { background: #fafafa; }

td {
    padding: 6px 8px;
    border-bottom: 1px solid #f0f0f0;
    vertical-align: middle;
    white-space: nowrap;
}

tr:hover td { background: #fafafa; }
tr:last-child td { border-bottom: none; }

.img-cell img {
    width: 32px; height: 32px;
    border-radius: 3px;
    background: #f5f5f5;
    object-fit: contain;
    display: block;
}

.name-cell { font-weight: 500; }
.hp { color: #dc2626; font-weight: 600; }
.dmg { color: #ea580c; font-weight: 600; }
.armor { color: #16a34a; font-weight: 600; }
.gold { color: #ca8a04; font-weight: 600; }

/* TREE */
.tree-wrap {
    display: grid;
    grid-template-columns: 1fr 380px 260px;
    gap: 24px;
    align-items: start;
}

.tree-main { min-width: 0; overflow-x: auto; }

.tree-img {
    position: sticky;
    top: 68px;
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 350px;
}

.tree-img img {
    width: 100%;
    height: auto;
    object-fit: contain;
    image-rendering: pixelated;
}

.tree-img .placeholder {
    color: #ccc;
    font-size: 12px;
}

.tree-info {
    position: sticky;
    top: 68px;
    height: fit-content;
}

.branch { margin-bottom: 28px; }

.branch-title {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #999;
    margin-bottom: 10px;
    padding-left: 10px;
    border-left: 2px solid #ddd;
}

.branch-title.warrior { border-color: #dc2626; color: #dc2626; }
.branch-title.mage { border-color: #2563eb; color: #2563eb; }
.branch-title.healer { border-color: #16a34a; color: #16a34a; }
.branch-title.archer { border-color: #ea580c; color: #ea580c; }
.branch-title.special { border-color: #7c3aed; color: #7c3aed; }

.evo-line {
    display: flex;
    align-items: center;
    gap: 6px;
    flex-wrap: wrap;
    margin-bottom: 6px;
}

.unit-card {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 5px 8px;
    background: #fff;
    border: 1px solid #e5e5e5;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.1s;
}

.unit-card:hover { border-color: #999; }
.unit-card.sel { background: #1a1a1a; border-color: #1a1a1a; color: #fff; }

.unit-card img {
    width: 24px; height: 24px;
    border-radius: 2px;
    background: #f5f5f5;
    object-fit: contain;
}

.unit-card .n { font-size: 11px; font-weight: 500; white-space: nowrap; }
.unit-card .l { font-size: 9px; color: #999; }
.unit-card.sel .l { color: #888; }

.arrow { color: #ccc; font-size: 11px; }

.fork {
    display: flex;
    flex-direction: column;
    gap: 6px;
    padding-left: 10px;
    border-left: 1px solid #e5e5e5;
}

/* INFO BOX */
.info-box {
    background: #fff;
    border: 1px solid #e5e5e5;
    border-radius: 6px;
    padding: 16px;
}

.info-empty {
    text-align: center;
    color: #999;
    padding: 16px 0;
    font-size: 12px;
}

.info-data { display: none; }
.info-data.show { display: block; }

.info-name { font-size: 16px; font-weight: 600; margin-bottom: 2px; }
.info-sub { font-size: 11px; color: #666; margin-bottom: 12px; }

.stats-4 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    margin-bottom: 12px;
}

.stat-box {
    background: #fafafa;
    padding: 8px;
    border-radius: 4px;
}

.stat-box .lbl {
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    color: #999;
    margin-bottom: 2px;
}

.stat-box .val { font-size: 14px; font-weight: 600; }
.stat-box .val.hp { color: #dc2626; }
.stat-box .val.dmg { color: #ea580c; }
.stat-box .val.armor { color: #16a34a; }
.stat-box .val.gold { color: #ca8a04; }

.extra {
    border-top: 1px solid #eee;
    padding-top: 10px;
}

.extra-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 11px;
    border-bottom: 1px solid #f5f5f5;
}

.extra-row:last-child { border-bottom: none; }
.extra-row .k { color: #666; }
.extra-row .v { font-weight: 500; }

.wiki-link {
    display: block;
    text-align: center;
    padding: 8px;
    margin-top: 10px;
    font-size: 11px;
    color: #666;
    border: 1px solid #e5e5e5;
    border-radius: 4px;
    text-decoration: none;
}

.wiki-link:hover { border-color: #999; color: #000; }

footer {
    text-align: center;
    padding: 20px;
    font-size: 11px;
    color: #999;
    border-top: 1px solid #eee;
    margin-top: 32px;
}

footer a { color: #666; text-decoration: none; }
footer a:hover { color: #000; }

/* RESPONSIVE */
@media (max-width: 1200px) {
    .tree-wrap { grid-template-columns: 1fr 280px 220px; gap: 16px; }
}

@media (max-width: 1024px) {
    main { padding: 60px 12px 32px; }
    h1 { font-size: 18px; }
    table { min-width: 900px; }
    .tree-wrap { grid-template-columns: 1fr 220px 200px; }
    .tree-img { min-height: 260px; }
}

@media (max-width: 800px) {
    .tree-wrap { 
        grid-template-columns: 1fr;
        gap: 16px;
    }
    .tree-img { 
        max-width: 300px;
        min-height: 300px;
        margin: 0 auto;
    }
    .tree-info { width: 100%; position: static; }
    .controls { flex-direction: column; align-items: stretch; }
    .search input { width: 100%; }
}

@media (max-width: 600px) {
    nav { padding: 0 12px; }
    .nav-links { gap: 12px; }
    .nav-links a { font-size: 12px; }
    main { padding: 56px 8px 24px; }
    h1 { font-size: 16px; }
    .sub { font-size: 11px; margin-bottom: 12px; }
    table { font-size: 11px; min-width: 700px; }
    th, td { padding: 6px; }
    .img-cell img { width: 28px; height: 28px; }
    .unit-card { padding: 4px 6px; }
    .unit-card img { width: 20px; height: 20px; }
    .unit-card .n { font-size: 10px; }
    .info-box { padding: 12px; }
    .tree-img { max-width: 220px; min-height: 220px; }
}
"""

TABLE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Империя — Disciples II</title>
    <style>""" + CSS + """</style>
</head>
<body>
    <nav>
        <div class="logo">Disciples II</div>
        <div class="nav-links">
            <a href="/" class="active">Таблица</a>
            <a href="/tree">Древо</a>
        </div>
    </nav>
    
    <main>
        <h1>Юниты Империи</h1>
        <p class="sub">{{ units|length }} существ</p>
        
        <div class="controls">
            <div class="search">
                <input type="text" id="q" placeholder="Поиск..." oninput="filter()">
            </div>
            <div class="sort-info" id="sort-info">Нажмите на заголовок для сортировки</div>
        </div>
        
        <div class="tbl-wrap">
            <table id="tbl">
                <thead>
                    <tr>
                        <th data-col="0"></th>
                        <th data-col="1" data-type="str">Имя</th>
                        <th data-col="2" data-type="num">Ур.</th>
                        <th data-col="3" data-type="num">HP</th>
                        <th data-col="4" data-type="num">Броня</th>
                        <th data-col="5" data-type="str">Атака</th>
                        <th data-col="6" data-type="num">Урон</th>
                        <th data-col="7" data-type="num">Иниц.</th>
                        <th data-col="8" data-type="str">Источник</th>
                        <th data-col="9" data-type="str">Шанс</th>
                        <th data-col="10" data-type="str">Дальн.</th>
                        <th data-col="11" data-type="num">Целей</th>
                        <th data-col="12" data-type="str">Защита</th>
                        <th data-col="13" data-type="str">Иммунитет</th>
                        <th data-col="14" data-type="num">Цена</th>
                        <th data-col="15" data-type="num">XP kill</th>
                        <th data-col="16" data-type="num">XP next</th>
                    </tr>
                </thead>
                <tbody>
                    {% for u in units %}
                    <tr>
                        <td class="img-cell">{% if u.image_url %}<img src="{{ u.image_url }}" alt="">{% endif %}</td>
                        <td class="name-cell">{{ u.name }}</td>
                        <td>{{ u.get('Уровень', '—') }}</td>
                        <td class="hp">{{ u.get('Здоровье', '—') }}</td>
                        <td class="armor">{{ u.get('Броня', '—') }}</td>
                        <td>{{ u.get('Атака', '—') }}</td>
                        <td class="dmg">{{ u.get('Урон', '—') }}</td>
                        <td>{{ u.get('Инициатива', '—') }}</td>
                        <td>{{ u.get('Источник', '—') }}</td>
                        <td>{{ u.get('Шанс попадания', '—') }}</td>
                        <td>{{ u.get('Дальность', '—') }}</td>
                        <td>{{ u.get('Кол-во целей', '—') }}</td>
                        <td>{{ u.get('Защита', '—') }}</td>
                        <td>{{ u.get('Иммунитет', '—') }}</td>
                        <td class="gold">{{ u.get('Цена', '—') }}</td>
                        <td>{{ u.get('Опыт за убийство', '—') }}</td>
                        <td>{{ u.get('Опыт до апгрейда', '—') }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </main>
    
    <footer>Данные: <a href="https://disciples.fandom.com" target="_blank">Disciples Wiki</a></footer>
    
    <script>
    // Фильтрация
    function filter() {
        const q = document.getElementById('q').value.toLowerCase();
        document.querySelectorAll('#tbl tbody tr').forEach(r => {
            r.style.display = r.textContent.toLowerCase().includes(q) ? '' : 'none';
        });
    }
    
    // Сортировка
    let currentSort = { col: -1, dir: 'asc' };
    
    document.querySelectorAll('#tbl th[data-col]').forEach(th => {
        if (th.dataset.col === '0') return; // Пропускаем колонку с картинкой
        
        th.addEventListener('click', () => {
            const col = parseInt(th.dataset.col);
            const type = th.dataset.type;
            
            // Определяем направление
            if (currentSort.col === col) {
                currentSort.dir = currentSort.dir === 'asc' ? 'desc' : 'asc';
            } else {
                currentSort.col = col;
                currentSort.dir = 'asc';
            }
            
            // Обновляем классы заголовков
            document.querySelectorAll('#tbl th').forEach(h => {
                h.classList.remove('sorted', 'asc', 'desc');
            });
            th.classList.add('sorted', currentSort.dir);
            
            // Сортируем строки
            const tbody = document.querySelector('#tbl tbody');
            const rows = Array.from(tbody.querySelectorAll('tr'));
            
            rows.sort((a, b) => {
                let aVal = a.cells[col].textContent.trim();
                let bVal = b.cells[col].textContent.trim();
                
                // Для числовых колонок
                if (type === 'num') {
                    // Извлекаем первое число из строки
                    const aNum = parseFloat(aVal.replace(/[^0-9.-]/g, '')) || 0;
                    const bNum = parseFloat(bVal.replace(/[^0-9.-]/g, '')) || 0;
                    return currentSort.dir === 'asc' ? aNum - bNum : bNum - aNum;
                }
                
                // Для строковых колонок
                if (aVal === '—') aVal = '';
                if (bVal === '—') bVal = '';
                return currentSort.dir === 'asc' 
                    ? aVal.localeCompare(bVal, 'ru') 
                    : bVal.localeCompare(aVal, 'ru');
            });
            
            // Перестраиваем таблицу
            rows.forEach(row => tbody.appendChild(row));
            
            // Обновляем инфо
            const colName = th.textContent;
            document.getElementById('sort-info').textContent = 
                `Сортировка: ${colName} (${currentSort.dir === 'asc' ? '↑' : '↓'})`;
        });
    });
    </script>
</body>
</html>
"""

TREE_HTML = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Древо — Disciples II</title>
    <style>""" + CSS + """</style>
</head>
<body>
    <nav>
        <div class="logo">Disciples II</div>
        <div class="nav-links">
            <a href="/">Таблица</a>
            <a href="/tree" class="active">Древо</a>
        </div>
    </nav>
    
    <main>
        <h1>Древо развития</h1>
        <p class="sub">Нажмите на юнита</p>
        
        <div class="tree-wrap">
            <div class="tree-main">
                
                <!-- ВОИНЫ -->
                <div class="branch">
                    <div class="branch-title warrior">Воины</div>
                    <div class="evo-line">
                        <div class="unit-card" data-u="Сквайр">
                            <img src="{{ m.get('Сквайр', {}).get('image_url', '') }}"><div><div class="n">Сквайр</div><div class="l">Ур.1</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Рыцарь">
                            <img src="{{ m.get('Рыцарь', {}).get('image_url', '') }}"><div><div class="n">Рыцарь</div><div class="l">Ур.2</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Имперский рыцарь">
                            <img src="{{ m.get('Имперский рыцарь', {}).get('image_url', '') }}"><div><div class="n">Имп. рыцарь</div><div class="l">Ур.3</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="fork">
                            <div class="unit-card" data-u="Ангел">
                                <img src="{{ m.get('Ангел', {}).get('image_url', '') }}"><div><div class="n">Ангел</div><div class="l">Ур.4</div></div>
                            </div>
                            <div class="unit-card" data-u="Паладин">
                                <img src="{{ m.get('Паладин', {}).get('image_url', '') }}"><div><div class="n">Паладин</div><div class="l">Ур.4</div></div>
                            </div>
                        </div>
                    </div>
                    <div class="evo-line" style="margin-left:160px;">
                        <span class="arrow">↳</span>
                        <div class="fork">
                            <div class="unit-card" data-u="Святой мститель">
                                <img src="{{ m.get('Святой мститель', {}).get('image_url', '') }}"><div><div class="n">Святой мститель</div><div class="l">Ур.5</div></div>
                            </div>
                            <div class="unit-card" data-u="Защитник Веры">
                                <img src="{{ m.get('Защитник Веры', {}).get('image_url', '') }}"><div><div class="n">Защитник Веры</div><div class="l">Ур.5</div></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ИНКВИЗИЦИЯ -->
                <div class="branch">
                    <div class="branch-title warrior">Инквизиция</div>
                    <div class="evo-line">
                        <div class="unit-card" data-u="Сквайр">
                            <img src="{{ m.get('Сквайр', {}).get('image_url', '') }}"><div><div class="n">Сквайр</div><div class="l">Ур.1</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Охотник на ведьм">
                            <img src="{{ m.get('Охотник на ведьм', {}).get('image_url', '') }}"><div><div class="n">Охотник на ведьм</div><div class="l">Ур.2</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Инквизитор">
                            <img src="{{ m.get('Инквизитор', {}).get('image_url', '') }}"><div><div class="n">Инквизитор</div><div class="l">Ур.3</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Великий инквизитор">
                            <img src="{{ m.get('Великий инквизитор', {}).get('image_url', '') }}"><div><div class="n">Вел. инквизитор</div><div class="l">Ур.4</div></div>
                        </div>
                    </div>
                </div>
                
                <!-- ЛУЧНИКИ -->
                <div class="branch">
                    <div class="branch-title archer">Лучники</div>
                    <div class="evo-line">
                        <div class="unit-card" data-u="Лучник">
                            <img src="{{ m.get('Лучник', {}).get('image_url', '') }}"><div><div class="n">Лучник</div><div class="l">Ур.1</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Стрелок">
                            <img src="{{ m.get('Стрелок', {}).get('image_url', '') }}"><div><div class="n">Стрелок</div><div class="l">Ур.2</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Имперский ассасин">
                            <img src="{{ m.get('Имперский ассасин', {}).get('image_url', '') }}"><div><div class="n">Имп. ассасин</div><div class="l">Ур.3</div></div>
                        </div>
                    </div>
                </div>
                
                <!-- МАГИ -->
                <div class="branch">
                    <div class="branch-title mage">Маги</div>
                    <div class="evo-line">
                        <div class="unit-card" data-u="Ученик">
                            <img src="{{ m.get('Ученик', {}).get('image_url', '') }}"><div><div class="n">Ученик</div><div class="l">Ур.1</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="unit-card" data-u="Маг">
                            <img src="{{ m.get('Маг', {}).get('image_url', '') }}"><div><div class="n">Маг</div><div class="l">Ур.2</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="fork">
                            <div class="evo-line">
                                <div class="unit-card" data-u="Волшебник">
                                    <img src="{{ m.get('Волшебник', {}).get('image_url', '') }}"><div><div class="n">Волшебник</div><div class="l">Ур.3</div></div>
                                </div>
                                <span class="arrow">→</span>
                                <div class="unit-card" data-u="Белый волшебник">
                                    <img src="{{ m.get('Белый волшебник', {}).get('image_url', '') }}"><div><div class="n">Белый волшебник</div><div class="l">Ур.4</div></div>
                                </div>
                            </div>
                            <div class="unit-card" data-u="Элементалист">
                                <img src="{{ m.get('Элементалист', {}).get('image_url', '') }}"><div><div class="n">Элементалист</div><div class="l">Ур.3</div></div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ЖРЕЦЫ -->
                <div class="branch">
                    <div class="branch-title healer">Жрецы</div>
                    <div class="evo-line">
                        <div class="unit-card" data-u="Послушник">
                            <img src="{{ m.get('Послушник', {}).get('image_url', '') }}"><div><div class="n">Послушник</div><div class="l">Ур.1</div></div>
                        </div>
                        <span class="arrow">→</span>
                        <div class="fork">
                            <div class="evo-line">
                                <div class="unit-card" data-u="Жрец">
                                    <img src="{{ m.get('Жрец', {}).get('image_url', '') }}"><div><div class="n">Жрец</div><div class="l">Ур.2</div></div>
                                </div>
                                <span class="arrow">→</span>
                                <div class="unit-card" data-u="Имперский жрец">
                                    <img src="{{ m.get('Имперский жрец', {}).get('image_url', '') }}"><div><div class="n">Имп. жрец</div><div class="l">Ур.3</div></div>
                                </div>
                                <span class="arrow">→</span>
                                <div class="unit-card" data-u="Иерофант">
                                    <img src="{{ m.get('Иерофант', {}).get('image_url', '') }}"><div><div class="n">Иерофант</div><div class="l">Ур.4</div></div>
                                </div>
                            </div>
                            <div class="evo-line">
                                <div class="unit-card" data-u="Клирик">
                                    <img src="{{ m.get('Клирик', {}).get('image_url', '') }}"><div><div class="n">Клирик</div><div class="l">Ур.2</div></div>
                                </div>
                                <span class="arrow">→</span>
                                <div class="unit-card" data-u="Матриарх">
                                    <img src="{{ m.get('Матриарх', {}).get('image_url', '') }}"><div><div class="n">Матриарх</div><div class="l">Ур.3</div></div>
                                </div>
                                <span class="arrow">→</span>
                                <div class="unit-card" data-u="Прорицательница">
                                    <img src="{{ m.get('Прорицательница', {}).get('image_url', '') }}"><div><div class="n">Прорицательница</div><div class="l">Ур.4</div></div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- ОСОБЫЕ -->
                <div class="branch">
                    <div class="branch-title special">Особые</div>
                    <div class="evo-line">
                        <div class="unit-card" data-u="Титан">
                            <img src="{{ m.get('Титан', {}).get('image_url', '') }}"><div><div class="n">Титан</div><div class="l">Большой</div></div>
                        </div>
                        <div class="unit-card" data-u="Оживший доспех">
                            <img src="{{ m.get('Оживший доспех', {}).get('image_url', '') }}"><div><div class="n">Оживший доспех</div><div class="l">Большой</div></div>
                        </div>
                        <div class="unit-card" data-u="Голем">
                            <img src="{{ m.get('Голем', {}).get('image_url', '') }}"><div><div class="n">Голем</div><div class="l">Большой</div></div>
                        </div>
                        <div class="unit-card" data-u="Мизраэль">
                            <img src="{{ m.get('Мизраэль', {}).get('image_url', '') }}"><div><div class="n">Мизраэль</div><div class="l">Босс</div></div>
                        </div>
                    </div>
                </div>
                
            </div>
            
            <!-- IMAGE CENTER -->
            <div class="tree-img" id="img-box">
                <span class="placeholder">Выберите юнита</span>
                <img id="i-img" src="" alt="" style="display:none;">
            </div>
            
            <!-- INFO RIGHT -->
            <div class="tree-info">
                <div class="info-box">
                    <div class="info-empty" id="empty">Характеристики</div>
                    <div class="info-data" id="info">
                        <div class="info-name" id="i-name"></div>
                        <div class="info-sub" id="i-sub"></div>
                        
                        <div class="stats-4">
                            <div class="stat-box"><div class="lbl">HP</div><div class="val hp" id="i-hp">—</div></div>
                            <div class="stat-box"><div class="lbl">Броня</div><div class="val armor" id="i-armor">—</div></div>
                            <div class="stat-box"><div class="lbl">Урон</div><div class="val dmg" id="i-dmg">—</div></div>
                            <div class="stat-box"><div class="lbl">Цена</div><div class="val gold" id="i-cost">—</div></div>
                        </div>
                        
                        <div class="extra">
                            <div class="extra-row"><span class="k">Уровень</span><span class="v" id="i-lvl">—</span></div>
                            <div class="extra-row"><span class="k">Атака</span><span class="v" id="i-atk">—</span></div>
                            <div class="extra-row"><span class="k">Инициатива</span><span class="v" id="i-init">—</span></div>
                            <div class="extra-row"><span class="k">Источник</span><span class="v" id="i-src">—</span></div>
                            <div class="extra-row"><span class="k">Шанс попадания</span><span class="v" id="i-hit">—</span></div>
                            <div class="extra-row"><span class="k">Дальность</span><span class="v" id="i-reach">—</span></div>
                            <div class="extra-row"><span class="k">Кол-во целей</span><span class="v" id="i-tgt">—</span></div>
                            <div class="extra-row"><span class="k">Защита</span><span class="v" id="i-ward">—</span></div>
                            <div class="extra-row"><span class="k">Иммунитет</span><span class="v" id="i-imm">—</span></div>
                            <div class="extra-row"><span class="k">XP за убийство</span><span class="v" id="i-xpk">—</span></div>
                            <div class="extra-row"><span class="k">XP до апгрейда</span><span class="v" id="i-xpn">—</span></div>
                        </div>
                        
                        <a href="#" class="wiki-link" id="i-link" target="_blank">Wiki →</a>
                    </div>
                </div>
            </div>
        </div>
    </main>
    
    <footer>Данные: <a href="https://disciples.fandom.com" target="_blank">Disciples Wiki</a></footer>
    
    <script>
    const D = {{ data | safe }};
    
    document.querySelectorAll('.unit-card').forEach(c => {
        c.addEventListener('click', () => {
            document.querySelectorAll('.unit-card').forEach(x => x.classList.remove('sel'));
            c.classList.add('sel');
            
            const n = c.dataset.u;
            const u = D[n];
            if (!u) return;
            
            // Центральное изображение
            const imgBox = document.getElementById('img-box');
            const img = document.getElementById('i-img');
            const placeholder = imgBox.querySelector('.placeholder');
            
            if (u.image_url) {
                img.src = u.image_url;
                img.style.display = 'block';
                if (placeholder) placeholder.style.display = 'none';
            }
            
            // Панель данных
            document.getElementById('empty').style.display = 'none';
            document.getElementById('info').classList.add('show');
            
            document.getElementById('i-name').textContent = n;
            document.getElementById('i-sub').textContent = u.name_en || '';
            
            document.getElementById('i-hp').textContent = u['Здоровье'] || '—';
            document.getElementById('i-armor').textContent = u['Броня'] || '—';
            document.getElementById('i-dmg').textContent = u['Урон'] || '—';
            document.getElementById('i-cost').textContent = u['Цена'] || '—';
            
            document.getElementById('i-lvl').textContent = u['Уровень'] || '—';
            document.getElementById('i-atk').textContent = u['Атака'] || '—';
            document.getElementById('i-init').textContent = u['Инициатива'] || '—';
            document.getElementById('i-src').textContent = u['Источник'] || '—';
            document.getElementById('i-hit').textContent = u['Шанс попадания'] || '—';
            document.getElementById('i-reach').textContent = u['Дальность'] || '—';
            document.getElementById('i-tgt').textContent = u['Кол-во целей'] || '—';
            document.getElementById('i-ward').textContent = u['Защита'] || '—';
            document.getElementById('i-imm').textContent = u['Иммунитет'] || '—';
            document.getElementById('i-xpk').textContent = u['Опыт за убийство'] || '—';
            document.getElementById('i-xpn').textContent = u['Опыт до апгрейда'] || '—';
            
            document.getElementById('i-link').href = u.url || '#';
        });
    });
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    cols, units = load_csv_data()
    if not units:
        return "<h1>Запустите python parser.py</h1>"
    return render_template_string(TABLE_HTML, units=units)


@app.route("/tree")
def tree():
    cols, units = load_csv_data()
    if not units:
        return "<h1>Запустите python parser.py</h1>"
    m = {u['name']: u for u in units}
    return render_template_string(TREE_HTML, m=m, data=json.dumps(m, ensure_ascii=False))


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    print(f"\nDisciples II — http://127.0.0.1:{port}\n")
    app.run(debug=False, host="0.0.0.0", port=port)
