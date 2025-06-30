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
  if (!popup) {
    popup = document.createElement('div');
    popup.id = 'popup-search';
    popup.className = 'popup-search';
    document.body.appendChild(popup);
  }
  popup.classList.remove('hidden');
  let type = currentType;
  function render() {
    popup.innerHTML = `<div class='popup-content'>
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

export function showModalPopup(contentHtml) {
  let modal = document.createElement('div');
  modal.className = 'modal-popup';
  modal.innerHTML = `<div class='modal-content'>${contentHtml}<button class='close-btn' id='close-modal-btn'>Закрыть</button></div>`;
  document.body.appendChild(modal);
  modal.querySelector('#close-modal-btn').onclick = () => { modal.remove(); };
  modal.onclick = (e) => {
    if (e.target === modal) modal.remove();
  };
  // Делегируем клик на моба
  modal.querySelectorAll('.mob-link').forEach(link => {
    link.onclick = (ev) => {
      ev.preventDefault();
      const mobId = link.getAttribute('data-mobid');
      if (mobId) {
        modal.remove();
        showModalPopup(renderMobDetails(allMobs.find(m => m.id === mobId)));
      }
    };
  });
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
  const locations = getMobLocations(mob.id);
  const sideNames = {north: 'Север', east: 'Восток', south: 'Юг', west: 'Запад'};
  let locHtml = '';
  if (locations.length) {
    locHtml = `<div style='margin:0.7rem 0 1.2rem 0;font-size:0.98em;'>Локации:<ul style='padding-left:1.2em;'>` +
      locations.map(l => `<li><a href='#' style='color:#a7c7ff;text-decoration:underline;cursor:pointer;' onclick='window._setLocationAndSide&&window._setLocationAndSide("${l.locId}","${l.sideKey}")'>${l.locName} (${sideNames[l.sideKey]||l.sideKey})</a></li>`).join('') +
      `</ul></div>`;
  }
  return `<div style='max-width:420px;width:95vw;max-height:95vh;margin:0 auto;'>
    <div style='display:flex;gap:1.2rem;align-items:flex-start;'>
      <img src='${mob.photo||''}' alt='${mob.name}' style='width:64px;height:64px;border-radius:8px;box-shadow:0 0 12px #3a5c8c33;background:#181a20;object-fit:cover;'>
      <div style='flex:1;'>
        <div class='mob-title'>${mob.name}</div>
        <div class='mob-id'>ID: ${mob.id} | FarmID: ${mob.farmId||''}</div>
        <div class='mob-desc'>${mob.desc||''}</div>
        ${locHtml}
      </div>
    </div>
    <div style='overflow-x:auto;max-width:100%;margin-top:0.7em;'>
      <table class='drop-table' style='min-width:420px;'>
        <tr><th>Иконка</th><th>Название</th><th>ID</th><th>Тип</th><th>Шанс</th><th>Кол-во</th><th>Уровень появления</th></tr>` +
        (mob.drop||[]).map(drop => `<tr><td></td><td>${drop.id}</td><td>${drop.id}</td><td>${drop.typeElement||''}</td><td>${drop.chance||''}%</td><td>${drop.count||''}</td><td>${drop.minLvlDrop||mob.lvl||''}</td></tr>`).join('') +
      `</table>
    </div>
  </div>`;
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