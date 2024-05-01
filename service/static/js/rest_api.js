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
        $("#product_likes").val(res.likes);
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

    let root = "/api/products"
 
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
            url: root,
            contentType: "application/json",
            data: JSON.stringify(data),
        });
 
 
        ajax.done(function(res){
            update_form_data(res)
            flash_message("Product has been created!")
        });
 
 
        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });
    });
 
    // ****************************************
    // Update a Product
    // ****************************************

    $("#update-btn").click(function () {

        let id = $("#product_id").val();
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
        if (id != ""){
            let ajax = $.ajax({
                    type: "PUT",
                    url: `/api/products/${id}`,
                    contentType: "application/json",
                    data: JSON.stringify(data)
                })
    
            ajax.done(function(res){
                update_form_data(res)
                flash_message("Product has been updated!")
            });
    
            ajax.fail(function(res){
                flash_message("Fail: Product " + id + " does not exist!")
            });
        }else{
            clear_form_data()
            flash_message("Please provide a valid product ID!");
        }
    });
 
    // ****************************************
    // Retrieve a Product
    // ****************************************

    $("#retrieve-btn").click(function () {

        let product_id = $("#product_id").val();

        $("#flash_message").empty();

        if (product_id != ""){
            let ajax = $.ajax({
                type: "GET",
                url: `/api/products/${product_id}`,
                contentType: "application/json",
                data: ''
            })

            ajax.done(function(res){
                //alert(res.toSource())
                update_form_data(res)
                flash_message("Success")
            });

            ajax.fail(function(res){
                clear_form_data()
                flash_message("Fail: Product " + id + " does not exist!")
            });
        }else{
            clear_form_data()
            flash_message("Please provide a valid product ID!")
        }

    });

    // ****************************************
    // Delete a Product
    // ****************************************

    $("#delete-btn").click(function () {

        let product_id = $("#product_id").val();
        if (!product_id) return;

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "DELETE",
            url: `${root}/${product_id}`,
            contentType: "application/json",
            data: '',
        })

        ajax.done(function(res){
            clear_form_data()
            flash_message("Product has been deleted!")
        });

        ajax.fail(function(res){
            flash_message("Server error!")
        });
    });
 
 
 
 
 
 
    // ****************************************
    // Clear the form
    // ****************************************
    $("#clear-btn").click(function () {
        $("#product_id").val("");
        $("#flash_message").empty();
        clear_form_data()
    });
    
    // ****************************************
    // Search for a Product
    // ****************************************
    $("#search-btn").click(function () {

        let name = $("#product_name").val();
        let category = $("#product_category").val();
        let price = $("#product_price").val();
        let rating = $("#product_rating").val()

        let queryString = ""

        if (name) {
            queryString += '?name=' + name
        }
        if (category) {
            if (queryString.length > 0) {
                queryString += '&category=' + category
            } else {
                queryString += '?category=' + category
            }
        }
        if (price) {
            if (queryString.length > 0) {
                queryString += '&price=' + price
            } else {
                queryString += '?price=' + price
            }
        }
        if (rating) {
            if (queryString.length > 0) {
                queryString += '&rating=' + rating
            } else {
                queryString += '?rating=' + rating
            }
        }

        $("#flash_message").empty();

        let ajax = $.ajax({
            type: "GET",
            url: `${root}${queryString}`,
            contentType: "application/json",
            data: ''
        })

        ajax.done(function(res){
            //alert(res.toSource())
            $("#search_results").empty();
            let table = '<table class="table table-striped" cellpadding="10">'
            table += '<thead><tr>'
            table += '<th class="col-md-2">ID</th>'
            table += '<th class="col-md-2">Name</th>'
            table += '<th class="col-md-2">Image URL</th>'
            table += '<th class="col-md-2">Description</th>'
            table += '<th class="col-md-2">Price</th>'
            table += '<th class="col-md-2">Rating</th>'
            table += '<th class="col-md-2">Category</th>'
            table += '<th class="col-md-2">Status</th>'
            table += '<th class="col-md-2">Likes</th>'
            table += '</tr></thead><tbody>'
            let firstProduct = "";
            for(let i = 0; i < res.length; i++) {
                let product = res[i];
                table +=  `<tr id="row_${i}"><td>${product.id}</td><td>${product.name}</td><td>${product.img_url}</td><td>${product.description}</td><td>${product.price}</td><td>${product.rating}</td><td>${product.category}</td><td>${product.status}</td><td>${product.likes}</td></tr>`;
                if (i == 0) {
                    firstProduct = product;
                }
            }
            table += '</tbody></table>';
            $("#search_results").append(table);

            // copy the first result to the form
            if (firstProduct != "") {
                update_form_data(firstProduct)
            }

            flash_message("Success")
        });

        ajax.fail(function(res){
            flash_message(res.responseJSON.message)
        });

    });
 }) 