import frappe
import requests
from frappe.model.document import get_doc

@frappe.whitelist(allow_guest=True)
def get_data():
    """Returns all yalidin wilaya"""
    settings = frappe.get_single("Yalidin")
    print(settings)
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    response = requests.get(settings.base_url+"wilayas/", headers=headers)
    wilayas = response.json()
    result = wilayas.get('data',None)
    return result


@frappe.whitelist(allow_guest=True)
def get_communs_true():
    """Returns cities which have official office"""
    settings = frappe.get_single("Settings")
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
def post_order(**args):
    """Set the order"""
    data = frappe._dict(args)
    print(data)
    new_order = frappe.new_doc("Wooliz Order")
    new_order.last_name = data['lastName']
    new_order.phone = data['phone']
    new_order.wilaya = data['wilaya']
    new_order.commun = data['commun']
    product = get_doc("Item",data['product'])
    new_order.append("products",{"item": product,"unit_price":product.custom_price,"qty":data['qty'],"total":product.custom_price})
    new_order.save()
    created_sales_order_id = new_order.name
    return {"success": True, "data": {"order_id":created_sales_order_id}}