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

function multipleSelect_three() {
    classes = $("#classes");
    var available_classes = classes.children().length;
    if (available_classes > 3){
    if (available_classes == 9) allSelected = "All classes selected"; else allSelected = "All available classes selected";
    classes.multipleSelect({allSelected: "All classes selected", placeholder: "No classes selected"});
    } else {
        classes.multipleSelect({allSelected: false, placeholder: "No classes selected", selectAll: false});
    }
    $("#bodygroups").multipleSelect({placeholder: "No bodygroup", selectAll: false});
    $("#equip_regions").multipleSelect({placeholder: "No equip region", filter: true, selectAll: false});
}