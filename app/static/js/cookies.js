
window.addEventListener("load", function () {
    // initlaise the cookie consent popup
    window.cookieconsent.initialise({
        palette: {
            popup: {
                background: "#eaf7f7",
                text: "#5c7291"
            },
            button: {
                background: "#56cbdb",
                text: "#ffffff"
            }
        },
        theme: "classic",
        position: "centre",
        content: {
            message: "This website uses cookies to allow for the best user expirence.",
            dismiss: "Great",
        },
    });
});
