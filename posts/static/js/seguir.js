function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function toggleSeguir(userId) {
    const btn = document.getElementById('btn-seguir');
    
    if (!btn) return;
    
    const icon = btn.querySelector('i');
    const text = btn.querySelector('#texto-seguir');
    
    fetch(`/seguir/${userId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        if (response.status === 401 || response.status === 403) {
            console.log('🔒 Usuario no autenticado');
            window.location.href = '/login/';
            return null;
        }
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (!data || !data.success) return;
        
        // Actualizar botón
        if (data.siguiendo) {
            btn.classList.remove('btn-primary');
            btn.classList.add('btn-outline-primary');
            if (icon) icon.className = 'fas fa-user-check';
            if (text) text.textContent = 'Siguiendo';
        } else {
            btn.classList.remove('btn-outline-primary');
            btn.classList.add('btn-primary');
            if (icon) icon.className = 'fas fa-user-plus';
            if (text) text.textContent = 'Seguir';
        }
        
        // Actualizar contador de seguidores
        const contadorSeguidores = document.querySelector('.stat-seguidores strong');
        if (contadorSeguidores) {
            contadorSeguidores.textContent = data.total_seguidores;
        }
    })
    .catch(error => {
        console.error('Error al seguir:', error);
    });
}