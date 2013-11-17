$(document).ready(function(){
    $('#submitQuery').on('click',function(){
        query = $('#q').val();
        $.get( "/articles?q="+query, function( data ) {
            console.log('done');
        });
        return false;
    });
});