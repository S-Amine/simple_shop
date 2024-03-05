
import frappe
def get_context(context):


    shop_settings = frappe.get_single("Shop Settings")
    context.shop_settings=shop_settings
