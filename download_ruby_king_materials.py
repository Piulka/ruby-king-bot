#!/usr/bin/env python3
"""
Скрипт для скачивания всех основных материалов с сайта Ruby King (жестко заданный список)
"""

import asyncio
import os
import re
import time
from pathlib import Path
from playwright.async_api import async_playwright
from markdownify import markdownify as md

BASE_URL = "https://ruby-king.ru"
SAVE_DIR = Path("useful_materials")

MATERIALS = [
    ("Лор", "/base/lore"),
    ("Погода и пора года", "/base/weather"),
    ("Игрок (персонаж)", "/base/player"),
    ("Мобы (монстры)", "/base/mobs"),
    ("Броня", "/base/armor"),
    ("Оружие", "/base/weapons"),
    ("Кланы", "/base/clans"),
    ("Клановые войны", "/base/clanwar"),
    ("Локации", "/base/locations"),
    ("Негативные события во время исследования", "/base/negative"),
    ("Позитивные события во время исследования", "/base/positive"),
    ("Профессии", "/base/professions"),
    ("События профессий (специализации)", "/base/profession_events"),
    ("Растения", "/base/plants"),
    ("Руда", "/base/ore"),
    ("Шкуры", "/base/skins"),
    ("База дропа", "/base/drop"),
    ("Торговец", "/base/trader"),
    ("Рынок", "/base/market"),
    ("Зал славы", "/base/halloffame"),
]

def sanitize_filename(name):
    if not name:
        return "untitled"
    clean_name = re.sub(r'[<>:"/\\|?*]', '_', name)
    clean_name = re.sub(r'[_\s]+', '_', clean_name).strip('_')
    return clean_name[:50] if clean_name else "untitled"

def extract_content(page):
    try:
        selectors = [
            "main",
            ".content",
            ".article",
            ".post",
            "[role='main']",
            ".main-content",
            ".page-content"
        ]
        for selector in selectors:
            element = page.query_selector(selector)
            if element:
                return element.inner_text()
        body = page.query_selector("body")
        if body:
            return body.inner_text()
        return "Контент не найден"
    except Exception as e:
        return f"Ошибка при извлечении контента: {e}"

async def fetch_and_save(page, url, filename):
    await page.goto(url)
    # Пробуем сначала .animeFade, если нет — fallback на body
    try:
        await page.wait_for_selector(".animeFade", timeout=10000)
        content = await page.inner_html(".animeFade")
    except Exception:
        content = await page.content()  # fallback: сохраняем всю страницу
    md_content = md(content, heading_style="ATX")
    md_content = f"[Оригинал]({url})\n\n" + md_content
    with open(SAVE_DIR / filename, "w", encoding="utf-8") as f:
        f.write(md_content)
    print(f"Saved: {filename}")

async def main():
    print("🚀 Начинаю скачивание основных материалов Ruby King...")
    SAVE_DIR.mkdir(exist_ok=True)
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        summary_lines = []
        for i, (title, path) in enumerate(MATERIALS, 1):
            url = BASE_URL + path
            try:
                print(f"\n📥 [{i}/{len(MATERIALS)}] Скачиваю: {title}")
                print(f"   🔗 URL: {url}")
                await fetch_and_save(page, url, sanitize_filename(title) + ".md")
                summary_lines.append(f"- [{title}]({sanitize_filename(title) + '.md'})")
                print(f"   ✅ Сохранено в {sanitize_filename(title) + '.md'}")
            except Exception as e:
                print(f"   ❌ Ошибка при скачивании {title}: {e}")
                summary_lines.append(f"- ❌ {title} (ошибка: {e})")
        print(f"\n📝 Создаю общий список материалов...")
        with open(SAVE_DIR / "README.md", "w", encoding="utf-8") as f:
            f.write("# 📚 Основные материалы Ruby King\n\n")
            f.write(f"Всего материалов: {len(MATERIALS)}\n\n")
            f.write("## 📋 Список материалов\n\n")
            f.write("\n".join(summary_lines))
            f.write(f"\n\n---\n\n")
            f.write(f"*Скачано автоматически: {time.strftime('%Y-%m-%d %H:%M:%S')}*\n")
        print(f"\n🎉 Готово! Все материалы сохранены в папке '{SAVE_DIR}/'")
        print(f"📁 Всего скачано: {len(MATERIALS)} материалов")
        print(f"📄 Общий список: {SAVE_DIR}/README.md")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main()) 