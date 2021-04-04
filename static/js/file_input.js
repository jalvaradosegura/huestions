const fileInput1 = document.querySelector('#file-js-1 input[type=file]');
fileInput1.onchange = () => {
  if (fileInput1.files.length > 0) {
    const fileName1 = document.querySelector('#file-js-1 .file-name');
    fileName1.textContent = fileInput1.files[0].name;
  }
}
const fileInput2 = document.querySelector('#file-js-2 input[type=file]');
fileInput2.onchange = () => {
  if (fileInput2.files.length > 0) {
    const fileName2 = document.querySelector('#file-js-2 .file-name');
    fileName2.textContent = fileInput2.files[0].name;
  }
}
