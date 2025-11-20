// reviews.js - Sistema de reseñas de productos

(function() {
    'use strict';

    // Agregar estilos CSS dinámicamente
    const style = document.createElement('style');
    style.textContent = `
        .rating-star {
            font-size: 24px;
            cursor: pointer;
            color: #ddd;
            transition: color 0.2s;
            display: inline-block;
            margin: 0 2px;
        }
        .rating-star:hover,
        .rating-star.active {
            color: #FFD700;
        }
        .review-stars i {
            font-size: 14px;
            margin-right: 2px;
        }
        #reviewsContainer {
            min-height: 100px;
        }
        .review-item {
            padding: 20px 0;
        }
        .review-comment {
            color: #666;
            line-height: 1.6;
        }
        .review-replies {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
        }
    `;
    document.head.appendChild(style);

    // Obtener CSRF token
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

    document.addEventListener('DOMContentLoaded', function() {
        const productoId = document.querySelector('[data-producto-id]')?.dataset.productoId;
        
        if (!productoId) {
            console.log('No se encontró ID de producto para reviews');
            return;
        }

        // Cargar reseñas al iniciar
        loadReviews(productoId);

        // Manejar envío de nueva reseña
        const reviewForm = document.getElementById('reviewForm');
        if (reviewForm) {
            reviewForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitReview(productoId);
            });
        }

        // Manejar cambio de ordenamiento
        const sortSelect = document.getElementById('reviewSortBy');
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                loadReviews(productoId, this.value);
            });
        }

        // Manejar clicks en estrellas para calificar
        setupRatingStars();
    });

    function setupRatingStars() {
        const stars = document.querySelectorAll('.rating-star');
        stars.forEach(star => {
            star.addEventListener('click', function() {
                const rating = this.dataset.rating;
                document.getElementById('reviewRating').value = rating;
                
                // Actualizar visualización de estrellas
                stars.forEach(s => {
                    if (parseInt(s.dataset.rating) <= parseInt(rating)) {
                        s.classList.add('active');
                    } else {
                        s.classList.remove('active');
                    }
                });
            });
        });
    }

    function loadReviews(productoId, sortBy = 'recent') {
        fetch(`/reviews/get/${productoId}/?sort=${sortBy}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    displayReviews(data.reviews);
                    updateReviewStats(data.stats);
                }
            })
            .catch(error => {
                console.error('Error loading reviews:', error);
            });
    }

    function displayReviews(reviews) {
        const container = document.getElementById('reviewsContainer');
        if (!container) return;

        if (reviews.length === 0) {
            container.innerHTML = `
                <div class="text-center py-5">
                    <p class="text-muted">No hay reseñas aún. ¡Sé el primero en dejar una!</p>
                </div>
            `;
            return;
        }

        let html = '';
        reviews.forEach(review => {
            html += `
                <div class="review-item mb-4 pb-4 border-bottom">
                    <div class="d-flex justify-content-between align-items-start mb-2">
                        <div>
                            <div class="d-flex align-items-center mb-2">
                                <div class="review-stars me-2">
                                    ${generateStars(review.rating)}
                                </div>
                                ${review.verified ? '<span class="badge bg-success ms-2">Verified Purchase</span>' : ''}
                            </div>
                            <h6 class="mb-1">${escapeHtml(review.title || 'Review')}</h6>
                            <small class="text-muted">${escapeHtml(review.user_name)} • ${review.created_at}</small>
                        </div>
                    </div>
                    <p class="review-comment">${escapeHtml(review.comment)}</p>
                    
                    ${review.replies && review.replies.length > 0 ? `
                        <div class="review-replies mt-3 ps-4 border-start">
                            ${review.replies.map(reply => `
                                <div class="reply-item mb-3">
                                    <div class="d-flex align-items-center mb-2">
                                        <strong class="me-2">${escapeHtml(reply.user_name)}</strong>
                                        <small class="text-muted">${reply.created_at}</small>
                                    </div>
                                    <p class="mb-0">${escapeHtml(reply.comment)}</p>
                                </div>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        });

        container.innerHTML = html;
    }

    function updateReviewStats(stats) {
        // Actualizar promedio general
        const avgElement = document.getElementById('averageRating');
        if (avgElement) {
            avgElement.textContent = stats.average;
        }

        // Actualizar total de reseñas
        const totalElement = document.getElementById('totalReviews');
        if (totalElement) {
            totalElement.textContent = `(${stats.total} Ratings)`;
        }

        // Actualizar barras de distribución
        for (let i = 1; i <= 5; i++) {
            const count = stats.rating_counts[i] || 0;
            const percentage = stats.total > 0 ? (count / stats.total * 100).toFixed(0) : 0;
            
            const barElement = document.getElementById(`rating-${i}-bar`);
            const countElement = document.getElementById(`rating-${i}-count`);
            
            if (barElement) {
                barElement.style.width = `${percentage}%`;
            }
            if (countElement) {
                countElement.textContent = count;
            }
        }
    }

    function submitReview(productoId) {
        const rating = document.getElementById('reviewRating').value;
        const title = document.getElementById('reviewTitle').value.trim();
        const comment = document.getElementById('reviewComment').value.trim();

        if (!rating || parseInt(rating) < 1) {
            showNotification('Por favor selecciona una calificación', 'error');
            return;
        }

        if (!comment) {
            showNotification('Por favor escribe un comentario', 'error');
            return;
        }

        const formData = new FormData();
        formData.append('rating', rating);
        formData.append('title', title);
        formData.append('comment', comment);

        fetch(`/reviews/submit/${productoId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrftoken,
                'X-Requested-With': 'XMLHttpRequest',
            },
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showNotification(data.message, 'success');
                
                // Limpiar formulario
                document.getElementById('reviewForm').reset();
                document.querySelectorAll('.rating-star').forEach(s => s.classList.remove('active'));
                
                // Recargar reseñas
                loadReviews(productoId);
                
                // Cerrar modal si está abierto
                const modal = bootstrap.Modal.getInstance(document.getElementById('writeReviewModal'));
                if (modal) {
                    modal.hide();
                }
            } else {
                showNotification(data.message, 'error');
            }
        })
        .catch(error => {
            console.error('Error submitting review:', error);
            showNotification('Error al enviar la reseña', 'error');
        });
    }

    function generateStars(rating) {
        let html = '';
        for (let i = 1; i <= 5; i++) {
            if (i <= rating) {
                html += '<i class="icon-star" style="color: #FFD700;"></i>';
            } else {
                html += '<i class="icon-star" style="color: #ddd;"></i>';
            }
        }
        return html;
    }

    function escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    }

    function showNotification(message, type = 'success') {
        // Implementación simple de notificación
        const notification = document.createElement('div');
        notification.className = `alert alert-${type === 'success' ? 'success' : 'danger'} position-fixed top-0 end-0 m-3`;
        notification.style.zIndex = '9999';
        notification.textContent = message;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.remove();
        }, 3000);
    }

    // Exponer funciones globales si es necesario
    window.reviewSystem = {
        loadReviews,
        submitReview
    };

})();
