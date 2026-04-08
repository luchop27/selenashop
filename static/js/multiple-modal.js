(function($, window, document) {
    'use strict';

    var MultiModal = function(element) {
        this.$element = $(element);
        this.modalCount = 0;
    };

    MultiModal.BASE_ZINDEX = 2000;
    MultiModal.BACKDROP_ZINDEX = 1900;

    MultiModal.prototype.ensureModalOnBody = function(target) {
        if (!target || target.nodeType !== 1) {
            return;
        }

        if (target.parentNode !== document.body) {
            document.body.appendChild(target);
        }
    };

    MultiModal.prototype.show = function(target) {
        var that = this;
        var $target = $(target);
        var modalIndex = that.modalCount++;

        that.ensureModalOnBody(target);

        $target.css('z-index', MultiModal.BASE_ZINDEX + (modalIndex * 20) + 10);

        // Bootstrap triggers the show event at the beginning of the show function and before
        // the modal backdrop element has been created. The timeout here allows the modal
        // show function to complete, after which the modal backdrop will have been created
        // and appended to the DOM.
        window.setTimeout(function() {
            // Keep a single backdrop for stacked flows and avoid stale layers.
            $('.modal-backdrop').not(':first').remove();

            that.adjustBackdrop();
            $('body').addClass('modal-open');
        });
    };

    MultiModal.prototype.hidden = function(target) {
        this.modalCount = Math.max(0, this.modalCount - 1);

        if (this.modalCount) {
            this.adjustBackdrop();

            // bootstrap removes the modal-open class when a modal is closed; add it back
            $('body').addClass('modal-open');
            return;
        }

        this.cleanupModalState();
    };

    MultiModal.prototype.adjustBackdrop = function() {
        $('.modal-backdrop:first').css('z-index', MultiModal.BACKDROP_ZINDEX);
    };

    MultiModal.prototype.cleanupModalState = function() {
        if ($('.modal.show').length) {
            this.adjustBackdrop();
            $('body').addClass('modal-open');
            return;
        }

        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open');
        document.body.style.overflow = '';
        document.body.style.paddingRight = '';
    };

    function Plugin(method, target) {
        return this.each(function() {
            var $this = $(this);
            var data = $this.data('multi-modal-plugin');

            if(!data)
                $this.data('multi-modal-plugin', (data = new MultiModal(this)));

            if(method)
                data[method](target);
        });
    }

    $.fn.multiModal = Plugin;
    $.fn.multiModal.Constructor = MultiModal;

    $(document).on('show.bs.modal', function(e) {
        $(document).multiModal('show', e.target);
    });

    $(document).on('shown.bs.modal', function(e) {
        $(document).multiModal('adjustBackdrop');
        $('body').addClass('modal-open');
    });

    $(document).on('hidden.bs.modal', function(e) {
        $(document).multiModal('hidden', e.target);
        window.setTimeout(function() {
            $(document).multiModal('cleanupModalState');
        });
    });
}(jQuery, window, document));
