$(function(){
    var search_data;
    var insert_div = $("#results");
    var search_form = $("#item_search");
    var bodygroups = $("#bodygroups");
    var classes = $("#classes");
    var equip_regions = $("#equip_regions");
    var item_name = $("#item_name");
    var description = $(".mod-description");
    var old_val = [];
    var num = 1;
    var ajax_call;
    function call_api(search_data, page){
        ajax_call = $.ajax({
            url: tf2_api,
            type: "POST",
            data: { search_data: search_data, page: page, mod_id: mod_id, bodygroups: search_data["bodygroups"] }
        }).done(function(results){
            insert_div.empty();
            if (results.err_msg) {
                insert_div.text(results.err_msg);
            }
            else if (results.items.length > 0){
                insert_div.html(results.items);
            }

            $(".next, .prev, .pagination .page").removeAttr("href");
        }).fail(function(results, status) {
            if (status != "abort") {
                insert_div.empty();
                insert_div.text("Fail!");
            }
        });
    }
    function make_search_data(){
        search_data = {
            item_name: item_name.val(),
            classes: classes.val(),
            bodygroups: bodygroups.val(),
            equip_regions: equip_regions.val()
        };
    }
    make_search_data();
    search_form.find("select").change(function(event){
        if (ajax_call){
            ajax_call.abort();
        }
        page = 1;
        event.preventDefault();
        make_search_data();
        call_api(search_data, page);
    });
    item_name.change(function(){
        if (ajax_call){
            ajax_call.abort();
        }
        page = 1;
        var name_value = item_name.val();
        if(name_value != "") {
            old_val = [equip_regions.val() || old_val[0], bodygroups.val() || old_val[1]];
            equip_regions.val("").multipleSelect('refresh');
            bodygroups.val("").multipleSelect('refresh');
        }
        if (old_val.length > 0 && name_value == ""){
            equip_regions.val(old_val[0]).multipleSelect('refresh');
            bodygroups.val(old_val[1]).multipleSelect('refresh');
        }
        make_search_data();
        call_api(search_data, page);
    });
    $(document).on("click", ".next, .prev", function(){
        var element = $(this);
        if (!element.parent().hasClass("disabled")) {
            if (element.hasClass("next")){
                page++;
            } else {
                page--;
            }
            call_api(search_data, page);
        }
    });
    $(document).on("click", ".pagination .page", function(){
        page = $(this).text();
        call_api(search_data, page);
    });
    multipleSelect_three();
    $(".next, .prev, .pagination .page").removeAttr("href");
});