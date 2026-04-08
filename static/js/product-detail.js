(function () {
    'use strict';

    let variantesStock = {};
    let selectedVariant = null;
    let maxStock = 999;

    document.addEventListener('DOMContentLoaded', function () {
        setTimeout(function () {
            initializeVariantsStock();
            setupVariantSelectors();
            setupQuantityControls();
            updateStockInfo();
        }, 100);
    });

    function initializeVariantsStock() {
        const variantElements = document.querySelectorAll('.variant-data');
        variantElements.forEach(function (element) {
            const variantId = element.dataset.variantId;
            const stock = parseInt(element.dataset.variantStock) || 0;
            const talla = element.dataset.variantSize || '';
            const color = element.dataset.variantColor || '';

            const key = `${color}_${talla}`.toLowerCase();
            variantesStock[key] = {
                id: variantId,
                stock: stock,
                talla: talla,
                color: color
            };
        });
    }

    function setupVariantSelectors() {
        const colorInputs = document.querySelectorAll('input[name="color1"]');
        colorInputs.forEach(function (input) {
            input.addEventListener('change', function () {
                updateSelectedVariant();
                updateStockInfo();
            });
        });

        const sizeInputs = document.querySelectorAll('input[name="size1"]');
        sizeInputs.forEach(function (input) {
            input.addEventListener('change', function () {
                updateSelectedVariant();
                updateStockInfo();
            });
        });

        const stickySelect = document.getElementById('stickyVariantSelect');
        if (stickySelect) {
            stickySelect.addEventListener('change', function () {
                const variantId = this.value;
                const key = Object.keys(variantesStock).find(k => variantesStock[k].id == variantId);

                if (key) {
                    const variantData = variantesStock[key];
                    const sizeInputs = document.querySelectorAll('input[name="size1"]');
                    sizeInputs.forEach(input => {
                        if (input.value === variantData.talla) {
                            input.checked = true;
                        }
                    });
                    const colorInputs = document.querySelectorAll('input[name="color1"]');
                    colorInputs.forEach(input => {
                        if (input.value === variantData.color) {
                            input.checked = true;
                        }
                    });
                    updateSelectedVariant();
                    updateStockInfo();
                }
            });
        }
    }

    function updateSelectedVariant() {
        const selectedColor = document.querySelector('input[name="color1"]:checked');
        const selectedSize = document.querySelector('input[name="size1"]:checked');

        let color = '';
        let talla = '';

        if (selectedColor) {
            const colorLabel = document.querySelector(`label[for="${selectedColor.id}"]`);
            color = colorLabel ? colorLabel.dataset.value || '' : '';
        }

        if (selectedSize) {
            const sizeLabel = document.querySelector(`label[for="${selectedSize.id}"]`);
            talla = sizeLabel ? sizeLabel.dataset.value || '' : '';
        }

        const key = `${color}_${talla}`.toLowerCase();
        selectedVariant = variantesStock[key] || null;

        if (selectedVariant) {
            maxStock = selectedVariant.stock;

            const stickySelect = document.getElementById('stickyVariantSelect');
            if (stickySelect) {
                stickySelect.value = selectedVariant.id;
            }
        } else {
            maxStock = 999;
        }

        // Esta sincronización afecta SOLO si variant-data los modificó
        // Sincronizacion movida al HTML
    }

    function setupQuantityControls() { /* Logic moved to HTML inline script for proper data sync */ })();
