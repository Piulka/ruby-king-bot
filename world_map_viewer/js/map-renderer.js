/**
 * Рендерит карту 4x8 по данным gridData.
 * @param {Array} gridData - Массив 32 клеток: {type: 'empty'|'mob'|'inner', label, mobLevel, innerInfo}
 * @param {HTMLElement} container - DOM-элемент для рендера
 * @param {function} onInnerLocationClick - callback для клика по внутренней локации
 * @param {function} openMobPopup - callback для открытия попапа с мобом
 */
export function renderMap(gridData, container, onInnerLocationClick, openMobPopup) {
  container.innerHTML = '';
  const grid = document.createElement('div');
  grid.className = 'map-grid';
  gridData.forEach((cell, idx) => {
    const cellDiv = document.createElement('div');
    cellDiv.className = 'map-cell';
    let cellLabel = cell.label || '';
    if (cell.type === 'inner') {
      cellDiv.classList.add('cell-inner');
      cellDiv.innerHTML = `<span class="cell-label" style="white-space:normal;word-break:break-word;">${cellLabel}</span>`;
      if (cell.innerInfo && cell.innerInfo.name) {
        cellDiv.title = cell.innerInfo.name;
      }
      cellDiv.style.cursor = 'pointer';
      cellDiv.onclick = () => onInnerLocationClick(cell.innerInfo);
    } else if ((cellLabel && cellLabel.includes('-')) || (cellLabel && !isNaN(Number(cellLabel)) && Number(cellLabel) > 0)) {
      cellDiv.classList.add('cell-mob');
      cellDiv.innerHTML = `<span class=\"cell-label\">${cellLabel}</span>`;
      if (cell.mobId && openMobPopup) {
        cellDiv.style.cursor = 'pointer';
        cellDiv.onclick = () => openMobPopup(cell.mobId);
      }
    } else if (cellLabel) {
      cellDiv.classList.add('cell-lvl');
      cellDiv.innerHTML = `<span class=\"cell-label\">${cellLabel}</span>`;
    } else {
      cellDiv.classList.add('cell-empty');
      cellDiv.textContent = '';
    }
    if (cell.cellId) {
      const idDiv = document.createElement('div');
      idDiv.textContent = cell.cellId;
      idDiv.style.position = 'absolute';
      idDiv.style.bottom = '2px';
      idDiv.style.right = '4px';
      idDiv.style.fontSize = '0.65em';
      idDiv.style.opacity = '0.7';
      idDiv.style.pointerEvents = 'none';
      cellDiv.appendChild(idDiv);
      cellDiv.style.position = 'relative';
    }
    grid.appendChild(cellDiv);
  });
  container.appendChild(grid);
} 