$(function(){
    var page, search_data;
    var insert_div = $(".results");
    function call_api(search_data, page){
        $.ajax({
            url: tf2_api,
            type: "POST",
            data: { search_data: search_data, page: page, mod_id: mod_id }
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
    $("#item_search").submit(function(event){
        event.preventDefault();
        page = 1;
        search_data = {
            item_name: $("#item_name").val(),
            class_name: $("#class_name").val(),
            bodygroup: $("#bodygroup").val(),
            equip_region: $("#equip_region").val()
        };
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
});