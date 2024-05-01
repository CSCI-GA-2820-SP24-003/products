"""
TestProduct API Service Test Suite
"""

import os
import logging
from unittest import TestCase
from urllib.parse import quote_plus
from wsgi import app
from service.common import status
from service.models.models import db, Product, Status
from tests.factories import ProductFactory


DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)
BASE_URL = "/api/products"


######################################################################
#  T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProductService(TestCase):
    """REST API Server Tests"""

    @classmethod
    def setUpClass(cls):
        """Run once before all tests"""
        # pylint: disable=duplicate-code
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        # Set up the test database
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """Run once after all tests"""
        db.session.close()

    def setUp(self):
        """Runs before each test"""
        self.client = app.test_client()
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    def _create_products(self, count):
        """Factory method to create products in bulk"""
        products = []
        for _ in range(count):
            test_product = ProductFactory()
            response = self.client.post(BASE_URL, json=test_product.serialize())
            self.assertEqual(
                response.status_code,
                status.HTTP_201_CREATED,
                "Could not create test product",
            )
            new_product = response.get_json()
            test_product.id = new_product["id"]
            products.append(test_product)
        return products

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_health(self):
        """It should get the health endpoint"""
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(data["status"], "OK")

    def test_index(self):
        """It should call the home page"""
        resp = self.client.get("/")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

    def assert_is_product(self, product):
        """Assert that a product has all the correct attributes"""
        self.assertIn("id", product)
        self.assertIsInstance(product["id"], int)
        self.assertIn("name", product)
        self.assertIsInstance(product["name"], str)
        self.assertIn("img_url", product)
        self.assertIsInstance(product["img_url"], str)
        self.assertIn("description", product)
        self.assertIsInstance(product["description"], str)
        self.assertIn("price", product)
        self.assertIsInstance(product["price"], float)
        self.assertIn("rating", product)
        self.assertIsInstance(product["rating"], float)
        self.assertIn("category", product)
        self.assertIsInstance(product["category"], str)
        self.assertIn("status", product)
        self.assertIsInstance(product["status"], str)
        self.assertIn(product["status"], [s.name for s in Status])
        self.assertIn("likes", product)
        self.assertIsInstance(product["likes"], int)

    def assert_two_products_are_the_same(self, product1, product2):
        """Assert that two products are the same"""
        self.assertEqual(product1["name"], product2.name)
        self.assertEqual(product1["price"], product2.price)
        self.assertEqual(product1["description"], product2.description)
        self.assertEqual(product1["status"], product2.status.name)
        self.assertEqual(product1["img_url"], product2.img_url)
        self.assertEqual(product1["rating"], product2.rating)
        self.assertEqual(product1["category"], product2.category)

    def test_create_product(self):
        """It should Create a new Product"""

        test_product = ProductFactory()
        logging.debug("Test Product: %s", test_product.serialize())
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Make sure location header is set
        location = response.headers.get("Location", None)
        self.assertIsNotNone(location)

        # Check the data is correct
        new_product = response.get_json()
        self.assert_is_product(new_product)
        self.assert_two_products_are_the_same(new_product, test_product)

        # Check that the location header was correct
        response = self.client.get(location)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_products(self):
        """It should Get a list of Products"""
        self._create_products(3)
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # validate the response
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 3)
        for product in data:
            self.assert_is_product(product)

    def test_list_products_empty(self):
        """It should Get an empty list of Products"""
        response = self.client.get(BASE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        # validate the response
        self.assertIsInstance(data, list)
        # validate the products
        self.assertEqual(len(data), 0)

    def test_read_product(self):
        """It should Get a single Product"""
        # get the id of a product
        test_product = self._create_products(1)[0]
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assert_is_product(data)
        self.assert_two_products_are_the_same(data, test_product)

    def test_read_product_not_found(self):
        """It should not Get a Product thats not found"""
        response = self.client.get(f"{BASE_URL}/0")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn("was not found", data["message"])

    def test_delete_product(self):
        """It should Delete a Product"""
        test_product = self._create_products(1)[0]
        response = self.client.delete(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(len(response.data), 0)
        # make sure they are deleted
        response = self.client.get(f"{BASE_URL}/{test_product.id}")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_nonexist_product(self):
        """It should return a HTTP 204 message"""
        response = self.client.delete(f"{BASE_URL}/10000000")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        logging.debug("not found")

    def test_update_product(self):
        """It should Update an existing Product"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = response.get_json()
        logging.debug(new_product)
        new_product["category"] = "unknown"
        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_product = response.get_json()
        self.assertEqual(updated_product["category"], "unknown")

    def test_update_product_with_invalid_data(self):
        """It should not update as product as the data is invalid"""
        # create a product to update
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # update the product
        new_product = response.get_json()
        logging.debug(new_product)
        new_product["category"] = "unknown" * 100
        response = self.client.put(f"{BASE_URL}/{new_product['id']}", json=new_product)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        updated_product = response.get_json()
        self.assertIn("at most 120", updated_product["message"])

    def test_update_nonexisting_product(self):
        """It should return a HTTP 404 message"""
        response = self.client.put(f"{BASE_URL}/10000000")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        logging.debug("not found")

    def test_query_by_category(self):
        """It should query products by category"""
        products = self._create_products(5)
        test_category = products[0].category
        category_count = len(
            [product for product in products if product.category == test_category]
        )
        resp = self.client.get(
            BASE_URL, query_string=f"category={quote_plus(test_category)}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), category_count)
        # check the data just to be sure
        for product in data:
            self.assertEqual(product["category"], test_category)

    def test_query_by_name(self):
        """It should query products by name"""
        products = self._create_products(5)
        test_name = products[0].name
        name_count = len([product for product in products if product.name == test_name])
        resp = self.client.get(BASE_URL, query_string=f"name={quote_plus(test_name)}")
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), name_count)
        for product in data:
            self.assertEqual(product["name"], test_name)

    def test_query_by_price(self):
        """It should query products by price"""
        products = self._create_products(5)
        test_price = products[0].price
        price_count = len(
            [product for product in products if product.price == test_price]
        )
        resp = self.client.get(
            BASE_URL, query_string=f"price={quote_plus(str(test_price))}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), price_count)
        for product in data:
            self.assertEqual(product["price"], test_price)

    def test_query_by_rating(self):
        """It should query products by rating"""
        products = self._create_products(5)
        test_rating = products[0].rating
        rating_count = len(
            [product for product in products if product.rating == test_rating]
        )
        resp = self.client.get(
            BASE_URL, query_string=f"rating={quote_plus(str(test_rating))}"
        )
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = resp.get_json()
        self.assertEqual(len(data), rating_count)
        for product in data:
            self.assertEqual(product["rating"], test_rating)

    def test_like_product(self):
        """It should increment the likes count of a product"""
        # create a product to like
        test_product = ProductFactory()
        response = self.client.post(BASE_URL, json=test_product.serialize())
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Like a product
        new_product = response.get_json()
        logging.debug(new_product)
        new_product_id = new_product["id"]

        like_response = self.client.post(f"{BASE_URL}/{new_product_id}/like")
        self.assertEqual(like_response.status_code, status.HTTP_200_OK)

        # Verify the like
        response = self.client.get(f"{BASE_URL}/{new_product_id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.get_json()
        self.assertEqual(
            data["likes"],
            1,
            "The likes count should be incremented",
        )

    def test_like_product_not_found(self):
        """It should return a HTTP 404 Not Found for a product that doesn't exist"""
        response = self.client.post(f"{BASE_URL}/0/like")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.get_json()
        logging.debug("Response data = %s", data)
        self.assertIn(" was not found", data["message"])

    def test_bad_request(self):
        """It should not create when sending the wrong data"""
        resp = self.client.post(BASE_URL, json={})
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unsupported_media_type(self):
        """It should not Create when sending wrong media type"""
        product = ProductFactory()
        resp = self.client.post(
            BASE_URL, json=product.serialize(), content_type="test/html"
        )
        self.assertEqual(resp.status_code, status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

    def test_method_not_allowed(self):
        """It should not allow an illegal method call"""
        resp = self.client.put(BASE_URL, json={})
        self.assertEqual(resp.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
