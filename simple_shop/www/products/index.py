import frappe

def get_context(context):
    # Get the search query and item_group from the form data
    query = frappe.local.form_dict.get('query')
    print(query)
    item_group = frappe.local.form_dict.get('category')

    # Specify filters for the search using logical OR
    or_filters = [{'variant_of': ""}]

    if query:
        # Add search filters for item_code, item_name, and description
        or_filters.extend([
            {'item_code': ['like', f'%{query}%']},
            {'item_name': ['like', f'%{query}%']},
            {'description': ['like', f'%{query}%']}
        ])


    # Specify additional filters using logical AND
    filters = {}

    if item_group:
        # Add filter for item_group
        filters['item_group'] = item_group
        # Add this for a frontend condition
        group = frappe.get_doc('Item Group', item_group)
        context.item_group = group

    # Fetch documents from the database using specified filters
    items = frappe.get_all("Item",
                           or_filters=or_filters,
                           filters=filters,
                           fields=["*"],
                           limit_page_length=20
                           )

    # Add the search results to the context
    context.items = items
    categories = frappe.db.get_all("Item Group",
                                  fields="*",
                                  filters={'show_in_website': True}
                                  )
    context.categories = categories

    shop_settings = frappe.get_single("Shop Settings")
    context.shop_settings=shop_settings
