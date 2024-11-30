
$(document).ready(function () {
    //due to teh large database,  its importnat to have client undestation on the laoding 
    // it will show it on clcik of a link
    window.addEventListener('beforeunload', function () {
        $('#loading-flash').show();
    });

    // hides the loading layer when finsihed laoding 
    window.addEventListener('load', function () {
        $('#loading-flash').hide();
    });
    //also if used of sarch engines arrow keys
    window.addEventListener('pageshow', function () {
        $('#loading-flash').hide();
    })

});