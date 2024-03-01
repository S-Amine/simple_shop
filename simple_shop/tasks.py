import frappe
import time
def update_item_stocks(item_code):
    time.sleep(0.1)
    stock_settings = frappe.get_doc("Shop Settings")
    default_warehouse = stock_settings.default_warehouse
    item_doc = frappe.get_doc("Item", item_code)
    item_doc.db_set('custom_qty', 0, commit=True)
    item_doc.save(
        ignore_permissions=True, # ignore write permissions during insert
    )