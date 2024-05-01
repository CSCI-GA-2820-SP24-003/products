"""
Test cases for Product Model
"""

import os
import logging
from unittest import TestCase
from unittest.mock import patch
from wsgi import app
from service.models.models import Product, db, DataValidationError
from tests.factories import ProductFactory

DATABASE_URI = os.getenv(
    "DATABASE_URI", "postgresql+psycopg://postgres:postgres@localhost:5432/testdb"
)


######################################################################
#  Product   M O D E L   T E S T   C A S E S
######################################################################
# pylint: disable=too-many-public-methods
class TestProduct(TestCase):
    """Test Cases for Product Model"""

    @classmethod
    def setUpClass(cls):
        """This runs once before the entire test suite"""
        # pylint: disable=duplicate-code
        app.config["TESTING"] = True
        app.config["DEBUG"] = False
        app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
        app.logger.setLevel(logging.CRITICAL)
        app.app_context().push()

    @classmethod
    def tearDownClass(cls):
        """This runs once after the entire test suite"""
        db.session.close()

    def setUp(self):
        """This runs before each test"""
        db.session.query(Product).delete()  # clean up the last tests
        db.session.commit()

    def tearDown(self):
        """This runs after each test"""
        db.session.remove()

    ######################################################################
    #  T E S T   C A S E S
    ######################################################################

    def test_create_product(self):
        """It should create a product"""
        product = ProductFactory()
        product.create()
        self.assertIsNotNone(product.id)
        found = Product.all()
        self.assertEqual(len(found), 1)
        data = Product.find(product.id)
        self.assertEqual(data.name, product.name)
        self.assertEqual(data.img_url, product.img_url)
        self.assertEqual(data.description, product.description)
        self.assertEqual(data.price, product.price)
        self.assertEqual(data.rating, product.rating)
        self.assertEqual(data.category, product.category)
        self.assertEqual(data.status, product.status)
        self.assertEqual(data.likes, product.likes)

    @patch("service.models.models.db.session.commit")
    def test_create_product_failed(self, exception_mock):
        """It should not create a product on database error"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.create)

    @patch("service.models.models.db.session.commit")
    def test_update_product_failed(self, exception_mock):
        """It should not update a product on database error"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.update)

    @patch("service.models.models.db.session.commit")
    def test_delete_product_failed(self, exception_mock):
        """It should not delete a product on database error"""
        exception_mock.side_effect = Exception()
        product = ProductFactory()
        self.assertRaises(DataValidationError, product.delete)

    def test_read_a_product(self):
        """It should Read a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.id = None
        product.create()
        self.assertIsNotNone(product.id)
        # Fetch it back
        found = Product.find(product.id)
        self.assertEqual(found.id, product.id)
        self.assertEqual(found.name, product.name)
        self.assertEqual(found.img_url, product.img_url)
        self.assertEqual(found.description, product.description)
        self.assertEqual(found.price, product.price)
        self.assertEqual(found.rating, product.rating)
        self.assertEqual(found.category, product.category)
        self.assertEqual(found.status, product.status)
        self.assertEqual(found.likes, product.likes)

    def test_like_a_product(self):
        """It should Like a Product"""
        product = ProductFactory()
        logging.debug(product)
        product.create()
        initial_likes = product.likes
        product.like()
        self.assertEqual(product.likes, initial_likes + 1)

    def test_serialize_a_product(self):
        """It should serialize a Product"""
        product = ProductFactory()
        data = product.serialize()
        self.assertNotEqual(data, None)
        self.assertIn("id", data)
        self.assertEqual(data["id"], product.id)
        self.assertIn("name", data)
        self.assertEqual(data["name"], product.name)
        self.assertIn("img_url", data)
        self.assertEqual(data["img_url"], product.img_url)
        self.assertIn("description", data)
        self.assertEqual(data["description"], product.description)
        self.assertIn("price", data)
        self.assertEqual(data["price"], product.price)
        self.assertIn("rating", data)
        self.assertEqual(data["rating"], product.rating)
        self.assertIn("category", data)
        self.assertEqual(data["category"], product.category)
        self.assertIn("status", data)
        self.assertEqual(data["status"], product.status.name)
        self.assertIn("likes", data)
        self.assertEqual(data["likes"], product.likes)

    def test_deserialize_a_product(self):
        """It should de-serialize a Product"""
        data = ProductFactory().serialize()
        product = Product()
        product.deserialize(data)
        self.assertNotEqual(product, None)
        self.assertEqual(product.id, None)
        self.assertEqual(product.name, data["name"])
        self.assertEqual(product.img_url, data["img_url"])
        self.assertEqual(product.description, data["description"])
        self.assertEqual(product.price, data["price"])
        self.assertEqual(product.rating, data["rating"])
        self.assertEqual(product.category, data["category"])
        self.assertEqual(product.status.name, data["status"])
        self.assertEqual(product.likes, 0 if data["likes"] is None else data["likes"])

    def test_deserialize_missing_data(self):
        """It should not deserialize a Product with missing data"""
        data = {"id": 1, "name": "Kola", "category": "drink", "price": 100}
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_data(self):
        """It should not deserialize bad data"""
        data = "Random Text"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_price(self):
        """It should not deserialize a bad price attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["price"] = "an random string"
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_deserialize_bad_url(self):
        """It should not deserialize a bad img_url attribute"""
        test_product = ProductFactory()
        data = test_product.serialize()
        data["img_url"] = 100  # wrong case
        product = Product()
        self.assertRaises(DataValidationError, product.deserialize, data)

    def test_filter_by_category(self):
        """It should filter products by category"""
        # create some products using the factory
        ProductFactory(category="electronics").create()
        ProductFactory(category="electronics").create()
        ProductFactory(category="clothes").create()

        # filter products by category
        products = Product.filter_by_query(category="electronics")
        self.assertEqual(len(products), 2)

    def test_filter_by_rating(self):
        """It should filter products by rating"""
        # create some products using the factory
        ProductFactory(rating=4.0).create()
        ProductFactory(rating=3.0).create()
        ProductFactory(rating=2.0).create()

        # filter products by rating
        products = Product.filter_by_query(rating="2-4")
        self.assertEqual(len(products), 3)

        products = Product.filter_by_query(rating="4")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].rating, 4.0)

    def test_filter_by_price(self):
        """It should filter products by price"""
        # create some products using the factory
        ProductFactory(price=50.0).create()
        ProductFactory(price=100.0).create()
        ProductFactory(price=200.0).create()

        # filter products by price
        products = Product.filter_by_query(price="0-150")
        self.assertEqual(len(products), 2)

        products = Product.filter_by_query(price="100")
        self.assertEqual(len(products), 1)
        self.assertEqual(products[0].price, 100.0)

    ######################################################################
    #  D A T A   V A L I D A T I O N   T E S T   C A S E S
    ######################################################################

    def test_create_product_with_missing_name(self):
        """It should not create a product with missing name"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.name = None
            product.create()

    def test_create_product_with_invalid_name(self):
        """It should not create a product with name longer than 120 characters"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.name = "t" * 121
            product.create()

    def test_create_product_with_missing_img_url(self):
        """It should not create a product with missing image URL"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.img_url = None
            product.create()

    def test_create_product_with_invalid_img_url(self):
        """It should not create a product with image URL longer than 63 characters"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.img_url = "t" * 121
            product.create()

    def test_create_product_with_invalid_description(self):
        """It should not create a product with description longer than 1024 characters"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.description = "t" * 2049
            product.create()

    def test_create_product_with_missing_price(self):
        """It should not create a product with missing price"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.price = None
            product.create()

    def test_create_product_with_invalid_price_type(self):
        """It should not create a product with invalid price type"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.price = "invalid"
            product.create()

    def test_create_product_with_negative_price(self):
        """It should not create a product with negative price"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.price = -1
            product.create()

    def test_create_product_with_invalid_rating_type(self):
        """It should not create a product with invalid rating type"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.rating = "invalid"
            product.create()

    def test_create_product_with_invalid_rating_range(self):
        """It should not create a product with rating out of range"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.rating = 10
            product.create()

    def test_create_product_with_invalid_category(self):
        """It should not create a product with category longer than 63 characters"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.category = "t" * 121
            product.create()

    def test_create_product_with_invalid_status(self):
        """It should not create a product with invalid status"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.status = "invalid"
            product.create()

    def test_create_product_with_invalid_likes_type(self):
        """It should not create a product with invalid likes type"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.likes = "invalid"
            product.create()

    def test_create_product_with_negative_likes(self):
        """It should not create a product with negative likes"""
        product = ProductFactory()
        with self.assertRaises(DataValidationError):
            product.likes = -1
            product.create()
