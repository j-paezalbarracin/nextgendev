document.addEventListener('DOMContentLoaded', function() {
    const notifBtn = document.getElementById('notif-btn');
    const notifDropdown = document.getElementById('notif-dropdown');
    const notifBadge = document.getElementById('notif-badge');
    const notifList = document.getElementById('notif-list');
    
    if (!notifBtn) return;
    
    let ws = null;
    // CARGAR NOTIFICACIONES //
    function cargarNotificaciones() {
        fetch('/api/notificaciones/')
            .then(r => r.json())
            .then(data => {
                renderNotificaciones(data.notificaciones);
                actualizarBadge(data.total_no_leidas);
            })
            .catch(error => console.error('Error:', error));
    }
    
    function renderNotificaciones(notifs) {
        if (notifs.length === 0) {
            notifList.innerHTML = '<div class="notif-empty">No tienes notificaciones</div>';
            return;
        }
        
        notifList.innerHTML = notifs.map(n => {
            const avatar = n.actor_avatar 
                ? `<img src="${n.actor_avatar}" class="notif-avatar">`
                : `<div class="notif-avatar-icon"><i class="fas fa-user"></i></div>`;
            
            let mensaje = '';
            let url = '#';
            
            if (n.tipo === 'like') {
                mensaje = `<strong>${n.actor}</strong> le dio like a tu post`;
                url = `/post/${n.post_id}/`;
            } else if (n.tipo === 'comentario') {
                mensaje = `<strong>${n.actor}</strong> comentó en tu post`;
                url = `/post/${n.post_id}/`;
            } else if (n.tipo === 'seguir') {
                mensaje = `<strong>${n.actor}</strong> empezó a seguirte`;
                url = `/perfil/${n.actor}/`;
            }
            
            return `
                <a href="${url}" 
                class="notif-item ${!n.leida ? 'no-leida' : ''}"
                data-notif-id="${n.id}"
                data-leida="${n.leida}"
                onclick="marcarYRedirigir(event, ${n.id}, '${url}')">
                    ${avatar}
                    <div class="notif-content">
                        <p>${mensaje}</p>
                        <small>${n.creada}</small>
                    </div>
                </a>
            `;
        }).join('');
    }
    
    function actualizarBadge(count) {
        if (count > 0) {
            notifBadge.textContent = count > 99 ? '99+' : count;
            notifBadge.style.display = 'flex';
        } else {
            notifBadge.style.display = 'none';
        }
    }

    // WEBSOCKET //
    function conectarWebSocket() {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${protocol}//${window.location.host}/ws/notificaciones/`);
        
        ws.onopen = () => console.log('✅ WebSocket notificaciones conectado');
        
        ws.onmessage = (e) => {
            const data = JSON.parse(e.data);
            if (data.type === 'notificacion') {
                cargarNotificaciones();
                mostrarToast(data.mensaje);
            }
        };
        
        ws.onerror = (error) => console.error('WebSocket error:', error);
        ws.onclose = () => {
            console.log('WebSocket desconectado, reconectando en 3s...');
            setTimeout(conectarWebSocket, 3000);
        };
    }
    
    function mostrarToast(mensaje) {
        const toast = document.createElement('div');
        toast.className = 'notif-toast';
        toast.innerHTML = `<i class="fas fa-bell"></i> ${mensaje}`;
        document.body.appendChild(toast);
        
        setTimeout(() => toast.classList.add('show'), 100);
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => toast.remove(), 300);
        }, 4000);
    }

    // MARCAR COMO LEÍDA Y REDIRIGIR //
    window.marcarYRedirigir = function(event, notifId, url) {
        event.preventDefault();
        
        // Si ya está leída, solo redirige
        const notifElement = document.querySelector(`[data-notif-id="${notifId}"]`);
        if (notifElement && notifElement.dataset.leida === 'true') {
            window.location.href = url;
            return;
        }
        
        // Marcar como leída
        fetch(`/notificaciones/${notifId}/leer/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
            },
        })
        .then(r => r.json())
        .then(data => {
            if (data.success) {
                // Actualizar badge
                actualizarBadge(data.total_no_leidas);
                
                // Quitar clase "no-leida" del elemento
                if (notifElement) {
                    notifElement.classList.remove('no-leida');
                    notifElement.dataset.leida = 'true';
                }
            }
            // Redirigir
            window.location.href = url;
        })
        .catch(error => {
            console.error('Error:', error);
            // Si falla, igual redirige
            window.location.href = url;
        });
    };

    // TOGGLE DROPDOWN //
    window.toggleNotifDropdown = function() {
        notifDropdown.classList.toggle('active');
        if (notifDropdown.classList.contains('active')) {
            cargarNotificaciones();
        }
    };
    
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.notif-container')) {
            notifDropdown.classList.remove('active');
        }
    });

    // INICIALIZAR //
    cargarNotificaciones();
    conectarWebSocket();
});