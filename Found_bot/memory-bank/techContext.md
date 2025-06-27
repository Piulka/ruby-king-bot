# Technical Context: Ruby King Bot

## Technology Stack

### Core Technologies
- **Python 3.8+** - основной язык разработки
- **requests** - HTTP клиент для API запросов
- **asyncio** - асинхронное программирование (опционально)
- **threading** - многопоточность для UI и API

### Development Tools
- **logging** - встроенная система логирования Python
- **json** - обработка JSON ответов API
- **time** - управление таймерами и задержками
- **datetime** - работа с временными метками

### External Dependencies
```python
# requirements.txt
requests>=2.28.0
colorama>=0.4.6      # Цветной вывод в консоль
rich>=13.0.0         # Красивые таблицы и прогресс-бары
python-dotenv>=1.0.0 # Управление переменными окружения
```

## API Integration

### Base Configuration
```python
API_BASE_URL = "https://ruby-king.ru/api"
GAME_URL = "https://ruby-king.ru/city"
TOKEN_PARAM = "name"
```

### API Endpoints

#### 1. Исследование территории
```python
ENDPOINT_EXPLORE = "/farm/farm-mob-one"
METHOD: POST
DATA: {"loco": "loco_0", "direction": "north"}
```

#### 2. Атака моба
```python
ENDPOINT_ATTACK = "/battle/user-attack"
METHOD: POST
DATA: {"mobId": "mob_id_from_explore"}
```

#### 3. Использование зелья
```python
ENDPOINT_HEAL = "/user/inventory/use-potion"
METHOD: POST
DATA: {"elemId": "m_1"}
```

#### 4. Разжигание костра
```python
ENDPOINT_START_REST = "/farm/add-fire"
METHOD: POST
DATA: {}
```

#### 5. Тушение костра
```python
ENDPOINT_END_REST = "/farm/add-fire-end"
METHOD: POST
DATA: {}
```

### HTTP Headers
```python
DEFAULT_HEADERS = {
    'Accept': 'application/json, text/plain, */*',
    'Accept-Language': 'ru,en;q=0.9,en-US;q=0.8,de;q=0.7',
    'Connection': 'keep-alive',
    'Content-Type': 'application/json',
    'Origin': 'https://ruby-king.ru',
    'Referer': 'https://ruby-king.ru/city',
    'Sec-Fetch-Dest': 'empty',
    'Sec-Fetch-Mode': 'cors',
    'Sec-Fetch-Site': 'same-origin',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36',
    'sec-ch-ua': '"Google Chrome";v="137", "Chromium";v="137", "Not/A)Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"macOS"'
}
```

## Development Environment

### Project Structure
```
r_king/
├── memory-bank/           # Документация проекта
├── ruby_king_bot/         # Основной код бота
├── config/               # Конфигурационные файлы
├── logs/                 # Логи работы бота
├── tests/                # Тесты
├── requirements.txt      # Зависимости Python
├── README.md            # Документация
└── .gitignore           # Исключения Git
```

### Configuration Files
```python
# config/token.py
GAME_TOKEN = "1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec"

# config/settings.py
class Settings:
    API_BASE_URL = "https://ruby-king.ru/api"
    REQUEST_TIMEOUT = 30
    ATTACK_COOLDOWN = 5
    HEAL_COOLDOWN = 30
    REST_DURATION = 1200  # 20 minutes
    HEAL_THRESHOLD = 50   # HP threshold for healing
    STAMINA_THRESHOLD = 0 # Stamina threshold for resting
```

## Runtime Requirements

### System Requirements
- **OS**: macOS, Linux, Windows
- **Python**: 3.8 или выше
- **Memory**: Минимум 128MB RAM
- **Network**: Стабильное интернет-соединение

### Performance Considerations
- **API Rate Limiting**: Соблюдение КД между запросами
- **Memory Management**: Очистка старых данных
- **Network Resilience**: Обработка сетевых ошибок
- **CPU Usage**: Минимизация нагрузки на процессор

## Security Considerations

### Token Security
- Токен хранится в отдельном файле
- Файл с токеном исключен из Git
- Возможность использования переменных окружения

### API Security
- Валидация всех входящих данных
- Обработка ошибок API
- Логирование подозрительной активности

### Data Protection
- Не сохранение чувствительных данных
- Очистка логов от персональной информации
- Безопасное хранение конфигурации

## Deployment Options

### Local Development
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

### Production Deployment
- Docker контейнеризация
- Системные сервисы (systemd)
- Мониторинг и логирование
- Автоматический перезапуск

## Monitoring and Logging

### Log Levels
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log'),
        logging.StreamHandler()
    ]
)
```

### Metrics to Track
- Количество API запросов
- Время ответа API
- Количество ошибок
- Статистика игрового прогресса
- Время работы бота

## Error Handling

### API Error Types
```python
class APIError(Exception):
    pass

class NetworkError(APIError):
    pass

class AuthenticationError(APIError):
    pass

class RateLimitError(APIError):
    pass
```

### Recovery Strategies
- **Network Errors**: Повторные попытки с экспоненциальной задержкой
- **API Errors**: Логирование и переход в безопасный режим
- **Authentication Errors**: Остановка бота и уведомление пользователя
- **Rate Limit Errors**: Соблюдение ограничений и ожидание

## Testing Framework

### Unit Tests
```python
import unittest
from unittest.mock import Mock, patch

class TestGameState(unittest.TestCase):
    def setUp(self):
        self.game_state = GameState()
    
    def test_state_transition(self):
        # Тестирование переходов состояний
        pass
```

### Integration Tests
- Тестирование полного API цикла
- Тестирование игровой логики
- Тестирование UI компонентов

### Mock API Responses
```python
MOCK_EXPLORE_RESPONSE = {
    "mob": {
        "id": "0_mob_164_65gd8",
        "name": "Test Mob",
        "hp": 100,
        "maxHp": 100
    }
}
``` 