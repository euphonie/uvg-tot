$(document).ready(function(){
    $('.submitQuery').removeClass('disabled');
    $('.submitQuery').on('click',function(){
        query = $(this).prev().find('.q').val();
        $(this).closest('.search').attr('action',$(this).closest('.search').attr('action')+"/"+query);
    });
    $("#tag-list").select2({tags:[]});
});