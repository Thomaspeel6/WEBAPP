$(document).ready(function () {
    console.log("Document is ready.");

    const csrfToken = $('meta[name="csrf-token"]').attr('content');

    $('.submit-rating-btn').off('click').on('click', function (event) {
        event.preventDefault(); //preavitnt he noraml button behavour 



        const button = $(this); //get the button that was clicked
        const destinationId = button.data('destination-id'); 
        const form = $(`#rating-form-${destinationId}`); 
        const ratingValue = form.find(`#rating-${destinationId}`).val(); // get the selected rating value


        if (!ratingValue || ratingValue < 1 || ratingValue > 5) {
            alert('Please select a valid rating.');
            return;
        }


        $.ajax({
            url: `/rate/${destinationId}`, // Fthe backedn fro teh rating function
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken, // including hte  CSRF token so it dosent get blocked 
            },
            data: {
                rating: ratingValue, //  the selected rating
            },
            success: function (data) {
                console.log("Rating submitted successfully.");
                if (data.average_rating !== undefined) {
                    //updating the the average rating for the specific destination, all wihtout reresrhifn the pgae
                    $(`#average-rating-${destinationId}`).text(`Average Rating: ${data.average_rating}`);

                }
            },
        });
    });
});
