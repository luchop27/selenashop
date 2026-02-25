/**
 * QuickView Manager - Sistema completo de vista rápida de productos
 * Basado en el código original con mejoras de modularidad
 */

(function() {
    'use strict';
    
    // ==================== CONFIGURACIÓN ====================
    const CONFIG = {
        apiEndpoint: '/productos/api/{id}/quick-view/',
        cartAddEndpoint: '/cart/add/',
        selectors: {
            modal: '#quick_view',
            quickViewBtn: '.btn-open-quickview',
            title: '#quickview-title',
            price: '#quickview-price',
            totalPrice: '#quickview-total-price',
            description: '#quickview-description',
            stock: '#quickview-stock',
            imagesContainer: '#quickview-images',
            variantsContainer: '#quickview-variants',
            quantityInput: 'input[name="number"]',
            minusBtn: '.minus-btn',
            plusBtn: '.plus-btn',
            addToCartBtn: '.btn-add-to-cart-quickview',
            detailsLink: '#quickview-link'
        }
    };
    
    // ==================== ESTADO GLOBAL ====================
    let isProcessing = false;
    let currentModal = null;
    
    // ==================== UTILIDADES ====================
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
    
    // ==================== INICIALIZACIÓN ====================
    function init() {
        console.log('✅ QuickView: Inicializando sistema');
        currentModal = document.querySelector(CONFIG.selectors.modal);
        
        if (!currentModal) {
            console.warn('⚠️ QuickView: Modal no encontrado');
            return;
        }
        
        setupEventListeners();
        setupModalControls();
    }
    
    // ==================== EVENT LISTENERS ====================
    function setupEventListeners() {
        // Event delegation para botones de Quick View
        document.addEventListener('click', function(e) {
            const btn = e.target.closest(CONFIG.selectors.quickViewBtn);
            if (btn) {
                e.preventDefault();
                handleQuickViewClick(btn);
            }
        });
        
        // Event listener cuando se abre el modal
        currentModal.addEventListener('shown.bs.modal', function() {
            resetQuantity();
        });
        
        // Event listener cuando se cierra el modal
        currentModal.addEventListener('hidden.bs.modal', function() {
            resetModal();
        });
    }
    
    function setupModalControls() {
        const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
        const minusBtn = currentModal.querySelector(CONFIG.selectors.minusBtn);
        const plusBtn = currentModal.querySelector(CONFIG.selectors.plusBtn);
        const addToCartBtn = currentModal.querySelector(CONFIG.selectors.addToCartBtn);
        
        if (!quantityInput || !minusBtn || !plusBtn) {
            console.warn('⚠️ QuickView: Controles de cantidad no encontrados');
            return;
        }
        
        // Botón incrementar
        plusBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            incrementQuantity();
        }, { capture: true });
        
        // Botón decrementar
        minusBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            decrementQuantity();
        }, { capture: true });
        
        // Botón agregar al carrito
        if (addToCartBtn) {
            addToCartBtn.addEventListener('click', function(e) {
                e.preventDefault();
                addToCart();
            });
        }
        
        // Manejar cambios en atributos
        currentModal.addEventListener('change', function(e) {
            if (e.target.type === 'radio' && e.target.name.startsWith('atributo_')) {
                updateVariantByAttributes();
            }
        });
    }
    
    // ==================== MANEJO DE CLICKS ====================
    function handleQuickViewClick(btn) {
        const productoId = btn.getAttribute('data-producto-id') || btn.getAttribute('data-product-id');
        
        if (!productoId) {
            console.error('❌ QuickView: No se pudo obtener el ID del producto');
            alert('Error: No se pudo identificar el producto');
            return;
        }
        
        console.log('🔍 QuickView: Cargando producto ID =', productoId);
        loadProduct(productoId);
    }
    
    // ==================== CARGA DE PRODUCTO ====================
    function loadProduct(productId) {
        showLoading();
        
        const apiUrl = CONFIG.apiEndpoint.replace('{id}', productId);
        
        fetch(apiUrl)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                console.log('✅ QuickView: Datos recibidos:', data);
                populateModal(data);
            })
            .catch(error => {
                console.error('❌ QuickView: Error al cargar producto:', error);
                showError();
            });
    }
    
    // ==================== INTERFAZ DEL MODAL ====================
    function showLoading() {
        document.querySelector(CONFIG.selectors.title).textContent = 'Cargando...';
        document.querySelector(CONFIG.selectors.price).textContent = '$0.00';
        document.querySelector(CONFIG.selectors.description).textContent = 'Cargando descripción...';
        document.querySelector(CONFIG.selectors.stock).textContent = '0';
        document.querySelector(CONFIG.selectors.variantsContainer).innerHTML = '';
    }
    
    function showError() {
        document.querySelector(CONFIG.selectors.title).textContent = 'Error al cargar el producto';
        document.querySelector(CONFIG.selectors.description).textContent = 'Por favor, intenta de nuevo más tarde.';
    }
    
    function populateModal(data) {
        // Guardar datos en el modal
        currentModal.dataset.productoId = data.id;
        currentModal.dataset.basePrice = data.precio;
        currentModal.dataset.maxStock = data.stock || 0;
        currentModal.dataset.variantes = JSON.stringify(data.variantes || []);
        currentModal.dataset.atributos = JSON.stringify(data.atributos || []);
        currentModal.dataset.varianteDefaultId = data.variante_default_id || '';
        
        console.log('📦 QuickView: Datos guardados en modal:', {
            productoId: data.id,
            precio: data.precio,
            stock: data.stock,
            tieneVariantes: (data.variantes || []).length > 0,
            tieneAtributos: (data.atributos || []).length > 0
        });
        
        // Actualizar elementos del DOM
        document.querySelector(CONFIG.selectors.title).textContent = data.nombre;
        document.querySelector(CONFIG.selectors.price).textContent = `$${data.precio}`;
        document.querySelector(CONFIG.selectors.totalPrice).textContent = `$${data.precio}`;
        document.querySelector(CONFIG.selectors.stock).textContent = data.stock || '0';
        document.querySelector(CONFIG.selectors.description).textContent = 
            data.descripcion_corta || data.descripcion_larga || 'Sin descripción disponible';
        
        // Actualizar imágenes
        updateImages(data.imagenes || []);
        
        // Actualizar link de detalles
        document.querySelector(CONFIG.selectors.detailsLink).href = `/product/${data.id}/`;
        
        // Manejar variantes
        if (data.variante_default_id) {
            // Producto sin atributos - usar variante default
            handleDefaultVariant(data);
        } else if (data.atributos && data.atributos.length > 0) {
            // Producto con atributos - renderizar selectores
            renderAttributes(data.atributos);
            updateVariantByAttributes();
        }
        
        // Reiniciar cantidad
        resetQuantity();
    }
    
    function updateImages(imagenes) {
        const container = document.querySelector(CONFIG.selectors.imagesContainer);
        container.innerHTML = '';
        
        if (!imagenes || imagenes.length === 0) {
            container.innerHTML = `
                <div class="swiper-slide">
                    <div class="item">
                        <img src="/static/images/products/placeholder.jpg" alt="Product">
                    </div>
                </div>
            `;
            return;
        }
        
        imagenes.forEach(imagen => {
            const slide = document.createElement('div');
            slide.className = 'swiper-slide';
            slide.innerHTML = `
                <div class="item">
                    <img src="${imagen.src}" alt="Product image">
                </div>
            `;
            container.appendChild(slide);
        });
        
        // Reinicializar Swiper si está disponible
        if (window.Swiper && typeof Swiper !== 'undefined') {
            setTimeout(() => {
                // Obtener el elemento Swiper específico del modal
                const swiperElement = currentModal.querySelector('.tf-single-slide');
                
                // Destruir instancia anterior si existe
                if (swiperElement.swiper) {
                    swiperElement.swiper.destroy(true, true);
                }
                
                // Crear nueva instancia
                new Swiper(swiperElement, {
                    navigation: {
                        nextEl: currentModal.querySelector('.single-slide-prev'),
                        prevEl: currentModal.querySelector('.single-slide-next'),
                    },
                });
            }, 100);
        }
    }
    
    function handleDefaultVariant(data) {
        // Para productos sin atributos (ej: Relojes, Accesorios)
        const variantesStock = data.variantes_stock || {};
        
        if (variantesStock['default']) {
            currentModal.dataset.selectedVariantId = variantesStock['default'].id;
            currentModal.dataset.basePrice = variantesStock['default'].precio;
            currentModal.dataset.maxStock = variantesStock['default'].stock;
            
            document.querySelector(CONFIG.selectors.price).textContent = `$${variantesStock['default'].precio}`;
            document.querySelector(CONFIG.selectors.stock).textContent = variantesStock['default'].stock;
            
            console.log('✅ QuickView: Variante DEFAULT activada:', {
                id: variantesStock['default'].id,
                stock: variantesStock['default'].stock,
                precio: variantesStock['default'].precio
            });
        }
        
        updatePrice();
    }
    
    function renderAttributes(atributos) {
        const container = document.querySelector(CONFIG.selectors.variantsContainer);
        container.innerHTML = '';
        
        atributos.forEach(atributo => {
            const atributoDiv = document.createElement('div');
            atributoDiv.className = 'variant-picker-item';
            
            const valoresArray = Object.values(atributo.valores);
            
            if (atributo.tipo === 'color') {
                // Renderizar colores
                atributoDiv.innerHTML = `
                    <div class="variant-picker-label">
                        ${atributo.nombre}: <span class="fw-6 variant-picker-label-value">Selecciona</span>
                    </div>
                    <div class="variant-picker-values">
                        ${valoresArray.map((valor, vIndex) => `
                            <input type="radio" 
                                   name="atributo_${atributo.id}" 
                                   id="qv-attr-${atributo.id}-${valor.id}" 
                                   value="${valor.id}"
                                   data-atributo-slug="${atributo.slug}"
                                   ${vIndex === 0 ? 'checked' : ''}>
                            <label class="hover-tooltip radius-60" 
                                   for="qv-attr-${atributo.id}-${valor.id}"
                                   data-value="${valor.valor}">
                                <span class="btn-checkbox ${valor.codigo_color ? '' : 'bg-color-' + valor.valor.toLowerCase()}" 
                                      ${valor.codigo_color ? `style="background-color: ${valor.codigo_color};"` : ''}></span>
                                <span class="tooltip">${valor.valor}</span>
                            </label>
                        `).join('')}
                    </div>
                `;
            } else {
                // Renderizar tallas u otros atributos
                atributoDiv.innerHTML = `
                    <div class="variant-picker-label">
                        ${atributo.nombre}: <span class="fw-6 variant-picker-label-value">Selecciona</span>
                    </div>
                    <div class="variant-picker-values">
                        ${valoresArray.map((valor, vIndex) => `
                            <input type="radio" 
                                   name="atributo_${atributo.id}" 
                                   id="qv-attr-${atributo.id}-${valor.id}" 
                                   value="${valor.id}"
                                   data-atributo-slug="${atributo.slug}"
                                   ${vIndex === 0 ? 'checked' : ''}>
                            <label class="style-text" 
                                   for="qv-attr-${atributo.id}-${valor.id}"
                                   data-value="${valor.valor}">
                                <p>${valor.valor}</p>
                            </label>
                        `).join('')}
                    </div>
                `;
            }
            
            container.appendChild(atributoDiv);
        });
    }
    
    // ==================== MANEJO DE VARIANTES ====================
    function updateVariantByAttributes() {
        const variantes = JSON.parse(currentModal.dataset.variantes || '[]');
        const atributos = JSON.parse(currentModal.dataset.atributos || '[]');
        
        // Obtener atributos seleccionados
        const selectedAttrs = {};
        atributos.forEach(atributo => {
            const selectedInput = currentModal.querySelector(`input[name="atributo_${atributo.id}"]:checked`);
            if (selectedInput) {
                const valorId = parseInt(selectedInput.value);
                selectedAttrs[atributo.slug] = valorId;
                
                // Actualizar label
                const label = selectedInput.closest('.variant-picker-item').querySelector('.variant-picker-label-value');
                if (label) {
                    label.textContent = selectedInput.nextElementSibling.dataset.value;
                }
            }
        });
        
        // Buscar variante coincidente
        const matchingVariant = variantes.find(variante => {
            return Object.keys(selectedAttrs).every(slug => {
                const varianteAttr = variante.atributos[slug];
                return varianteAttr && varianteAttr.valor_id === selectedAttrs[slug];
            });
        });
        
        if (matchingVariant) {
            currentModal.dataset.selectedVariantId = matchingVariant.id;
            currentModal.dataset.basePrice = matchingVariant.precio;
            currentModal.dataset.maxStock = matchingVariant.stock;
            
            document.querySelector(CONFIG.selectors.price).textContent = `$${matchingVariant.precio}`;
            document.querySelector(CONFIG.selectors.stock).textContent = matchingVariant.stock;
            
            console.log('🔄 QuickView: Variante actualizada:', {
                id: matchingVariant.id,
                stock: matchingVariant.stock,
                precio: matchingVariant.precio
            });
            
            // Ajustar cantidad si excede stock
            const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
            const currentQty = parseInt(quantityInput.value) || 1;
            
            if (currentQty > matchingVariant.stock) {
                quantityInput.value = matchingVariant.stock > 0 ? matchingVariant.stock : 1;
            }
            
            if (matchingVariant.stock === 0) {
                quantityInput.value = 1;
            }
        } else {
            const basePrice = currentModal.dataset.basePrice;
            document.querySelector(CONFIG.selectors.price).textContent = `$${basePrice}`;
            currentModal.dataset.selectedVariantId = '';
            currentModal.dataset.maxStock = 0;
            console.log('❌ QuickView: No se encontró variante coincidente');
        }
        
        updateQuantityButtons();
        updatePrice();
    }
    
    // ==================== CONTROL DE CANTIDAD ====================
    function incrementQuantity() {
        if (isProcessing) return;
        
        isProcessing = true;
        const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
        const current = parseInt(quantityInput.value) || 1;
        const maxStock = parseInt(currentModal.dataset.maxStock) || 0;
        
        console.log('➕ QuickView: Incrementar - Actual:', current, 'Max:', maxStock);
        
        if (current < maxStock && maxStock > 0) {
            quantityInput.value = current + 1;
            updateQuantityButtons();
            updatePrice();
        }
        
        setTimeout(() => { isProcessing = false; }, 100);
    }
    
    function decrementQuantity() {
        if (isProcessing) return;
        
        isProcessing = true;
        const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
        const current = parseInt(quantityInput.value) || 1;
        
        console.log('➖ QuickView: Decrementar - Actual:', current);
        
        if (current > 1) {
            quantityInput.value = current - 1;
            updateQuantityButtons();
            updatePrice();
        }
        
        setTimeout(() => { isProcessing = false; }, 100);
    }
    
    function updateQuantityButtons() {
        const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
        const plusBtn = currentModal.querySelector(CONFIG.selectors.plusBtn);
        const minusBtn = currentModal.querySelector(CONFIG.selectors.minusBtn);
        
        const current = parseInt(quantityInput.value) || 1;
        const maxStock = parseInt(currentModal.dataset.maxStock) || 0;
        
        // Botón +
        if (current >= maxStock || maxStock === 0) {
            plusBtn.style.opacity = '0.5';
            plusBtn.style.pointerEvents = 'none';
        } else {
            plusBtn.style.opacity = '1';
            plusBtn.style.pointerEvents = 'auto';
        }
        
        // Botón -
        if (current <= 1) {
            minusBtn.style.opacity = '0.5';
            minusBtn.style.pointerEvents = 'none';
        } else {
            minusBtn.style.opacity = '1';
            minusBtn.style.pointerEvents = 'auto';
        }
    }
    
    function updatePrice() {
        const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
        const quantity = parseInt(quantityInput.value) || 1;
        const basePrice = parseFloat(currentModal.dataset.basePrice) || 0;
        const total = (basePrice * quantity).toFixed(2);
        
        document.querySelector(CONFIG.selectors.totalPrice).textContent = `$${total}`;
    }
    
    function resetQuantity() {
        const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
        if (quantityInput) {
            quantityInput.value = 1;
            updateQuantityButtons();
            updatePrice();
        }
    }
    
    // ==================== AGREGAR AL CARRITO ====================
    function addToCart() {
        const productoId = currentModal.dataset.productoId;
        const variantId = currentModal.dataset.selectedVariantId || currentModal.dataset.varianteDefaultId;
        const quantityInput = currentModal.querySelector(CONFIG.selectors.quantityInput);
        const quantity = parseInt(quantityInput.value) || 1;
        const maxStock = parseInt(currentModal.dataset.maxStock) || 0;
        
        // Validaciones
        if (!productoId) {
            alert('Error: No se pudo identificar el producto');
            return;
        }
        
        if (!variantId) {
            alert('Por favor, selecciona todas las opciones del producto');
            return;
        }
        
        if (maxStock === 0) {
            alert('Producto sin stock disponible');
            return;
        }
        
        if (quantity > maxStock) {
            alert(`Stock insuficiente. Solo hay ${maxStock} unidades disponibles.`);
            return;
        }
        
        // Preparar datos
        const formData = new FormData();
        formData.append('producto_id', productoId);
        formData.append('variante_id', variantId);
        formData.append('quantity', quantity);
        
        // Enviar petición
        fetch(CONFIG.cartAddEndpoint, {
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
                // Cerrar modal
                const modalInstance = bootstrap.Modal.getInstance(currentModal);
                if (modalInstance) {
                    modalInstance.hide();
                }
                
                // Mostrar mensaje de éxito
                alert('Producto agregado al carrito');
                
                // Recargar página
                location.reload();
            } else {
                alert(data.message || 'Error al agregar al carrito');
            }
        })
        .catch(error => {
            console.error('❌ QuickView: Error al agregar al carrito:', error);
            alert('Error al agregar al carrito. Por favor intenta de nuevo.');
        });
    }
    
    // ==================== RESET ====================
    function resetModal() {
        currentModal.dataset.productoId = '';
        currentModal.dataset.selectedVariantId = '';
        currentModal.dataset.basePrice = '0';
        currentModal.dataset.maxStock = '0';
        resetQuantity();
    }
    
    // ==================== AUTO-INICIALIZACIÓN ====================
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Exportar funciones públicas si es necesario
    window.QuickViewManager = {
        init: init,
        loadProduct: loadProduct
    };
    
})();