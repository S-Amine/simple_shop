import frappe

no_cache = 1

def get_context(context):
    print("get_context")

    # Check if the user is a guest
    is_guest = frappe.session.user == 'Guest'  # Replace with your guest user's email
    # Set permissions based on the user type


    categories = frappe.db.get_all("Item Group",
                                   fields="*",
                                   filters={'show_in_website': True}
                                   )
    home_categories = frappe.db.get_all("Item Group",
                                        fields="*",
                                        filters={'custom_show_in_home': True})
    recent_items = frappe.db.get_list("Item",
                                      fields="*",
                                      filters={'variant_of': ""}
                                      )
    shop_settings = frappe.get_single("Shop Settings")

    # Assign variables to the context
    context.categories = categories
    context.recent_items = recent_items
    context.home_categories = home_categories
    context.shop_settings = shop_settings
