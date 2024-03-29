import frappe
from simple_shop.utils import build_variant_data, convert_to_variant_structure, handle_variant_data

def get_context(context):
    item_code = frappe.local.form_dict.get('item_code') or frappe.local.form_dict.get('item_code')
    shop_settings = frappe.get_single("Shop Settings")
    context.shop_settings=shop_settings

    if item_code:
        item = frappe.get_doc('Item', item_code)
        recommendations = frappe.get_list('Item', fields="*",
                                        filters=[{'item_code': ['not like', f'%{item_code}%']},{'item_group': ['like', f'%{item.item_group}%']}, {'variant_of': ""}]
                                        )
        context.recommendations = recommendations
        context.item = item

        if item.has_variants:
            item_variants = frappe.get_list('Item', fields="*",
                                            filters={
                                                'variant_of': item_code
                                            })
            # The build_variant_data func return a json like this one [{'Attribute': 'Colour', 'Values': ['Blue', 'Red']}, {'Attribute': 'Size', 'Values': ['Extra Large', 'Large']}]
            context.item_variants_values = build_variant_data(item, item_variants)

            context.item_variants = item_variants
            handle_variant=handle_variant_data(item, item_variants)
            context.handle_variant = handle_variant

    else:
        frappe.local.flags.redirect_location = '/'
        raise frappe.Redirect
    categories = frappe.db.get_all("Item Group",
                                  fields="*",
                                  filters={'show_in_website': True}
                                  )
    context.categories = categories
