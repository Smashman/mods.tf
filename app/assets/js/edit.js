$(function() {
    var bodygroups = $("#bodygroups");
    var equip_regions = $("#equip_regions");
    var defindex = $("#defindex");
    var hide_downloads = $("#hide_downloads")
    function call_count(search_data) {
        $.ajax({
            url: tf2_api,
            type: "POST",
            data: { search_data: search_data, page: 1, bodygroups: search_data["bodygroups"] }
        }).done(function(results) {
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
    $("#tags").multipleSelect({selectAll: false, placeholder: "No tags selected", allSelected: false});
    if (!defindex.val()) {
        hide_downloads.prop('disabled', true);
    }
    defindex.change(function(){
        if ($(this).val()) {
            hide_downloads.prop('disabled', false);
        }
        else{
            hide_downloads.prop('disabled', true);
        }
    });
});