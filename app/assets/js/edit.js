$(function() {
    var bodygroups = $("#bodygroups");
    var equip_regions = $("#equip_regions");
    function call_count(search_data) {
        $.ajax({
            url: tf2_api,
            type: "POST",
            data: { search_data: search_data, page: 1, bodygroups: search_data["bodygroups"] }
        }).done(function(results) {
                console.log("abnhas");
                $("#item-count span").text(results.count);
            }
        );
    }
    var get_count = function get_count(){
        search_data = {
            "item_name": "",
            classes: classes,
            bodygroups: bodygroups.val(),
            equip_regions: equip_regions.val()
        };
        call_count(search_data);
    };
    multipleSelect_three(true, get_count);
});