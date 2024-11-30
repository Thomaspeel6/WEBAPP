$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    //  selection of a destination
    $('#search-input').on('input', function () {
        const searchTerm = $(this).val(); //  the typed query
        const country = $('#destinations-container').data('country'); 

        $.ajax({
            url: `/places/${country}`,
            type: 'GET',
            data: { q: searchTerm }, 
            dataType: 'json',
            headers: {
                'X-CRSFToken': csrfToken
            },
            success: function (response) {
                $('#destinations-container').html(response.cards);
                $('#pagination-container').html(response.pagination);
            },
            error: function (xhr, status, error) { //cathcing errors 
                console.error('Failed to fetch destinations:', error);
            }
        });
    });

    //dynamic pagantion 
    $(document).on('click', '.page-link', function (e) {
        e.preventDefault(); // preventing default page reload
        const url = $(this).attr('href'); 
        
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                $('#destinations-container').html(response.cards); 
                $('#pagination-container').html(response.pagination); 
            },
            error: function (xhr, status, error) {
                console.error("Failed to fetch destinations:", xhr.responseText);
            }
        });
    });

    //sort dynamically 
    $(document).on('click', '.sort-link', function (e) {
        e.preventDefault(); 
        const url = $(this).attr('href'); 
        $('.sort-link').removeClass('active');

     
        $(this).addClass('active');
    
    
        $.ajax({
            url: url,
            type: 'GET',
            dataType: 'json',
            success: function (response) {
                $('#destinations-container').html(response.cards); 
                $('#pagination-container').html(response.pagination); 
            },
            error: function (xhr, status, error) {
                console.error("Failed to fetch sorted destinations:", xhr.responseText);
            }
        });
    });


});



