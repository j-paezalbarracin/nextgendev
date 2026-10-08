        // Auto-cerrar alertas después de 4 segundos
        setTimeout(function() {
            var alerts = document.querySelectorAll('.alert.alert-success');
            alerts.forEach(function(alert) {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(function() {
                    alert.remove();
                }, 500);
            });
        }, 4000);
