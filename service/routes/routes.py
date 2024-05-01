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

from flask import current_app as app  # Import Flask application
from flask_restx import Resource, fields, reqparse
from service.models.models import Product, Status
from service.common import status  # HTTP Status Codes
from .. import api


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
    # return {
    #     "status": "OK"
    # }, status.HTTP_200_OK  # using this as place holder, should change to return the index.html file
    return app.send_static_file("index.html")


create_model = api.model(
    "Product",
    {
        "name": fields.String(
            required=True,
            description="The name of the product",
            max_length=120,
            example="Product Name",
        ),
        "img_url": fields.String(
            required=True,
            description="The image URL of the product",
            max_length=120,
            example="https://example.com/product.jpg",
        ),
        "description": fields.String(
            description="The description of the product",
            max_length=2048,
            example="This is a product description.",
        ),
        "price": fields.Float(
            required=True,
            description="The price of the product",
            example=9.99,
        ),
        "rating": fields.Float(
            description="The rating of the product",
            default=0.0,
            max=10.0,
            example=5.0,
        ),
        "category": fields.String(
            description="The category of the product",
            max_length=120,
            example="clothes",
        ),
        "status": fields.String(
            description="The status of the product",
            enum=[e.name for e in Status],
            default=Status.ACTIVE.name,
        ),
        "likes": fields.Integer(
            description="The number of likes for the product",
            default=0,
            min=0,
            example=10,
        ),
    },
)


product_model = api.inherit(
    "ProductModel",
    create_model,
    {
        "id": fields.Integer(
            readOnly=True,
            description="The unique identifier of the product",
        ),
    },
)

product_args = reqparse.RequestParser()
product_args.add_argument(
    "rating", type=str, location="args", required=False, help="List Products by rating"
)
product_args.add_argument(
    "category",
    type=str,
    location="args",
    required=False,
    help="List Product by category",
)
product_args.add_argument(
    "price", type=str, location="args", required=False, help="List Products by price"
)
product_args.add_argument(
    "name", type=str, location="args", required=False, help="List Products by name"
)

######################################################################
#  R E S T   A P I   E N D P O I N T S
######################################################################


######################################################################
#  PATH: /products/{id}
######################################################################
@api.route("/products/<int:product_id>")
@api.param("product_id", "The Product identifier")
class ProductResource(Resource):
    """
    ProductResource class

    Allows the manipulation of a single Product
    GET /products/{id} - Returns a Product with the id
    PUT /products/{id} - Update a Product with the id
    DELETE /products/{id} -  Deletes a Product with the id
    """

    # ------------------------------------------------------------------
    # RETRIEVE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("get_products")
    @api.response(404, "Product not found")
    @api.marshal_with(product_model)
    def get(self, product_id):
        """
        Retrieve a single Product

        This endpoint will return a Product based on it's id
        """
        app.logger.info("Request for product with id: %s", product_id)
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # UPDATE AN EXISTING PRODUCT
    # ------------------------------------------------------------------
    @api.doc("update_products")
    @api.response(404, "Product not found")
    @api.response(400, "The posted Product data was not valid")
    @api.expect(product_model)
    @api.marshal_with(product_model)
    def put(self, product_id):
        """
        Update a Product

        This endpoint will update a Product based the body that is posted
        """
        app.logger.info("Request to update product with id: %s", product_id)
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )
        app.logger.debug("Payload = %s", api.payload)
        data = api.payload
        product.deserialize(data)
        product.id = product_id
        product.update()
        return product.serialize(), status.HTTP_200_OK

    # ------------------------------------------------------------------
    # DELETE A PRODUCT
    # ------------------------------------------------------------------
    @api.doc("delete_products")
    @api.response(204, "Product deleted")
    def delete(self, product_id):
        """
        Delete a Product

        This endpoint will delete a Product based the id specified in the path
        """
        app.logger.info("Request to delete product with id: %s", product_id)
        product = Product.find(product_id)
        if product:
            product.delete()
            app.logger.info("Product with ID: %d delete complete.", product_id)
        return "", status.HTTP_204_NO_CONTENT


######################################################################
#  PATH: /products
######################################################################
@api.route("/products", strict_slashes=False)
class ProductCollection(Resource):
    """Handles all interactions with collections of Products"""

    # ------------------------------------------------------------------
    # LIST ALL PRODUCTS
    # ------------------------------------------------------------------
    @api.doc("list_products")
    @api.expect(product_args, validate=True)
    @api.marshal_list_with(product_model)
    def get(self):
        """Returns all Products"""
        app.logger.info("Request to list Products")
        products = []
        args = product_args.parse_args()
        if args["category"]:
            print(args["category"])
            app.logger.info("Filtering by category: %s", args["category"])
            products = Product.filter_by_query(category=args["category"])
        elif args["price"]:
            app.logger.info("Filtering by price: %s", args["price"])
            products = Product.filter_by_query(price=args["price"])
        elif args["rating"]:
            app.logger.info("Filtering by rating: %s", args["rating"])
            products = Product.filter_by_query(rating=args["rating"])
        elif args["name"]:
            app.logger.info("Filtering by name: %s", args["name"])
            products = Product.filter_by_query(name=args["name"])
        else:
            app.logger.info("Returning unfiltered list")
            products = Product.all()
        results = [product.serialize() for product in products]
        app.logger.info("Returning %d products", len(results))
        return results, status.HTTP_200_OK

    # ------------------------------------------------------------------
    # ADD A NEW PRODUCT
    # ------------------------------------------------------------------
    @api.doc("create_products")
    @api.response(400, "The posted data was not valid")
    @api.expect(create_model)
    @api.marshal_with(product_model, code=201)
    def post(self):
        """
        Creates a Product
        This endpoint will create a Product based the data in the body that is posted
        """
        app.logger.info("Request to create a product")
        product = Product()
        app.logger.debug("Payload = %s", api.payload)
        product.deserialize(api.payload)
        product.create()
        app.logger.info("Product with new id [%s] created!", product.id)
        location_url = api.url_for(
            ProductResource, product_id=product.id, _external=True
        )
        return product.serialize(), status.HTTP_201_CREATED, {"Location": location_url}


######################################################################
#  PATH: /products/{id}/like
######################################################################
@api.route("/products/<int:product_id>/like")
@api.param("product_id", "The Product identifier")
class LikeResource(Resource):
    """Like actions on a Product"""

    @api.doc("like_products")
    @api.response(404, "Product not found")
    def post(self, product_id):
        """
        Like a Product

        This endpoint will like a Product
        """
        app.logger.info("Request to like a product")
        product = Product.find(product_id)
        if not product:
            abort(
                status.HTTP_404_NOT_FOUND,
                f"Product with id '{product_id}' was not found.",
            )
        product.like()
        app.logger.info(f"Product {product_id} got a like")
        return {
            "message": "The product got a like successfully",
            "likes": product.likes,
        }, status.HTTP_200_OK


######################################################################
# UTILITY FUNCTIONS
######################################################################


def abort(error_code: int, message: str):
    """Logs errors before aborting"""
    app.logger.error(message)
    api.abort(error_code, message)


def data_reset():
    """Removes all Products from the database"""
    Product.remove_all()
