# Copyright (c) 2024, The Zoldycks and contributors
# For license information, please see license.txt

# import frappe
from frappe.model.document import Document
from simple_shop.yalidine import delete_yalidine_order, extract_first_number, send_yalidin_order, update_yalidine_order


class WoolizOrder(Document):
    def before_save(self):
        print("Before saving order................")
        #extract number from center 
        if self.custom_stop_desk_bureau:
            self.custom_center_id=extract_first_number(self.custom_center)
        if self.custom_tracking_id in ["",None] and self.custom_status=="En préparation":
            print("send yalidine order ................")
            my_response=send_yalidin_order(self.name)
            tracking=my_response[self.name]['tracking']
            label=my_response[self.name]['label']
            self.custom_tracking_id=tracking
            self.custom_bordereau=label
        elif self.custom_tracking_id is not None:
            print("Update yalidine order ................")
            update_yalidine_order(self.name)
    def after_delete(self):
        print("After deleting ................")
        if self.custom_tracking_id:
            response=delete_yalidine_order(self.custom_tracking_id)
            print(response.text)