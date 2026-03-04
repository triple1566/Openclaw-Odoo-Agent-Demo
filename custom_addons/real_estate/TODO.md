Le, implement related Practice Assignment Tasks too.
https://www.odoo.com/documentation/17.0/developer/tutorials/server_framework_101.html



Real Estate Custom Module Practice Assignment Tasks

Task 1 (Computed Field): Add a new field price_per_sqm (Float). It should be calculated as expected_price / total_area.

Task 2 (Onchange): If the number of bedrooms is more than ≥ 5, automatically set the description to "Luxury Mansion".

Task 1 (Inherit) : Inherit the Users model (res.users) and add a field called agent_license_code (Char). Then, make sure this field appears in the user's settings form.

Task 1 (Buttons): Add a button called "Set to New" that only appears when the property is Canceled. This button should change the state back to New.

Task 2 (Decoration): In the Tree (List) View, make the rows change color based on the state.

    Sold = Green
    Canceled = Red (Hint: Use decoration-success="state == 'sold'" and decoration-danger="state == 'canceled'" on the <tree> tag).

 

Task 1 (QWeb Report): Add a table to the report that lists all Offers received for the property (if you have an offer model). If not, add the Salesperson's Name and Buyer's Name in a professional "Agent Information" box at the bottom.

Task 2 (Conditional Formatting): Use t-if to show a red "SOLD" stamp on the PDF only if the property state is sold.

    (Hint: <div t-if="o.state == 'sold'" style="color: red;">SOLD</div>)

Wizard Task 1: create a pop-up window to ask the user for more info before selling a property

Wizard Task 2:

Create a Wizard to Bulk Update the "Expected Price" for multiple properties at once.

    Select multiple properties in the Tree View.
    Click an "Action" menu button to open a Wizard.
    Enter a percentage (e.g., 10%).
    The Wizard should increase the price of all selected properties by 10%.

Task 1 (Cron): Create a cron job that runs every hour to count how many "Offer Received" properties exist and log it in the server console using _logger.info().

Task 2 (Notification): When a property's price is changed by more than 10%, automatically post a "Internal Note" in the Chatter saying "Large price drop detected!"