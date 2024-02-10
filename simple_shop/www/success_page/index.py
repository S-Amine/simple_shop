import frappe
from frappe.model.document import get_doc
def get_context(context):
    # Get the order_id from the form data
    order_id = frappe.local.form_dict.get('id')
    order = get_doc("Wooliz Order", order_id)

    # Calculate order total using lambda function and sum
    calculate_item_total = lambda item: item.unit_price * item.qty
    order_items = order.get_all_children()
    order_total = sum(map(calculate_item_total, order_items))

    # Add the order and order_total to the context
    context.order = order
    context.order_total = order_total