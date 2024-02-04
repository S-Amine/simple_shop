import frappe

no_cache = 1

def get_context(context):
    # collections = frappe.db.get_all("Collection", fields="*")
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
    # context.collections = collections
    context.categories = categories
    context.recent_items = recent_items
    context.home_categories = home_categories
