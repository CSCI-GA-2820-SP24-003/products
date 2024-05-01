Feature: The product store service back-end
   As a Product Catalog Owner
   I need a RESTful catalog service
   So that I can keep track of all my products


Background:
   Given the following products
      | name        | img_url                 | description         | price | rating |  category |  status  | likes |
      | hamburger   | http://test/hamburger   | Delicious food      | 5.99  | 4.6    |  food     |  Active  |   0   |
      | coke        | http://test/coke        | A coke              | 2.99  | 4.8    |  beverage |  Active  |   0   |
      | water       | http://test/water       | A bottle of water   | 3.29  | 4.7    |  beverage |  Active  |   0   |
      | apple       | http://test/apple       | An apple            | 1.09  | 4.6    |  fruit    |  Active  |   0   |


Scenario: The server is running
   When I visit the "Home Page"
   Then I should see "Product" in the title
   And I should not see "404 Not Found"


#####################################################################
#                       Create scenario                             #
#####################################################################
Scenario: Create a Product
   When I visit the "Home Page"
   And I set the "Name" to "Banana"
   And I set the "Img_url" to "http://test/banana"
   And I set the "Description" to "A banana"
   And I set the "Price" to "0.5"
   And I set the "Rating" to "4.2"
   And I set the "Category" to "fruit"
   And I select "Active" in the "Status" dropdown
   And I set the "Likes" to "0"
   And I press the "Create" button
   Then I should see the message "Product has been created!"
   When I copy the "Id" field
   And I press the "Clear" button
   Then the "Id" field should be empty
   And the "Name" field should be empty
   And the "Category" field should be empty
   When I paste the "Id" field
   And I press the "Retrieve" button
   Then I should see the message "Success"
   And I should see "Banana" in the "Name" field
   And I should see "http://test/banana" in the "Img_url" field
   And I should see "A banana" in the "Description" field
   And I should see "0.5" in the "Price" field
   And I should see "4.2" in the "Rating" field
   And I should see "fruit" in the "Category" field
   And I should see "Active" in the "Status" dropdown
   And I should see "0" in the "Likes" field


#####################################################################
#                       List scenario                               #
#####################################################################
Scenario: List all Products
   When I visit the "Home Page"
   And I press the "Search" button
   Then I should see the message "Success"
   And I should see "hamburger" in the results
   And I should see "coke" in the results
   And I should not see "milk" in the results

#####################################################################
#                 Search product by name scenario                   #
#####################################################################
Scenario: Search product by name
   When I visit the "Home Page"
   And I change "Name" to "hamburger"
   And I press the "Search" button
   Then I should see the message "Success"
   And I should see "hamburger" in the results
   And I should not see "coke" in the results
   And I should not see "milk" in the results


#####################################################################
#                       Update scenario                             #
#####################################################################
Scenario: Update a product
   When I visit the "Home Page"
   And I set the "Name" to "hamburger"
   And I press the "Search" button
   Then I should see the message "Success"
   And I should see "hamburger" in the "Name" field
   And I should see "food" in the "Category" field
   When I change "Name" to "fries"
   And I change "Img_url" to "http://test/fries"
   And I press the "Update" button
   Then I should see the message "Product has been updated!"
   When I copy the "Id" field
   And I press the "Clear" button
   And I paste the "Id" field
   And I press the "Retrieve" button
   Then I should see the message "Success"
   And I should see "fries" in the "Name" field
   When I press the "Clear" button
   And I press the "Search" button
   Then I should see the message "Success"
   And I should see "fries" in the results
   And I should not see "hamburger" in the results

Scenario: Update a product without id field
   When I visit the "Home Page"
   And I press the "Update" button
   Then I should see the message "Please provide a valid product ID!"

Scenario: Update a product not exisetd
   When I visit the "Home Page"
   And I press the "Search" button
   And I set the "Id" to "-1"
   And I press the "Update" button
   Then I should see the message "Fail: Product -1 does not exist!"


#####################################################################
#                       Delete scenario                             #
#####################################################################
Scenario: Delete a Product
   When I visit the "Home Page"
   And I press the "Clear" button
   And I set the "Name" to "hamburger"
   And I press the "Search" button
   Then I should see the message "Success"
   And I should see "hamburger" in the results
   When I copy the "Id" field
   And I press the "Clear" button
   And I paste the "Id" field
   And I press the "Delete" button
   Then I should see the message "Product has been deleted!"
   When I press the "Clear" button
   And I set the "Name" to "hamburger"
   And I press the "Search" button
   Then I should see the message "Success"
   And I should not see "hamburger" in the results
   When I press the "Clear" button
   And I set the "Id" to "-1"
   And I press the "Delete" button
   Then I should see the message "Server error!"



