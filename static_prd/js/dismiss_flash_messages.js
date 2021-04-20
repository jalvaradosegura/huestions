var boxes = document.querySelectorAll("#close_button");
var boxes_array = [...boxes]; // expand boxes, similar to python * :)
boxes_array.forEach(box => {
  box.addEventListener("click", function() { this.parentElement.parentElement.style.display = 'none'; });
});
