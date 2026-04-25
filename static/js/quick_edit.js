/**
 * quick_edit.js  — v2.0
 * ----------------------
 * Edición Rápida de productos para administradores (is_staff).
 *
 * Funcionalidades:
 *  - Carga dinámica de datos del producto (GET AJAX).
 *  - Imágenes: previsualización, reemplazo y eliminación con botón rojo destacado.
 *  - Tallas: tabla editable de stock, eliminar filas reactivamente,
 *    agregar tallas nuevas desde el catálogo de Talla del sistema.
 *  - Precio ÚNICO global (sin precio por talla).
 *  - Validación: stock no negativo.
 *  - Al guardar: POST AJAX → actualiza la tarjeta del producto en el DOM
 *    y muestra un Toast de éxito.
 */

(function () {
    'use strict';

    // ─── Estado del modal ──────────────────────────────────────────────────
    let productoIdActual  = null;   // ID del producto en edición
    let cardActual        = null;   // Referencia al .card-product del DOM
    let imagenesAEliminar = [];     // IDs de Imagen a borrar al guardar
    let variantesAEliminar = [];    // IDs de Variante a borrar al guardar
    let variantesNuevas   = [];     // [{tallaId, tallaCodigo, stock}]
    let tallasDisponibles = [];     // Tallas del sistema retornadas por la API
    let tallasCargadas    = [];     // Tallas actualmente en uso por el producto (para filtrado)

    // ─── Selectores del DOM ────────────────────────────────────────────────
    const modal          = document.getElementById('quick_edit_modal');
    const form           = document.getElementById('quickEditForm');
    const loadingDiv     = document.getElementById('quick-edit-loading');
    const alertDiv       = document.getElementById('quick-edit-alert');
    const saveBtn        = document.getElementById('quick-edit-save-btn');
    const saveBtnText    = document.getElementById('quick-edit-btn-text');
    const saveBtnSpinner = document.getElementById('quick-edit-btn-spinner');

    // Elementos del panel "Agregar Talla"
    const btnMostrarAgregar    = document.getElementById('qe-btn-mostrar-agregar-talla');
    const panelAgregarTalla    = document.getElementById('qe-agregar-talla-panel');
    const selectNuevaTalla     = document.getElementById('qe-nueva-talla-select');
    const inputNuevaTallaStock = document.getElementById('qe-nueva-talla-stock');
    const btnConfirmarAgregar  = document.getElementById('qe-btn-confirmar-agregar-talla');
    const btnCancelarAgregar   = document.getElementById('qe-btn-cancelar-agregar-talla');

    // ─── Evento: apertura del modal ────────────────────────────────────────
    if (modal) {
        modal.addEventListener('show.bs.modal', function (event) {
            const trigger = event.relatedTarget;
            if (!trigger) return;

            productoIdActual   = trigger.dataset.productId;
            cardActual         = trigger.closest('.card-product');
            imagenesAEliminar  = [];
            variantesAEliminar = [];
            variantesNuevas    = [];
            tallasCargadas     = [];

            mostrarCargando(true);
            ocultarAlerta();
            ocultarPanelAgregarTalla();

            cargarDatosProducto(productoIdActual);
        });

        // Limpiar al cerrar
        modal.addEventListener('hidden.bs.modal', function () {
            productoIdActual   = null;
            cardActual         = null;
            imagenesAEliminar  = [];
            variantesAEliminar = [];
            variantesNuevas    = [];
            if (form) form.reset();
            limpiarContenedor('qe-imagenes-container');
            limpiarContenedor('qe-variantes-container');
            ocultarPanelAgregarTalla();
        });
    }

    // ─── Cargar datos del producto ─────────────────────────────────────────
    function cargarDatosProducto(productoId) {
        fetch(`/productos/api/quick-edit/${productoId}/`, {
            method: 'GET',
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(function (r) {
            if (!r.ok) throw new Error(`HTTP ${r.status}`);
            return r.json();
        })
        .then(function (data) {
            tallasDisponibles = data.tallas_disponibles || [];
            rellenarFormulario(data);
            mostrarCargando(false);
        })
        .catch(function (err) {
            console.error('[QuickEdit] Error al cargar:', err);
            mostrarAlerta('danger', '⚠️ No se pudieron cargar los datos. Intenta de nuevo.');
            mostrarCargando(false);
        });
    }

    // ─── Rellenar el formulario ────────────────────────────────────────────
    function rellenarFormulario(data) {
        document.getElementById('quick-edit-product-id').value        = data.id;
        document.getElementById('quick-edit-product-name-header').textContent = data.nombre;
        document.getElementById('qe-nombre').value      = data.nombre             || '';
        document.getElementById('qe-marca').value       = data.marca              || '';
        document.getElementById('qe-precio').value      = data.precio_base        || '';
        document.getElementById('qe-descripcion').value = data.descripcion_corta  || '';

        renderizarImagenes(data.imagenes   || []);
        renderizarVariantes(data.variantes || []);
        poblarSelectorTallas(data.variantes || []);
    }

    // ═══════════════════════════════════════════════════════════════════════
    //  IMÁGENES
    // ═══════════════════════════════════════════════════════════════════════

    function renderizarImagenes(imagenes) {
        const contenedor = document.getElementById('qe-imagenes-container');
        if (!contenedor) return;
        contenedor.innerHTML = '';

        if (imagenes.length === 0) {
            contenedor.innerHTML = '<p class="text-muted small mb-2">Este producto no tiene imágenes cargadas.</p>';
        }

        // Mostrar cada imagen existente
        imagenes.forEach(function (img, idx) {
            const etiqueta = idx === 0 ? 'Principal' : (idx === 1 ? 'Hover' : `Imagen ${idx + 1}`);
            const badgeColor = idx === 0 ? 'bg-primary' : (idx === 1 ? 'bg-secondary' : 'bg-dark');

            const div = document.createElement('div');
            div.className = 'border rounded p-2 mb-2 position-relative';
            div.id = `qe-imagen-bloque-${img.id}`;
            div.style.cssText = 'background:#fafafa; transition: opacity 0.25s;';

            div.innerHTML = `
                <div class="d-flex align-items-start gap-3">
                    <div style="position:relative; flex-shrink:0;">
                        <img src="${esc(img.url)}"
                             alt="${etiqueta}"
                             id="qe-preview-${img.id}"
                             style="width:80px;height:80px;object-fit:cover;border-radius:6px;border:1px solid #ddd;">
                        <button type="button"
                                class="btn-eliminar-imagen position-absolute"
                                data-imagen-id="${img.id}"
                                title="Eliminar imagen"
                                style="top:-8px;right:-8px;width:24px;height:24px;border-radius:50%;
                                       background:#dc3545;color:#fff;border:none;cursor:pointer;
                                       font-size:14px;line-height:1;display:flex;align-items:center;
                                       justify-content:center;box-shadow:0 2px 6px rgba(220,53,69,.5);">
                            ✕
                        </button>
                    </div>
                    <div class="flex-grow-1">
                        <span class="badge ${badgeColor} mb-1">${etiqueta}</span>
                        <div>
                            <label class="form-label small mb-1 text-muted">Reemplazar:</label>
                            <input type="file"
                                   class="form-control form-control-sm"
                                   name="imagen_nueva_${img.id}"
                                   accept="image/*"
                                   data-preview-id="qe-preview-${img.id}">
                        </div>
                    </div>
                </div>
            `;
            contenedor.appendChild(div);
        });

        // Sección para agregar nuevas imágenes
        const divNuevas = document.createElement('div');
        divNuevas.className = 'border-top pt-3 mt-2';
        divNuevas.innerHTML = `
            <label class="form-label fw-semibold small mb-1">➕ Agregar nuevas imágenes:</label>
            <input type="file" class="form-control form-control-sm" name="imagenes_nuevas" multiple accept="image/*">
            <small class="text-muted">Puedes seleccionar múltiples archivos.</small>
        `;
        contenedor.appendChild(divNuevas);

        // ── Listeners de previsualización ──
        contenedor.querySelectorAll('input[type="file"][data-preview-id]').forEach(function (input) {
            input.addEventListener('change', function () {
                const file = this.files[0];
                if (!file) return;
                const preview = document.getElementById(this.dataset.previewId);
                if (preview) preview.src = URL.createObjectURL(file);
            });
        });

        // ── Listeners de eliminación ──
        contenedor.querySelectorAll('.btn-eliminar-imagen').forEach(function (btn) {
            btn.addEventListener('click', function () {
                const imgId = parseInt(this.dataset.imagenId);
                const bloque = document.getElementById(`qe-imagen-bloque-${imgId}`);
                if (!imagenesAEliminar.includes(imgId)) imagenesAEliminar.push(imgId);
                // Efecto visual de eliminación
                if (bloque) {
                    bloque.style.opacity = '0';
                    setTimeout(function () { bloque.remove(); }, 250);
                }
            });
        });
    }

    // ═══════════════════════════════════════════════════════════════════════
    //  VARIANTES / TALLAS
    // ═══════════════════════════════════════════════════════════════════════

    function renderizarVariantes(variantes) {
        const contenedor   = document.getElementById('qe-variantes-container');
        const sinVariantes = document.getElementById('qe-sin-variantes');
        if (!contenedor) return;
        contenedor.innerHTML = '';

        // Guardar tallas cargadas para filtrar el selector "Agregar"
        tallasCargadas = variantes
            .filter(function (v) { return v.talla_codigo; })
            .map(function (v) { return v.talla_codigo; });

        if (variantes.length === 0) {
            if (sinVariantes) sinVariantes.style.display = 'block';
            return;
        }
        if (sinVariantes) sinVariantes.style.display = 'none';

        // Tabla principal
        const tabla = document.createElement('table');
        tabla.className = 'table table-sm table-bordered align-middle mb-0';
        tabla.innerHTML = `
            <thead class="table-light">
                <tr>
                    <th class="small">Talla / SKU</th>
                    <th class="small" style="width:120px;">Stock</th>
                    <th class="small text-center" style="width:60px;">Quitar</th>
                </tr>
            </thead>
            <tbody id="qe-variantes-tbody"></tbody>
        `;
        contenedor.appendChild(tabla);

        const tbody = tabla.querySelector('#qe-variantes-tbody');
        variantes.forEach(function (v) {
            agregarFilaVariante(tbody, v.id, v.talla_codigo, v.color, v.sku, v.stock);
        });
    }

    /**
     * Agrega una fila de variante a la tabla.
     * @param {HTMLElement} tbody  - El <tbody> donde insertar la fila.
     * @param {number|null} varId  - ID de variante existente (null si es nueva).
     * @param {string|null} tallaCodigo
     * @param {string|null} color
     * @param {string|null} sku
     * @param {number} stock
     * @param {number|null} tallaId   - Solo para variantes nuevas.
     */
    function agregarFilaVariante(tbody, varId, tallaCodigo, color, sku, stock, tallaId) {
        const esNueva = varId === null;
        const etiqueta = tallaCodigo
            ? `${tallaCodigo}${color ? ' / ' + color : ''}`
            : (sku || 'Sin talla');

        const tr = document.createElement('tr');
        tr.dataset.varId = varId !== null ? varId : `nueva-${tallaId}`;

        // Nombre del input de stock
        const stockName = esNueva ? `nueva_variante_stock_nuevo_${tallaId}` : `variante_stock_${varId}`;

        tr.innerHTML = `
            <td class="small fw-semibold" style="${esNueva ? 'color:#198754;' : ''}">
                ${esc(etiqueta)}${esNueva ? ' <span class="badge bg-success-subtle text-success ms-1">Nueva</span>' : ''}
            </td>
            <td>
                <input type="number"
                       class="form-control form-control-sm qe-stock-input"
                       name="${stockName}"
                       value="${stock}"
                       min="0"
                       style="max-width:90px;"
                       data-var-id="${varId !== null ? varId : ''}"
                       data-talla-id="${tallaId || ''}">
            </td>
            <td class="text-center">
                <button type="button"
                        class="btn btn-sm btn-danger btn-quitar-variante"
                        data-var-id="${varId !== null ? varId : ''}"
                        data-talla-id="${tallaId || ''}"
                        data-es-nueva="${esNueva ? '1' : '0'}"
                        title="Quitar esta talla"
                        style="width:28px;height:28px;padding:0;line-height:1;">
                    🗑
                </button>
            </td>
        `;
        tbody.appendChild(tr);

        // Listener del botón eliminar
        tr.querySelector('.btn-quitar-variante').addEventListener('click', function () {
            const esN = this.dataset.esNueva === '1';
            if (esN) {
                // Quitar de variantesNuevas
                const tId = parseInt(this.dataset.tallaId);
                variantesNuevas = variantesNuevas.filter(function (v) { return v.tallaId !== tId; });
                // Liberar talla en el selector
                tallasCargadas = tallasCargadas.filter(function (c) {
                    const info = tallasDisponibles.find(function (t) { return t.id === tId; });
                    return info ? c !== info.codigo : true;
                });
                poblarSelectorTallas(null); // refrescar selector
            } else {
                const vId = parseInt(this.dataset.varId);
                if (!variantesAEliminar.includes(vId)) variantesAEliminar.push(vId);
                // Liberar talla del selector
                const tallaFilas = tbody.parentElement;
                const codigoTalla = tr.querySelector('td:first-child').textContent.trim().split(' ')[0];
                tallasCargadas = tallasCargadas.filter(function (c) { return c !== codigoTalla; });
                poblarSelectorTallas(null);
            }
            // Eliminar fila visualmente
            tr.style.transition = 'opacity 0.2s';
            tr.style.opacity = '0';
            setTimeout(function () { tr.remove(); }, 200);
        });
    }

    // ─── Poblar el selector de tallas disponibles ──────────────────────────
    function poblarSelectorTallas(variantesActuales) {
        if (!selectNuevaTalla) return;

        // Si se pasan variantes, actualizar tallasCargadas
        if (variantesActuales !== null) {
            tallasCargadas = variantesActuales
                .filter(function (v) { return v.talla_codigo; })
                .map(function (v) { return v.talla_codigo; });
        }

        // IDs ya en variantesNuevas (para no duplicar)
        const idsNuevas = variantesNuevas.map(function (v) { return v.tallaId; });

        selectNuevaTalla.innerHTML = '<option value="">-- Selecciona --</option>';
        tallasDisponibles.forEach(function (t) {
            // Filtrar tallas ya en uso o ya en cola de nuevas
            if (tallasCargadas.includes(t.codigo)) return;
            if (idsNuevas.includes(t.id)) return;
            const opt = document.createElement('option');
            opt.value = t.id;
            opt.textContent = t.nombre ? `${t.codigo} (${t.nombre})` : t.codigo;
            selectNuevaTalla.appendChild(opt);
        });
    }

    // ─── Panel "Agregar Talla" ─────────────────────────────────────────────
    if (btnMostrarAgregar) {
        btnMostrarAgregar.addEventListener('click', function () {
            if (panelAgregarTalla) panelAgregarTalla.style.display = 'block';
            this.style.display = 'none';
            if (inputNuevaTallaStock) inputNuevaTallaStock.value = '1';
        });
    }

    if (btnCancelarAgregar) {
        btnCancelarAgregar.addEventListener('click', function () {
            ocultarPanelAgregarTalla();
        });
    }

    if (btnConfirmarAgregar) {
        btnConfirmarAgregar.addEventListener('click', function () {
            const tallaId  = parseInt(selectNuevaTalla ? selectNuevaTalla.value : '');
            const stockVal = parseInt(inputNuevaTallaStock ? inputNuevaTallaStock.value : '0');

            if (!tallaId) {
                alert('Selecciona una talla antes de agregar.');
                return;
            }
            if (isNaN(stockVal) || stockVal < 0) {
                alert('El stock no puede ser negativo.');
                return;
            }

            // Buscar info de la talla
            const tallaInfo = tallasDisponibles.find(function (t) { return t.id === tallaId; });
            if (!tallaInfo) return;

            // Agregar a la cola de nuevas
            variantesNuevas.push({ tallaId: tallaId, tallaCodigo: tallaInfo.codigo, stock: stockVal });
            tallasCargadas.push(tallaInfo.codigo);

            // Agregar fila a la tabla
            let tbody = document.getElementById('qe-variantes-tbody');
            if (!tbody) {
                // Crear tabla si no existe (producto sin tallas previas)
                const contenedor = document.getElementById('qe-variantes-container');
                if (contenedor) {
                    contenedor.innerHTML = `
                        <table class="table table-sm table-bordered align-middle mb-0">
                            <thead class="table-light">
                                <tr>
                                    <th class="small">Talla / SKU</th>
                                    <th class="small" style="width:120px;">Stock</th>
                                    <th class="small text-center" style="width:60px;">Quitar</th>
                                </tr>
                            </thead>
                            <tbody id="qe-variantes-tbody"></tbody>
                        </table>
                    `;
                    tbody = document.getElementById('qe-variantes-tbody');
                    const sinVariantes = document.getElementById('qe-sin-variantes');
                    if (sinVariantes) sinVariantes.style.display = 'none';
                }
            }
            if (tbody) {
                agregarFilaVariante(tbody, null, tallaInfo.codigo, null, null, stockVal, tallaId);
            }

            // Refrescar selector y ocultar panel
            poblarSelectorTallas(null);
            ocultarPanelAgregarTalla();
        });
    }

    function ocultarPanelAgregarTalla() {
        if (panelAgregarTalla)  panelAgregarTalla.style.display = 'none';
        if (btnMostrarAgregar)  btnMostrarAgregar.style.display = 'inline-block';
        if (selectNuevaTalla)   selectNuevaTalla.value = '';
        if (inputNuevaTallaStock) inputNuevaTallaStock.value = '1';
    }

    // ═══════════════════════════════════════════════════════════════════════
    //  ENVÍO DEL FORMULARIO AJAX
    // ═══════════════════════════════════════════════════════════════════════

    if (form) {
        form.addEventListener('submit', function (e) {
            e.preventDefault();
            if (!productoIdActual) return;

            // ── Validar stocks negativos ──
            let stockInvalido = false;
            document.querySelectorAll('.qe-stock-input').forEach(function (inp) {
                const val = parseInt(inp.value);
                if (isNaN(val) || val < 0) {
                    inp.classList.add('is-invalid');
                    stockInvalido = true;
                } else {
                    inp.classList.remove('is-invalid');
                }
            });
            if (stockInvalido) {
                mostrarAlerta('danger', '⚠️ El stock no puede ser negativo. Corrige los valores marcados en rojo.');
                return;
            }

            const formData = new FormData(form);

            // Añadir imágenes a eliminar
            imagenesAEliminar.forEach(function (id) {
                formData.append('eliminar_imagenes[]', id);
            });

            // Añadir variantes a eliminar
            variantesAEliminar.forEach(function (id) {
                formData.append('eliminar_variantes[]', id);
            });

            // Añadir nuevas variantes con índice secuencial
            variantesNuevas.forEach(function (v, idx) {
                formData.append(`nueva_variante_talla_${idx}`, v.tallaId);
                formData.append(`nueva_variante_stock_${idx}`, v.stock);
            });

            setBtnGuardar(true);
            ocultarAlerta();

            fetch(`/productos/api/quick-edit/${productoIdActual}/guardar/`, {
                method: 'POST',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': obtenerCsrf(),
                },
                body: formData,
            })
            .then(function (r) {
                return r.json().then(function (d) { return { status: r.status, data: d }; });
            })
            .then(function ({ status, data }) {
                if (status === 200 && data.ok) {
                    actualizarCardEnDOM(data);
                    const bsModal = bootstrap.Modal.getInstance(modal);
                    if (bsModal) bsModal.hide();
                    mostrarToast(data.nombre || 'Producto');
                } else {
                    mostrarAlerta('danger', `⚠️ ${data.error || 'Error desconocido al guardar.'}`);
                }
            })
            .catch(function (err) {
                console.error('[QuickEdit] Error al guardar:', err);
                mostrarAlerta('danger', '⚠️ Error de conexión. Por favor, intenta de nuevo.');
            })
            .finally(function () { setBtnGuardar(false); });
        });
    }

    // ─── Actualizar tarjeta del producto en el DOM ─────────────────────────
    function actualizarCardEnDOM(data) {
        if (!cardActual) return;

        const tituloEl = cardActual.querySelector('.card-product-info .title');
        if (tituloEl && data.nombre) tituloEl.textContent = data.nombre;

        const precioEl = cardActual.querySelector('.card-product-info .price');
        if (precioEl && data.precio_base !== undefined) {
            precioEl.textContent = `$${parseFloat(data.precio_base).toFixed(2)}`;
        }

        if (data.main_image_url) {
            const imgPrincipal = cardActual.querySelector('.img-product');
            if (imgPrincipal) {
                imgPrincipal.src = data.main_image_url;
                imgPrincipal.setAttribute('data-src', data.main_image_url);
            }
        }
    }

    // ─── Toast de éxito ───────────────────────────────────────────────────
    function mostrarToast(nombre) {
        let tc = document.getElementById('quick-edit-toast-container');
        if (!tc) {
            tc = document.createElement('div');
            tc.id = 'quick-edit-toast-container';
            tc.style.cssText = 'position:fixed;top:85px;right:18px;z-index:9999;';
            document.body.appendChild(tc);
        }
        if (!document.getElementById('qe-toast-kf')) {
            const s = document.createElement('style');
            s.id = 'qe-toast-kf';
            s.textContent = '@keyframes qeSlideIn{from{opacity:0;transform:translateY(-8px)}to{opacity:1;transform:translateY(0)}}';
            document.head.appendChild(s);
        }
        const el = document.createElement('div');
        el.innerHTML = `
            <div style="background:#111;color:#fff;border-radius:999px;padding:10px 20px;
                        font-size:13px;font-weight:500;box-shadow:0 6px 20px rgba(0,0,0,.22);
                        display:flex;align-items:center;gap:8px;margin-bottom:8px;
                        animation:qeSlideIn 0.3s ease;">
                ✅ <strong>${esc(nombre)}</strong> actualizado correctamente
            </div>`;
        tc.appendChild(el);
        setTimeout(function () { el.remove(); }, 4000);
    }

    // ─── Helpers ──────────────────────────────────────────────────────────
    function mostrarCargando(v) {
        if (loadingDiv) loadingDiv.style.display = v ? 'block' : 'none';
        if (form)       form.style.display        = v ? 'none'  : 'block';
    }
    function mostrarAlerta(tipo, msg) {
        if (!alertDiv) return;
        alertDiv.style.display = 'block';
        alertDiv.innerHTML = `<div class="alert alert-${tipo} py-2 mb-0">${msg}</div>`;
    }
    function ocultarAlerta() {
        if (!alertDiv) return;
        alertDiv.style.display = 'none';
        alertDiv.innerHTML = '';
    }
    function setBtnGuardar(cargando) {
        if (!saveBtn) return;
        saveBtn.disabled = cargando;
        if (saveBtnText)    saveBtnText.textContent     = cargando ? 'Guardando...' : '💾 Guardar Cambios';
        if (saveBtnSpinner) saveBtnSpinner.style.display = cargando ? 'inline-block' : 'none';
    }
    function limpiarContenedor(id) {
        const el = document.getElementById(id);
        if (el) el.innerHTML = '';
    }
    function obtenerCsrf() {
        const el = form ? form.querySelector('[name=csrfmiddlewaretoken]') : null;
        return el ? el.value : '';
    }
    function esc(text) {
        if (text === null || text === undefined) return '';
        return String(text)
            .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;').replace(/'/g, '&#039;');
    }

})();
