import { loadAllData, getWorldMapData, getMobsData, getItemsData } from './data-loader.js';
import { renderMap } from './map-renderer.js';
import { showSearchPopup, renderMobDetails, showMobInPopup, closeAllPopups } from './search-engine.js';

let selectedLocation = null;
let selectedSide = null;
let allData = null;
let openedRecipeId = null;

window.addEventListener('DOMContentLoaded', async () => {
  allData = await loadAllData();
  console.log('allData loaded', allData);
  initLocationSelect();
  document.getElementById('search-btn').onclick = openSearch;

  // --- Меню ---
  const menuBtn = document.getElementById('menu-btn');
  const menuDropdown = document.getElementById('menu-dropdown');
  menuBtn.onclick = (e) => {
    e.stopPropagation();
    menuDropdown.classList.toggle('hidden');
  };
  // Закрытие меню при клике вне меню
  document.body.addEventListener('click', (e) => {
    if (!menuDropdown.classList.contains('hidden')) {
      menuDropdown.classList.add('hidden');
    }
  });
  menuDropdown.onclick = (e) => { e.stopPropagation(); };
  // Skills
  document.getElementById('menu-skills').onclick = (e) => {
    e.preventDefault();
    menuDropdown.classList.add('hidden');
    showPopupStub('Скиллы');
  };
  // Equip
  document.getElementById('menu-equip').onclick = (e) => {
    e.preventDefault();
    menuDropdown.classList.add('hidden');
    showPopupStub('Эквип');
  };

  // === РЕЦЕПТЫ ===
  document.getElementById('menu-recipes').onclick = (e) => {
    e.preventDefault();
    menuDropdown.classList.add('hidden');
    showRecipesPanel();
  };

  // Панель рецептов
  function showRecipesPanel() {
    // Скрываем остальные секции
    document.getElementById('side-select-section').style.display = 'none';
    document.getElementById('map-section').style.display = 'none';
    document.getElementById('mobs-section').style.display = 'none';
    // Проверяем, есть ли уже панель
    let panel = document.getElementById('recipes-panel');
    if (!panel) {
      panel = document.createElement('div');
      panel.id = 'recipes-panel';
      panel.className = 'recipes-panel';
      document.querySelector('main').appendChild(panel);
    }
    panel.innerHTML = `<button id='close-recipes-panel' style='float:right;margin:0.5em 0.5em 0 0;'>✖</button><h2 style='margin-top:0;'>Рецепты</h2><div id='recipes-list'></div>`;
    document.getElementById('close-recipes-panel').onclick = () => {
      panel.remove();
      document.getElementById('side-select-section').style.display = '';
      document.getElementById('map-section').style.display = '';
      document.getElementById('mobs-section').style.display = '';
    };
    renderRecipesList();
  }

  function renderRecipesList() {
    const recipes = (allData && allData.recipes) || (allData && allData.Rec) || [];
    // Если структура как в Rec.json
    const recipeList = Array.isArray(recipes.list) ? recipes.list : recipes;
    const listDiv = document.getElementById('recipes-list');
    if (!listDiv) return;
    listDiv.innerHTML = '';
    // Карта рецептов по id для быстрого доступа
    const recipesById = {};
    recipeList.forEach(r => { recipesById[r.id] = r; });

    recipeList.forEach(recipe => {
      const itemDiv = document.createElement('div');
      itemDiv.className = 'recipe-list-item';
      itemDiv.innerHTML = `
        <img src='${recipe.icon || ''}' alt='' style='width:36px;height:36px;vertical-align:middle;margin-right:0.7em;border-radius:6px;'>
        <span style='font-weight:600;'>${recipe.name}</span>
        <button class='l2-expand-btn' style='float:right;'>▼</button>
      `;
      // Создаём блок для раскрывающихся деталей
      const detailsDiv = document.createElement('div');
      detailsDiv.className = 'recipe-details-animated';
      detailsDiv.style.maxHeight = '0';
      detailsDiv.style.overflow = 'hidden';
      detailsDiv.style.transition = 'max-height 0.35s cubic-bezier(0.4,0,0.2,1)';
      itemDiv.appendChild(detailsDiv);
      let isOpen = false;
      itemDiv.querySelector('.l2-expand-btn').onclick = () => {
        isOpen = !isOpen;
        if (isOpen) {
          renderRecipeDetails(recipe, detailsDiv, recipesById, 1);
          detailsDiv.classList.add('open');
          detailsDiv.style.maxHeight = detailsDiv.scrollHeight + 3332 + 'px';
          itemDiv.querySelector('.l2-expand-btn').textContent = '▲';
        } else {
          detailsDiv.classList.remove('open');
          detailsDiv.style.maxHeight = '0';
          itemDiv.querySelector('.l2-expand-btn').textContent = '▼';
        }
      };
      listDiv.appendChild(itemDiv);
    });
  }

  // Рекурсивный рендеринг деталей рецепта и вложенных ресурсов
  function renderRecipeDetails(recipe, container, recipesById, craftCount) {
    const totalResources = calculateTotalResources(recipe.id, craftCount, recipesById);
    const items = recipe.craftItems || [];
    let html = `<div class='l2-details'><div class='l2-title-row'><span class='l2-details-title'>Ресурсы для крафта:</span></div><ul class='l2-materials-list'>`;
    for (const item of items) {
      const subRecipe = Object.values(recipesById).find(r => r.craftElem === item.id);
      const total = totalResources[item.id]?.count || item.count;
      html += `<li class='l2-material-item'>
        <img src='${item.icon || ''}' class='l2-mat-icon item-popup-link' data-itemid='${item.id}' style='width:28px;height:28px;vertical-align:middle;margin-right:0.5em;border-radius:5px;cursor:pointer;'>
        <span class='l2-mat-name item-popup-link' data-itemid='${item.id}' style='cursor:pointer;'>${item.name}</span>
        <span class='l2-mat-count'>${item.count} <span style='opacity:0.7;'>( ${total} )</span></span>
        ${subRecipe ? `<button class='l2-expand-btn' style='margin-left:0.7em;font-size:0.95em;'>▼</button>` : ''}
        <div class='l2-mat-children'></div>
      </li>`;
    }
    html += `</ul></div>`;
    container.innerHTML = html;

    // Обработчики поп-апа по предмету
    container.querySelectorAll('.item-popup-link').forEach(el => {
      el.onclick = (e) => {
        const itemId = el.getAttribute('data-itemid');
        if (!itemId) return;
        // showModalPopup из search-engine.js
        import('./search-engine.js').then(mod => {
          mod.showModalPopup(renderItemPopup(itemId, recipesById));
          // Навешиваем обработчики на рецепты внутри поп-апа
          setTimeout(() => {
            document.querySelectorAll('.recipe-link').forEach(link => {
              link.onclick = (ev) => {
                ev.preventDefault();
                const rid = link.getAttribute('data-recipeid');
                if (!rid) return;
                // Открываем вложенный поп-ап с этим рецептом
                mod.showModalPopup(renderItemPopup(itemId, recipesById));
                // Можно доработать: показывать детали рецепта прямо в поп-апе
              };
            });
          }, 0);
        });
      };
    });

    // Навешиваем обработчики для вложенных рецептов
    const itemsEls = container.querySelectorAll('.l2-material-item');
    items.forEach((item, idx) => {
      const subRecipe = Object.values(recipesById).find(r => r.craftElem === item.id);
      if (subRecipe) {
        const btn = itemsEls[idx].querySelector('.l2-expand-btn');
        const childDiv = itemsEls[idx].querySelector('.l2-mat-children');
        let subOpen = false;
        btn.onclick = () => {
          subOpen = !subOpen;
          if (subOpen) {
            renderRecipeDetails(subRecipe, childDiv, recipesById, item.count * (craftCount || 1));
            childDiv.classList.add('open');
            childDiv.style.maxHeight = childDiv.scrollHeight + 2400 + 'px';
            btn.textContent = '▲';
          } else {
            childDiv.classList.remove('open');
            childDiv.style.maxHeight = '0';
            btn.textContent = '▼';
          }
        };
      }
    });
  }

  function renderItemPopup(itemId, recipesById) {
    const items = (allData && allData.itemsData) || [];
    const mobs = (allData && allData.mobsData) || [];
    const item = items.find(it => it.id === itemId) || {};
    // --- Информация о предмете ---
    let html = `<div style='display:flex;gap:1.2em;align-items:flex-start;flex-wrap:wrap;'>
      <img src='${item.icon || ''}' alt='' style='width:64px;height:64px;border-radius:8px;background:#23242a;object-fit:cover;'>
      <div style='flex:1;min-width:180px;'>
        <div class='mob-title' style='font-size:1.15em;font-weight:600;'>${item.name || itemId}</div>
        <div class='mob-id' style='font-size:0.95em;opacity:0.7;'>ID: ${itemId}</div>
        <div class='mob-desc' style='margin:0.5em 0 0.7em 0;'>${item.desc || ''}</div>
      </div>
    </div>`;
    // --- Дроп с мобов ---
    const dropMobs = mobs.filter(mob => (mob.drop||[]).some(drop => drop.id === itemId));
    if (dropMobs.length) {
      html += `<div style='margin:1.1em 0 0.7em 0;font-size:0.98em;'>Дроп с мобов:<ul style='padding-left:1.2em;margin:0;'>` +
        dropMobs.map(mob => `<li><a href='#' class='mob-link' data-mobid='${mob.id}' style='color:#a7c7ff;text-decoration:underline;cursor:pointer;font-weight:600;'>${mob.name}</a></li>`).join('') +
        `</ul></div>`;
    }
    // --- Рецепты, где участвует предмет ---
    const recipesWithItem = Object.values(recipesById).filter(r => (r.craftItems||[]).some(it => it.id === itemId));
    if (recipesWithItem.length) {
      html += `<div style='margin:1.1em 0 0.7em 0;font-size:0.98em;'>Участвует в рецептах:<ul style='padding-left:1.2em;margin:0;'>` +
        recipesWithItem.map(r => `<li><a href='#' class='recipe-link' data-recipeid='${r.id}' style='color:#7ecfff;text-decoration:underline;cursor:pointer;font-weight:600;'>${r.name}</a></li>`).join('') +
        `</ul></div>`;
    }
    return html;
  }
});

function initLocationSelect() {
  const select = document.getElementById('location-select');
  const mapData = getWorldMapData();
  const locations = Object.entries(mapData.world_map || {});
  select.innerHTML = '';
  locations.forEach(([locId, locObj]) => {
    const opt = document.createElement('option');
    opt.value = locId;
    opt.textContent = locObj.name || locId;
    select.appendChild(opt);
  });
  select.onchange = () => {
    selectedLocation = select.value;
    selectedSide = 0;
    renderSideSelect();
    renderMapSection();
    renderMobsSection();
  };
  if (locations.length) {
    select.value = locations[0][0];
    selectedLocation = locations[0][0];
    selectedSide = 0;
    renderSideSelect();
    renderMapSection();
    renderMobsSection();
  }
}

function renderSideSelect() {
  const section = document.getElementById('side-select-section');
  section.innerHTML = '';
  if (!selectedLocation) return;
  const mapData = getWorldMapData();
  const locObj = mapData.world_map[selectedLocation];
  const sideKeys = Object.keys(locObj.directions || {});
  const sideNames = {north: 'Север', east: 'Восток', south: 'Юг', west: 'Запад'};
  sideKeys.forEach((sideKey, idx) => {
    const btn = document.createElement('button');
    btn.className = 'side-btn' + (selectedSide === idx ? ' active' : '');
    btn.textContent = sideNames[sideKey] || sideKey;
    btn.onclick = () => {
      selectedSide = idx;
      renderSideSelect();
      renderMapSection();
      renderMobsSection();
    };
    section.appendChild(btn);
  });
}

function clearMapAndMobs() {
  document.getElementById('map-section').innerHTML = '';
  document.getElementById('mobs-section').innerHTML = '';
}

function renderMapSection() {
  console.log('renderMapSection called', selectedLocation, selectedSide, getWorldMapData());
  const mapSection = document.getElementById('map-section');
  if (!selectedLocation || selectedSide === null) return;
  const mapData = getWorldMapData();
  const mobsData = getMobsData();
  const locObj = mapData.world_map[selectedLocation];
  const sideKeys = Object.keys(locObj.directions || {});
  const sideKey = sideKeys[selectedSide];
  const squares = locObj.directions[sideKey]?.squares || {};
  const sideNames = {north: 'Север', east: 'Восток', south: 'Юг', west: 'Запад'};
  const gridOrder = [
    "R1","R2","R3","R4",
    "U1","U2","U3","U4",
    "B1","B2","B3","B4",
    "Y1","Y2","Y3","Y4",
    "K1","K2","K3","K4",
    "I1","I2","I3","I4",
    "N1","N2","N3","N4",
    "G1","G2","G3","G4"
  ];
  const gridData = gridOrder.map(cellId => {
    const cell = squares[cellId] || {};
    let type = 'empty';
    let mobId = null;
    let label = '';
    let innerInfo = undefined;

    // --- ВНУТРЕННЯЯ ЛОКАЦИЯ ---
    if (cell.mob_level && cell.mob_level.locoId) {
      type = 'inner';
      label = cell.mob_level.locoName || '';
      innerInfo = { name: cell.mob_level.locoName, id: cell.mob_level.locoId };
    } else if (cell.has_mobs) {
      type = 'mob';
      // Найти моба по location и side только из mobs-database.json
      const locName = locObj.name;
      const mob = mobsData.find(m => m.location === locName && m.side === sideNames[sideKey]);
      if (mob) mobId = mob.id;
    } else if (cell.mob_level && typeof cell.mob_level === 'object' && cell.mob_level.mobLvl !== undefined) {
      label = String(cell.mob_level.mobLvl);
    } else if (cell.mob_level) {
      label = String(cell.mob_level);
    }
    return {
      type,
      label,
      innerInfo,
      cellId,
      mobId
    };
  });
  renderMap(gridData, mapSection, showInnerLocationInfo, openMobPopup);
}

function showInnerLocationInfo(innerInfo) {
  // Показываем pop-up с описанием внутренней локации
  const popup = document.getElementById('popup-search');
  popup.classList.remove('hidden');
  popup.innerHTML = `<div class='popup-content'><h3>${innerInfo.name}</h3><p>${innerInfo.desc||''}</p><button class='popup-close-btn'>✕</button></div>`;
}

function renderMobsSection() {
  const mobsSection = document.getElementById('mobs-section');
  mobsSection.innerHTML = '';
  if (!selectedLocation || selectedSide === null) return;
  const mapData = getWorldMapData();
  const mobsData = getMobsData();
  const locObj = mapData.world_map[selectedLocation];
  const sideKeys = Object.keys(locObj.directions || {});
  const sideKey = sideKeys[selectedSide];
  const sideNames = {north: 'Север', east: 'Восток', south: 'Юг', west: 'Запад'};
  const filteredMobs = mobsData.filter(mob =>
    (Array.isArray(mob.locations) &&
      mob.locations.some(loc => loc.location === locObj.name && loc.side === sideNames[sideKey]))
    ||
    (mob.location === locObj.name && mob.side === sideNames[sideKey])
  );
  if (filteredMobs.length) {
    mobsSection.innerHTML = filteredMobs.map((mob, idx) => `<div class='mob-list-row' style='margin-bottom:1.2em;cursor:pointer;' id='mob-list-row-${idx}'>${renderMobDetails(mob)}</div>`).join('');
    filteredMobs.forEach((mob, idx) => {
      const row = document.getElementById(`mob-list-row-${idx}`);
      if (row) row.onclick = () => showMobInPopup(mob);
    });
  }
}

function setLocationAndSide(locId, sideKey) {
  const mapData = getWorldMapData();
  if (!mapData.world_map[locId]) return;
  selectedLocation = locId;
  // Найти индекс стороны
  const sideKeys = Object.keys(mapData.world_map[locId].directions || {});
  const idx = sideKeys.indexOf(sideKey);
  if (idx !== -1) selectedSide = idx;
  renderSideSelect();
  renderMapSection();
  renderMobsSection();
  // Закрыть все попапы
  closeAllPopups();
}

function openMobPopup(mobId) {
  const mob = getMobsData().find(m => m.id === mobId);
  if (mob) {
    showMobInPopup(mob);
  }
}

function openSearch() {
  const mobs = getMobsData();
  const items = getItemsData();
  // Собираем все уникальные id предметов из дропа мобов
  const dropItemIds = new Set();
  mobs.forEach(mob => {
    (mob.drop || []).forEach(drop => dropItemIds.add(drop.id));
  });

  // --- ДОБАВЛЯЕМ ПРЕДМЕТЫ ИЗ РЕЦЕПТОВ ---
  let recipeItems = [];
  if (allData && allData.recipes) {
    const recipes = Array.isArray(allData.recipes.list) ? allData.recipes.list : allData.recipes;
    const recipesById = {};
    recipes.forEach(r => { recipesById[r.id] = r; });
    // Собираем все уникальные id предметов из craftItems
    const recipeItemMap = {};
    recipes.forEach(r => {
      (r.craftItems || []).forEach(it => {
        if (!recipeItemMap[it.id]) recipeItemMap[it.id] = it;
      });
    });
    // Добавляем предметы из рецептов, которых нет в itemsData
    recipeItems = Object.values(recipeItemMap).filter(it => !items.find(i => i.id === it.id));
  }

  // Формируем массив предметов для отображения
  const dropItems = Array.from(dropItemIds).map(id => {
    const item = items.find(it => it.id === id);
    if (item) return item;
    // Если предмета нет в itemsData, делаем заглушку
    return { id, name: id, icon: '', type: '' };
  });
  // Добавляем крафтовые предметы
  const allSearchItems = [...dropItems, ...items, ...recipeItems];
  // Убираем дубли по id
  const uniqueItems = [];
  const seen = new Set();
  for (const it of allSearchItems) {
    if (!seen.has(it.id)) {
      uniqueItems.push(it);
      seen.add(it.id);
    }
  }
  // ---
  import('./search-engine.js').then(mod => {
    mod.showSearchPopup({
      mobs,
      items: uniqueItems,
      onSelectMob: mob => {},
      onSelectItem: item => {
        // Открываем поп-ап с подробной инфой о предмете
        const recipes = (allData && allData.recipes) || (allData && allData.Rec) || [];
        const recipeList = Array.isArray(recipes.list) ? recipes.list : recipes;
        const recipesById = {};
        recipeList.forEach(r => { recipesById[r.id] = r; });
        mod.showModalPopup(renderItemPopup(item.id, recipesById));
      },
      setLocationAndSide,
      openMobPopup
    });
  });
}

function showPopupStub(title) {
  const popup = document.getElementById('popup-search');
  popup.classList.remove('hidden');
  popup.innerHTML = `<div class='popup-content'><h2 style='margin-bottom:1em;'>${title}</h2><div style='opacity:0.7;'>Раздел в разработке</div><button class='popup-close-btn'>✕</button></div>`;
}

// === РЕЦЕПТЫ: Рекурсивный подсчёт итоговых ресурсов ===

/**
 * Рекурсивно считает итоговое количество каждого ресурса для крафта рецепта
 * @param {string} recipeId - id рецепта из Rec.json
 * @param {number} craftCount - сколько раз нужно скрафтить (по умолчанию 1)
 * @param {Object} recipesById - карта всех рецептов по id
 * @param {Set} [visited] - защита от зацикливания
 * @returns {Object} { [resourceId]: { count, info } }
 */
export function calculateTotalResources(recipeId, craftCount, recipesById, visited = new Set()) {
  if (!recipesById[recipeId] || visited.has(recipeId)) return {};
  visited.add(recipeId);
  const recipe = recipesById[recipeId];
  const result = {};
  const items = recipe.craftItems || [];
  for (const item of items) {
    // Проверяем, есть ли рецепт для этого ресурса
    const subRecipe = Object.values(recipesById).find(r => r.craftElem === item.id);
    if (subRecipe) {
      // Рекурсивно считаем вложенные ресурсы
      const subTotals = calculateTotalResources(subRecipe.id, item.count * (craftCount || 1), recipesById, visited);
      for (const [resId, resObj] of Object.entries(subTotals)) {
        if (!result[resId]) result[resId] = { ...resObj };
        else result[resId].count += resObj.count;
      }
    } else {
      // Базовый ресурс
      if (!result[item.id]) {
        result[item.id] = {
          count: 0,
          info: item
        };
      }
      result[item.id].count += item.count * (craftCount || 1);
    }
  }
  visited.delete(recipeId);
  return result;
} 