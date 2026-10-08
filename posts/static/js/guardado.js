function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function toggleGuardado(postId) {
    const saveBtn = document.querySelector(`button[data-post-id="${postId}"].save-btn`);
    
    if (!saveBtn) return;
    
    const icon = saveBtn.querySelector('i');
    const textSpan = saveBtn.querySelector('span');
    
    fetch(`/guardar/${postId}/`, {
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
        if (!data) return;
        
        if (data.success) {
            if (data.saved) {
                saveBtn.classList.add('saved');
                if (icon) icon.className = 'fas fa-bookmark';
                if (textSpan && textSpan.textContent !== 'Guardado') {
                    textSpan.textContent = 'Guardado';
                }
            } else {
                saveBtn.classList.remove('saved');
                if (icon) icon.className = 'far fa-bookmark';
                if (textSpan && textSpan.textContent !== 'Guardar') {
                    textSpan.textContent = 'Guardar';
                }
            }
        }
    })
    .catch(error => {
        console.error('Error al guardar:', error);
    });
}