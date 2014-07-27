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

function multipleSelect_three(edit, get_count) {
    var classes = $("#classes");
    var shared_options = {};
    if (edit) {
        $.extend(shared_options, {onClose: function(){
            get_count();
        }})
    }
    var available_classes = classes.children().length;
    if (available_classes > 3){
    if (available_classes == 9) allSelected = "All classes selected"; else allSelected = "All available classes selected";
        classes.multipleSelect($.extend({allSelected: allSelected, placeholder: "No classes selected"}, shared_options));
    } else {
        classes.multipleSelect($.extend({allSelected: false, placeholder: "No classes selected", selectAll: false}, shared_options));
    }
    console.log($.extend({placeholder: "No bodygroup"}, shared_options));
    $("#bodygroups").multipleSelect($.extend({placeholder: "No bodygroup", selectAll: false}, shared_options));
    $("#equip_regions").multipleSelect($.extend({placeholder: "No equip region", filter: true, selectAll: false}, shared_options));
}