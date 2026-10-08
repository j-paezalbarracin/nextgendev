document.addEventListener('DOMContentLoaded', function() {
    // 🔥 BUSCAR POR ID DIRECTO (Django genera estos IDs)
    const nombreInput = document.getElementById('id_nombre');
    const slugInput = document.getElementById('id_slug');
    
    // Si no los encuentra, intenta por 'name'
    if (!nombreInput || !slugInput) {
        const nombreInput = document.querySelector('input[name="nombre"]');
        const slugInput = document.querySelector('input[name="slug"]');
    }

    if (nombreInput && slugInput) {
        nombreInput.addEventListener('input', function() {
            const nombre = this.value;
            const slug = nombre
                .toLowerCase()
                .normalize('NFD').replace(/[\u0300-\u036f]/g, '')  //  Elimina tildes
                .replace(/[^a-z0-9\s-]/g, '')                       //  Solo letras, números, espacios y guiones
                .trim()                                              //  Elimina espacios al inicio y final
                .replace(/\s+/g, '-')                               //  Reemplaza espacios por guiones
                .replace(/-+/g, '-');                               //  Evita guiones dobles
            slugInput.value = slug;
        });
    }
});