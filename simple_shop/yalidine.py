from collections import OrderedDict
import json
import re
import frappe
from frappe.model.document import get_doc
import requests


def get_order_total_price(order_id):
    """
    Returns the total price with the shipping fees
    """
    order = get_doc("Wooliz Order", order_id)
    # Calculate order total using lambda function and sum
    calculate_item_total = lambda item: item.unit_price * item.qty
    order_items = order.get_all_children()
    order_total = sum(map(calculate_item_total, order_items))
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
    data = OrderedDict(
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
            ("product_to_collect", str(product_list) if product_list else "product_to_collect does not exist" )])
    requests.patch(url=url, headers=headers, data=json.dumps((data)))
                   

def extract_alpha_chars(input_string):
    # Remove numbers from the string
    result_string = ''.join(char for char in input_string if not char.isdigit())

    # Remove the first whitespace
    result_string = result_string.lstrip()

    return result_string