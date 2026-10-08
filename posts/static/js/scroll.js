document.addEventListener('DOMContentLoaded', function() {  
    // ELEMENTOS DEL DOM //
    const container = document.getElementById('posts-container');
    const sentinel = document.getElementById('scroll-sentinel');
    const spinner = document.getElementById('loading-spinner');
    const noMorePosts = document.getElementById('no-more-posts');

    // ESTADO INICIAL //
    let nextCursor = document.getElementById('next-cursor')?.value || null;
    let hasNext = document.getElementById('has-next')?.value === 'true';
    let isLoading = false;
    
    // Obtener ID de categoría (si existe)
    const categoriaId = document.getElementById('categoria-id')?.value || null;
    
    console.log('📌 nextCursor inicial:', nextCursor);
    console.log('📌 hasNext inicial:', hasNext);
    console.log('📌 categoriaId:', categoriaId);
    
    if (!hasNext) {
        if (noMorePosts) noMorePosts.style.display = 'block';
        console.log('No hay más posts desde el inicio');
    }

    // FUNCIÓN: CARGAR MÁS POSTS //
    function loadMorePosts() {
        if (isLoading) {
            console.log('Ya está cargando...');
            return;
        }
        
        if (!hasNext) {
            console.log('No hay más posts para cargar');
            return;
        }
        
        if (!nextCursor) {
            console.log('No hay cursor, deteniendo carga');
            hasNext = false;
            if (noMorePosts) noMorePosts.style.display = 'block';
            return;
        }
        
        isLoading = true;
        if (spinner) spinner.style.display = 'block';

        // CONSTRUIR URL CON FILTRO DE CATEGORÍA//
        const guardadosMode = document.getElementById('guardados-mode')?.value === 'true';
        const feedMode = document.getElementById('feed-mode')?.value === 'true';  // ← AGREGAR ESTO
        const categoriaId = document.getElementById('categoria-id')?.value || null;
        const perfilUsername = document.getElementById('perfil-username')?.value || null;
                
        let url = `/api/posts/?last_id=${nextCursor}`;
        
        if (feedMode) {
            url += `&feed=true`;
        } else if (guardadosMode) {
            url += `&guardados=true`;
        } else if (categoriaId) {
            url += `&categoria_id=${categoriaId}`;
        } else if (perfilUsername) {
            url += `&perfil_username=${perfilUsername}`;
        }
        console.log(`Cargando con url: ${url}`);
        
        fetch(url, {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Datos recibidos:', data);
            
            if (spinner) spinner.style.display = 'none';
            isLoading = false;
            
            if (!data.posts || data.posts.length === 0) {
                console.log('No hay más posts');
                hasNext = false;
                if (noMorePosts) noMorePosts.style.display = 'block';
                return;
            }

            // VERIFICAR DUPLICADOS //
            const existingIds = new Set();
            document.querySelectorAll('.post-item').forEach(el => {
                const id = parseInt(el.dataset.postId);
                if (!isNaN(id)) existingIds.add(id);
            });
            
            const newPosts = data.posts.filter(p => !existingIds.has(p.id));
            
            if (newPosts.length === 0) {
                console.warn('Todos los posts ya estaban cargados');
                hasNext = data.has_next || false;
                if (!hasNext && noMorePosts) noMorePosts.style.display = 'block';
                return;
            }

            // AGREGAR NUEVOS POSTS AL DOM //
            newPosts.forEach((post, index) => {
                const postHTML = createPostHTML(post, index);
                container.insertAdjacentHTML('beforeend', postHTML);
            });

            // ACTUALIZAR ESTADO //
            nextCursor = data.next_cursor;
            hasNext = data.has_next || false;
            
            const cursorInput = document.getElementById('next-cursor');
            const hasNextInput = document.getElementById('has-next');
            
            if (cursorInput) cursorInput.value = nextCursor || '';
            if (hasNextInput) hasNextInput.value = hasNext ? 'true' : 'false';
            
            console.log(`✅ Próximo cursor: ${nextCursor}`);
            console.log(`✅ ¿Hay más posts? ${hasNext}`);
            
            if (!hasNext && noMorePosts) {
                noMorePosts.style.display = 'block';
                console.log('Has llegado al final de los posts');
            }
        })
        .catch(error => {
            console.error('❌ Error cargando posts:', error);
            if (spinner) spinner.style.display = 'none';
            isLoading = false;
        });
    }

    // FUNCIÓN: CREAR HTML DE UN POST //
function createPostHTML(post, index) {
    const delay = (index + 1) * 100;
    
    const categoriaBadge = post.categoria 
        ? `<span class="badge-category">${post.categoria}</span>` 
        : '';
    
    const imagenHTML = post.imagen 
        ? `<img src="${post.imagen}" class="card-img-top">` 
        : '';
    
    const likedClass = post.user_has_liked ? 'liked' : '';
    const heartIcon = post.user_has_liked ? 'fas' : 'far';
    const savedClass = post.user_has_saved ? 'saved' : '';
    const bookmarkIcon = post.user_has_saved ? 'fas' : 'far';
    
    return `
        <article class="card-modern mb-4 fade-in-up post-item" 
                style="animation-delay: ${delay}ms;" 
                data-post-id="${post.id}">
            ${imagenHTML}
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-start">
                    <h2 class="h3 fw-bold">
                        <a href="/post/${post.id}/" class="text-decoration-none text-dark">
                            ${post.titulo}
                        </a>
                    </h2>
                    ${categoriaBadge}
                </div>
                
                <div class="text-muted small mb-3">
                    <i class="fas fa-user"></i> ${post.autor} 
                    <i class="fas fa-calendar-alt ms-2"></i> ${post.fecha}
                </div>
                
                <p>${post.contenido}</p>
                
                <div class="post-actions">
                    <button class="action-btn like-btn ${likedClass}" 
                            data-post-id="${post.id}"
                            onclick="toggleLike(${post.id})">
                        <i class="${heartIcon} fa-thumbs-up"></i>
                        <span class="count" id="like-count-${post.id}">${post.likes_count}</span>
                    </button>
                    
                    <button class="action-btn save-btn ${savedClass}" 
                            data-post-id="${post.id}"
                            onclick="toggleGuardado(${post.id})">
                        <i class="${bookmarkIcon} fa-bookmark"></i>
                    </button>
                    
                    <a href="/post/${post.id}/" class="action-btn comment-btn">
                        <i class="far fa-comment"></i>
                        <span class="count">${post.comentarios_count}</span>
                    </a>
                    
                    <a href="/post/${post.id}/" class="btn btn-primary-modern btn-modern ms-auto">
                        Leer más <i class="fas fa-arrow-right"></i>
                    </a>
                </div>
            </div>
        </article>
    `;
}

    // INTERSECTION OBSERVER //
    if (sentinel) {
        console.log('🔭 Observando sentinel');
        
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    console.log('Sentinel visible, cargando más...');
                    loadMorePosts();
                }
            });
        }, {
            root: null,
            rootMargin: '0px 0px 100px 0px',
            threshold: 0.1
        });
        
        observer.observe(sentinel);
        console.log('Observer configurado correctamente');
    } else {
        console.error('Sentinel no encontrado en el DOM');
    }

    // DEPURACIÓN //
    window.debugScroll = {
        loadMore: loadMorePosts,
        state: () => ({
            nextCursor,
            hasNext,
            isLoading,
            categoriaId,
            totalPosts: document.querySelectorAll('.post-item').length
        })
    };
    
    console.log('Para depurar, usa: debugScroll.state() o debugScroll.loadMore()');
});