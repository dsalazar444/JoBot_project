// reviews.js
(function(){
  const DATA_URL = './data/reviews.json';

  const container = document.getElementById('reviews');
  const empty = document.getElementById('empty');

  // Si se abre como file://, fetch suele fallar por CORS
  if (location.protocol === 'file:') {
    container?.setAttribute('aria-busy', 'false');
    console.info('[reviews] Ejecutando en modo archivo; levanta un servidor local para cargar datos.');
    return;
  }

  async function loadReviews(){
    try {
      const resp = await fetch(DATA_URL, { cache: 'no-store' });
      if (!resp.ok) throw new Error('No se pudo cargar reviews.json');
      const data = await resp.json();
      if (!Array.isArray(data) || data.length === 0){
        container?.setAttribute('aria-busy', 'false');
        return; // mantener estado vacío
      }

      // limpiar estado vacío
      empty?.remove();

      for (const item of data){
        if (!item || !item.quote || !item.name) continue;

        const card = document.createElement('article');
        card.className = 'card';
        card.setAttribute('aria-label', `Opinión de ${item.name}`);

        const quote = document.createElement('p');
        quote.className = 'quote';
        quote.textContent = '“' + item.quote + '”';
        card.appendChild(quote);

        const author = document.createElement('div');
        author.className = 'author';

        const avatar = document.createElement('img');
        avatar.className = 'avatar';
        avatar.alt = '';
        avatar.loading = 'lazy';
        avatar.decoding = 'async';
        avatar.src = item.avatarUrl || 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 40 40"><circle cx="20" cy="20" r="20" fill="%23f8fafc" stroke="%23e2e8f0"/><circle cx="20" cy="15" r="7" fill="%23e2e8f0"/><rect x="7" y="25" width="26" height="10" rx="5" fill="%23e2e8f0"/></svg>';
        author.appendChild(avatar);

        const meta = document.createElement('div');
        meta.className = 'meta';
        const name = document.createElement('div');
        name.className = 'name';
        name.textContent = item.name;
        const role = document.createElement('div');
        role.className = 'role';
        role.textContent = item.role || '';
        meta.appendChild(name);
        meta.appendChild(role);
        author.appendChild(meta);

        card.appendChild(author);
        container.appendChild(card);
      }

      container?.setAttribute('aria-busy', 'false');
    } catch (err){
      container?.setAttribute('aria-busy', 'false');
      console.warn('Reviews no disponibles aún:', err);
    }
  }

  loadReviews();
})();
