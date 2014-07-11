$(function(){
    var page, search_data;
    var insert_div = $(".results");
    function call_api(search_data, page){
        $.ajax({
            url: tf2_api,
            type: "POST",
            data: { item_name: search_data, page: page }
        }).done(function(results){
            console.log(results);
            insert_div.empty();
            if (results.items.length > 0){
                insert_div.html(results.items);
            }
            else {
                insert_div.text("No results!");
            }
        }).fail(function(response) {
            insert_div.empty();
            insert_div.text("Fail!");
        });
    }
    $(".submit").click(function(){
        page = 1;
        search_data = $(".search").val();
        if (search_data.length < 3){
            insert_div.text("More char than 2!");
        }
        else {
            call_api(search_data, page);
        }
    });
    $(document).on("click", ".next", function(){
        console.log("click")
        page++;
        call_api(search_data, page);
    });
});