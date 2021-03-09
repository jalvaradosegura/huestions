function copyToClipboard(urlToCopy){
    const el = document.createElement('textarea');
    el.value = urlToCopy;
    document.body.appendChild(el);
    el.select();
    el.setSelectionRange(0, 99999);
    document.execCommand('copy');
    document.body.removeChild(el);
}

$(document).ready(function(){
    $('[data-toggle="tooltip"]').tooltip({
        title: 'Copied to clipboard!',
        trigger: 'click',
    });
});
$(document).on('show.bs.tooltip', function (e) {
    setTimeout(function() {
        $('[data-toggle="tooltip"]').tooltip('hide');
    }, 2000);
});
