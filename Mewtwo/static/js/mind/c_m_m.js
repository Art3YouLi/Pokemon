function common_alert(text, class_str) {
    if (!class_str) {
        class_str = 'alert-warning'
    }
    // reset bootstrap.bundle.js 里的方法
    const bundle_alert = typeof ($('.alert').alert) === 'function'
    if (bundle_alert) {
        $('.alert').alert('close')
    }
    // content
    const content = `
    <div class="alert ${class_str} fade show" role="alert" style="z-index: 2000;position: absolute;top: 0;width: calc(100%);">
      ${text}
    </div>`
    // append
    $('body').append(content)
    // clean
    setTimeout(function () {
        if (bundle_alert) {
            $('.alert').alert('close')
        } else {
            $('.alert').fadeOut('slow')
        }
    }, 1500)
}

function primary_alert(text) {
    common_alert(text, 'alert-primary')
}