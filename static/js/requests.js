// JavaScript do funkcjonalności AJAX paginacji i wyszukiwania
$(document).ready(function() {
    // Funkcja do obsługi wyszukiwania AJAX
    $('#search-form').on('submit', function(event) {
        event.preventDefault(); // Zapobieganie domyślnemu zachowaniu formularza
        const searchQuery = $('#search-input').val(); // Pobranie wartości wyszukiwania
        $.ajax({
            type: 'GET', // Typ żądania
            url: $(this).attr('action'), // URL z atrybutu "action" formularza
            data: {
                'q': searchQuery // Dane wyszukiwania
            },
            success: function(response) {
                // Aktualizacja listy rekruterów i paginacji na podstawie odpowiedzi serwera
                $('#recruiter-list').html(response.recruiters);
                $('.pagination').html(response.pagination);
            }
        });
    });

    // Funkcja do obsługi paginacji AJAX
    $(document).on('click', '.pagination-link', function(event) {
        event.preventDefault(); // Zapobieganie domyślnemu zachowaniu linka
        const pageUrl = $(this).attr('href'); // Pobranie URL z atrybutu "href" linka
        $.ajax({
            type: 'GET', // Typ żądania
            url: pageUrl, // URL do paginacji
            success: function(response) {
                // Aktualizacja listy rekruterów i paginacji na podstawie odpowiedzi serwera
                $('#recruiter-list').html(response.recruiters);
                $('.pagination').html(response.pagination);
            }
        });
    });
});
