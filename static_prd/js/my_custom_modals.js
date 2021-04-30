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

base_message = '<p>Images of alternatives uploaded by <b>Huestions</b> are taken from sites like <b>Pexels</b> and <b>Wikimedia Commons</b>. Normally using licenses with no restrictions, otherwise the respective attribution to the author and everything else it may need is given.</p><br><p>Transformations: Huestions shrinks the images and adds a blurry background to them.</p><br><p>On the other hand, users are responsible for meeting the license of the  pictures they upload. By using this site, they agreed to the terms and conditions in which it says what transformations Huestions does to the images.</p><br><p>If some credit was given, it comes after this line.</p>'

button1.onclick = function() {
  modal1.style.display = 'block';
  text1.innerHTML = base_message + '<br><h5 class="title is-5">' + input_text1.innerHTML + '</h3>';
}

close1.onclick = function() {
  modal1.style.display = 'none';
}

button2.onclick = function() {
  modal2.style.display = 'block';
  text2.innerHTML = base_message + '<br><h5 class="title is-5">' + input_text2.innerHTML + '</h3>';
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
