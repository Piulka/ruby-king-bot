# System Patterns: Ruby King Bot Architecture

## Architecture Overview

### Modular Design Pattern
```
ruby_king_bot/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Основные настройки
│   └── token.py            # Токен игры (отдельный файл)
├── core/
│   ├── __init__.py
│   ├── game_state.py       # Управление состоянием игры
│   ├── player.py           # Логика персонажа
│   └── mob.py              # Логика мобов
├── api/
│   ├── __init__.py
│   ├── client.py           # HTTP клиент для API
│   ├── endpoints.py        # Определения эндпоинтов
│   └── responses.py        # Обработка ответов API
├── logic/
│   ├── __init__.py
│   ├── combat.py           # Боевая логика
│   ├── healing.py          # Логика восстановления
│   └── resting.py          # Логика отдыха
├── ui/
│   ├── __init__.py
│   ├── display.py          # Отображение интерфейса
│   ├── progress_bars.py    # Прогресс-бары
│   └── statistics.py       # Статистическая таблица
├── utils/
│   ├── __init__.py
│   ├── logger.py           # Система логирования
│   └── timers.py           # Управление таймерами
└── main.py                 # Точка входа
```

## Core Design Patterns

### 1. State Machine Pattern
```python
class GameState:
    CITY = "city"           # В городе/главном меню
    EXPLORING = "exploring" # Поиск моба (временно)
    COMBAT = "combat"       # В бою с мобом (после explore)
    RESTING = "resting"     # Отдых у костра
    HEALING = "healing"     # Использование зелья
```

### 2. Observer Pattern
- **GameState** уведомляет **UI** об изменениях
- **Player** уведомляет **Logic** об изменении ресурсов
- **API** уведомляет **Core** о новых данных

### 3. Strategy Pattern
```python
class ActionStrategy:
    def should_attack(self, player, mob) -> bool
    def should_heal(self, player) -> bool
    def should_rest(self, player) -> bool
    def should_explore(self, player) -> bool
    # КРИТИЧНО: explore только если не в бою
```

### 4. Factory Pattern
```python
class APIEndpointFactory:
    def create_explore_request()
    def create_attack_request(mob_id)
    def create_heal_request()
    def create_rest_request()
```

## Critical Combat Flow

### Combat State Management
```python
class CombatManager:
    def __init__(self):
        self.current_mob = None
        self.combat_active = False
    
    def start_combat(self, mob_data):
        """Начинает бой после explore запроса"""
        self.current_mob = Mob(mob_data)
        self.combat_active = True
        return GameState.COMBAT
    
    def continue_combat(self, player):
        """Продолжает бой до победы"""
        if self.current_mob.hp <= 0:
            return self.end_combat()
        
        if player.hp < 50 and can_heal():
            use_healing_potion()
        
        attack_mob(self.current_mob.id)
        time.sleep(5)  # Attack cooldown
        return GameState.COMBAT
    
    def end_combat(self):
        """Завершает бой после победы"""
        self.combat_active = False
        self.current_mob = None
        return GameState.CITY
```

### Updated Game Flow
```python
def main_game_loop():
    while True:
        current_state = determine_current_state()
        
        if current_state == GameState.CITY:
            # Можно исследовать территорию
            explore_result = explore_territory()
            if explore_result.has_mob:
                # АВТОМАТИЧЕСКИ переходим в бой
                current_state = GameState.COMBAT
                start_combat(explore_result.mob_data)
        
        elif current_state == GameState.COMBAT:
            # Должны завершить бой до следующего explore
            if mob.hp <= 0:
                # Победа - возвращаемся в город
                current_state = GameState.CITY
            else:
                # Продолжаем бой
                attack_mob(mob.id)
                time.sleep(5)
        
        elif current_state == GameState.RESTING:
            # Ждем окончания отдыха
            if rest_timer.is_finished():
                end_rest()
                current_state = GameState.CITY
```

## Data Flow Architecture

### Request Flow
```
UI Event → Game State → Action Strategy → API Client → Ruby King Server
```

### Response Flow
```
Ruby King Server → API Client → Response Parser → Game State → UI Update
```

### State Management Flow
```
API Response → State Analyzer → State Machine → Action Decider → Next Action
```

### Critical Combat Flow
```
Explore Request → [AUTO COMBAT] → Attack Loop → Victory → Back to City
```

## Component Responsibilities

### Core Components
- **GameState**: Центральное управление состоянием игры
- **Player**: Управление данными персонажа (HP, MP, Stamina)
- **Mob**: Управление данными моба (HP, характеристики)
- **CombatManager**: КРИТИЧНО - управление боевым состоянием

### API Components
- **Client**: HTTP запросы к Ruby King API
- **Endpoints**: Определения всех API эндпоинтов
- **Responses**: Парсинг и валидация ответов

### Logic Components
- **Combat**: Боевая логика и атаки (КРИТИЧНО - принудительное завершение)
- **Healing**: Логика восстановления здоровья
- **Resting**: Логика отдыха у костра

### UI Components
- **Display**: Основной интерфейс
- **ProgressBars**: Визуализация HP
- **Statistics**: Таблица статистики

## Error Handling Patterns

### 1. Retry Pattern
```python
def api_request_with_retry(endpoint, max_retries=3):
    for attempt in range(max_retries):
        try:
            return make_api_request(endpoint)
        except APIError as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(2 ** attempt)  # Exponential backoff
```

### 2. Circuit Breaker Pattern
```python
class APICircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failure_count = 0
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.last_failure_time = None
```

### 3. Graceful Degradation
- При ошибках API → переход в безопасный режим
- При потере соединения → сохранение состояния
- При некорректных данных → логирование и продолжение
- **КРИТИЧНО**: При ошибках в бою → принудительное завершение

### 4. Combat Error Recovery
```python
def handle_combat_error(error):
    """Обработка ошибок во время боя"""
    logger.error(f"Combat error: {error}")
    
    # Пытаемся определить состояние
    try:
        current_state = check_current_state()
        if current_state == GameState.COMBAT:
            # Продолжаем бой
            continue_combat()
        else:
            # Возвращаемся в город
            return GameState.CITY
    except:
        # Принудительно завершаем бой
        force_end_combat()
        return GameState.CITY
```

## Configuration Management

### Environment-based Configuration
```python
class Config:
    API_BASE_URL = "https://ruby-king.ru/api"
    REQUEST_TIMEOUT = 30
    ATTACK_COOLDOWN = 5
    HEAL_COOLDOWN = 30
    REST_DURATION = 1200  # 20 minutes
    HEAL_THRESHOLD = 50   # HP threshold for healing
    STAMINA_THRESHOLD = 0 # Stamina threshold for resting
    # КРИТИЧНО: Настройки боевого состояния
    COMBAT_TIMEOUT = 300  # Максимальное время боя (5 минут)
    FORCE_END_COMBAT = True  # Принудительное завершение боя
```

### Token Management
```python
# config/token.py
GAME_TOKEN = "1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec"
```

## Logging Strategy

### Structured Logging
```python
class GameLogger:
    def log_state_change(self, old_state, new_state)
    def log_combat_action(self, action, result)
    def log_resource_change(self, resource, old_value, new_value)
    def log_api_request(self, endpoint, response)
    # КРИТИЧНО: Логирование боевого состояния
    def log_combat_start(self, mob_data)
    def log_combat_end(self, result, duration)
    def log_combat_error(self, error, recovery_action)
```

### Log Levels
- **DEBUG**: Детальная информация о запросах
- **INFO**: Основные действия и изменения состояния
- **WARNING**: Потенциальные проблемы
- **ERROR**: Ошибки API и системы
- **CRITICAL**: КРИТИЧНО - проблемы с боевым состоянием

## Testing Strategy

### Unit Testing
- Тестирование каждой логической компоненты
- Мокирование API ответов
- Тестирование состояний игры
- **КРИТИЧНО**: Тестирование боевого цикла

### Integration Testing
- Тестирование полного цикла игры
- Тестирование API взаимодействий
- Тестирование UI обновлений
- **КРИТИЧНО**: Тестирование explore → combat → victory цикла

### End-to-End Testing
- Полный игровой цикл
- Обработка ошибок
- Долгосрочная стабильность
- **КРИТИЧНО**: Тестирование восстановления после сбоев в бою

### Combat Testing Scenarios
```python
def test_combat_scenarios():
    # Тест 1: Нормальный бой
    test_normal_combat_cycle()
    
    # Тест 2: Бой с ошибками
    test_combat_with_errors()
    
    # Тест 3: Принудительное завершение
    test_force_end_combat()
    
    # Тест 4: Восстановление после сбоя
    test_combat_recovery()
``` 