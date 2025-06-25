"""
База данных предметов Ruby King
Сопоставление ID предметов с их названиями
"""

# База данных предметов: {item_id: item_name}
ITEM_DATABASE = {
    # Ресурсы (Resources)
    "m_0_1": "Золото",
    "m_0_2": "Черепа", 
    "m_1": "Зелье лечения",
    "m_3": "Зелье маны",
    "m_11": "Железо",
    "m_17": "Драгоценный камень",
    "res_25": "Дерево",
    "quest_0_1": "Квестовый предмет",
    "book_skill_16_page": "Страница навыка",
    
    # Оружие (Weapons) - на основе изображений
    "weapon_1": "Меч",  # w-1.jpg
    "weapon_2": "Меч",  # w-2.jpg
    "weapon_46": "Топор",  # w-46.jpg
    "weapon_47": "Кинжал",  # w-47.jpg
    "weapon_48": "Топор",  # w-48.jpg
    
    # Броня (Armors) - на основе изображений
    "armor_81": "Перчатки",  # armor-81.jpg
    "armor_86": "Перчатки",  # armor-86.jpg
    "armor_89": "Сапоги",  # armor-89.jpg
    "armor_92": "Сапоги",  # armor-92.jpg
    "armor_97": "Шлем",  # armor-97.jpg
    "armor_101": "Шлем",  # a-101.jpg
    "armor_102": "Нагрудник",  # a-102.jpg
    "armor_103": "Штаны",  # a-103.jpg
    "armor_104": "Сапоги",  # a-104.jpg
    "armor_105": "Перчатки",  # a-105.jpg
    "armor_106": "Кольцо",  # a-106.jpg
    
    # Украшения (Jewelry) - на основе изображений
    "jew_2": "Кольцо",  # jew-2.webp
    "jew_3": "Амулет",  # jew-3.webp
}

def get_item_name(item_id: str) -> str:
    """
    Получить название предмета по его ID
    
    Args:
        item_id: ID предмета
        
    Returns:
        Название предмета или ID если название не найдено
    """
    return ITEM_DATABASE.get(item_id, item_id)

def get_item_category(item_id: str) -> str:
    """
    Получить категорию предмета по его ID
    
    Args:
        item_id: ID предмета
        
    Returns:
        Категория предмета
    """
    if item_id.startswith("m_") or item_id.startswith("res_") or item_id.startswith("quest_") or item_id.startswith("book_"):
        return "Ресурсы"
    elif item_id.startswith("weapon_"):
        return "Оружие"
    elif item_id.startswith("armor_"):
        return "Броня"
    elif item_id.startswith("jew_"):
        return "Украшения"
    else:
        return "Неизвестно"

def format_item_display(item_id: str, count: int = 1) -> str:
    """
    Форматировать отображение предмета для UI
    
    Args:
        item_id: ID предмета
        count: Количество предметов
        
    Returns:
        Отформатированная строка для отображения
    """
    item_name = get_item_name(item_id)
    category = get_item_category(item_id)
    
    if count == 1:
        return f"{item_name} ({category})"
    else:
        return f"{item_name} x{count} ({category})"

def get_item_emoji(item_id: str) -> str:
    """
    Получить эмодзи для предмета
    
    Args:
        item_id: ID предмета
        
    Returns:
        Эмодзи для предмета
    """
    emoji_map = {
        # Ресурсы
        "m_0_1": "💰",  # Золото
        "m_0_2": "💀",  # Черепа
        "m_1": "💚",   # Зелье лечения
        "m_3": "🔵",   # Зелье маны
        "m_11": "⚒️",  # Железо
        "m_17": "💎",  # Драгоценный камень
        "res_25": "🪵", # Дерево
        "quest_0_1": "📜", # Квестовый предмет
        "book_skill_16_page": "📖", # Страница навыка
        
        # Оружие
        "weapon_1": "⚔️",   # Меч
        "weapon_2": "⚔️",   # Меч
        "weapon_46": "🪓",  # Топор
        "weapon_47": "🗡️",  # Кинжал
        "weapon_48": "🪓",  # Топор
        
        # Броня
        "armor_81": "🧤",   # Перчатки
        "armor_86": "🧤",   # Перчатки
        "armor_89": "👢",   # Сапоги
        "armor_92": "👢",   # Сапоги
        "armor_97": "🪖",   # Шлем
        "armor_101": "🪖",  # Шлем
        "armor_102": "🛡️",  # Нагрудник
        "armor_103": "👖",  # Штаны
        "armor_104": "👢",  # Сапоги
        "armor_105": "🧤",  # Перчатки
        "armor_106": "💍",  # Кольцо
        
        # Украшения
        "jew_2": "💍",      # Кольцо
        "jew_3": "📿",      # Амулет
    }
    
    return emoji_map.get(item_id, "❓")

def format_item_display_with_emoji(item_id: str, count: int = 1) -> str:
    """
    Форматировать отображение предмета для UI с эмодзи
    
    Args:
        item_id: ID предмета
        count: Количество предметов
        
    Returns:
        Отформатированная строка для отображения с эмодзи
    """
    item_name = get_item_name(item_id)
    emoji = get_item_emoji(item_id)
    
    if count == 1:
        return f"{emoji}{item_name}"
    else:
        return f"{emoji}{item_name} x{count}" 