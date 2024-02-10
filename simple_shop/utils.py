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

