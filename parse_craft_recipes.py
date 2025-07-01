import time
import json
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import hashlib
import sys

# --- НАСТРОЙКИ ---
START_URL = "https://ruby-king.ru/city?name=1750764015078_145327_6700_95b44b31447fdc4c593251e276531049ed0c51d9f73ae0c50bec&timeEnd=1751300208114"
OUTPUT_FILE = "recipes_db.json"
WAIT_TIMEOUT = 10

chrome_options = Options()
chrome_options.add_argument('--start-maximized')
chrome_options.add_argument('--disable-blink-features=AutomationControlled')
chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1')

def open_craft_menu():
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(START_URL)
    wait = WebDriverWait(driver, WAIT_TIMEOUT)
    print("[AUTO] Ожидание ручного входа в меню крафта...")
    return driver, wait

# --- Новый этап: сбор вкладок и их названий ---
def get_craft_tabs(driver):
    tabs = driver.find_elements(By.CSS_SELECTOR, ".m_6d731127.mantine-Stack-root > div")
    tab_info = []
    for tab in tabs:
        # Пробуем найти подпись вкладки
        try:
            tab_name = tab.find_element(By.CSS_SELECTOR, "p").text.strip()
        except Exception:
            tab_name = ""
        tab_info.append({
            "element": tab,
            "name": tab_name
        })
    return tab_info

def extract_texts_and_imgs(container):
    """Собирает все текстовые и графические элементы из контейнера."""
    data = {}
    # Тексты
    texts = container.find_elements(By.XPATH, ".//*[self::p or self::span or self::div][string-length(normalize-space(text())) > 0]")
    for idx, el in enumerate(texts):
        key = f"text_{idx}"
        try:
            data[key] = el.text.strip()
        except Exception:
            pass
    # Картинки
    imgs = container.find_elements(By.TAG_NAME, "img")
    for idx, img in enumerate(imgs):
        key = f"img_{idx}"
        try:
            data[key] = img.get_attribute("src")
        except Exception:
            pass
    return data

def analyze_and_unlock_recipe_element(driver, element):
    """Анализирует и пытается разблокировать DOM для клика по рецепту."""
    result = {}

    # 1. Проверка видимости через JS
    is_visible = driver.execute_script("""
        const el = arguments[0];
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return (
            style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            style.opacity !== '0' &&
            el.offsetParent !== null
        );
    """, element)
    result['is_visible'] = is_visible

    # 2. Проверка aria-hidden у родителей
    aria_hidden_parent = driver.execute_script("""
        let el = arguments[0];
        while (el) {
            if (el.getAttribute && el.getAttribute('aria-hidden') === 'true') return true;
            el = el.parentElement;
        }
        return false;
    """, element)
    result['aria_hidden_parent'] = aria_hidden_parent

    # 3. Проверка display:none у родителей
    display_none_parent = driver.execute_script("""
        let el = arguments[0];
        while (el) {
            if (el instanceof HTMLElement) {
                const style = window.getComputedStyle(el);
                if (style.display === 'none') return true;
            }
            el = el.parentElement;
        }
        return false;
    """, element)
    result['display_none_parent'] = display_none_parent

    # 4. Проверка перекрытия другим элементом
    rect = element.rect
    center_x = int(rect['x'] + rect['width'] / 2)
    center_y = int(rect['y'] + rect['height'] / 2)
    top_element = driver.execute_script("""
        return document.elementFromPoint(arguments[0], arguments[1]);
    """, center_x, center_y)
    is_covered = top_element != element
    result['is_covered'] = is_covered

    # 5. Проверка наличия обработчика клика (очень базово)
    has_onclick = driver.execute_script("""
        const el = arguments[0];
        return !!el.onclick;
    """, element)
    result['has_onclick'] = has_onclick

    # 6. Попытка разблокировать: снять aria-hidden и display:none с родителей
    driver.execute_script("""
        let el = arguments[0];
        while (el) {
            if (el.getAttribute && el.getAttribute('aria-hidden') === 'true') {
                el.setAttribute('aria-hidden', 'false');
            }
            if (el instanceof HTMLElement) {
                const style = window.getComputedStyle(el);
                if (style.display === 'none') el.style.display = '';
                if (style.visibility === 'hidden') el.style.visibility = '';
            }
            el = el.parentElement;
        }
    """, element)

    # 7. Повторная проверка видимости
    is_visible_after = driver.execute_script("""
        const el = arguments[0];
        if (!el) return false;
        const style = window.getComputedStyle(el);
        return (
            style.display !== 'none' &&
            style.visibility !== 'hidden' &&
            style.opacity !== '0' &&
            el.offsetParent !== null
        );
    """, element)
    result['is_visible_after_unlock'] = is_visible_after

    return result

def get_hash(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def parse_active_tab(driver):
    # Найти активную вкладку (фон отличается, например, background: var(--mantine-color-dark-filled))
    try:
        active_tab = driver.find_element(By.CSS_SELECTOR, ".m_6d731127.mantine-Stack-root > div[style*='background']")
        tab_name = active_tab.find_element(By.CSS_SELECTOR, "p").text.strip()
        img = active_tab.find_element(By.TAG_NAME, "img").get_attribute("src")
        return {"tab_name": tab_name, "tab_img": img}
    except Exception:
        return None

def parse_recipe_popup_v2(popup):
    data = {}
    # 1. Главная картинка рецепта
    try:
        recipe_img = popup.find_element(
            By.XPATH,
            "(.//div[@style and contains(@style, 'position: relative')])[1]//div[contains(@class, 'cell-item-res_Cell__Qw3Oq')]//img[contains(@class, 'cell-item-res_IconOriginal__X9o_Y')]"
        )
        data['recipe_img'] = recipe_img.get_attribute("src")
    except Exception:
        data['recipe_img'] = ""
    # 2. Название рецепта
    try:
        recipe_name = popup.find_element(
            By.XPATH,
            "(.//div[@style and contains(@style, 'position: relative')])[1]/following-sibling::div//p[1]"
        )
        data['recipe_name'] = recipe_name.text.strip()
    except Exception:
        data['recipe_name'] = ""
    # 3. Материалы
    data['materials'] = []
    try:
        mats = popup.find_elements(By.CSS_SELECTOR, ".city-blacksmith-list_NeedMaterials__8rGF8 .city-blacksmith-list_Cell__wParG")
        for mat in mats:
            try:
                img = mat.find_element(By.TAG_NAME, "img").get_attribute("src")
                count = mat.find_element(By.CLASS_NAME, "cell-item-res_Count__cTEQo").text
                data['materials'].append({"img": img, "count": count})
            except Exception:
                continue
    except Exception:
        pass
    # 4. Получаемый предмет
    try:
        result_img = popup.find_element(By.XPATH, ".//p[contains(text(), 'Получаемый предмет')]/following-sibling::div//img[contains(@class, 'cell-item-res_IconOriginal__X9o_Y')]")
        data['result_img'] = result_img.get_attribute("src")
    except Exception:
        data['result_img'] = ""
    # 5. Описание
    try:
        desc_p = popup.find_element(By.XPATH, ".//div[contains(@style, 'opacity: 0.5')]//p")
        data['description'] = desc_p.text.strip()
    except Exception:
        data['description'] = ""
    # 6. Вес и цена продажи
    try:
        weight = popup.find_element(By.XPATH, ".//p[text()='Вес']/following-sibling::p").text.strip()
        data['weight'] = weight
    except Exception:
        data['weight'] = ""
    try:
        sell_price = popup.find_element(By.XPATH, ".//p[contains(text(), 'Цена продажи')]/following-sibling::p").text.strip()
        data['sell_price'] = sell_price
    except Exception:
        data['sell_price'] = ""
    return data

def parse_material_popup_v2(popup):
    data = {}
    try:
        name_p = popup.find_element(By.XPATH, ".//p[contains(@class, 'Text-root')]")
        data['name'] = name_p.text.strip()
    except Exception:
        data['name'] = ""
    try:
        img = popup.find_element(By.XPATH, ".//img[contains(@class, 'cell-item-res_IconOriginal__X9o_Y')]")
        data['img'] = img.get_attribute("src")
    except Exception:
        data['img'] = ""
    return data

def find_modal_popup(driver, timeout=10):
    # Ждём появления модального окна Mantine
    WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mantine-Modal-inner"))
    )
    return driver.find_element(By.CSS_SELECTOR, "div.mantine-Modal-inner")

def close_modal_popup(driver, popup=None, timeout=5):
    try:
        if popup is not None:
            # Ищем кнопку закрытия только внутри данного поп-апа
            close_btn = WebDriverWait(popup, timeout).until(
                lambda p: p.find_element(By.CSS_SELECTOR, ".mantine-Modal-close")
            )
        else:
            # Старый вариант (fallback)
            close_btn = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, ".mantine-Modal-close"))
            )
        close_btn.click()
    except Exception:
        pass

def is_recipe_popup(popup):
    try:
        # Проверяем по наличию текста "Рецепт" или соответствующего элемента
        if "Рецепт" in popup.text:
            return True
        found = popup.find_elements(By.XPATH, ".//p[contains(text(), 'Рецепт')]")
        return bool(found)
    except Exception:
        return False

if __name__ == "__main__":
    if '--debug-popup' in sys.argv:
        driver, wait = open_craft_menu()
        print("[DEBUG] Кликаю по первому рецепту...")
        try:
            # Ждем появления списка рецептов
            wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".city-blacksmith-list_CellWrap__b5Awu")) > 0)
            recipe = driver.find_elements(By.CSS_SELECTOR, ".city-blacksmith-list_CellWrap__b5Awu")[0]
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", recipe)
            time.sleep(0.2)
            recipe.click()
            print("[DEBUG] Клик выполнен, жду поп-ап...")
            # Ждем появления модального окна
            popup = WebDriverWait(driver, 10).until(
                EC.visibility_of_element_located((By.CSS_SELECTOR, "div.mantine-Modal-inner"))
            )
            html = popup.get_attribute("outerHTML")
            with open("debug_recipe_popup.html", "w", encoding="utf-8") as f:
                f.write(html)
            print("[DEBUG] HTML поп-апа сохранён в debug_recipe_popup.html")
        except Exception as e:
            print(f"[DEBUG] Ошибка при поиске/клике/сохранении поп-апа: {e}")
        finally:
            input("Нажмите Enter для выхода и закрытия браузера...")
            driver.quit()
        sys.exit(0)
    driver, wait = open_craft_menu()
    print("[AUTO] Ожидание появления вкладки 'Ресурсы'...")
    # Ждем, пока пользователь вручную не откроет меню крафта и не появится вкладка 'Ресурсы'
    try:
        wait.until(lambda d: any('Ресурсы' in (el.text or '') for el in d.find_elements(By.CSS_SELECTOR, ".m_6d731127.mantine-Stack-root > div p")))
    except Exception:
        print("[AUTO] Не удалось найти вкладку 'Ресурсы'. Проверьте, что вы открыли меню крафта!")
        driver.quit()
        exit(1)
    print("[AUTO] Вкладка 'Ресурсы' найдена. Начинаю автоматический обход вкладок и рецептов...")
    all_data = []
    try:
        tab_elems = driver.find_elements(By.CSS_SELECTOR, ".m_6d731127.mantine-Stack-root > div")
        for tab_idx, tab in enumerate(tab_elems):
            try:
                tab_name = tab.find_element(By.CSS_SELECTOR, "p").text.strip()
            except Exception:
                tab_name = f"tab_{tab_idx}"
            print(f"[AUTO] Вкладка: {tab_name}")
            ActionChains(driver).move_to_element(tab).click(tab).perform()
            wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, ".city-blacksmith-list_CellWrap__b5Awu")) > 0)
            tab_data = {"tab_name": tab_name, "recipes": []}
            recipe_elems = driver.find_elements(By.CSS_SELECTOR, ".city-blacksmith-list_CellWrap__b5Awu")
            for rec_idx in range(len(recipe_elems)):
                try:
                    recipe = driver.find_elements(By.CSS_SELECTOR, ".city-blacksmith-list_CellWrap__b5Awu")[rec_idx]
                    wait.until(EC.element_to_be_clickable((By.XPATH, f"(//div[contains(@class, 'city-blacksmith-list_CellWrap__b5Awu')])[{rec_idx+1}]")))
                    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", recipe)
                    ActionChains(driver).move_to_element(recipe).click(recipe).perform()
                    print(f"[AUTO]  Рецепт {rec_idx+1}/{len(recipe_elems)}: жду поп-ап...")
                    # Ищем среди всех поп-апов тот, что действительно рецепт
                    popups = driver.find_elements(By.CSS_SELECTOR, "div.mantine-Modal-inner")
                    popup = None
                    for p in popups:
                        print(f"[DEBUG] popup.text[:100]: {p.text[:100]}")
                        if is_recipe_popup(p):
                            popup = p
                            break
                    if not popup:
                        print("[ERROR] Не найден поп-ап рецепта после клика!")
                        continue
                    recipe_data = parse_recipe_popup_v2(popup)
                    # Логируем если поля пустые
                    if not recipe_data.get('recipe_name'):
                        print(f"[WARN] Не удалось распарсить название рецепта для рецепта #{rec_idx+1} во вкладке '{tab_name}'")
                    if not recipe_data.get('recipe_img'):
                        print(f"[WARN] Не удалось распарсить картинку рецепта для рецепта #{rec_idx+1} во вкладке '{tab_name}'")
                    for mat in recipe_data['materials']:
                        try:
                            mat_div = popup.find_element(By.XPATH, f".//img[contains(@src, '{os.path.basename(mat['img'])}')]/ancestor::div[contains(@class, 'cell-item-res_Cell__Qw3Oq')]")
                            wait.until(EC.element_to_be_clickable((By.XPATH, f".//img[contains(@src, '{os.path.basename(mat['img'])}')]/ancestor::div[contains(@class, 'cell-item-res_Cell__Qw3Oq')]")))
                            ActionChains(driver).move_to_element(mat_div).click(mat_div).perform()
                            mat_popup = find_modal_popup(driver, timeout=5)
                            mat_info = parse_material_popup_v2(mat_popup)
                            mat['name'] = mat_info['name']
                            close_modal_popup(driver, mat_popup)
                        except Exception as e:
                            print(f"[AUTO]   [!] Не удалось получить имя материала: {e}")
                            mat['name'] = ""
                    tab_data['recipes'].append(recipe_data)
                    print(f"[AUTO]  Рецепт '{recipe_data.get('recipe_name', '')}' успешно обработан.")
                    close_modal_popup(driver, popup)
                except Exception as e:
                    print(f"[AUTO]  [!] Ошибка при парсинге рецепта {rec_idx+1}: {e}")
                    # Пробуем закрыть только если popup найден
                    try:
                        if popup:
                            close_modal_popup(driver, popup)
                    except Exception:
                        pass
                    continue
            all_data.append(tab_data)
            with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
                json.dump(all_data, f, ensure_ascii=False, indent=2)
            print(f"[AUTO] Вкладка '{tab_name}' обработана и сохранена.")
        print("[AUTO] Готово! Все данные сохранены в", OUTPUT_FILE)
    except KeyboardInterrupt:
        print("Остановка по Ctrl+C. Всего вкладок обработано:", len(all_data))
    finally:
        driver.quit() 