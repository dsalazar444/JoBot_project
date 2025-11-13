// interview.js
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('streak-calendar');
  if (!container) return;

  const today = new Date();
  let currentMonth = today.getMonth(); // 0-11
  let currentYear = today.getFullYear();

  // set de fechas marcadas (YYYY-MM-DD)
  const streakSet = new Set(Array.isArray(window.initialStreak) ? window.initialStreak : []);

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
      if (streakSet.has(dateStr)) cell.classList.add('sc-streak');

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

  // delegation: clicks on day toggles streak
  container.addEventListener('click', (e) => {
    const dayEl = e.target.closest('.sc-day[data-date]');
    if (!dayEl) return;
    const date = dayEl.dataset.date;
    if (streakSet.has(date)) {
      streakSet.delete(date);
      dayEl.classList.remove('sc-streak');
    } else {
      streakSet.add(date);
      dayEl.classList.add('sc-streak');
    }
    // dispatch event for other code / backend
    document.dispatchEvent(new CustomEvent('streakChanged', { detail: Array.from(streakSet) }));
    // Optional: call saveStreakToServer(Array.from(streakSet));
  });

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

document.addEventListener('DOMContentLoaded', function () {
    const endButton = document.getElementById('end-session-button');
    const summaryBox = document.getElementById('session-summary');
    const avgTimeSpan = document.getElementById('avg-time');
    const recommendationP = document.getElementById('recommendation-text');

    // URL del resumen (usa el name de la ruta que pusimos en urls.py)
    const sessionSummaryUrl = "{% url 'session_summary' session.id %}";

    if (endButton) {
        endButton.addEventListener('click', async function () {
            try {
                const response = await fetch(sessionSummaryUrl, {
                    method: 'GET'
                });

                const data = await response.json();

                if (data.success) {
                    avgTimeSpan.textContent = data.average_formatted;
                    recommendationP.textContent = data.recommendation;
                    summaryBox.classList.remove('d-none');
                    summaryBox.scrollIntoView({ behavior: 'smooth' });
                } else {
                    alert(data.error || 'No se pudo calcular el promedio de la sesión.');
                }
            } catch (error) {
                console.error(error);
                alert('Error obteniendo el resumen de la sesión.');
            }
        });
    }
});