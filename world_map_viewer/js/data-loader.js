let worldMapData = null;
let mobsData = null;
let itemsData = null;

async function loadJSON(url) {
  const response = await fetch(url);
  if (!response.ok) throw new Error(`Ошибка загрузки ${url}`);
  return await response.json();
}

export async function loadAllData() {
  if (!worldMapData) worldMapData = await loadJSON('data/complete_world_map.json');
  if (!mobsData) mobsData = await loadJSON('data/mobs-database.json');
  if (!itemsData) itemsData = await loadJSON('data/items-database.json');
  window.__worldMapData = worldMapData;
  return { worldMapData, mobsData, itemsData };
}

export function getWorldMapData() { return worldMapData; }
export function getMobsData() { return mobsData; }
export function getItemsData() { return itemsData; } 