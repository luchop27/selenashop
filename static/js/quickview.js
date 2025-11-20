/**
 * QuickView Modal - Control de Stock y Variantes
 * Funcionalidad compartida para el modal de vista rápida
 */

// Función para actualizar el precio total en quickview
function updateQuickViewPrice() {
    const modal = document.getElementById('quick_view');
    if (!modal) return;
    
    const quantity = parseInt(modal.querySelector('input[name="number"]').value);
    const basePrice = parseFloat(modal.dataset.basePrice);
    
    if (!isNaN(basePrice) && !isNaN(quantity)) {
        const totalPrice = (basePrice * quantity).toFixed(2);
        const totalPriceElement = document.getElementById('quickview-total-price');
        if (totalPriceElement) {
            totalPriceElement.textContent = `$${totalPrice}`;
        }
    }
}

    // Variable global para prevenir múltiples ejecuciones
    let isProcessingQuickView = false;
    
    // Función para actualizar el estado de los botones de cantidad en quickview
    function updateQuickViewButtons() {
        const modal = document.getElementById('quick_view');
        if (!modal) return;
        
        const quantityInput = modal.querySelector('input[name="number"]');
        const btnIncrease = modal.querySelector('.plus-btn');
        const btnDecrease = modal.querySelector('.minus-btn');
        
        if (!quantityInput || !btnIncrease || !btnDecrease) return;
        
        const currentQty = parseInt(quantityInput.value) || 1;
        const maxStock = parseInt(modal.dataset.maxStock) || 0;
        
        console.log('QuickView - Actualizando botones:', {currentQty, maxStock});
        
        // Deshabilitar botón de incremento si llegamos al stock máximo o no hay stock
        if (currentQty >= maxStock || maxStock === 0) {
            btnIncrease.classList.add('disabled');
            btnIncrease.style.opacity = '0.5';
            btnIncrease.style.cursor = 'not-allowed';
            btnIncrease.style.pointerEvents = 'none';
        } else {
            btnIncrease.classList.remove('disabled');
            btnIncrease.style.opacity = '1';
            btnIncrease.style.cursor = 'pointer';
            btnIncrease.style.pointerEvents = 'auto';
        }
        
        // Deshabilitar botón de decremento si estamos en 1
        if (currentQty <= 1) {
            btnDecrease.classList.add('disabled');
            btnDecrease.style.opacity = '0.5';
            btnDecrease.style.cursor = 'not-allowed';
            btnDecrease.style.pointerEvents = 'none';
        } else {
            btnDecrease.classList.remove('disabled');
            btnDecrease.style.opacity = '1';
            btnDecrease.style.cursor = 'pointer';
            btnDecrease.style.pointerEvents = 'auto';
        }
    }// Función para actualizar variante según atributos seleccionados
function updateVariantByAttributes() {
    const modal = document.getElementById('quick_view');
    if (!modal) return;
    
    const variantes = JSON.parse(modal.dataset.variantes || '[]');
    const atributos = JSON.parse(modal.dataset.atributos || '[]');
    
    // Obtener atributos seleccionados
    const selectedAttrs = {};
    atributos.forEach(atributo => {
        const selectedInput = modal.querySelector(`input[name="atributo_${atributo.id}"]:checked`);
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
    
    // Buscar variante que coincida
    const matchingVariant = variantes.find(variante => {
        return Object.keys(selectedAttrs).every(slug => {
            const varianteAttr = variante.atributos[slug];
            return varianteAttr && varianteAttr.valor_id === selectedAttrs[slug];
        });
    });
    
    if (matchingVariant) {
        modal.dataset.selectedVariantId = matchingVariant.id;
        modal.dataset.basePrice = matchingVariant.precio;
        modal.dataset.maxStock = matchingVariant.stock;
        document.getElementById('quickview-price').textContent = `$${matchingVariant.precio}`;
        document.getElementById('quickview-stock').textContent = matchingVariant.stock;
        
        console.log('🔄 QuickView - Variante actualizada:', {
            id: matchingVariant.id,
            stock: matchingVariant.stock,
            precio: matchingVariant.precio,
            modalMaxStock: modal.dataset.maxStock
        });
        
        // Ajustar cantidad si excede el nuevo stock
        const quantityInput = modal.querySelector('input[name="number"]');
        const currentQty = parseInt(quantityInput.value) || 1;
        if (currentQty > matchingVariant.stock) {
            quantityInput.value = matchingVariant.stock > 0 ? matchingVariant.stock : 1;
            console.log('⚠️ QuickView - Cantidad ajustada de', currentQty, 'a', quantityInput.value);
        }
        if (matchingVariant.stock === 0) {
            quantityInput.value = 1;
        }
    } else {
        const basePrice = modal.dataset.basePrice;
        document.getElementById('quickview-price').textContent = `$${basePrice}`;
        modal.dataset.selectedVariantId = '';
        modal.dataset.maxStock = 0;
        console.log('❌ QuickView - No se encontró variante coincidente');
    }
    
    updateQuickViewButtons();
    updateQuickViewPrice();
}

// Inicializar event listeners para el modal quickview
function initQuickViewModal() {
    const modal = document.getElementById('quick_view');
    if (!modal) {
        console.warn('Modal quickview no encontrado');
        return;
    }
    
    const minusBtn = modal.querySelector('.minus-btn');
    const plusBtn = modal.querySelector('.plus-btn');
    const quantityInput = modal.querySelector('input[name="number"]');
    
    if (minusBtn && plusBtn && quantityInput) {
        // Event listener para botón de incremento con protección contra múltiples ejecuciones
        plusBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            // Prevenir procesamiento múltiple
            if (isProcessingQuickView) {
                console.log('QuickView - Ya procesando, ignorando click adicional');
                return false;
            }
            
            // Verificar si el botón está deshabilitado
            if (this.classList.contains('disabled') || this.style.pointerEvents === 'none') {
                console.log('QuickView - Botón + está deshabilitado');
                return false;
            }
            
            isProcessingQuickView = true;
            
            const currentQty = parseInt(quantityInput.value) || 1;
            const maxStock = parseInt(modal.dataset.maxStock) || 0;
            
            console.log('=== QuickView INCREMENTO ===');
            console.log('Cantidad actual:', currentQty);
            console.log('Stock máximo:', maxStock);
            
            // Validación estricta: solo incrementar si hay stock disponible
            if (currentQty < maxStock && maxStock > 0) {
                const newQty = currentQty + 1;
                console.log('Intentando incrementar a:', newQty);
                
                // Triple verificación antes de asignar
                if (newQty <= maxStock) {
                    quantityInput.value = newQty;
                    console.log('✅ Cantidad actualizada a:', newQty);
                    updateQuickViewButtons();
                    updateQuickViewPrice();
                } else {
                    console.log('❌ Bloqueado: excedería stock máximo');
                }
            } else {
                console.log('❌ Bloqueado: ya en stock máximo');
            }
            
            // Liberar el flag después de un pequeño delay
            setTimeout(() => {
                isProcessingQuickView = false;
            }, 100);
            
            return false;
        }, { capture: true });
        
        // Event listener para botón de decremento
        minusBtn.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            e.stopImmediatePropagation();
            
            // Prevenir procesamiento múltiple
            if (isProcessingQuickView) {
                return false;
            }
            
            // Verificar si el botón está deshabilitado
            if (this.classList.contains('disabled') || this.style.pointerEvents === 'none') {
                console.log('QuickView - Botón - está deshabilitado');
                return false;
            }
            
            isProcessingQuickView = true;
            
            const currentQty = parseInt(quantityInput.value) || 1;
            console.log('=== QuickView DECREMENTO ===');
            console.log('Cantidad actual:', currentQty);
            
            if (currentQty > 1) {
                quantityInput.value = currentQty - 1;
                console.log('✅ Cantidad decrementada a:', currentQty - 1);
                updateQuickViewButtons();
                updateQuickViewPrice();
            }
            
            setTimeout(() => {
                isProcessingQuickView = false;
            }, 100);
            
            return false;
        }, { capture: true });
        
        // Event listener para validar cuando el usuario termina de editar manualmente
        quantityInput.addEventListener('blur', function() {
            let value = parseInt(this.value) || 1;
            const maxStock = parseInt(modal.dataset.maxStock) || 0;
            
            console.log('QuickView - Validación manual (blur):', value, 'max:', maxStock);
            
            // Limitar al stock máximo
            if (value > maxStock) {
                value = maxStock > 0 ? maxStock : 1;
                console.log('QuickView - Ajustado a stock máximo:', value);
            }
            
            // Mínimo 1
            if (value < 1) {
                value = 1;
                console.log('QuickView - Ajustado a mínimo 1');
            }
            
            this.value = value;
            updateQuickViewButtons();
            updateQuickViewPrice();
        });
        
        // Prevenir que el input acepte valores no numéricos
        quantityInput.addEventListener('keypress', function(e) {
            if (e.key && !/[0-9]/.test(e.key)) {
                e.preventDefault();
            }
        });
        
        console.log('QuickView - Event listeners de cantidad inicializados');
    }
    
    // Manejar cambio de atributos
    modal.addEventListener('change', function(e) {
        if (e.target.type === 'radio' && e.target.name.startsWith('atributo_')) {
            console.log('QuickView - Cambio de atributo detectado');
            updateVariantByAttributes();
        }
    });
    
    console.log('QuickView Modal inicializado correctamente');
}

// Inicializar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initQuickViewModal);
} else {
    initQuickViewModal();
}
