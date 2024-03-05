import json
import frappe
import requests
from frappe.model.document import get_doc
from simple_shop.utils import rehandling_checkout_products, remove_numbers

@frappe.whitelist(allow_guest=True)
def get_data():
    """Returns all yalidin wilaya"""
    # Check if data is already in the cache
    cached_data = frappe.cache().get_value("yalidin_wilayas")

    if cached_data:
        # Return cached data if available
        return cached_data

    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key, "X-API-TOKEN": settings.api_token}
    response = requests.get(settings.base_url + "wilayas/", headers=headers)
    wilayas = response.json()
    result = wilayas.get('data', None)

    # Cache the result for future use (valid for 1 hour, adjust as needed)
    frappe.cache().set_value("yalidin_wilayas", result, expires_in_sec=36000)

    return result


@frappe.whitelist(allow_guest=True)
def get_communs_true():
    """
    Get desk stop yalidin communs
    """
    # Check if data is already in the cache
    cached_data = frappe.cache().get_value("yalidin_communs_true")

    if cached_data:
        # Return cached data if available
        return cached_data

    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key, "X-API-TOKEN": settings.api_token }

    try:
        response = requests.get(settings.base_url + "communes/?has_stop_desk=true&page_size=2000", headers=headers)
        response_delivery = requests.get(settings.base_url + "deliveryfees/", headers=headers)

        communes_data = response.json().get('data', None)
        deliveryfees_data = response_delivery.json().get('data', None)
    except Exception as e:
        # Handle exceptions, log the error, or take appropriate action
        print(f"Error fetching data: {str(e)}")
        communes_data, deliveryfees_data = {}, {}

    # Cache the result for future use (valid for 1 hour, adjust as needed)
    result = {"communs": communes_data, "deliveryfees": deliveryfees_data}
    frappe.cache().set_value("yalidin_communs_true", result, expires_in_sec=36000)

    return result


def fetch_data(api_url, headers):
    data = []
    next_page = True
    index = 1

    try:
        while next_page:
            response = requests.get(f"{api_url}?page={index}", headers=headers)
            api_data = response.json()
            result = api_data.get('data', None)
            next_page = api_data.get('links', {}).get('next', None)

            if result:
                data.extend(result)

            index += 1

    except Exception as e:
        # Handle exceptions, log the error, or take appropriate action
        print(f"Error fetching data: {str(e)}")
        data = []

    return data

@frappe.whitelist(allow_guest=True)
def get_communs():
    """
    Get all yalidine communs
    """
    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key, "X-API-TOKEN": settings.api_token}
    
    # Check if data is already in the cache
    cached_data = frappe.cache().get_value("yalidin_communs")

    if cached_data:
        # Return cached data if available
        return {"communs": cached_data}

    # Fetch data from the API
    communs_data = fetch_data(f"{settings.base_url}communes/?fields=wilaya_name,name,wilaya_id", headers)

    # Cache the result for future use (valid for 1 hour, adjust as needed)
    frappe.cache().set_value("yalidin_communs", communs_data, expires_in_sec=36000)

    return {"communs": communs_data}

@frappe.whitelist(allow_guest=True)
def get_centers():
    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key, "X-API-TOKEN": settings.api_token}
    
    # Check if data is already in the cache
    cached_data = frappe.cache().get_value("yalidin_centers")

    if cached_data:
        # Return cached data if available
        return {"centers": cached_data}

    # Fetch data from the API
    centers_data = fetch_data(f"{settings.base_url}centers/", headers)

    # Cache the result for future use (valid for 1 hour, adjust as needed)
    frappe.cache().set_value("yalidin_centers", centers_data, expires_in_sec=36000)

    return {"centers": centers_data}



@frappe.whitelist(allow_guest=True)
def post_order(**args):
    """Set the order"""
    data = frappe._dict(args)
    print(data)
    new_order = frappe.new_doc("Wooliz Order")
    new_order.last_name = data['lastName']
    new_order.phone = data['phone']
    new_order.wilaya = data['wilaya']
    new_order.custom_address = data['address']

    new_order.commun = data['commun']
    new_order.custom_stop_desk_bureau = data['is_stop_desk']
    if data['is_stop_desk']:
        new_order.custom_center_id = data['center_id'] # IN YALIDIN this field is required if stop_desk is true
        new_order.custom_center = f"{data['center_id']} - {data['commun']}"
    
    product = get_doc("Item",data['product'])
    print(product)
    new_order.append("products",{"item": product.item_code,"unit_price":product.custom_price,"qty":data['qty'],"total":product.custom_price})
    new_order.save()
    created_sales_order_id = new_order.name
    return {"success": True, "data": {"order_id":created_sales_order_id}}


@frappe.whitelist(allow_guest=True)
def post_order_checkout(**args):
    """Set the order"""
    data = frappe._dict(args)
    print(data)
    new_order = frappe.new_doc("Wooliz Order")
    new_order.last_name = data['lastName']
    new_order.phone = data['phone']
    new_order.wilaya = data['wilaya']
    new_order.commun = data['commun']
    new_order.custom_stop_desk_bureau = data['is_stop_desk']
    products = data['products']
    if data['is_stop_desk']:
        new_order.custom_center_id = data['center_id'] # IN YALIDIN this field is required if stop_desk is true
        new_order.custom_center = f"{data['center_id']} - {data['commun']}"
        new_order.commun = remove_numbers(data['wilaya']).lstrip()
    items = rehandling_checkout_products(products)
    for item in items:

        new_order.append("products",item)
    new_order.save()
    created_sales_order_id = new_order.name
    return {"success": True, "data": {"order_id":created_sales_order_id}}

