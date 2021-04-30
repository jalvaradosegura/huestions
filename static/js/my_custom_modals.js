var button = document.getElementById('my-modal-button-1');
var modal = document.getElementById('my-modal-1');
var close = document.getElementById('my-modal-close-1');

button.onclick = function() {
  modal.style.display = 'block';
}

close.onclick = function() {
  modal.style.display = 'none';
}

window.onclick = function(event) {
  if (event.target.className == 'modal-background') {
    modal.style.display = 'none';
  }
}
