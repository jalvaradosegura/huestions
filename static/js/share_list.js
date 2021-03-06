function showThenHideDiv(){
    document.getElementById("copy-to-clipboard-div").style.display = 'block';
    setTimeout(function(){
    document.getElementById("copy-to-clipboard-div").style.display = 'none';
    }, 5000);
}

function copyToClipboard(urlToCopy){
    const el = document.createElement('textarea');
    el.value = urlToCopy;
    document.body.appendChild(el);
    el.select();
    el.setSelectionRange(0, 99999);
    document.execCommand('copy');
    document.body.removeChild(el);
    showThenHideDiv();
}
