var close_button = document.getElementById("close_button");
close_button.addEventListener("click", function() {
    this.parentElement.parentElement.style.display = 'none';
});
