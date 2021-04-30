var button1 = document.getElementById('my-modal-button-1');
var modal1 = document.getElementById('my-modal-1');
var close1 = document.getElementById('my-modal-close-1');
var text1 = document.getElementById('modal-text-1');
var input_text1 = document.getElementById('my-modal-image-text-1');

var button2 = document.getElementById('my-modal-button-2');
var modal2 = document.getElementById('my-modal-2');
var close2 = document.getElementById('my-modal-close-2');
var text2 = document.getElementById('modal-text-2');
var input_text2 = document.getElementById('my-modal-image-text-2');

button1.onclick = function() {
  modal1.style.display = 'block';
  text1.innerHTML = input_text1.innerHTML;
}

close1.onclick = function() {
  modal1.style.display = 'none';
}

button2.onclick = function() {
  modal2.style.display = 'block';
  text2.innerHTML = input_text2.innerHTML;
}

close2.onclick = function() {
  modal2.style.display = 'none';
}

window.onclick = function(event) {
  if (event.target.className == 'modal-background') {
    modal1.style.display = 'none';
    modal2.style.display = 'none';
  }
}
