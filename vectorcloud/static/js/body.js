$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})


$(document).ready(function(){
    $('[data-toggle="popover"]').popover({html:true});
});

$('.popover-dismiss').popover({
  trigger: 'focus'
})
