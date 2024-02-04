import frappe
import requests

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
def set_order():
    """Set the order"""
