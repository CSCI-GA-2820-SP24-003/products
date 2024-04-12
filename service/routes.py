######################################################################
# Copyright 2016, 2024 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
######################################################################

"""
Product Service

This service implements a REST API that allows you to Create, Read, Update
and Delete Products
"""

from flask import jsonify, request, url_for, abort
from flask import current_app as app  # Import Flask application
from service.models import Product
from service.common import status  # HTTP Status Codes


############################################################
# Health Endpoint
############################################################
@app.route("/health")
def health():
    """Health Status"""
    return {"status": "OK"}, status.HTTP_200_OK


######################################################################
# GET INDEX
######################################################################
@app.route("/")
def index():
    """Root URL response"""
    return app.send_static_file("index.html")


######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################

############################################################
# Create product
############################################################


@app.route("/products", methods=["POST"])
def create_products():
    """Create a product
    This Endpoint will create a Product based on the data provided in the body of the request
    """
    app.logger.info("Request to Create product...")
    check_content_type("application/json")

    data = request.get_json()
    product_id = data.get("id")

    if product_id:
        product = Product.find(product_id)
        if product:
            error(
                status.HTTP_409_CONFLICT,
                f"Product with Id'{product_id}' already exists.",
            )

    product = Product()
    product.deserialize(request.get_json())
    product.create()
    message = product.serialize()
    location_url = url_for("read_products", product_id=product.id, _external=True)

    app.logger.info("Product with ID: %d created.", product.id)
    return jsonify(message), status.HTTP_201_CREATED, {"Location": location_url}


@app.route("/products", methods=["GET"])
def list_products():
    """Returns all products"""
    app.logger.info("Request to list all products...")
    products = Product.all()
    results = [product.serialize() for product in products]

    app.logger.info("Returning %d products", len(results))
    return jsonify({"products": results}), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["GET"])
def read_products(product_id):
    """
    Retrieve a single Product

    This endpoint will return a Product based on it's id
    """
    app.logger.info("Request for product with id: %s", product_id)
    product = Product.find(product_id)
    if not product:
        error(
            status.HTTP_404_NOT_FOUND, f"Product with id '{product_id}' was not found."
        )

    app.logger.info("Returning product: %s", product.name)
    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>", methods=["DELETE"])
def delete_products(product_id):
    """
    Delete a Product

    This endpoint will delete a Product based the id specified in the path
    """
    app.logger.info("Request to delete product with id: %d", product_id)

    product = Product.find(product_id)
    if product:
        product.delete()
        app.logger.info("Product with ID: %d delete complete.", product_id)
    else:
        app.logger.info("Product with ID: %d was not found.", product_id)

    return "", status.HTTP_204_NO_CONTENT


@app.route("/products/<int:product_id>", methods=["PUT"])
def update_products(product_id):
    """
    Update a Product

    This endpoint will update a Product based the body that is posted
    """
    app.logger.info("Request to update product with id: %d", product_id)
    check_content_type("application/json")

    product = Product.find(product_id)
    if not product:
        error(
            status.HTTP_404_NOT_FOUND, f"Product with id: '{product_id}' was not found."
        )

    product.deserialize(request.get_json())
    product.id = product_id
    product.update()

    app.logger.info("Product with ID: %d updated.", product.id)
    return jsonify(product.serialize()), status.HTTP_200_OK


@app.route("/products/<int:product_id>/like", methods=["POST"])
def like_product(product_id):
    """Like a product
    This Endpoint will like a Product based on the data provided in the body of the request
    """
    app.logger.info("Request to Like a product...")
    product = Product.query.get(product_id)
    if not product:
        error(status.HTTP_404_NOT_FOUND, "This product doesn't exist.")

    product.like()
    app.logger.info(f"Product {product_id} got a like")
    return (
        jsonify(
            {"message": "The product got a like successfully", "likes": product.likes}
        ),
        status.HTTP_200_OK,
    )


######################################################################
# Checks the ContentType of a request
######################################################################
def check_content_type(content_type):
    """Checks that the media type is correct"""
    if "Content-Type" not in request.headers:
        app.logger.error("No Content-Type specified.")
        error(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {content_type}",
        )

    if request.headers["Content-Type"] == content_type:
        return

    app.logger.error("Invalid Content-Type: %s", request.headers["Content-Type"])
    error(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {content_type}",
    )


######################################################################
# Logs error messages before aborting
######################################################################
def error(status_code, reason):
    """Logs the error and then aborts"""
    app.logger.error(reason)
    abort(status_code, reason)
