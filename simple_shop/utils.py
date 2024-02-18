import json
import re
import frappe

@frappe.whitelist()
def build_variant_data(item, item_variants):
    data = []

    for attribute in item.attributes:
        attribute_data = {
            'Attribute': attribute.attribute,
            'Values': set()  # Use a set instead of a list
        }
        data.append(attribute_data)

    for item_variant in item_variants:
        item_variant = frappe.get_doc('Item', item_variant)
        if item_variant.attributes:
            for item_variant_attribute in item_variant.attributes:
                for attribute_data in data:
                    if attribute_data['Attribute'] == item_variant_attribute.attribute:
                        attribute_data['Values'].add(item_variant_attribute.attribute_value)

    # Convert sets back to lists
    for attribute_data in data:
        attribute_data['Values'] = list(attribute_data['Values'])

    print(data)
    return data

def calculate_total_price(products):
    try:
        # Parse the JSON string to a Python list of dictionaries

        # Calculate the total price
        total_price = sum(float(product["price"]) * int(product["qty"]) for product in products)

        return total_price
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return None
    except KeyError as e:
        print(f"Error accessing key in product: {e}")
        return None
def rehandling_checkout_products(products):
    items = []
    products_array = json.loads(products)
    for product in products_array:
        product_obj =  frappe.get_doc("Item",product['id'])
        item = {"item": product_obj,"unit_price":product['price'],"qty":product['qty'],"total":product_obj.custom_price,"custom_color":product['color'],"custom_size":product['size']}
        items.append(item)
    return items


def remove_numbers(input_string):
    # Use a regular expression to replace digits with an empty string
    result = re.sub(r'\d', '', input_string)
    return result