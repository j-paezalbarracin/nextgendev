document.addEventListener('DOMContentLoaded', function() {
    console.log('🔍 search.js cargado correctamente');

    // ELEMENTOS DEL DOM //
    const searchInput = document.getElementById('search-input');
    const searchResults = document.getElementById('search-results');
    const searchInputMobile = document.getElementById('search-input-mobile');
    const searchResultsMobile = document.getElementById('search-results-mobile');
    
    let debounceTimer = null;

    // FUNCIÓN: REALIZAR BÚSQUEDA //
    function performSearch(query, resultsContainer) {
        if (!resultsContainer) return;
        
        // Si el query es muy corto, ocultar resultados
        if (query.length < 2) {
            resultsContainer.classList.remove('active');
            resultsContainer.innerHTML = '';
            return;
        }
        
        // Mostrar loading
        resultsContainer.innerHTML = `<div class="search-loading">Buscando...</div>`;
        resultsContainer.classList.add('active');
        
        // Hacer fetch a la API
        fetch(`/api/search/?q=${encodeURIComponent(query)}`)
            .then(r => r.json())
            .then(data => {
                // Si no hay resultados
                if (data.results.length === 0) {
                    resultsContainer.innerHTML = `
                        <div class="search-empty">
                            No se encontraron resultados para "<strong>${query}</strong>"
                        </div>
                    `;
                    return;
                }
                
                // Construir HTML con los resultados
                let html = '';
                data.results.forEach(post => {
                    html += `
                        <div class="search-item" onclick="window.location.href='/post/${post.id}/'">
                            <div class="search-item-title">${post.titulo}</div>
                        </div>
                    `;
                });
                resultsContainer.innerHTML = html;
            })
            .catch(error => {
                console.error('Error en búsqueda:', error);
                resultsContainer.innerHTML = `
                    <div class="search-empty">Error al buscar. Intenta de nuevo.</div>
                `;
            });
    }

    // EVENTO: BUSCADOR DE ESCRITORIO //
    if (searchInput) {
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(() => {
                performSearch(query, searchResults);
            }, 300);
        });
    }

    // EVENTO: BUSCADOR DE MÓVIL //
    if (searchInputMobile) {
        searchInputMobile.addEventListener('input', function() {
            const query = this.value.trim();
            clearTimeout(debounceTimer);
            
            debounceTimer = setTimeout(() => {
                performSearch(query, searchResultsMobile);
            }, 300);
        });
    }

    // CERRAR RESULTADOS AL HACER CLIC FUERA //
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.sidebar-search')) {
            if (searchResults) searchResults.classList.remove('active');
            if (searchResultsMobile) searchResultsMobile.classList.remove('active');
        }
    });

    // CERRAR CON ESC //
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
            if (searchResults) searchResults.classList.remove('active');
            if (searchResultsMobile) searchResultsMobile.classList.remove('active');
        }
    });
});