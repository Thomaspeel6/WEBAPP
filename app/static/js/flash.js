document.addEventListener("DOMContentLoaded", function() {
    // auto fade funciton for flash imessagse 
    setTimeout(function() {
        const flashes = document.querySelectorAll('.flash-message');
        flashes.forEach((flash) => {
            flash.classList.remove('show'); 
            flash.classList.add('fade'); 
        });
    }, 2500); 
});
