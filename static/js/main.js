$(document).ready(function(){
    $('#submitQuery').removeClass('disabled');
    $('#submitQuery').on('click',function(){
        query = $('#q').val();
        $('#search').attr('action',$('#search').attr('action')+"/"+query);
    });
});