/**
 * Script para manejar la funcionalidad del wishlist
 * Permite agregar/remover productos del wishlist del usuario
 */

document.addEventListener('DOMContentLoaded', function() {
    const wishlistSelector = '.wishlist.btn-icon-action';
    const wishlistButtons = document.querySelectorAll('.wishlist.btn-icon-action');

    if (!wishlistButtons.length) {
        console.warn('No se encontraron botones de wishlist al cargar la pagina.');
    }

    document.addEventListener('click', function(e) {
        const button = e.target.closest(wishlistSelector);
        if (!button) return;

        e.preventDefault();

        const productId = button.getAttribute('data-product-id');
        const wishlistId = button.getAttribute('data-wishlist-id');
        const hasValidWishlistId = !!wishlistId && wishlistId !== 'None' && wishlistId !== '';
        if (!productId) return;

        if (button.classList.contains('active') || hasValidWishlistId) {
            removeFromWishlist(productId, wishlistId, button);
        } else {
            addToWishlist(productId, button);
        }
    });

    function addToWishlist(productId, button) {
        fetch('/api/wishlist/add/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: new URLSearchParams({ product_id: productId })
        })
            .then(response => response.json())
            .then(data => {
                // Si ya existia en wishlist, el backend responde in_wishlist=true.
                if (data.success || data.in_wishlist) {
                    const alreadyInWishlist = !data.success && !!data.in_wishlist;
                    syncWishlistButtons(productId, true, data.wishlist_id || '');

                    if (!alreadyInWishlist) {
                        updateWishlistCount(1);
                    }

                    showWishlistToast(
                        data.message || (alreadyInWishlist ? 'El producto ya esta en favoritos' : 'Producto agregado a favoritos'),
                        alreadyInWishlist ? 'info' : 'success'
                    );
                    return;
                }

                showWishlistToast(data.message || 'No se pudo agregar a favoritos', 'error');
            })
            .catch(error => {
                console.error('Error al agregar a favoritos:', error);
                showWishlistToast('No se pudo agregar a favoritos', 'error');
            });
    }

    function removeFromWishlist(productId, wishlistId, button) {
        const hasValidWishlistId = !!wishlistId && wishlistId !== 'None' && wishlistId !== '';

        fetch('/api/wishlist/remove/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: hasValidWishlistId
                ? new URLSearchParams({ wishlist_id: wishlistId })
                : new URLSearchParams({ product_id: productId })
        })
            .then(response => response.json())
            .then(data => {
                if (!data.success) {
                    showWishlistToast(data.message || 'No se pudo quitar de favoritos', 'error');
                    return;
                }

                syncWishlistButtons(productId, false, '');

                const isWishlistPage = window.location.pathname.includes('/wishlist');
                if (isWishlistPage) {
                    const productCard = button.closest('.card-product');
                    if (productCard) {
                        productCard.style.transition = 'opacity 0.3s ease';
                        productCard.style.opacity = '0';
                        setTimeout(() => {
                            productCard.remove();
                            if (document.querySelectorAll('.card-product').length === 0) {
                                window.location.reload();
                            }
                        }, 300);
                    }
                }

                updateWishlistCount(-1);
                showWishlistToast(data.message || 'Producto removido de favoritos', 'remove');
            })
            .catch(error => {
                console.error('Error al remover de favoritos:', error);
                showWishlistToast('No se pudo quitar de favoritos', 'error');
            });
    }

    function updateWishlistCount(delta) {
        const counters = document.querySelectorAll('.counter-wishlist, .count-wishlist, .nav-wishlist .count-box');

        counters.forEach(counter => {
            const current = parseInt(counter.textContent || '0', 10) || 0;
            const next = Math.max(current + delta, 0);

            counter.textContent = String(next);
            counter.style.display = next > 0 ? 'inline-flex' : 'none';
        });
    }

    function syncWishlistButtons(productId, inWishlist, wishlistId) {
        if (!productId) return;

        const buttons = document.querySelectorAll(`${wishlistSelector}[data-product-id="${productId}"]`);
        buttons.forEach(btn => {
            btn.classList.toggle('active', !!inWishlist);
            btn.setAttribute('data-wishlist-id', inWishlist ? (wishlistId || '') : '');

            const tooltip = btn.querySelector('.tooltip');
            if (tooltip) {
                tooltip.textContent = inWishlist ? 'Eliminar de Favoritos' : 'Agregar a Favoritos';
            }
        });
    }

    function showWishlistToast(message, tone) {
        if (!message) return;

        let container = document.getElementById('wishlist-toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'wishlist-toast-container';
            container.className = 'wishlist-toast-container';
            document.body.appendChild(container);
        }

        const toast = document.createElement('div');
        toast.className = `wishlist-toast ${tone || 'info'}`;
        toast.textContent = message;
        container.appendChild(toast);

        requestAnimationFrame(() => {
            toast.classList.add('show');
        });

        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 220);
        }, 2200);
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
});
