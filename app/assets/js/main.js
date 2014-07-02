$(function(){

    // JavaScript is enabled
    $("body").addClass("js");

    // Hide alerts
    $(".alert button.close").click(function(){
        $(this).parent().slideUp();
    });

    // User dropdown handler
    header_steam = $(".header .steam_block")
    header_steam.click(function(event){
        event.preventDefault();
        event.stopPropagation();
        $(this).toggleClass("active");
    });
    $(document).click(function(){
        header_steam.removeClass("active");
    });

});