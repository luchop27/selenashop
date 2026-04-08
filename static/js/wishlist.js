/**
 * Script para manejar la funcionalidad del wishlist
 * Permite agregar/remover productos del wishlist del usuario
 */

if (window.__wishlistScriptInitialized) {
    console.warn('Wishlist ya inicializado, se evita doble binding de eventos.');
} else {
    window.__wishlistScriptInitialized = true;

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

        if (button.dataset.wishlistBusy === '1') {
            return;
        }

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
        setWishlistBusy(button, true);

        fetch('/api/favoritos/agregar/', {
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
            })
            .finally(() => {
                setWishlistBusy(button, false);
            });
    }

    function removeFromWishlist(productId, wishlistId, button) {
        const hasValidWishlistId = !!wishlistId && wishlistId !== 'None' && wishlistId !== '';
        setWishlistBusy(button, true);

        fetch('/api/favoritos/eliminar/', {
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

                const isWishlistPage = window.location.pathname.includes('/wishlist') || window.location.pathname.includes('/favoritos');
                if (isWishlistPage) {
                    const productCard = button.closest('.card-product');
                    if (productCard) {
                        productCard.style.transition = 'opacity 0.25s ease, transform 0.25s ease';
                        productCard.style.opacity = '0';
                        productCard.style.transform = 'scale(0.98)';
                        setTimeout(() => {
                            productCard.remove();
                        }, 250);
                    }
                    updateWishlistResultsCounter(-1);
                }

                updateWishlistCount(-1);
                showWishlistToast(data.message || 'Producto removido de favoritos', 'remove');
            })
            .catch(error => {
                console.error('Error al remover de favoritos:', error);
                showWishlistToast('No se pudo quitar de favoritos', 'error');
            })
            .finally(() => {
                setWishlistBusy(button, false);
            });
    }

    function setWishlistBusy(button, busy) {
        if (!button) return;
        button.dataset.wishlistBusy = busy ? '1' : '0';
        button.style.pointerEvents = busy ? 'none' : 'auto';
    }

    function updateWishlistResultsCounter(delta) {
        const counterEl = document.getElementById('wishlist-results-count');
        if (!counterEl) return;

        const currentFromData = parseInt(counterEl.dataset.count || '', 10);
        const currentFromTextMatch = (counterEl.textContent || '').match(/\d+/);
        const currentFromText = currentFromTextMatch ? parseInt(currentFromTextMatch[0], 10) : 0;
        const current = Number.isNaN(currentFromData) ? currentFromText : currentFromData;

        const next = Math.max((current || 0) + delta, 0);
        counterEl.dataset.count = String(next);
        counterEl.textContent = `Mostrando ${next} resultado${next === 1 ? '' : 's'}`;

        const pageSummary = document.querySelector('.tf-page-title .text-2');
        if (pageSummary) {
            pageSummary.textContent = next > 0
                ? `Tienes ${next} producto${next === 1 ? '' : 's'} en tu lista de favoritos`
                : 'Tu lista de favoritos está vacía';
        }

        if (next !== 0) return;

        const grid = document.querySelector('.wrapper-shop');
        if (grid) {
            grid.remove();
        }

        if (document.getElementById('wishlist-empty-dynamic')) {
            return;
        }

        const sectionContainer = document.querySelector('section.flat-spacing-2 .container');
        if (!sectionContainer) return;

        const continueShoppingLink = document.querySelector('.tf-control-filter a');
        const shopUrl = continueShoppingLink ? continueShoppingLink.getAttribute('href') : '/collections/';

        const emptyState = document.createElement('div');
        emptyState.id = 'wishlist-empty-dynamic';
        emptyState.className = 'text-center py-5';
        emptyState.innerHTML = `
            <h4 class="fw-5 mb-3">Tu lista de favoritos está vacía</h4>
            <p class="text-secondary mb-4">Agrega productos a tu lista de favoritos haciendo clic en el icono del corazón</p>
            <a href="${shopUrl}" class="tf-btn btn-fill">
                <span>Explorar productos</span>
                <i class="icon icon-arrow-right"></i>
            </a>
        `;

        sectionContainer.appendChild(emptyState);
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

        // Fijar siempre notificaciones en esquina inferior derecha.
        container.style.position = 'fixed';
        container.style.top = 'auto';
        container.style.left = 'auto';
        container.style.right = '20px';
        container.style.bottom = '20px';
        container.style.zIndex = '1200';

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

}
