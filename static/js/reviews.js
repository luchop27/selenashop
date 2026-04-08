// Sistema de Reseñas para Productos
(function() {
    'use strict';
    
    const productoSection = document.querySelector('[data-producto-id]');
    const productoId = productoSection ? productoSection.dataset.productoId : null;
    let currentSort = 'recent';
    let selectedReviewRating = 0;
    let ratingStarElements = [];
    
    // Agregar estilos CSS dinámicamente
    const style = document.createElement('style');
    style.textContent = `
        .rating-star {
            font-size: 30px;
            cursor: pointer;
            color: #b8b8b8;
            transition: color 0.2s;
            display: inline-block;
            margin: 0 2px;
            line-height: 1;
        }
        .rating-star.active,
        .rating-star.hover {
            color: #FFD700;
        }
        .list-rating-check {
            display: flex;
            align-items: center;
            gap: 2px;
        }
        .rating-stars {
            font-size: 14px;
            letter-spacing: 2px;
        }
        .avatar-placeholder {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #007bff;
            color: white;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 20px;
            font-weight: bold;
        }
        .write-review-wrap {
            display: none;
        }
        .btn-cancel-review {
            display: none;
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
    
    // Cargar reseñas al iniciar
    document.addEventListener('DOMContentLoaded', function() {
        if (productoId) {
            loadReviews();
            setupEventListeners();
        }
    });

    function paintRatingStars(rating) {
        ratingStarElements.forEach(star => {
            const starRating = parseInt(star.dataset.rating, 10);
            const shouldFill = starRating <= rating;
            star.classList.toggle('active', shouldFill);
            star.classList.remove('hover');
            star.textContent = shouldFill ? '★' : '☆';
        });
    }

    function previewRatingStars(rating) {
        ratingStarElements.forEach(star => {
            const starRating = parseInt(star.dataset.rating, 10);
            const shouldFill = starRating <= rating;
            star.classList.toggle('hover', shouldFill);
            star.classList.remove('active');
            star.textContent = shouldFill ? '★' : '☆';
        });
    }

    function setSelectedRating(rating) {
        selectedReviewRating = rating;
        const ratingInput = document.getElementById('reviewRating');
        if (ratingInput) {
            ratingInput.value = String(rating);
        }
        paintRatingStars(selectedReviewRating);
    }

    function resetSelectedRating() {
        setSelectedRating(0);
    }
    
    function setupEventListeners() {
        // Botón de escribir reseña
        const btnWriteReview = document.querySelector('.btn-write-review');
        const btnCancelReview = document.querySelector('.btn-cancel-review');
        const writeReviewWrap = document.querySelector('.write-review-wrap');
        
        if (btnWriteReview) {
            btnWriteReview.addEventListener('click', function() {
                writeReviewWrap.style.display = 'block';
                btnWriteReview.style.display = 'none';
                btnCancelReview.style.display = 'inline-block';
            });
        }
        
        if (btnCancelReview) {
            btnCancelReview.addEventListener('click', function() {
                writeReviewWrap.style.display = 'none';
                btnWriteReview.style.display = 'inline-block';
                btnCancelReview.style.display = 'none';
                document.getElementById('reviewForm').reset();
                resetSelectedRating();
            });
        }
        
        // Sistema de estrellas para rating
        ratingStarElements = Array.from(document.querySelectorAll('.rating-star'));
        const ratingInput = document.getElementById('reviewRating');
        selectedReviewRating = parseInt(ratingInput ? ratingInput.value : '0', 10) || 0;
        paintRatingStars(selectedReviewRating);

        ratingStarElements.forEach(star => {
            star.addEventListener('click', function() {
                const rating = parseInt(this.dataset.rating, 10) || 0;
                setSelectedRating(rating);
            });

            star.addEventListener('mouseenter', function() {
                const rating = parseInt(this.dataset.rating, 10) || 0;
                previewRatingStars(rating);
            });

            star.addEventListener('keydown', function(e) {
                if (e.key !== 'Enter' && e.key !== ' ') {
                    return;
                }
                e.preventDefault();
                const rating = parseInt(this.dataset.rating, 10) || 0;
                setSelectedRating(rating);
            });
        });

        const ratingContainer = document.querySelector('.list-rating-check');
        if (ratingContainer) {
            ratingContainer.addEventListener('mouseleave', function() {
                paintRatingStars(selectedReviewRating);
            });
        }
        
        // Submit del formulario de reseña
        const reviewForm = document.getElementById('reviewForm');
        if (reviewForm) {
            reviewForm.addEventListener('submit', function(e) {
                e.preventDefault();
                submitReview();
            });
        }
        
        // Ordenamiento de reseñas
        const sortSelect = document.getElementById('reviewSortBy');
        if (sortSelect) {
            sortSelect.addEventListener('change', function() {
                currentSort = this.value;
                loadReviews();
            });
        }
    }
    
    function loadReviews() {
        fetch(`/reviews/get/${productoId}/?sort=${currentSort}`)
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    updateReviewsDisplay(data);
                }
            })
            .catch(error => {
                console.error('Error loading reviews:', error);
            });
    }
    
    function updateReviewsDisplay(data) {
        const { reviews, stats, user_has_reviewed } = data;
        
        // Actualizar promedio rating
        const avgElement = document.getElementById('averageRating');
        if (avgElement) {
            avgElement.textContent = stats.average > 0 ? stats.average.toFixed(1) : '0.0';
        }
        
        // Actualizar estrellas del promedio
        updateAverageStars(stats.average);
        
        // Actualizar total de ratings
        const totalText = document.getElementById('totalRatingsText');
        if (totalText) {
            totalText.textContent = `(${stats.total} valoraci${stats.total !== 1 ? 'ones' : 'on'})`;
        }
        
        document.getElementById('totalReviewsCount').textContent = stats.total;
        
        // Actualizar barras de rating
        const totalReviews = stats.total || 1;
        [5, 4, 3, 2, 1].forEach(rating => {
            const count = stats.rating_counts[rating] || 0;
            const percentage = stats.total > 0 ? (count / stats.total) * 100 : 0;
            const item = document.querySelector(`.rating-score .item[data-rating="${rating}"]`);
            if (item) {
                const bar = item.querySelector('.rating-bar');
                const countEl = item.querySelector('.rating-count');
                if (bar) bar.style.width = `${percentage}%`;
                if (countEl) countEl.textContent = count;
            }
        });
        
        // Mostrar/ocultar formulario según si el usuario ya reseñó
        const userStatusDiv = document.getElementById('userReviewStatus');
        const reviewForm = document.getElementById('reviewForm');
        
        if (user_has_reviewed && userStatusDiv && reviewForm) {
            userStatusDiv.classList.remove('d-none');
            userStatusDiv.classList.add('alert-info');
            userStatusDiv.innerHTML = '<p class="mb-0">Ya reseñaste este producto. Puedes ver tu reseña aquí abajo.</p>';
            reviewForm.style.display = 'none';
            
            // Ocultar botones de write review
            const btnWrite = document.querySelector('.btn-write-review');
            const btnCancel = document.querySelector('.btn-cancel-review');
            if (btnWrite) btnWrite.style.display = 'none';
            if (btnCancel) btnCancel.style.display = 'none';
        } else if (userStatusDiv) {
            userStatusDiv.classList.add('d-none');
        }
        
        // Actualizar lista de reseñas
        const container = document.getElementById('reviewsContainer');
        if (reviews.length === 0) {
            container.innerHTML = '<p class="text-center text_black-2 py-5">Aún no hay reseñas. ¡Sé la primera persona en reseñar este producto!</p>';
        } else {
            container.innerHTML = reviews.map(review => createReviewHTML(review)).join('');
        }
    }
    
    function updateAverageStars(average) {
        const starsContainer = document.getElementById('averageStars');
        if (!starsContainer) return;
        
        const stars = starsContainer.querySelectorAll('i');
        const fullStars = Math.floor(average);
        
        stars.forEach((star, index) => {
            if (index < fullStars) {
                star.style.color = '#FFD700';
            } else {
                star.style.color = '#ddd';
            }
        });
    }
    
    function createReviewHTML(review) {
        const stars = '★'.repeat(review.rating) + '☆'.repeat(5 - review.rating);
        
        let html = `
            <div class="reply-comment-item">
                <div class="user">
                    <div class="image">
                        <div class="avatar-placeholder">${review.user_name.charAt(0).toUpperCase()}</div>
                    </div>
                    <div>
                        ${review.title ? `<h6><span class="link">${review.title}</span></h6>` : ''}
                        <div class="d-flex align-items-center gap-2 mb-1">
                            <span class="rating-stars text-warning">${stars}</span>
                            ${review.verified ? '<span class="badge bg-success text-white" style="font-size: 10px;">Compra verificada</span>' : ''}
                        </div>
                        <div class="d-flex align-items-center gap-2">
                            <span class="fw-6">${review.user_name}</span>
                            <span class="day text_black-2">${review.created_at}</span>
                        </div>
                    </div>
                </div>
                <p class="text_black-2">${review.comment}</p>
            </div>
        `;
        
        // Agregar respuestas si existen
        if (review.replies && review.replies.length > 0) {
            review.replies.forEach(reply => {
                html += `
                    <div class="reply-comment-item type-reply">
                        <div class="user">
                            <div class="image">
                                <div class="avatar-placeholder">M</div>
                            </div>
                            <div>
                                <h6>
                                    <span class="link">Respuesta de ${reply.user_name}</span>
                                </h6>
                                <div class="day text_black-2">${reply.created_at}</div>
                            </div>
                        </div>
                        <p class="text_black-2">${reply.comment}</p>
                    </div>
                `;
            });
        }
        
        return html;
    }
    
    function submitReview() {
        const rating = document.getElementById('reviewRating').value;
        const title = document.getElementById('reviewTitle').value;
        const comment = document.getElementById('reviewComment').value;
        
        if (!rating || rating === '0') {
            alert('Selecciona una calificación antes de enviar tu reseña.');
            return;
        }
        
        if (!comment.trim()) {
            alert('Escribe un comentario para continuar.');
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
                alert('Reseña enviada correctamente.');
                // Resetear formulario
                document.getElementById('reviewForm').reset();
                resetSelectedRating();
                
                // Ocultar formulario
                document.querySelector('.write-review-wrap').style.display = 'none';
                document.querySelector('.btn-write-review').style.display = 'inline-block';
                document.querySelector('.btn-cancel-review').style.display = 'none';
                
                // Recargar reseñas
                loadReviews();
            } else {
                alert(data.message || 'No se pudo enviar la reseña.');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Ocurrió un error al enviar la reseña.');
        });
    }
    
})();
