let popup = null;
let currentType = 'mob';
let allMobs = [];
let allItems = [];
let onSelectMob = null;
let onSelectItem = null;

function renderList(list, type) {
  const results = document.createElement('div');
  results.className = 'search-results';
  list.forEach(obj => {
    const row = document.createElement('div');
    row.className = 'search-row';
    row.onclick = (e) => {
      e.stopPropagation();
      showModalPopup(type === 'mob' ? renderMobDetails(obj) : renderItemDetails(obj));
      if (type === 'mob' && onSelectMob) onSelectMob(obj);
      if (type === 'item' && onSelectItem) onSelectItem(obj);
    };
    const icon = document.createElement('img');
    icon.className = 'mob-icon';
    icon.src = obj.photo || obj.icon || '';
    icon.alt = obj.name;
    row.appendChild(icon);
    const name = document.createElement('span');
    name.textContent = obj.name;
    row.appendChild(name);
    results.appendChild(row);
  });
  return results;
}

export function showSearchPopup({mobs, items, onSelectMob: mobCb, onSelectItem: itemCb, setLocationAndSide, openMobPopup}) {
  allMobs = mobs;
  allItems = items;
  onSelectMob = mobCb;
  onSelectItem = itemCb;
  window._setLocationAndSide = setLocationAndSide;
  window._openMobPopup = openMobPopup;
  const oldPopup = document.getElementById('popup-search');
  if (oldPopup) oldPopup.remove();
  popup = document.createElement('div');
  popup.id = 'popup-search';
  popup.className = 'popup-search';
  document.body.appendChild(popup);
  popup.classList.remove('hidden');
  let type = currentType;
  function render() {
    popup.innerHTML = `<div class='popup-content' style='overflow-x:hidden;box-sizing:border-box;width:100%;'>
      <div style='display:flex;gap:1rem;margin-bottom:1rem;'>
        <button class='search-type-btn${type==='mob'?' active':''}' id='search-mob-btn'>Мобы</button>
        <button class='search-type-btn${type==='item'?' active':''}' id='search-item-btn'>Предметы</button>
      </div>
      <input class='search-input' id='search-input' placeholder='Поиск...'>
      <div id='search-results'></div>
      <button class='close-btn' id='close-search-btn'>Закрыть</button>
    </div>`;
    const mobBtn = document.getElementById('search-mob-btn');
    const itemBtn = document.getElementById('search-item-btn');
    mobBtn.onclick = () => { type = 'mob'; currentType = 'mob'; mobBtn.classList.add('active'); itemBtn.classList.remove('active'); updateResults(); };
    itemBtn.onclick = () => { type = 'item'; currentType = 'item'; itemBtn.classList.add('active'); mobBtn.classList.remove('active'); updateResults(); };
    document.getElementById('search-input').oninput = updateResults;
    document.getElementById('close-search-btn').onclick = () => { popup.classList.add('hidden'); };
    updateResults();
  }
  function updateResults() {
    const val = document.getElementById('search-input').value.toLowerCase();
    const list = type === 'mob' ? allMobs : allItems;
    const filtered = list.filter(obj => (obj.name||'').toLowerCase().includes(val));
    const results = renderList(filtered, type);
    const resultsDiv = document.getElementById('search-results');
    resultsDiv.innerHTML = '';
    resultsDiv.appendChild(results);
  }
  popup.onclick = (e) => {
    if (e.target === popup) popup.classList.add('hidden');
  };
  render();
}

// Универсальная функция для показа любого HTML в popup-search
export function showInfoPopup(contentHtml) {
  let popup = document.getElementById('popup-search');
  if (!popup) {
    popup = document.createElement('div');
    popup.id = 'popup-search';
    popup.className = 'popup-search';
    document.body.appendChild(popup);
  }
  popup.classList.remove('hidden');
  popup.innerHTML = `<div class='popup-content'>${contentHtml}<button class='close-btn' id='close-info-btn'>Закрыть</button></div>`;
  document.getElementById('close-info-btn').onclick = () => { popup.classList.add('hidden'); };
  // Добавляем обработку клика по .mob-link для открытия карточки моба
  popup.querySelectorAll('.mob-link').forEach(link => {
    link.onclick = (ev) => {
      ev.preventDefault();
      const mobId = link.getAttribute('data-mobid');
      if (mobId && typeof window._openMobPopup === 'function') {
        window._openMobPopup(mobId);
      }
    };
  });
}

// showModalPopup теперь просто вызывает showInfoPopup
export function showModalPopup(contentHtml) {
  showInfoPopup(contentHtml);
}

// Получить список {location, side} где встречается моб
function getMobLocations(mobId) {
  try {
    const mapData = window.getWorldMapData && window.getWorldMapData();
    if (!mapData || !mapData.world_map) return [];
    const res = [];
    for (const [locId, locObj] of Object.entries(mapData.world_map)) {
      for (const [sideKey, sideObj] of Object.entries(locObj.directions || {})) {
        const squares = Object.values(sideObj.squares || {});
        if (squares.some(cell => cell.has_mobs && (cell.mob_id === mobId || (cell.mob_ids && cell.mob_ids.includes(mobId))))) {
          res.push({ locId, locName: locObj.name, sideKey });
        }
      }
    }
    return res;
  } catch { return []; }
}

export function renderMobDetails(mob) {
  let locHtml = '';
  if (Array.isArray(mob.locations) && mob.locations.length) {
    locHtml = `<div style='margin:0.7rem 0 1.2rem 0;font-size:0.98em;'>Локации:<ul style='padding-left:1.2em;margin:0;'>` +
      mob.locations.map(loc =>
        `<li><a href='#' style='color:#a7c7ff;text-decoration:underline;cursor:pointer;font-weight:600;' onclick='window.handleLocationClick("${loc.location}","${loc.side}")'>${loc.location} ${loc.side}</a></li>`
      ).join('') +
      `</ul></div>`;
  }
  return `
    <div class="mob-details">
      <div style='display:flex;gap:1.2rem;align-items:flex-start;flex-wrap:wrap;'>
        <img src='${mob.photo||''}' alt='${mob.name}' class='mob-details-img'>
        <div style='flex:1;min-width:180px;'>
          <div class='mob-title' style='font-size:1.25em;font-weight:600;'>${mob.name}</div>
          <div class='mob-id' style='font-size:0.95em;opacity:0.7;'>ID: ${mob.id} | FarmID: ${mob.farmId||''}</div>
          <div class='mob-desc' style='margin:0.5em 0 0.7em 0;'>${mob.desc||''}</div>
          ${locHtml}
        </div>
      </div>
      <div style='overflow-x:auto;max-width:100%;margin-top:1.1em;'>
        <table class='drop-table mob-drop-table'>
          <tr>
            <th style='min-width:60px;'>Иконка</th>
            <th style='min-width:110px;'>Название</th>
            <th style='min-width:90px;'>ID</th>
            <th style='min-width:90px;'>Тип</th>
            <th style='min-width:90px;'>Шанс</th>
            <th style='min-width:90px;'>Кол-во</th>
            <th style='min-width:110px;'>Уровень появления</th>
          </tr>` +
          (mob.drop||[]).map(drop => `<tr><td></td><td>${drop.id}</td><td>${drop.id}</td><td>${drop.typeElement||''}</td><td>${drop.chance||''}%</td><td>${drop.count||''}</td><td>${drop.minLvlDrop||mob.lvl||''}</td></tr>`).join('') +
        `</table>
      </div>
    </div>
  `;
}

function renderItemDetails(item) {
  // Найти всех мобов, у которых есть этот предмет в дропе
  const mobsWithDrop = allMobs.filter(m => (m.drop||[]).some(d => d.id === item.id));
  let mobsHtml = '';
  if (mobsWithDrop.length) {
    mobsHtml = `<div style='margin:0.7rem 0 1.2rem 0;font-size:0.98em;'>Добывается с мобов:<ul style='padding-left:1.2em;'>` +
      mobsWithDrop.map(mob => `<li><a href='#' class='mob-link' data-mobid='${mob.id}' style='color:#a7c7ff;text-decoration:underline;cursor:pointer;'>${mob.name}</a></li>`).join('') +
      `</ul></div>`;
  }
  return `<div style='display:flex;gap:1.2rem;align-items:flex-start;'>
    <img src='${item.icon||''}' alt='${item.name}' style='width:64px;height:64px;border-radius:8px;box-shadow:0 0 12px #3a5c8c33;background:#181a20;object-fit:cover;'>
    <div style='flex:1;'>
      <div class='mob-title'>${item.name}</div>
      <div class='mob-id'>ID: ${item.id}</div>
      <div class='mob-desc'>${item.type||''}</div>
      ${mobsHtml}
    </div>
  </div>`;
}

function hidePopup() {
  if (popup) popup.classList.add('hidden');
}

if (typeof window.getWorldMapData !== 'function') {
  window.getWorldMapData = () => window.__worldMapData;
}

// Исправляю обработку клика на моба в поп-апе предмета
window._openMobPopup = function(mobId) {
  const mob = allMobs.find(m => m.id === mobId);
  if (mob) {
    showModalPopup(renderMobDetails(mob));
  }
};

if (!window._setLocationAndSideByName) {
  window._setLocationAndSideByName = function(locName, sideRu) {
    const mapData = window.getWorldMapData && window.getWorldMapData();
    if (!mapData || !mapData.world_map) return;
    let locId = null, sideKey = null;
    for (const [id, obj] of Object.entries(mapData.world_map)) {
      if (obj.name === locName) {
        locId = id;
        for (const [key, val] of Object.entries(obj.directions||{})) {
          const sideNames = {north:'Север',east:'Восток',south:'Юг',west:'Запад'};
          if (sideNames[key] === sideRu) { sideKey = key; break; }
        }
        break;
      }
    }
    if (locId && sideKey) window._setLocationAndSide && window._setLocationAndSide(locId, sideKey);
  }
}

// Функция для закрытия всех попапов
export function closeAllPopups() {
  document.querySelectorAll('.modal-popup').forEach(e => e.remove());
  const popup = document.getElementById('popup-search');
  if (popup) popup.classList.add('hidden');
}

// Функция для отображения карточки моба прямо в popup-search
export function showMobInPopup(mob) {
  let popup = document.getElementById('popup-search');
  if (!popup) {
    popup = document.createElement('div');
    popup.id = 'popup-search';
    popup.className = 'popup-search';
    document.body.appendChild(popup);
  }
  popup.classList.remove('hidden');
  popup.innerHTML = `<div class='popup-content'>${renderMobDetails(mob)}<button class='close-btn' id='close-mob-btn'>Закрыть</button></div>`;
  document.getElementById('close-mob-btn').onclick = () => { popup.classList.add('hidden'); };
}

// --- Добавляю функцию для перехода по локации и закрытия попапа ---
window.handleLocationClick = function(loc, side) {
  if (window._setLocationAndSideByName) {
    window._setLocationAndSideByName(loc, side);
  }
  // Закрыть попап моба
  const popup = document.getElementById('popup-search');
  if (popup) popup.classList.add('hidden');
}; 