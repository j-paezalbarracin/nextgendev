function getCSRFToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
}

function toggleLike(postId) {
    const likeBtn = document.querySelector(`button[data-post-id="${postId}"].like-btn`);
    const likeCount = document.getElementById(`like-count-${postId}`);
    
    if (!likeBtn || !likeCount) return;
    
    const icon = likeBtn.querySelector('i');
    
    fetch(`/like/${postId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCSRFToken(),
            'Content-Type': 'application/json',
        },
    })
    .then(response => {
        // Si no está autenticado (401) o no tiene permisos (403)
        // → Redirigir al login
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
            likeCount.textContent = data.likes_count;
            
            if (data.liked) {
                likeBtn.classList.add('liked');
                if (icon) icon.className = 'fas fa-thumbs-up';
            } else {
                likeBtn.classList.remove('liked');
                if (icon) icon.className = 'far fa-thumbs-up';
            }
        }
    })
    .catch(error => {
        //  Solo errores reales (no autenticación)
        console.error('Error en like:', error);
        alert('Hubo un error al procesar tu like. Intenta de nuevo.');
    });
}