/**
 * Nhimbe AI — Main JavaScript
 * Handles mobile nav panel, alerts
 */

document.addEventListener('DOMContentLoaded', function () {

    // --- Mobile Navigation Panel ---
    var toggle = document.getElementById('navToggle');
    var panel = document.getElementById('navPanel');
    var overlay = document.getElementById('navOverlay');
    var closeBtn = document.getElementById('navClose');

    function openPanel() {
        panel.classList.add('open');
        overlay.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closePanel() {
        panel.classList.remove('open');
        overlay.classList.remove('active');
        document.body.style.overflow = '';
    }

    if (toggle) {
        toggle.addEventListener('click', openPanel);
    }

    if (closeBtn) {
        closeBtn.addEventListener('click', closePanel);
    }

    if (overlay) {
        overlay.addEventListener('click', closePanel);
    }

    // Close panel on Escape key
    document.addEventListener('keydown', function (e) {
        if (e.key === 'Escape' && panel.classList.contains('open')) {
            closePanel();
        }
    });


    // --- Auto-dismiss Alerts ---
    var alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s, transform 0.4s';
            alert.style.opacity = '0';
            alert.style.transform = 'translateY(-10px)';
            setTimeout(function () {
                alert.remove();
            }, 400);
        }, 5000);
    });

});