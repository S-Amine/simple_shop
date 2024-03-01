from collections import OrderedDict
import hashlib
import hmac
import json
import re
import frappe
from frappe.model.document import get_doc
import requests
from frappe import _


def get_order_total_price(order_id):
    """
    Returns the total price with the shipping fees
    """
    order = get_doc("Wooliz Order", order_id)
    # Calculate order total using lambda function and sum
    calculate_item_total = lambda item: item.unit_price * item.qty
    order_items = order.get_all_children()
    order_total = sum(map(calculate_item_total, order_items))
    # add shipping charges
    ...
    return order_total

def get_product_list(order_id):
    """
    function for get product list
    """
    product_list = []
    order_obj = get_doc("Wooliz Order",order_id)
    orders_items = order_obj.get_all_children()
    for item in orders_items:
        product = get_doc('Item', item)
        product_list.append(f'{product.item_name} X {item.qty}')
    return product_list

def get_yalidine_order(order_id):
    settings = frappe.get_single("Yalidin")
    order_obj = get_doc("Wooliz Order",order_id)
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    url = f"{settings.base_url}parcels/{order_obj.custom_tracking_id}"
    response=requests.get(url=url,headers=headers)
    my_response=response.json()
    return my_response
def send_yalidin_order(order_id):
    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    url = settings.base_url+"parcels/"
    order_obj = get_doc("Wooliz Order",order_id)
    get_cart_total=get_order_total_price(order_id)
    product_list=get_product_list(order_id)
    print(extract_alpha_chars(order_obj.wilaya))
    data = OrderedDict(
        [(0,
            OrderedDict(
            [("order_id", order_obj.name), 
            ("firstname", order_obj.last_name),
            ("familyname", order_obj.last_name),
            ("contact_phone",  order_obj.phone),
            ("address", order_obj.custom_address if order_obj.custom_address is not None else order_obj.commun + order_obj.wilaya),
            ("to_commune_name", order_obj.commun),
            ("to_wilaya_name", extract_alpha_chars(order_obj.wilaya)),
            ("product_list", str(product_list)),
            ("price", int(get_cart_total)),
            ("freeshipping", False), 
            ("is_stopdesk", order_obj.custom_stop_desk_bureau), 
            ("has_exchange", False),
            ("product_to_collect", str(product_list) if product_list else "product_to_collect does not exist" )])),])
    response = requests.post(url=url, headers=headers, data=json.dumps((data)))
    my_response=response.json()

    return my_response

def delete_yalidine_order(tracking_id):
    """Delete order"""
    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    url = f"{settings.base_url}parcels/{tracking_id}"
    response = requests.delete(url=url, headers=headers)
    return response

def update_yalidine_order(order_id):
    """Update the order"""
    settings = frappe.get_single("Yalidin")
    order_obj = get_doc("Wooliz Order",order_id)
    product_list=get_product_list(order_id)
    get_cart_total=get_order_total_price(order_id)
    tracking_id=order_obj.custom_tracking_id
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    url = f"{settings.base_url}parcels/{tracking_id}"
    data = OrderedDict([
        ("order_id", order_obj.name),
        ("firstname", order_obj.last_name),  # Assuming you meant 'first_name'
        ("familyname", order_obj.last_name),
        ("contact_phone", order_obj.phone),
        ("address", order_obj.custom_address if order_obj.custom_address is not None else order_obj.commun + order_obj.wilaya),
        ("to_commune_name", order_obj.commun),
        ("to_wilaya_name", extract_alpha_chars(order_obj.wilaya)),
        ("product_list", str(product_list)),
        ("price", int(get_cart_total)),
        ("freeshipping", False),
        ("do_insurance", 1) if order_obj.custom_insurance else ("do_insurance",0), 
        ("is_stopdesk", 1) if order_obj.custom_stop_desk_bureau else ("is_stopdesk",0),
        ("stopdesk_id", order_obj.custom_center_id) if order_obj.custom_stop_desk_bureau is not None else ("stopdesk_id", None),  # Assuming 'None' if condition is not met
        ("has_exchange", 1 ) if order_obj.custom_has_exchange else  ("has_exchange", 0 ) ,
        ("product_to_collect", str(product_list) if product_list else "product_to_collect does not exist")
    ])

    requests.patch(url=url, headers=headers, data=json.dumps((data)))
                   

def extract_alpha_chars(input_string):
    # Remove numbers from the string
    result_string = ''.join(char for char in input_string if not char.isdigit())

    # Remove the first whitespace
    result_string = result_string.lstrip()

    return result_string

def extract_first_number(input_string):
    # Using regular expression to find the first number
    match = re.search(r'\d+', input_string)
    
    # Check if a match is found
    if match:
        return int(match.group())
    else:
        return None  


def verify_signature(secret_key, payload, received_signature):
    # Compute the verification hash using the hmac module
    computed_signature = hmac.new(
        key=secret_key.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    # Compare the received signature with the computed verification hash
    return received_signature == computed_signature


@frappe.whitelist(allow_guest=True)

def yalidine_webhook(**args):
    # Get the webhook secret key from your site's configuration
    settings = frappe.get_single("Yalidin")
    webhook_secret_key = settings.webhook

    # Get the payload and signature from the request
    payload = frappe._dict(args)
    print(payload)
    yalidine_signature = frappe.get_request_header("HTTP_X_YALIDINE_SIGNATURE")
    # Verify if the signature is present in the headers
    if not yalidine_signature:
        return _("Missing X-YALIDINE-SIGNATURE in the headers")

    # Compare the received signature with the computed verification hash
    if not verify_signature(secret_key=webhook_secret_key, payload=payload, received_signature=yalidine_signature):
        frappe.throw(_("Invalid X-YALIDINE-SIGNATURE"), title="Webhook Error")

    # If the signatures match, process the payload
    process_webhook_payload(payload)

    return _("Webhook processed successfully")


def process_webhook_payload(payload):
    """
    `YALIDINE` webhook for receiving real-time updates
    """
    event_type = payload['type']
    events = payload['events']
    if event_type == "parcel_status_updated":
        for event in events:
            tracking = event['data']['tracking']
            status = event['data']['status']

            order = frappe.get_doc("Wooliz Order", {"custom_tracking_id": tracking})
            order.status=status
            order.save()

