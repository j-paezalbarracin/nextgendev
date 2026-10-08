document.addEventListener('DOMContentLoaded', function() {
    const postId = document.getElementById('post-id').value;
    
    // SELECTORES MÁS ESPECÍFICOS
    const input = document.querySelector('#comentario-input');
    const btnEnviar = document.querySelector('#btn-enviar-comentario');
    const form = document.querySelector('#form-comentario');
    
    console.log('🔍 Selectores encontrados:', {
        input: !!input,
        btnEnviar: !!btnEnviar,
        form: !!form
    });
    
    let socket = null;
    let reconectarTimeout = null;

    function conectarWebSocket() {
        if (reconectarTimeout) {
            clearTimeout(reconectarTimeout);
            reconectarTimeout = null;
        }
        
        const wsUrl = `ws://${window.location.host}/ws/comentarios/${postId}/`;
        socket = new WebSocket(wsUrl);
        
        socket.onopen = function(e) {
            console.log('✅ WebSocket conectado');
        };

        socket.onmessage = function(e) {
            try {
                const data = JSON.parse(e.data);
                console.log('📩 Datos recibidos:', data);
                
                if (data.error) {
                    alert('Error: ' + data.error);
                    return;
                }
                
                if (data.tipo === 'conexion') {
                    console.log('📡', data.mensaje);
                    return;
                }
                
                //  Pasar el avatar a la función
                agregarComentario(data.usuario, data.mensaje, data.fecha, data.avatar);
            } catch (error) {
                console.error('Error al procesar mensaje:', error);
            }
        };

        socket.onerror = function(e) {
            console.error('❌ Error WebSocket:', e);
        };

        socket.onclose = function(e) {
            console.log('🔌 Desconectado, reconectando...');
            reconectarTimeout = setTimeout(conectarWebSocket, 3000);
        };
    }

    //  FUNCIÓN ACTUALIZADA: Recibe el avatar
    function agregarComentario(usuario, mensaje, fecha, avatar) {
        console.log('📝 Agregando comentario:', usuario, mensaje, avatar);
        
        const comentariosSection = document.querySelector('.card-modern.mt-4 .card-body');
        if (!comentariosSection) {
            console.error('❌ No se encontró el contenedor de comentarios');
            return;
        }
        
        const emptyMsg = comentariosSection.querySelector('.text-center');
        if (emptyMsg) {
            emptyMsg.remove();
        }
        
        let container = comentariosSection.querySelector('.comentarios-lista');
        if (!container) {
            container = document.createElement('div');
            container.className = 'comentarios-lista';
            const title = comentariosSection.querySelector('h4');
            if (title) {
                title.after(container);
            } else {
                comentariosSection.prepend(container);
            }
        }
        //  ACTUALIZAR CONTADOR
        const contador = document.getElementById('contador-comentarios');
        if (contador) {
            const currentCount = parseInt(contador.textContent) || 0;
            contador.textContent = currentCount + 1;
            
            // Animación (opcional)
            contador.style.transform = 'scale(1.3)';
            contador.style.transition = 'transform 0.3s ease';
            setTimeout(() => {
                contador.style.transform = 'scale(1)';
            }, 300);
            
            console.log(`✅ Contador actualizado: ${currentCount + 1}`);
        }
        //  Avatar HTML
        const avatarHTML = avatar 
            ? `<img src="${avatar}" alt="${usuario}">`
            : `<i class="fas fa-user"></i>`;
        
        const div = document.createElement('div');
        div.className = 'comment-item';
        div.style.animation = 'fadeIn 0.3s ease-in';
        div.innerHTML = `
            <div class="d-flex gap-2">
                <!-- Avatar clickeable -->
                <div class="comment-avatar">
                    <a href="/perfil/${usuario}/" class="comment-avatar-link">
                        ${avatarHTML}
                    </a>
                </div>
                
                <!-- Contenido -->
                <div class="comment-body">
                    <div class="d-flex justify-content-between">
                        <strong>
                            <a href="/perfil/${usuario}/" class="comment-author-link">
                                ${usuario}
                            </a>
                        </strong>
                        <small class="text-muted">${fecha || 'Ahora'}</small>
                    </div>
                    <p class="mb-0 mt-1">${mensaje}</p>
                </div>
            </div>
        `;
        
        container.prepend(div);
        console.log('✅ Comentario agregado al DOM');
        
        const counter = comentariosSection.querySelector('h4 .badge');
        if (counter) {
            const currentCount = parseInt(counter.textContent) || 0;
            counter.textContent = currentCount + 1;
        }
        
        if (input) {
            input.value = '';
        }
    }

    //  FUNCIÓN PARA ENVIAR COMENTARIO
    function enviarComentario() {
        if (!input) {
            console.error('❌ Input no encontrado');
            return;
        }
        
        const mensaje = input.value.trim();
        if (!mensaje) {
            input.focus();
            input.style.borderColor = 'red';
            setTimeout(() => {
                input.style.borderColor = '';
            }, 2000);
            return;
        }
        
        if (!socket || socket.readyState !== WebSocket.OPEN) {
            alert('No hay conexión en tiempo real. El comentario se guardará al recargar.');
            if (form) {
                form.submit();
            }
            return;
        }
        
        console.log('📤 Enviando comentario por WebSocket:', mensaje);
        socket.send(JSON.stringify({
            'mensaje': mensaje
        }));
        
        if (btnEnviar) {
            btnEnviar.disabled = true;
            btnEnviar.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enviando...';
            setTimeout(() => {
                btnEnviar.disabled = false;
                btnEnviar.innerHTML = '<i class="fas fa-paper-plane"></i> Comentar';
            }, 2000);
        }
        
        if (input) {
            input.value = '';
        }
    }

    //  EVENTO PARA EL BOTÓN
    if (btnEnviar) {
        console.log('✅ Botón encontrado, agregando evento click');
        btnEnviar.addEventListener('click', function(e) {
            e.preventDefault();
            console.log('🖱️ Click en botón');
            enviarComentario();
        });
    } else {
        console.warn('⚠️ Botón NO encontrado');
    }

    //  EVENTO PARA EL FORMULARIO (fallback)
    if (form) {
        console.log('✅ Formulario encontrado, agregando evento submit');
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            console.log('📋 Submit del formulario');
            enviarComentario();
        });
    } else {
        console.warn('⚠️ Formulario NO encontrado');
    }

    //  EVENTO PARA ENTER
    if (input) {
        input.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                console.log('⌨️ Enter presionado');
                enviarComentario();
            }
        });
    }

    //  INICIAR CONEXIÓN
    conectarWebSocket();
});

//  ESTILO PARA ANIMACIÓN
const style = document.createElement('style');
style.textContent = `
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);