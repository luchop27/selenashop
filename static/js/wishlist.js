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

                    button.classList.add('active');
                    if (data.wishlist_id) {
                        button.setAttribute('data-wishlist-id', data.wishlist_id);
                    }

                    const tooltip = button.querySelector('.tooltip');
                    if (tooltip) {
                        tooltip.textContent = 'Eliminar de Favoritos';
                    }

                    if (!alreadyInWishlist) {
                        updateWishlistCount(1);
                    }
                }
            })
            .catch(error => {
                console.error('Error al agregar a favoritos:', error);
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
                if (!data.success) return;

                button.classList.remove('active');
                button.setAttribute('data-wishlist-id', '');

                const tooltip = button.querySelector('.tooltip');
                if (tooltip) {
                    tooltip.textContent = 'Agregar a Favoritos';
                }

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
            })
            .catch(error => {
                console.error('Error al remover de favoritos:', error);
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
