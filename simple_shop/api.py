import json
import frappe
import requests
from frappe.model.document import get_doc

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
            response = requests.get(settings.base_url+f"communes/?fields=wilaya_name,name&page={index}", headers=headers)
            communs = response.json()
            result = communs.get('data',None)
            next = communs.get('links',{}).get('next',None)
            for commun in result:
                data.append(commun)
            index+=1
            
    except Exception as e:
        print(e)
        data={}
    print(data)
    return {"communs":data}


@frappe.whitelist(allow_guest=True)
def get_centers():
    settings = frappe.get_single("Yalidin")
    print(settings)
    headers = {"X-API-ID": settings.api_key,"X-API-TOKEN": settings.api_token }
    try:
        response = requests.get(settings.base_url+"centers/", headers=headers)
        response_delevery = requests.get(settings.base_url+"deliveryfees/", headers=headers)
        print(response_delevery.text)
        communs = response.json()
        result = communs.get('data',None)
    except:
        result={}

    return {"centers": result}




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
    new_order.custom_stop_desk_bureau = data['is_stop_desk']
    product = get_doc("Item",data['product'])
    new_order.append("products",{"item": product,"unit_price":product.custom_price,"qty":data['qty'],"total":product.custom_price})
    new_order.save()
    created_sales_order_id = new_order.name
    return {"success": True, "data": {"order_id":created_sales_order_id}}

@frappe.whitelist()
def generate_bordereau(**args):
    """Set the order"""
    print("Generating bordereau ........")
    print(args)

    # Convert the string representation of the document to a dictionary
    doc_dict = json.loads(args["doc"])

    # Access the custom_bordereau field
    pdf = doc_dict.get("custom_bordereau")

    print("PDF URL:", pdf)

    if pdf:
        # Return JavaScript code for redirection
        return f"window.location.href = '{pdf}';"
    else:
        frappe.msgprint("The custom_bordereau field is empty.")