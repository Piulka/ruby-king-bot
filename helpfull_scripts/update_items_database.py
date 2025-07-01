import json
import os

# Пути к файлам
BASE = "world_map_viewer/data"
REC_PATH = os.path.join(BASE, "Rec.json")
MOBS_PATH = os.path.join(BASE, "mobs-database.json")
ITEMS_PATH = os.path.join(BASE, "items-database.json")

# Загрузка данных
with open(REC_PATH, encoding='utf-8') as f:
    rec_data = json.load(f)
with open(MOBS_PATH, encoding='utf-8') as f:
    mobs_data = json.load(f)
with open(ITEMS_PATH, encoding='utf-8') as f:
    items_data = json.load(f)

# Индексируем предметы по id
items_by_id = {item['id']: item for item in items_data}

# Индексируем рецепты по id
if isinstance(rec_data, dict) and 'list' in rec_data:
    rec_items = rec_data['list']
else:
    rec_items = rec_data

rec_by_id = {item['id']: item for item in rec_items}

# Собираем все уникальные id предметов
all_item_ids = set(items_by_id) | set(rec_by_id)

# Собираем инфу о дропах
drops_map = {}
for mob in mobs_data:
    for drop in mob.get('drop', []):
        drop_id = drop.get('id')
        if not drop_id:
            continue
        if drop_id not in drops_map:
            drops_map[drop_id] = []
        drops_map[drop_id].append({
            "mobId": mob.get('id'),
            "mobName": mob.get('name'),
            "location": mob.get('location'),
            "chance": drop.get('chance'),
            "count": drop.get('count')
        })

# Формируем итоговый список предметов
result = []
for item_id in all_item_ids:
    # Приоритет: Rec.json > items-database.json
    item = rec_by_id.get(item_id, items_by_id.get(item_id, {})).copy()
    item['id'] = item_id
    # Тип
    if 'type' not in item:
        item['type'] = item.get('typeElement', 'resources')
    # Дропы
    if item_id in drops_map:
        item['dropsFrom'] = drops_map[item_id]
    result.append(item)

# Сохраняем
with open(ITEMS_PATH, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# Также сохраняем в all-items-database.json
ALL_ITEMS_PATH = os.path.join(BASE, "all-items-database.json")
with open(ALL_ITEMS_PATH, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print('items-database.json и all-items-database.json обновлены!') 