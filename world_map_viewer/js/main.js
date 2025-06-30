import { loadAllData, getWorldMapData, getMobsData, getItemsData } from './data-loader.js';
import { renderMap } from './map-renderer.js';
import { showSearchPopup } from './search-engine.js';

let selectedLocation = null;
let selectedSide = null;
let allData = null;

window.addEventListener('DOMContentLoaded', async () => {
  allData = await loadAllData();
  initLocationSelect();
  document.getElementById('search-btn').onclick = openSearch;
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
    if (cell.loco_id) {
      type = 'inner';
    } else if (cell.has_mobs) {
      type = 'mob';
      // Найти моба по location и side
      const locName = locObj.name;
      const mob = mobsData.find(m => m.location === locName && m.side === sideNames[sideKey]);
      if (mob) mobId = mob.id;
    }
    return {
      type,
      label: cell.loco_name || (cell.mob_level ? String(cell.mob_level) : ''),
      innerInfo: cell.loco_id ? { name: cell.loco_name, desc: '' } : undefined,
      cellId,
      mobId
    };
  });
  // Рендер с обработчиком клика по мобу
  renderMap(gridData, mapSection, showInnerLocationInfo, openMobPopup);
}

function showInnerLocationInfo(innerInfo) {
  // Показываем pop-up с описанием внутренней локации
  const popup = document.getElementById('popup-search');
  popup.classList.remove('hidden');
  popup.innerHTML = `<div class='popup-content'><h3>${innerInfo.name}</h3><p>${innerInfo.desc||''}</p><button onclick="document.getElementById('popup-search').classList.add('hidden')">Закрыть</button></div>`;
}

function renderMobsSection() {
  const mobsSection = document.getElementById('mobs-section');
  mobsSection.innerHTML = '';
  if (!selectedLocation || selectedSide === null) return;
  // Пока нет данных о мобах для новых локаций — оставляем пусто
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
  // Закрыть все модальные окна
  document.querySelectorAll('.modal-popup').forEach(e => e.remove());
}

function openMobPopup(mobId) {
  const mob = getMobsData().find(m => m.id === mobId);
  if (mob) {
    // Импортируем функцию из search-engine.js
    import('./search-engine.js').then(mod => {
      mod.showSearchPopup({
        mobs: getMobsData(),
        items: getItemsData(),
        onSelectMob: () => {},
        onSelectItem: () => {},
        setLocationAndSide,
        openMobPopup
      });
      // Открываем только модалку моба
      mod.showSearchPopup({
        mobs: getMobsData(),
        items: getItemsData(),
        onSelectMob: () => {},
        onSelectItem: () => {},
        setLocationAndSide,
        openMobPopup
      });
      // showModalPopup уже есть в глобале
      window.showModalPopup && window.showModalPopup(mod.renderMobDetails(mob));
    });
  }
}

function openSearch() {
  showSearchPopup({
    mobs: getMobsData(),
    items: getItemsData(),
    onSelectMob: mob => {},
    onSelectItem: item => {},
    setLocationAndSide,
    openMobPopup
  });
} 