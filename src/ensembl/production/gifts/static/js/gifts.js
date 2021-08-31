
function statusFormat(value) {
    if (value === 'Complete') {
        return '<span class="badge badge-success">' + value + '</span>'
    } else if (value === 'Failed') {
      return '<span class="badge badge-danger">' + value + '</span>'
    } else {
        return '<span class="badge badge-primary">' + value + '</span>'
    }
}
