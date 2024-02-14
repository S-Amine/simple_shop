# Copyright (c) 2024, The Zoldycks and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from simple_shop.yalidine import delete_yalidine_order, send_yalidin_order


class WoolizOrder(Document):
    def before_save(self):
        print("Before saving ................")
        if self.custom_tracking_id in ["",None]:
            my_response=send_yalidin_order(self.name)
            tracking=my_response[self.name]['tracking']
            label=my_response[self.name]['label']
            self.custom_tracking_id=tracking
            self.custom_bordereau=label
    def after_delete(self):
        print("After deleting ................")
        if self.custom_tracking_id:
            response=delete_yalidine_order(self.custom_tracking_id)
            print(response.text)