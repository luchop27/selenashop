// static/js/cart.js
// Funcionalidad del carrito de compras

(function() {
    'use strict';

    // Función para obtener el token CSRF
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

    const csrftoken = getCookie('csrftoken');

    // Actualizar el contador del carrito en el header
    function updateCartCount(count) {
        const cartCounts = document.querySelectorAll('.tf-cart-count, .toolbar-count');
        cartCounts.forEach(function(element) {
            element.textContent = count;
        });
    }

    // Actualizar el total del carrito
    function updateCartTotal(total) {
        const cartTotals = document.querySelectorAll('.tf-totals-total-value');
        cartTotals.forEach(function(element) {
            element.textContent = '$' + parseFloat(total).toFixed(2) + ' USD';
        });
    }

    // Cargar y mostrar los items del carrito
    function loadCartItems() {
        fetch('/cart/detail/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cart_count);
                updateCartTotal(data.cart_total);
                renderCartItems(data.items);
                loadCartRecommendations(); // Cargar recomendaciones
            }
        })
        .catch(error => {
            console.error('Error loading cart:', error);
        });
    }

    // Cargar productos recomendados
    function loadCartRecommendations() {
        fetch('/cart/recommendations/', {
            method: 'GET',
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            },
        })
        .then(response => response.json())
        .then(data => {
            if (data.success && data.recommendations) {
                renderCartRecommendations(data.recommendations);
            }
        })
        .catch(error => {
            console.error('Error loading recommendations:', error);
        });
    }

    // Renderizar productos recomendados
    function renderCartRecommendations(recommendations) {
        const wrapper = document.getElementById('cart-recommendations-wrapper');
        if (!wrapper) return;

        if (recommendations.length === 0) {
            wrapper.innerHTML = '';
            return;
        }

        let html = '';
        recommendations.forEach(function(product) {
            const imageUrl = product.imagen || '/static/images/item/default-product.jpg';
            
            html += `
                <div class="swiper-slide">
                    <div class="tf-minicart-recommendations-item">
                        <div class="tf-minicart-recommendations-item-image">
                            <a href="${product.url}">
                                <img src="${imageUrl}" alt="${product.nombre}">
                            </a>
                        </div>
                        <div class="tf-minicart-recommendations-item-infos flex-grow-1">
                            <a class="title" href="${product.url}">${product.nombre}</a>
                            <div class="price">$${parseFloat(product.precio).toFixed(2)}</div>
                        </div>
                        <div class="tf-minicart-recommendations-item-quickview">
                            <a href="${product.url}" class="hover-tooltip">
                                <span class="icon icon-view"></span>
                                <span class="tooltip">View Details</span>
                            </a>
                        </div>
                    </div>
                </div>
            `;
        });

        wrapper.innerHTML = html;

        // Reinicializar Swiper si existe
        if (typeof Swiper !== 'undefined') {
            // Destruir Swiper existente si lo hay
            const existingSwiper = document.querySelector('.tf-cart-slide')?.swiper;
            if (existingSwiper) {
                existingSwiper.destroy(true, true);
            }

            // Crear nuevo Swiper
            setTimeout(function() {
                new Swiper('.tf-cart-slide', {
                    slidesPerView: 1,
                    spaceBetween: 15,
                    pagination: {
                        el: '.cart-slide-pagination',
                        clickable: true,
                    },
                });
            }, 100);
        }
    }

    // Renderizar los items del carrito en el modal
    function renderCartItems(items) {
        const cartItemsContainer = document.querySelector('.tf-mini-cart-items');
        if (!cartItemsContainer) return;

        if (items.length === 0) {
            cartItemsContainer.innerHTML = `
                <div class="text-center py-4">
                    <p class="text-muted">Tu carrito está vacío</p>
                </div>
            `;
            return;
        }

        let html = '';
        items.forEach(function(item) {
            const imageUrl = item.imagen || '/static/images/item/default-product.jpg';
            const variant = item.color || item.talla ? `${item.color || ''} ${item.talla || ''}`.trim() : '';
            
            html += `
                <div class="tf-mini-cart-item" data-product-id="${item.product_id}">
                    <div class="tf-mini-cart-image">
                        <a href="/product/${item.producto_id}/">
                            <img src="${imageUrl}" alt="${item.nombre}">
                        </a>
                    </div>
                    <div class="tf-mini-cart-info">
                        <a class="title link" href="/product/${item.producto_id}/">${item.nombre}</a>
                        ${variant ? `<div class="meta-variant">${variant}</div>` : ''}
                        <div class="price fw-6">$${parseFloat(item.precio).toFixed(2)}</div>
                        <div class="tf-mini-cart-btns">
                            <div class="wg-quantity small">
                                <span class="btn-quantity minus-btn" data-action="decrease">-</span>
                                <input type="text" name="number" value="${item.quantity}" readonly>
                                <span class="btn-quantity plus-btn" data-action="increase">+</span>
                            </div>
                            <div class="tf-mini-cart-remove" data-action="remove">Remove</div>
                        </div>
                    </div>
                </div>
            `;
        });

        cartItemsContainer.innerHTML = html;
        attachCartItemListeners();
    }

    // Adjuntar event listeners a los botones del carrito
    function attachCartItemListeners() {
        // Botones de incrementar/decrementar cantidad
        document.querySelectorAll('.tf-mini-cart-item .btn-quantity').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const item = this.closest('.tf-mini-cart-item');
                const productId = item.dataset.productId;
                const input = item.querySelector('input[name="number"]');
                let quantity = parseInt(input.value);
                const action = this.dataset.action;

                if (action === 'increase') {
                    quantity += 1;
                } else if (action === 'decrease' && quantity > 1) {
                    quantity -= 1;
                }

                updateCartQuantity(productId, quantity);
            });
        });

        // Botones de eliminar
        document.querySelectorAll('.tf-mini-cart-remove').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                const item = this.closest('.tf-mini-cart-item');
                const productId = item.dataset.productId;
                removeFromCart(productId);
            });
        });
    }

    // Agregar producto al carrito
    window.addToCart = function(productoId, varianteId, quantity) {
        quantity = quantity || 1;

        const formData = new FormData();
        formData.append('producto_id', productoId);
        if (varianteId) {
            formData.append('variante_id', varianteId);
        }
        formData.append('quantity', quantity);

        fetch('/cart/add/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cart_count);
                updateCartTotal(data.cart_total);
                loadCartItems(); // Esto también carga las recomendaciones
                
                // Mostrar el modal del carrito
                const cartModal = document.getElementById('shoppingCart');
                if (cartModal) {
                    const bsModal = new bootstrap.Modal(cartModal);
                    bsModal.show();
                }
                
                // Mostrar notificación de éxito
                showNotification('Producto agregado al carrito', 'success');
            } else {
                showNotification(data.message || 'Error al agregar el producto', 'error');
            }
        })
        .catch(error => {
            console.error('Error adding to cart:', error);
            showNotification('Error al agregar el producto al carrito', 'error');
        });
    };

    // Actualizar cantidad en el carrito
    function updateCartQuantity(productId, quantity) {
        const formData = new FormData();
        formData.append('product_id', productId);
        formData.append('quantity', quantity);

        fetch('/cart/update/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cart_count);
                updateCartTotal(data.cart_total);
                loadCartItems();
            }
        })
        .catch(error => {
            console.error('Error updating cart:', error);
        });
    }

    // Eliminar producto del carrito
    function removeFromCart(productId) {
        const formData = new FormData();
        formData.append('product_id', productId);

        fetch('/cart/remove/', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData,
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                updateCartCount(data.cart_count);
                updateCartTotal(data.cart_total);
                loadCartItems(); // Esto también actualiza las recomendaciones
                showNotification('Producto eliminado del carrito', 'success');
            }
        })
        .catch(error => {
            console.error('Error removing from cart:', error);
        });
    }

    // Mostrar notificación
    function showNotification(message, type) {
        // Puedes personalizar esto con tu propio sistema de notificaciones
        console.log(`[${type}] ${message}`);
        // Aquí podrías usar una librería de toast/notifications
    }

    // Event listener para el botón "Add to cart" en product detail
    document.addEventListener('DOMContentLoaded', function() {
        // Cargar el carrito al inicio
        loadCartItems();

        // Manejar click en botones "Add to cart"
        document.querySelectorAll('.btn-add-to-cart').forEach(function(btn) {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                
                // Obtener el producto ID desde el DOM
                const productoId = document.querySelector('[data-producto-id]')?.dataset.productoId;
                if (!productoId) {
                    showNotification('Error: No se pudo encontrar el ID del producto', 'error');
                    return;
                }

                // Obtener la variante seleccionada (si existe)
                let varianteId = null;
                const varianteSelect = document.querySelector('input[name="variant"]:checked, select[name="variant"]');
                if (varianteSelect) {
                    varianteId = varianteSelect.value || varianteSelect.dataset.varianteId;
                }

                // Obtener la cantidad
                const quantityInput = document.querySelector('.quantity-product, input[name="number"]');
                const quantity = quantityInput ? parseInt(quantityInput.value) : 1;

                // Agregar al carrito
                addToCart(productoId, varianteId, quantity);
            });
        });

        // Cargar items cuando se abre el modal del carrito
        const cartModal = document.getElementById('shoppingCart');
        if (cartModal) {
            cartModal.addEventListener('show.bs.modal', function() {
                loadCartItems();
            });
        }
    });

})();
