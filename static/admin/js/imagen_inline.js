// Script para alternar entre campos de imagen y video
(function($) {
    console.log('=== IMAGEN INLINE JS LOADED ===');
    
    $(document).ready(function() {
        console.log('DOM ready');
        
        function toggleMediaFields() {
            console.log('toggleMediaFields called');
            
            // Para cada fila del inline
            $('tr.inline-related').each(function() {
                var $row = $(this);
                var $tipoSelect = $row.find('select[id$="-tipo_medio"]');
                
                if ($tipoSelect.length > 0) {
                    var tipo = $tipoSelect.val();
                    console.log('Row tipo:', tipo);
                    
                    // Agregar atributo data-tipo a la fila
                    $row.attr('data-tipo', tipo);
                }
            });
        }
        
        // Ejecutar al cargar
        toggleMediaFields();
        
        // Ejecutar al cambiar el select
        $(document).on('change', 'select[id$="-tipo_medio"]', function() {
            console.log('Tipo medio changed to:', $(this).val());
            toggleMediaFields();
        });
        
        // Para nuevas filas agregadas dinámicamente
        $(document).on('formset:added', function(event, $row) {
            console.log('Nueva fila agregada');
            toggleMediaFields();
        });
    });
})(django.jQuery);
