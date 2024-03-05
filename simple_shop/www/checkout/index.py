import frappe
from frappe.model.mapper import get_mapped_doc


def get_context(context):
    # Check if it's a POST request
    categories = frappe.db.get_all("Item Group",
                                  fields="*",
                                  filters={'show_in_website': True}
                                  )
    context.categories = categories
    shop_settings = frappe.get_single("Shop Settings")
    context.shop_settings=shop_settings
    if frappe.request.method == "POST":
        # Get the post request data
        post_data = frappe.local.form_dict

        # Create a new Sales Order document using the post request data
        new_sales_order = frappe.new_doc("Sales Order")
        new_sales_order.update({
            "customer": post_data.get("customer"),
            "delivery_date": post_data.get("date")
        })

        # Add items to the Sales Order using item_code and qty from the post data
        item_code = post_data.get("item_code")
        qty = post_data.get("qty")

        if item_code and qty:
            new_sales_order.append("items", {
                "item_code": item_code,
                "qty": qty,
                "delivery_warehouse": "Goods In Transit - TD"
                # Add more item fields as needed based on your requirements
            })

        # Save the new Sales Orderfrappe.csrf_token()
        new_sales_order.insert()

        # You can print the new Sales Order name for verification
        print(f"New Sales Order created: {new_sales_order.name}")
        # Redirect to the new Sales Order document
        example_path = f"/api/method/frappe.utils.print_format.download_pdf?doctype=Sales%20Order&name={new_sales_order.name}&format=Standard&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
        frappe.local.flags.redirect_location = example_path
        raise frappe.Redirect
    else :
      pass
        # Add other context data or processing as needed
        # ...
