// interview.js
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('streak-calendar');
  if (!container) return;

  const today = new Date();
  let currentMonth = today.getMonth(); // 0-11
  let currentYear = today.getFullYear();

  // set de fechas marcadas (YYYY-MM-DD)
  console.log('Practice dates from window:', window.practiceDates);
  const streakSet = new Set(Array.isArray(window.practiceDates) ? window.practiceDates : []);
  console.log('Streak set initialized:', Array.from(streakSet));

  const monthNames = ["January","February","March","April","May","June","July","August","September","October","November","December"];
  const weekNames = ["S","M","T","W","T","F","S"];

  function pad(n){ return String(n).padStart(2,'0'); }
  function fmtDate(y,m,d){ return `${y}-${pad(m+1)}-${pad(d)}`; } // m is 0-based

  function renderCalendar() {
    container.innerHTML = ''; // clear

    // header: month + nav
    const header = document.createElement('div');
    header.className = 'sc-header d-flex align-items-center justify-content-between';
    header.innerHTML = `
      <button class="sc-nav sc-prev" aria-label="prev">&lt;</button>
      <div class="sc-month">${monthNames[currentMonth]} ${currentYear}</div>
      <button class="sc-nav sc-next" aria-label="next">&gt;</button>
    `;
    container.appendChild(header);

    // weekdays row
    const weekdays = document.createElement('div');
    weekdays.className = 'sc-weekdays';
    weekNames.forEach(w => {
      const el = document.createElement('div');
      el.className = 'sc-weekday';
      el.textContent = w;
      weekdays.appendChild(el);
    });
    container.appendChild(weekdays);

    // grid of days
    const grid = document.createElement('div');
    grid.className = 'sc-grid';

    const firstDay = new Date(currentYear, currentMonth, 1).getDay(); // 0..6
    const daysInMonth = new Date(currentYear, currentMonth+1, 0).getDate();

    // blanks for first week
    for (let i=0;i<firstDay;i++){
      const blank = document.createElement('div');
      blank.className = 'sc-day sc-day--empty';
      grid.appendChild(blank);
    }

    for (let d=1; d<=daysInMonth; d++){
      const dateStr = fmtDate(currentYear, currentMonth, d);
      const cell = document.createElement('button');
      cell.type = 'button';
      cell.className = 'sc-day';
      cell.dataset.date = dateStr;
      cell.innerHTML = `<span class="sc-day-number">${d}</span>`;

      // today marker
      const isToday = dateStr === fmtDate(today.getFullYear(), today.getMonth(), today.getDate());
      if (isToday) cell.classList.add('sc-today');

      // if present in streakSet, add class
      if (streakSet.has(dateStr)) {
        console.log('Marking date as streak:', dateStr);
        cell.classList.add('sc-streak');
      }

      grid.appendChild(cell);
    }

    container.appendChild(grid);

    // attach nav listeners
    header.querySelector('.sc-prev').onclick = () => {
      changeMonth(-1);
    };
    header.querySelector('.sc-next').onclick = () => {
      changeMonth(1);
    };
  }

  function changeMonth(delta){
    currentMonth += delta;
    if (currentMonth < 0){ currentMonth = 11; currentYear -= 1; }
    if (currentMonth > 11){ currentMonth = 0; currentYear += 1; }
    renderCalendar();
  }

  // Los días de práctica son de solo lectura, no se pueden modificar manualmente

  // expose helper to set streak days from outside
  window.setStreakDates = (arr) => {
    streakSet.clear();
    if (Array.isArray(arr)) arr.forEach(d => streakSet.add(d));
    renderCalendar();
  };

  window.getStreakDates = () => Array.from(streakSet);

  // initial render
  renderCalendar();
});
