$(function(){

    function header_dropdown() {
        header_steam = $(".header .steam_block")
        $(".header .steam_block .dropdown-arrow").css({"display":"inline-block"});
        header_steam.click(function(event){
            event.preventDefault();
            event.stopPropagation();
            $(this).toggleClass("active");
        });
        $(document).click(function(){
            header_steam.removeClass("active");
        });
    }
    function alert_dissmiss() {
        $(".alert button.close").click(function(){
            $(this).parent().hide();
        });
    }

    header_dropdown()
    alert_dissmiss()
});