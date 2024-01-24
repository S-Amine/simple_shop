import frappe

def get_context(context):
    item_code = frappe.local.form_dict.get('item_code') or frappe.local.form_dict.get('item_code')
    if item_code:
        item = frappe.get_doc('Item', item_code)
        context.item = item
    else:
        frappe.local.flags.redirect_location = '/'
        raise frappe.Redirect
