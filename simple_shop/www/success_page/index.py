import frappe
from frappe.model.document import get_doc
from simple_shop.yalidine import get_order_total_price
def get_context(context):
    order_id = frappe.local.form_dict.get('id')
    order = get_doc("Wooliz Order", order_id)
    # Get the order_id from the form data
    order_total=get_order_total_price(order_id)

    # Add the order and order_total to the context
    context.order = order
    context.order_total = order_total
