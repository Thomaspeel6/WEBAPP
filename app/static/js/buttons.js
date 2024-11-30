$(document).ready(function () {
    const csrfToken = $('meta[name="csrf-token"]').attr('content');
    $('.like-btn').on('click', function () {
        const tripId = $(this).data('trip-id');
        const likeButton = $(this);

        //send a POST request to like/unlike the trip
        $.ajax({
            url: '/like_trip',
            type: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            },
            data: {
                trip_id: tripId
            },
            success: function (data) {
                if (data.likes !== undefined) {
                    likeButton.find('.like-count').text(data.likes);
                    // ipdating the button liek count
                }
            },
        });
    });
    $('.delete-btn').on('click', function () {
        const tripId = $(this).data('trip-id'); // get the trip id from the buttons data attribute
        const tripCard = $(`#trip-${tripId}`); 

        if (confirm('Are you sure you want to delete this trip?')) { //cjeck witht he user
            $.ajax({
                url: `/delete_trip/${tripId}`, // flask route for deletion
                type: 'DELETE',
                headers: {
                    'X-CSRFToken': csrfToken
                },
                success: function (data) {
                    if (data.success) {
                        // rempve the trip card from the using fdade for astehctics 
                        tripCard.fadeOut(300, function () {
                            tripCard.remove(); // cpmpletely remove after fade-out
                        });
                    } else {
                        alert(data.error || 'Failed to delete trip.');
                    }
                },
            });
        }
    });
});