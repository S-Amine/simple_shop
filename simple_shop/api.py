import json
import frappe
import requests
from frappe.model.document import get_doc
from simple_shop.utils import rehandling_checkout_products, remove_numbers

@frappe.whitelist(allow_guest=True)
def get_data():
    """Returns all yalidin wilaya"""
    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    response = requests.get(settings.base_url+"wilayas/", headers=headers)
    wilayas = response.json()
    result = wilayas.get('data',None)
    return result


@frappe.whitelist(allow_guest=True)
def get_communs_true():
    """
    Get desk stop yalidin communs
    """
    settings = frappe.get_single("Yalidin")
    print(settings)
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    try:
        response = requests.get(settings.base_url+"communes/?has_stop_desk=true&page_size=2000", headers=headers)
        response_delevery = requests.get(settings.base_url+"deliveryfees/", headers=headers)
        print(response_delevery.text)
        communs = response.json()
        deliveryfees = response_delevery.json()
        result = communs.get('data',None)
        result_2 = deliveryfees.get('data',None)
    except:
        result,result_2={},{}

    return {"communs": result, "deliveryfees": result_2}

@frappe.whitelist(allow_guest=True)
def get_communs():
    """
    Get all yalidine communs
    """
    settings = frappe.get_single("Yalidin")
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    data=[]
    next=True
    index = 1
    try:
        while next:
            response = requests.get(settings.base_url+f"communes/?fields=wilaya_name,name,wilaya_id&page={index}", headers=headers)
            communs = response.json()
            result = communs.get('data',None)
            next = communs.get('links',{}).get('next',None)
            for commun in result:
                data.append(commun)
            index+=1
            
    except Exception as e:
        print(e)
        data={}
    return {"communs":data}


@frappe.whitelist(allow_guest=True)
def get_centers():
    settings = frappe.get_single("Yalidin")
    print(settings)
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    data=[]
    next=True
    index = 1
    try:
        while next:
            response = requests.get(f"{settings.base_url}centers/?page={index}", headers=headers)
            communs = response.json()
            result = communs.get('data',None)
            next = communs.get('links',{}).get('next',None)
            for commun in result:
                data.append(commun)
            index+=1
    except:
        result={}

    return {"centers": data}




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

