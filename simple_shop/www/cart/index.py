import frappe

no_cache = 1

def get_context(context):
    # collections = frappe.db.get_all("Collection", fields="*")
    categories = frappe.db.get_all("Item Group",
                                  fields="*",
                                  filters={
                                  'show_in_website': True
                                  }
                                  )
    recent_items = frappe.db.get_list("Item",
                                      fields="*"
                                      )
    # context.collections = collections
    context.categories = categories
    context.recent_items = recent_items
    shop_settings = frappe.get_single("Shop Settings")
    context.shop_settings=shop_settings