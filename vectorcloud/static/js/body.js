$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})


$(document).ready(function(){
    $('[data-toggle="popover"]').popover();
});

$('.popover-dismiss').popover({
  trigger: 'focus'
})
