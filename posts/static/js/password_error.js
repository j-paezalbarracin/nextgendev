// VALIDACIÓN EN TIEMPO REAL (opcional) 
document.addEventListener('DOMContentLoaded', function() {
    const password1 = document.querySelector('input[name="new_password1"]');
    const password2 = document.querySelector('input[name="new_password2"]');

    // Si no los encuentra por nombre, intenta por ID (por si acaso)
    // const password1 = document.getElementById('id_new_password1') || document.querySelector('input[name="new_password1"]');
    // const password2 = document.getElementById('id_new_password2') || document.querySelector('input[name="new_password2"]');

    if (password1 && password2) {
        password2.addEventListener('input', function() {
            if (password1.value !== this.value) {
                this.classList.add('is-invalid');
                let feedback = this.parentElement.querySelector('.invalid-feedback');
                if (!feedback) {
                    feedback = document.createElement('div');
                    feedback.className = 'invalid-feedback d-block';
                    feedback.innerHTML = '<i class="fas fa-exclamation-circle"></i> Las contraseñas no coinciden.';
                    this.parentElement.appendChild(feedback);
                }
            } else {
                this.classList.remove('is-invalid');
                const feedback = this.parentElement.querySelector('.invalid-feedback');
                if (feedback) {
                    feedback.remove();a
                }
            }
        });
    } else {
        console.error("❌ No se encontraron los inputs.");
    }
});