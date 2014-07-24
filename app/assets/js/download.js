$(function(){
    var page, search_data;
    var insert_div = $(".results");
    var search_form = $("#item_search");
    var bodygroups = $("#bodygroups");
    var classes = $("#classes");
    var equip_regions = $("#equip_regions");
    var item_name = $("#item_name");
    function call_api(search_data, page){
        $.ajax({
            url: tf2_api,
            type: "POST",
            data: { search_data: search_data, page: page, mod_id: mod_id, bodygroups: search_data["bodygroups"] }
        }).done(function(results){
            console.log(results);
            insert_div.empty();
            if (results.items.length > 0){
                insert_div.html(results.items);
            }
            else {
                insert_div.text("No results!");
            }
        }).fail(function() {
            insert_div.empty();
            insert_div.text("Fail!");
        });
    }
    search_form.submit(function(event){
        event.preventDefault();
        page = 1;
        search_data = {
            item_name: item_name.val(),
            classes: classes.val(),
            bodygroups: bodygroups.val(),
            equip_regions: equip_regions.val()
        };
        console.log(search_data);
        call_api(search_data, page);
    });
    $(document).on("click", ".next", function(){
        page++;
        call_api(search_data, page);
    });
    $(document).on("click", ".prev", function(){
        page--;
        call_api(search_data, page);
    });
    search_form.submit();
    multipleSelect_three();
});