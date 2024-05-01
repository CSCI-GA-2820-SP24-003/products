# NYU DevOps Product Squad

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Language-Python-blue.svg)](https://python.org/)
[![CI Build](https://github.com/CSCI-GA-2820-SP24-003/products/actions/workflows/ci.yml/badge.svg)](https://github.com/CSCI-GA-2820-SP24-003/products/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/CSCI-GA-2820-SP24-003/products/graph/badge.svg?token=8ULJTQ5HXX)](https://codecov.io/gh/CSCI-GA-2820-SP24-003/products)

This repository contains the code for the NYU DevOps Product Squad project. This service handles product operations on a an e-commerce website.

## Overview

The product service is a Python Flask application that provides a RESTful API for managing products in an e-commerce website. It is part of a microservices architecture and is designed to be deployed in a containerized environment.

The `/service` folder contains our `models.py` file for our model and a `routes.py` file for our service. The `/tests` folder has test case starter code for testing the model and the service separately.

## How to get started

### Reset database/model

```bash
flask db-create
```

### Run the app

```bash
flask run
```

### Run the tests

```bash
make test
```

### Run linter

```bash
make lint
```

### Run bdd

```bash
behave
```

# Database Schema

The product service uses a SQLite database to store product data. The database schema is defined in the `models.py` module. The schema consists of a single table called `products` with the following columns:

| Column    | Type    | Description               | Constraints               |
|-----------|---------|---------------------------|---------------------------|
| id        | Integer | Unique product identifier | Primary key, autoincrement|
| name      | String  | Product name              | Not null                  |
| img_url   | String  | Product image URL         | Not null                  |
| description| String  | Product description       |                           |
| price     | Float   | Product price             | Not null                  |
| rating    | Integer | Product rating            | Not null, default=0        |
| category  | String  | Product category          |                           |
| status    | Enum    | Product status            | Not null, default="active"|

## Constraints and Validations

- **id**: Must be an integer greater than 0.
- **name**: Must be a non-empty string.
- **img_url**: Must be a non-empty string.
- **description**: Can be an empty string.
- **price**: Must be a float representing the price in dollars.
- **rating**: Must be an integer representing the rating, default is 0.
- **category**: Must be a string representing the category.
- **status**: Must be one of the predefined values in the Status enum, default is "active".

# API Endpoints

Overview of the API endpoints for the product service:

1. [Root URL](#root-url) - The root URL for the service
2. [Product Endpoints](#product-endpoints) - Endpoints for managing products
    1. Create a new product
    2. Get a list of all products
    3. Delete a product
3. [Error Handling](#error-handling) - How the service handles HTTP errors

## Root URL

The root URL for the service is `/products`. All routes are relative to this URL.

## Product Endpoints

The service provides the following endpoints for managing products:

| Method | URI              | Description                         |
|--------|------------------|-------------------------------------|
| GET    | /products        | Retrieves a list of all products    |
| GET    | /products/<id>   | Retrieves a single product by its ID|
| POST   | /products        | Creates a new product               |
| PUT    | /products/<id>   | Updates a product by its ID         |
| DELETE | /products/<id>   | Deletes a product by its ID         |

## Usage

- **Create Product**

```http
POST /products
```

URL - `localhost:8000/products`

Request Body:

```json
{
    "name": "Product Name",
    "img_url": "https://example.com/image.jpg",
    "description": "Product description",
    "price": 9.99,
    "category": "Category",
    "status": "active"
}
```

Request Response: 201 Created

```json
{
    "id": 1,
    "name": "Product Name",
    "img_url": "https://example.com/image.jpg",
    "description": "Product description",
    "price": 9.99,
    "rating": 0,
    "category": "Category",
    "status": "active"
}
```

- **Get All Products**

```http
GET /products
```

URL - `localhost:8000/products`

Request Response: 200 OK

```json
[
    {
        "id": 1,
        "name": "Product Name",
        "img_url": "https://example.com/image.jpg",
        "description": "Product description",
        "price": 9.99,
        "rating": 0,
        "category": "Category",
        "status": "active"
    },
        {
        "id": 2,
        "name": "Product Name 2 ",
        "img_url": "https://example.com/image2.jpg",
        "description": "Product description2",
        "price": 14.26,
        "rating": 0,
        "category": "Category",
        "status": "disabled"
    }
]
```

- **Get Product by ID**

```http
GET /products/<product_id>
```

URL - `localhost:8000/products/<product_id>`

Request Response: 200 OK

```json
{
    "id": "<product_id>",
    "name": "Product Name",
    "img_url": "https://example.com/image.jpg",
    "description": "Product description",
    "price": 9.99,
    "rating": 0,
    "category": "Category",
    "status": "active"
}
```

- **Update Product**

```http
PUT /products/<product_id>
```

URL - `localhost:8000/products/<product_id>`

Request Body:

```json
{
    "name": "New Product Name",
    "img_url": "https://example.com/new-image.jpg",
    "description": "New product description",
    "price": 19.99,
    "category": "New Category",
    "status": "inactive"
}
```

Request Response: 200 OK

```json
{
    "id": 1,
    "name": "New Product Name",
    "img_url": "https://example.com/new-image.jpg",
    "description": "New product description",
    "price": 19.99,
    "rating": 0,
    "category": "New Category",
    "status": "inactive"
}
```

- **Delete Product**

```http
DELETE /products/<product_id>
```

URL - `localhost:8000/products/<product_id>`

Request Response: 204 No Content

## Error Handling

The service uses the `@app.errorhandler` decorator to handle HTTP errors. The `common/error_handlers.py` module contains the error handling code. The `common/status.py` module contains the HTTP status constants.

## Deploying to local Kubernetes Cluster
- In order to create the cluster run
  ```
  make cluster
  ```
- To delete a cluster run
  ```
  make cluster-rm
  ```
- After creating a cluster, to build the docker image run
  ```
  docker build -t prod:1.0 .
  ```
-  Then tag the docker image to cluster-registry using
   ```
   docker tag prod:1.0 cluster-registry:32000/prod:1.0
   ```
- Later Push the docker image to the cluster registry
  ```
  docker push cluster-registry:32000/prod:1.0
  ```
- Then run the following commands to setup the deployment, postgresql server and the persistent volume.
  ```
  kubectl apply -f k8s/pv.yaml
  kubectl apply -f k8s/postgreql.yaml
  kubectl apply -f k8s/deployment.yaml
  kubectl apply -f k8s/service.yaml
  kubectl apply -f k8s/ingress.yaml
  ```
- The app should not be running and would be accesable at `localhost:8080`, in order to check the status of the services,pods,ingress run:
  ```
  kc get all
  ```
- To check the logs of a specific container/service run:
   ```
   kc logs <service-name>
   ```
- To delete the service, ingress and deployment run:
  ```
  kc delete deploy,svc,ing <service-name>
  ```



# Repository Structure

Our project repository and its files possess the following structure:

```text
.gitignore          - this will ignore vagrant and other metadata files
.flaskenv           - Environment variables to configure Flask
.gitattributes      - File to gix Windows CRLF issues
.devcontainers/     - Folder with support for VSCode Remote Containers
dot-env-example     - copy to .env to use environment variables
pyproject.toml      - Poetry list of Python libraries required by your code

service/                   - service python package
├── __init__.py            - package initializer
├── config.py              - configuration parameters
├── models.py              - module with business models
├── routes.py              - module with service routes
└── common                 - common code package
    ├── cli_commands.py    - Flask command to recreate all tables
    ├── error_handlers.py  - HTTP error handling code
    ├── log_handlers.py    - logging setup code
    └── status.py          - HTTP status constants

tests/                     - test cases package
├── __init__.py            - package initializer
├── test_cli_commands.py   - test suite for the CLI
├── test_models.py         - test suite for business models
└── test_routes.py         - test suite for service routes
```

## License

Copyright (c) 2016, 2024 [John Rofrano](https://www.linkedin.com/in/JohnRofrano/). All rights reserved.

Licensed under the Apache License. See [LICENSE](LICENSE)

This repository is part of the New York University (NYU) masters class: **CSCI-GA.2820-001 DevOps and Agile Methodologies** created and taught by [John Rofrano](https://cs.nyu.edu/~rofrano/), Adjunct Instructor, NYU Courant Institute, Graduate Division, Computer Science, and NYU Stern School of Business.
