$(function () {

    // ****************************************
    //  U T I L I T Y   F U N C T I O N S
    // ****************************************

    // Updates the form with data from the response
    function update_form_data(res) {
        $("#product_id").val(res.id);
        $("#product_name").val(res.name);
        $("#product_img_url").val(res.img_url);
        $("#product_description").val(res.description);
        $("#product_price").val(res.price);
        $("#product_rating").val(res.rating);
        $("#product_category").val(res.category);
        $("#product_status").val(res.status);
        $("#product_likes").val(res.like);
    }

    /// Clears all form fields
    function clear_form_data() {
        $("#product_id").val("");
        $("#product_name").val("");
        $("#product_img_url").val("");
        $("#product_description").val("");
        $("#product_price").val("");
        $("#product_rating").val("");
        $("#product_category").val("");
        $("#product_status").val("");
        $("#product_likes").val("");
    }

    // Updates the flash message area
    function flash_message(message) {
        $("#flash_message").empty();
        $("#flash_message").append(message);
    }

    // ****************************************
    // Create a Product
    // ****************************************

    $("#create-btn").click(function () {

        let name = $("#product_name").val();
        let img_url = $("#product_img_url").val();
        let description = $("#product_description").val();
        let price = parseFloat($("#product_price").val());
        let rating = parseFloat($("#product_rating").val());
        let category = $("#product_category").val();
        let status = $("#product_status").val();
        let likes = parseInt($("#product_likes").val(), 10);
        if (isNaN(likes)) {
            likes = 0;
        }

        let data = {
            "name": name,
            "img_url": img_url,
            "description": description,
            "price": price,
            "rating": rating,
            "category": category,
            "status": status,
            "likes": likes
        };

        $("#flash_message").empty();
        
        let ajax = $.ajax({
            type: "POST",
            url: "/products",
            contentType: "application/json",
            data: JSON.stringify(data),
        });

        ajax.done(function(res){
            update_form_data(res)
            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });


    // ****************************************
    // Update a Product
    // ****************************************



    // ****************************************
    // Retrieve a Product
    // ****************************************



    // ****************************************
    // Delete a Product
    // ****************************************



    // ****************************************
    // Clear the form
    // ****************************************


    // ****************************************
    // Search for a Product
    // ****************************************


})
