#!/usr/bin/env python3
"""
Анализ оптимальных скиллов для автофарма в Ruby King
"""

import json
from typing import Dict, List, Any

class SkillAnalyzer:
    """Анализатор скиллов для автофарма"""
    
    def __init__(self):
        # Базовые скиллы по типам оружия (на основе логики бота и механик)
        self.weapon_skills = {
            "sword": {
                "name": "Меч",
                "skills": {
                    "basic_attack": {
                        "name": "Базовая атака",
                        "damage": "100% силы",
                        "cooldown": "5.1 сек",
                        "auto_farm_rating": 10,
                        "description": "Основная атака, всегда доступна"
                    },
                    "power_strike": {
                        "name": "Мощный удар",
                        "damage": "150% силы",
                        "cooldown": "11 сек",
                        "auto_farm_rating": 9,
                        "description": "Сильная атака, используется ботом при HP моба > 100"
                    },
                    "critical_strike": {
                        "name": "Критический удар",
                        "damage": "200% силы (крит)",
                        "cooldown": "15 сек",
                        "auto_farm_rating": 8,
                        "description": "Высокий урон, но долгий кулдаун"
                    },
                    "defensive_stance": {
                        "name": "Оборонительная стойка",
                        "effect": "+20% защита",
                        "cooldown": "20 сек",
                        "auto_farm_rating": 7,
                        "description": "Снижает получаемый урон"
                    }
                }
            },
            "axe": {
                "name": "Топор",
                "skills": {
                    "basic_attack": {
                        "name": "Базовая атака",
                        "damage": "110% силы",
                        "cooldown": "5.5 сек",
                        "auto_farm_rating": 9,
                        "description": "Медленнее меча, но сильнее"
                    },
                    "heavy_strike": {
                        "name": "Тяжелый удар",
                        "damage": "180% силы",
                        "cooldown": "12 сек",
                        "auto_farm_rating": 8,
                        "description": "Очень сильная атака"
                    },
                    "berserker_rage": {
                        "name": "Ярость берсерка",
                        "effect": "+30% урон, -10% защита",
                        "cooldown": "25 сек",
                        "auto_farm_rating": 6,
                        "description": "Рискованный, но мощный"
                    }
                }
            },
            "spear": {
                "name": "Копье",
                "skills": {
                    "basic_attack": {
                        "name": "Базовая атака",
                        "damage": "95% силы",
                        "cooldown": "4.8 сек",
                        "auto_farm_rating": 9,
                        "description": "Быстрые атаки"
                    },
                    "piercing_strike": {
                        "name": "Проникающий удар",
                        "damage": "140% силы, игнорирует броню",
                        "cooldown": "10 сек",
                        "auto_farm_rating": 9,
                        "description": "Эффективен против бронированных мобов"
                    },
                    "defensive_stance": {
                        "name": "Оборонительная стойка",
                        "effect": "+15% защита, +10% уклонение",
                        "cooldown": "18 сек",
                        "auto_farm_rating": 8,
                        "description": "Хорошая защита"
                    }
                }
            },
            "staff": {
                "name": "Посох",
                "skills": {
                    "basic_attack": {
                        "name": "Базовая атака",
                        "damage": "90% силы",
                        "cooldown": "5.0 сек",
                        "auto_farm_rating": 7,
                        "description": "Слабый базовый урон"
                    },
                    "magic_bolt": {
                        "name": "Магический снаряд",
                        "damage": "160% силы",
                        "cooldown": "8 сек",
                        "auto_farm_rating": 8,
                        "description": "Сильная магическая атака"
                    },
                    "heal": {
                        "name": "Лечение",
                        "effect": "Восстанавливает 30% HP",
                        "cooldown": "30 сек",
                        "auto_farm_rating": 9,
                        "description": "Автоматическое лечение"
                    },
                    "mana_shield": {
                        "name": "Магический щит",
                        "effect": "Поглощает урон маной",
                        "cooldown": "25 сек",
                        "auto_farm_rating": 7,
                        "description": "Защита за счет маны"
                    }
                }
            }
        }
        
        # Универсальные скиллы (не зависят от оружия)
        self.universal_skills = {
            "healing_potion": {
                "name": "Зелье лечения",
                "effect": "Восстанавливает 50% HP",
                "cooldown": "5.5 сек",
                "auto_farm_rating": 10,
                "description": "Критично для автофарма, используется при HP < 50%"
            },
            "mana_potion": {
                "name": "Зелье маны",
                "effect": "Восстанавливает 50% MP",
                "cooldown": "5.5 сек",
                "auto_farm_rating": 8,
                "description": "Нужно для магических скиллов"
            },
            "rest": {
                "name": "Отдых у костра",
                "effect": "Восстанавливает стамину за 20 минут",
                "cooldown": "1200 сек",
                "auto_farm_rating": 10,
                "description": "Автоматически при стамине = 0"
            }
        }
    
    def analyze_weapon_for_autofarm(self) -> Dict[str, Any]:
        """Анализ лучшего оружия для автофарма"""
        results = {}
        
        for weapon_type, weapon_data in self.weapon_skills.items():
            total_rating = 0
            skill_count = len(weapon_data["skills"])
            
            for skill_name, skill_data in weapon_data["skills"].items():
                total_rating += skill_data["auto_farm_rating"]
            
            avg_rating = total_rating / skill_count
            results[weapon_type] = {
                "name": weapon_data["name"],
                "average_rating": avg_rating,
                "total_rating": total_rating,
                "skill_count": skill_count,
                "best_skills": self._get_best_skills(weapon_data["skills"])
            }
        
        return results
    
    def _get_best_skills(self, skills: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Получить лучшие скиллы из набора"""
        sorted_skills = sorted(
            skills.items(),
            key=lambda x: x[1]["auto_farm_rating"],
            reverse=True
        )
        
        return [
            {
                "name": skill_data["name"],
                "rating": skill_data["auto_farm_rating"],
                "description": skill_data["description"]
            }
            for skill_name, skill_data in sorted_skills[:3]
        ]
    
    def get_optimal_build(self) -> Dict[str, Any]:
        """Получить оптимальный билд для автофарма"""
        weapon_analysis = self.analyze_weapon_for_autofarm()
        
        # Найти лучшее оружие
        best_weapon = max(weapon_analysis.items(), key=lambda x: x[1]["average_rating"])
        
        return {
            "recommended_weapon": {
                "type": best_weapon[0],
                "name": best_weapon[1]["name"],
                "rating": best_weapon[1]["average_rating"]
            },
            "weapon_comparison": weapon_analysis,
            "essential_skills": self._get_essential_skills(),
            "skill_priority": self._get_skill_priority(best_weapon[0])
        }
    
    def _get_essential_skills(self) -> List[Dict[str, Any]]:
        """Получить критически важные скиллы для автофарма"""
        essential = []
        
        for skill_name, skill_data in self.universal_skills.items():
            if skill_data["auto_farm_rating"] >= 9:
                essential.append({
                    "name": skill_data["name"],
                    "rating": skill_data["auto_farm_rating"],
                    "description": skill_data["description"],
                    "importance": "Критично"
                })
        
        return essential
    
    def _get_skill_priority(self, weapon_type: str) -> List[Dict[str, Any]]:
        """Получить приоритет скиллов для конкретного оружия"""
        weapon_skills = self.weapon_skills[weapon_type]["skills"]
        
        # Сортируем по рейтингу автофарма
        sorted_skills = sorted(
            weapon_skills.items(),
            key=lambda x: x[1]["auto_farm_rating"],
            reverse=True
        )
        
        priority_list = []
        for i, (skill_name, skill_data) in enumerate(sorted_skills, 1):
            priority_list.append({
                "priority": i,
                "name": skill_data["name"],
                "rating": skill_data["auto_farm_rating"],
                "cooldown": skill_data.get("cooldown", "N/A"),
                "description": skill_data["description"]
            })
        
        return priority_list

def main():
    """Основная функция анализа"""
    analyzer = SkillAnalyzer()
    optimal_build = analyzer.get_optimal_build()
    
    print("🎯 ОПТИМАЛЬНЫЙ БИЛД ДЛЯ АВТОФАРМА RUBY KING")
    print("=" * 60)
    
    # Рекомендуемое оружие
    weapon = optimal_build["recommended_weapon"]
    print(f"\n⚔️ РЕКОМЕНДУЕМОЕ ОРУЖИЕ: {weapon['name']}")
    print(f"   Рейтинг автофарма: {weapon['rating']:.1f}/10")
    
    # Сравнение оружия
    print(f"\n📊 СРАВНЕНИЕ ОРУЖИЯ:")
    for weapon_type, data in optimal_build["weapon_comparison"].items():
        print(f"   {data['name']}: {data['average_rating']:.1f}/10 ({data['skill_count']} скиллов)")
    
    # Критически важные скиллы
    print(f"\n🔴 КРИТИЧЕСКИ ВАЖНЫЕ СКИЛЛЫ:")
    for skill in optimal_build["essential_skills"]:
        print(f"   {skill['name']} ({skill['rating']}/10): {skill['description']}")
    
    # Приоритет скиллов для рекомендуемого оружия
    print(f"\n📈 ПРИОРИТЕТ СКИЛЛОВ ДЛЯ {weapon['name'].upper()}:")
    for skill in optimal_build["skill_priority"]:
        print(f"   {skill['priority']}. {skill['name']} ({skill['rating']}/10)")
        print(f"      Кулдаун: {skill['cooldown']}")
        print(f"      {skill['description']}")
    
    # Рекомендации по использованию
    print(f"\n💡 РЕКОМЕНДАЦИИ ПО ИСПОЛЬЗОВАНИЮ:")
    print("   1. Настройте бота на использование скиллов при HP моба > 80")
    print("   2. Приоритет: зелья лечения > основной скилл > базовая атака")
    print("   3. Автоматический отдых при стамине = 0")
    print("   4. Мониторинг количества зелий (автопокупка при < 20)")
    
    # Сохранить результаты в JSON
    with open("optimal_autofarm_build.json", "w", encoding="utf-8") as f:
        json.dump(optimal_build, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результаты сохранены в optimal_autofarm_build.json")

if __name__ == "__main__":
    main() 