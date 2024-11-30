$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content'); //for protection
    $("#destinations").select2({
        placeholder: "Select or add destinations",
        allowClear: true,
        minimumInputLength: 2, // triggering the  search after 2 characters
        ajax: {
            url: "/search_destinations",  // the route to the backend
            dataType: "json",  // expect a joson response
            delay: 250,  //to avoid spamming ot server
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: function(params) {
                return {
                    q: params.term  // sedining the search term to the server
                };
            },
            processResults: function(data) {
                return {
                    results: data  // presednt the data from the server to Select2's format
                };
            }
        },
    });
});
