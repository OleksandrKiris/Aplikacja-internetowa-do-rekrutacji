// JavaScript for AJAX pagination and search functionality
$(document).ready(function() {
    // Function to handle AJAX search
    $('#search-form').on('submit', function(event) {
        event.preventDefault();
        const searchQuery = $('#search-input').val();
        $.ajax({
            type: 'GET',
            url: $(this).attr('action'),
            data: {
                'q': searchQuery
            },
            success: function(response) {
                $('#recruiter-list').html(response.recruiters);
                $('.pagination').html(response.pagination);
            }
        });
    });

    // Function to handle AJAX pagination
    $(document).on('click', '.pagination-link', function(event) {
        event.preventDefault();
        const pageUrl = $(this).attr('href');
        $.ajax({
            type: 'GET',
            url: pageUrl,
            success: function(response) {
                $('#recruiter-list').html(response.recruiters);
                $('.pagination').html(response.pagination);
            }
        });
    });
});
