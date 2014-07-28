$(function(){
    var search_data;
    var insert_div = $("#results");
    var search_form = $("#item_search");
    var bodygroups = $("#bodygroups");
    var classes = $("#classes");
    var equip_regions = $("#equip_regions");
    var item_name = $("#item_name");
    var description = $(".mod-description");
    function call_api(search_data, page){
        $.ajax({
            url: tf2_api,
            type: "POST",
            data: { search_data: search_data, page: page, mod_id: mod_id, bodygroups: search_data["bodygroups"] }
        }).done(function(results){
            insert_div.empty();
            if (results.status) {
                insert_div.text(results.status);
            }
            else if (results.items.length > 0){
                insert_div.html(results.items);
            }

            $(".next, .prev, .pagination .page").removeAttr("href");
        }).fail(function() {
            insert_div.empty();
            insert_div.text("Fail!");
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
    search_form.submit(function(event){
        page = 1;
        event.preventDefault();
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