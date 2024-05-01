"""
Models for Product

All of the models are stored in this module
@see https://github.com/CSCI-GA-2820-SP24-003/products/issues/22
@see https://www.youtube.com/watch?v=k8-Aw-_xZR8
@see https://github.com/nyu-devops/lab-flask-tdd/blob/master/service/models.py

Models
------
Product - A Product sold in a Store

Attributes:
-----------
id (integer) - the unique identifier for a product
name (string, required) - the name of the product
img_url (string, required) - the image url of the product
description (string) - the description of the product
price (float, required) - the price of the product, in dollars (e.g. 9.99)
rating (float, required, default=0.0) - the rating of the product (e.g. 4.5)
category (string) - the category of the product (e.g. "clothes")
status (enum, required, default="active") - the status of the product (i.e. "active" or "disabled")
"""

import logging
from enum import Enum
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import validates

logger = logging.getLogger("flask.app")

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()


class DataValidationError(Exception):
    """Used for an data validation errors when deserializing or validating data fields"""


class Status(Enum):
    """Enumeration of the status of a Product"""

    ACTIVE = 0
    DISABLED = 1


class Product(db.Model):
    # pylint: disable=too-many-instance-attributes
    """
    Class that represents a Product
    """

    ##################################################
    # Table Schema
    ##################################################
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(63), nullable=False)
    img_url = db.Column(db.String(63), nullable=False)
    description = db.Column(db.String(1024))
    price = db.Column(db.Float(), nullable=False)
    rating = db.Column(db.Float(), nullable=False, server_default="0.0")
    category = db.Column(db.String(63))
    status = db.Column(
        db.Enum(Status), nullable=False, server_default=(Status.ACTIVE.name)
    )
    likes = db.Column(db.Integer, nullable=False, default=0)

    def __repr__(self):
        return f"<Product {self.name} id=[{self.id}]>"

    def create(self):
        """
        Creates a Product to the database
        """
        logger.info("Creating %s", self.name)
        self.id = None  # pylint: disable=invalid-name
        try:
            db.session.add(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error creating record: %s", self)
            raise DataValidationError(e) from e

    def update(self):
        """
        Updates a Product to the database
        """
        logger.info("Saving %s", self.name)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error updating record: %s", self)
            raise DataValidationError(e) from e

    def delete(self):
        """Removes a Product from the data store"""
        logger.info("Deleting %s", self.name)
        try:
            db.session.delete(self)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error deleting record: %s", self)
            raise DataValidationError(e) from e

    def like(self):
        """
        Increases the like count for a product
        """
        logger.info("Adding like to %s", self.name)
        self.likes += 1
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            logger.error("Error adding like to product: %s", self)
            raise DataValidationError(e) from e

    def serialize(self):
        """Serializes a Product into a dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "img_url": self.img_url,
            "description": self.description,
            "price": self.price,
            "rating": self.rating,
            "category": self.category,
            "status": self.status.name,
            "likes": self.likes,
        }

    def deserialize(self, data):
        """
        Deserializes a Product from a dictionary

        Args:
            data (dict): A dictionary containing the resource data
        """
        try:
            self.name = data["name"]
            if isinstance(data["img_url"], str):
                self.img_url = data["img_url"]
            else:
                raise DataValidationError(
                    "Invalid type for str [img_url]: " + str(type(data["img_url"]))
                )
            self.description = data.get("description")
            if isinstance(data["price"], (float, int)):
                self.price = float(data["price"])
            else:
                raise DataValidationError(
                    "Invalid type for float [price]: " + str(type(data["price"]))
                )

            self.rating = data.get("rating", 0.0)
            self.category = data.get("category")
            self.status = Status[data.get("status", "active").upper()]
            try:
                self.likes = int(data.get(["likes"], 0))
            except ValueError:
                self.likes = 0
        except AttributeError as error:
            raise DataValidationError("Invalid attribute: " + error.args[0]) from error
        except KeyError as error:
            raise DataValidationError(
                "Invalid Product: missing " + error.args[0]
            ) from error
        except TypeError as error:
            raise DataValidationError(
                "Invalid Product: body of request contained bad or no data "
                + str(error)
            ) from error
        return self

    ##################################################
    # CLASS METHODS
    ##################################################

    @classmethod
    def all(cls):
        """Returns all of the Products in the database"""
        logger.info("Processing all Products")
        return cls.query.all()

    @classmethod
    def find(cls, by_id):
        """Finds a Product by it's ID"""
        logger.info("Processing lookup for id %s ...", by_id)
        return cls.query.get(by_id)

    @classmethod
    def filter_by_query(cls, **query):
        """Find all products that match the given query parameters"""
        logger.info("Processing query: %s", query)
        query_obj = cls.query
        for key, value in query.items():
            if key == "category":
                query_obj = query_obj.filter(cls.category.ilike(f"%{value}%"))
            elif key == "rating":
                # Handle rating range queries
                if "-" in value:
                    min_rating, max_rating = map(float, value.split("-"))
                    query_obj = query_obj.filter(
                        cls.rating.between(min_rating, max_rating)
                    )
                else:
                    query_obj = query_obj.filter(cls.rating == float(value))
            elif key == "price":
                # Handle price range queries
                if "-" in value:
                    min_price, max_price = map(float, value.split("-"))
                    query_obj = query_obj.filter(
                        cls.price.between(min_price, max_price)
                    )
                else:
                    query_obj = query_obj.filter(cls.price == float(value))
        return query_obj.all()

    ##################################################
    # DATA VALIDATIONS
    ##################################################

    # pylint: disable=unused-argument

    @validates("name")
    def validate_name(self, key, name):
        """Validates the Name field in model to have maximum of 120 characters"""
        if not name:
            raise DataValidationError("Name is required")
        if len(name) > 120:
            raise DataValidationError("Name must be at most 120 characters")
        return name

    @validates("img_url")
    def validate_img_url(self, key, img_url):
        """Validates the Image Url field in model to have maximum of 120 characters"""
        if not img_url:
            raise DataValidationError("Image URL is required")
        if len(img_url) > 120:
            raise DataValidationError("Image URL must be at most 120 characters")
        return img_url

    @validates("description")
    def validate_description(self, key, description):
        """Validates the Description field in model to have maximum of 2048 characters"""
        if description and len(description) > 2048:
            raise DataValidationError("Description must be at most 2048 characters")
        return description

    @validates("price")
    def validate_price(self, key, price):
        """Validates the Price field in model to be not None, non-negative and be float or int type value"""
        if price is None:
            raise DataValidationError("Price is required")
        if not isinstance(price, (float, int)):
            raise DataValidationError("Price must be a float or integer")
        if price < 0:
            raise DataValidationError("Price must be non-negative")
        return price

    @validates("rating")
    def validate_rating(self, key, rating):
        """Validates the rating field in model to be a float or int value and be in the 0.0 to 9.9 range"""
        if not isinstance(rating, (float, int)):
            raise DataValidationError("Rating must be a float or integer")
        if rating < 0.0 or rating > 9.9:
            raise DataValidationError("Rating must be between 0 and 5")
        return rating

    @validates("category")
    def validate_category(self, key, category):
        """Validates the Category field in model to have maximum of 120 characters"""
        if category and len(category) > 120:
            raise DataValidationError("Category must be at most 120 characters")
        return category

    @validates("status")
    def validate_status(self, key, status):
        """Validates the status field"""
        if status is None:
            raise DataValidationError("Status is required")
        if not isinstance(status, Status):
            raise DataValidationError("Invalid status value")
        return status

    @validates("likes")
    def validate_likes(self, key, likes):
        """Validates the likes field in model to be non negative and be a integer"""
        if not isinstance(likes, int):
            raise DataValidationError("Likes must be an integer")
        if likes < 0:
            raise DataValidationError("Likes must be non-negative")
        return likes
