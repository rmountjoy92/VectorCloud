$(function () {
  $('[data-toggle="tooltip"]').tooltip()
})


$(document).ready(function(){
    $('[data-toggle="popover"]').popover({
        html : true,
        title : '<a href="#" class="close" data-dismiss="alert">&times;</a>',
    });
    $(document).on("click", ".popover .close" , function(){
        $(this).parents(".popover").popover('hide');
    });
});

$('.popover-dismiss').popover({
  trigger: 'focus'
})

$('.collapse').collapse({
  toggle: false
})
