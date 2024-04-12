Feature: The product store service back-end
As a Product Catalog Owner
I need a RESTful catalog service
So that I can keep track of all my products

# Background: 
#         Given the following products
#         | name        | img_url                 | description         | price | rating |  category |  status  | likes |
#         | hamburger   | http://test/hamburger   | A hamburger         | 5.99  | 4.6    |  food     | DISABLED |   1   |
#         | coke        | http://test/coke        | A coke              | 2.99  | 4.8    |  beverage | DISABLED |   1   |
#         | water       | http://test/water       | A bottle of water   | 3.29  | 4.7    |  beverage | DISABLED |   1   |
#         | apple       | http://test/apple       | An apple            | 1.09  | 4.6    |  fruit    | DISABLED |   1   |

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
    Then I should see the message "Success"