import re
import json
from collections import defaultdict
from statistics import mean

LOG_PATH = 'logs/api_responses.log'

# Ключевые слова для поиска
ACTIONS = {
    'attack_mob': '--- attack_mob ---',
    'use_skill': '--- use_skill ---',
    'use_healing_potion': '--- use_healing_potion ---',
    'use_mana_potion': '--- use_mana_potion ---',
}

def extract_timestamps(action):
    timestamps = []
    with open(LOG_PATH, encoding='utf-8') as f:
        lines = f.readlines()
    i = 0
    while i < len(lines):
        if ACTIONS[action] in lines[i]:
            # Ищем json-ответ
            j = i + 1
            json_lines = []
            while j < len(lines) and not lines[j].startswith('---'):
                json_lines.append(lines[j])
                j += 1
            try:
                data = json.loads(''.join(json_lines))
                if 'start' in data:
                    timestamps.append(int(data['start']))
            except Exception:
                pass
            i = j
        else:
            i += 1
    return timestamps

def analyze_cooldown(timestamps):
    if len(timestamps) < 2:
        return None, None, None
    diffs = [ (b - a)/1000 for a, b in zip(timestamps, timestamps[1:]) ]
    return min(diffs), max(diffs), mean(diffs)

def main():
    print('Cooldown analysis:')
    for action in ACTIONS:
        timestamps = extract_timestamps(action)
        if not timestamps:
            print(f'{action}: нет данных')
            continue
        min_cd, max_cd, avg_cd = analyze_cooldown(timestamps)
        if min_cd is None:
            print(f'{action}: недостаточно данных')
        else:
            print(f'{action}: min={min_cd:.2f}s, max={max_cd:.2f}s, avg={avg_cd:.2f}s, samples={len(timestamps)}')

if __name__ == '__main__':
    main() 