# Copyright (c) 2024, The Zoldycks and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from simple_shop.yalidine import delete_yalidine_order, extract_first_number, send_yalidin_order, update_yalidine_order


class WoolizOrder(Document):

    def before_save(self):
        if self.is_new():
            old_status = None  # No old value for new documents
        else:
            old_doc = frappe.get_doc(self.doctype, self.name)
            old_status = old_doc.woolize_status
        total = 0
        total_qty = 0
        for item in self.products:
            line_total = item.unit_price * item.qty
            item.total = line_total
            total_qty += item.qty
            total += line_total
        self.total_qty = total_qty
        self.total_price = total
        print("Before saving order................")
        #extract number from center 
        if self.custom_stop_desk_bureau:
            self.custom_center_id=extract_first_number(self.custom_center)
        if self.custom_tracking_id in ["",None] and self.custom_status=="En préparation":
            print("send yalidine order ................")
            my_response=send_yalidin_order(self.name)
            print(my_response)
            tracking=my_response[self.name]['tracking']
            label=my_response[self.name]['label']
            self.custom_tracking_id=tracking
            self.custom_bordereau=label
        elif self.custom_tracking_id is not None:
            print("Update yalidine order ................")
            update_yalidine_order(self.name)
        
        if self.woolize_status != old_status :
            print(f"The previous status was: {old_status}")
            if self.woolize_status == "created":
                if old_status is None:
                    pass
                else:
                    self.woolize_status = old_status
                    frappe.throw("You can't change the status to 'created' because this document is already created.")
            elif self.woolize_status == "pending":
                if old_status is None or old_status == "created" or old_status == "cancelled":
                    print(self.products)
                    self.move_stock_to_pending_warehouse()
                    self.create_raw_sales_order()
                    self.save_sales_order()
                else:
                    if old_status == "confirmed":
                        frappe.throw("You can't change the status to 'pending' from 'confirmed' status. You can cancel the existing one or pack it for delivery.")
                    else:
                        self.woolize_status = old_status
                        frappe.throw("You can't change the status to 'pending' from '{}' status. You can create a new document or cancel the existing one.".format(old_status))
            elif self.woolize_status == "cancelled":
                if old_status == "pending" or old_status == "confirmed" or old_status == "packed":
                    self.return_products_to_public_warehouse()
                else:
                    self.woolize_status = old_status
                    frappe.throw("You can't cancel a document in '{}' status. You can cancel a pending or confirmed document.".format(old_status))
            elif self.woolize_status == "confirmed":
                if old_status == "pending":
                    self.check_quantity_in_pending_warehouse()
                    # if not self.is_quantity_in_pending_warehouse():
                        # self.move_stock_to_pending_warehouse()
                    self.submit_sales_order()
                else:
                    self.woolize_status = old_status
                    frappe.throw("You can't confirm a document in '{}' status. You can confirm a pending document.".format(old_status))
            elif self.woolize_status == "packed":
                if old_status == "confirmed":
                    self.check_quantity_in_pending_warehouse()
                    # if not self.is_quantity_in_pending_warehouse():
                        # self.move_stock_to_pending_warehouse()
                    self.submit_sales_order()
                else:
                    self.woolize_status = old_status
                    frappe.throw("You can't pack a document in '{}' status. You can pack a confirmed document.".format(old_status))
            elif self.woolize_status == "delivered":
                if old_status == "packed":
                    self.check_quantity_in_pending_warehouse()
                    #if not self.is_quantity_in_pending_warehouse():
                        #self.move_stock_to_pending_warehouse()
                    self.create_delivery_note()
                else:
                    self.woolize_status = old_status
                    frappe.throw("You can't mark a document as delivered in '{}' status. You can mark a packed document as delivered.".format(old_status))
            elif self.woolize_status == "paid":
                if old_status == "delivered":
                    self.check_if_delivered()
                else:
                    self.woolize_status = old_status
                    frappe.throw("You can't mark a document as 'paid on delivery' in '{}' status. You can only mark a delivered document as 'paid on delivery'.".format(old_status))
            elif self.woolize_status == "returned":
                if old_status == "delivered" or old_status == "paid":
                    self.check_if_delivered()
                    self.return_items()
                else:
                    self.woolize_status = old_status
                    frappe.throw("You can't return a document in '{}' status. You can return a delivered document.".format(old_status))
    
    
    def on_change(self):
        """
        Recalculates the actual quantity (QTY) for each item.
        """
        for item in self.products:
            item_doc = frappe.get_doc("Item", item.item)
            item_doc.db_set('custom_qty', 0, commit=True)
            item_doc.save(
                ignore_permissions=True, # ignore write permissions during insert
            )

    def move_stock_to_pending_warehouse(self):
        print("Moving stock to pending warehouse")
        stock_settings = frappe.get_doc("Shop Settings")
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.from_warehouse = stock_settings.default_warehouse
        stock_entry.to_warehouse = stock_settings.pending_warehouse
        
        for item in self.products :
            stock_entry.append("items", {"item_code": item.item,
                                        "qty": item.qty                                        })
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.insert(
            ignore_permissions=True,
        )
        print("Done")


    
    def create_raw_sales_order(self):
        print("Creating the raw sales order")
    
    def save_sales_order(self):
        print("Saving the sales order")
    
    def return_products_to_public_warehouse(self):
        print("Returning products to public warehouse")
        stock_settings = frappe.get_doc("Shop Settings")
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.from_warehouse = stock_settings.pending_warehouse
        stock_entry.to_warehouse = stock_settings.default_warehouse
        
        for item in self.products :
            stock_entry.append("items", {"item_code": item.item,
                                        "qty": item.qty                                        })
        stock_entry.stock_entry_type = "Material Transfer"
        stock_entry.insert(
            ignore_permissions=True,
        )
        print("Done")
    
    def check_quantity_in_pending_warehouse(self):
        print("Checking quantity in pending warehouse")
    
    def is_quantity_in_pending_warehouse(self):
        print("Checking if quantity is in pending warehouse")
        # Placeholder for actual logic
    
    def submit_sales_order(self):
        print("Submitting the sales order")
    
    def create_delivery_note(self):
        print("Creating a delivery note")
        stock_settings = frappe.get_doc("Shop Settings")
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.from_warehouse = stock_settings.pending_warehouse
        
        for item in self.products :
            stock_entry.append("items", {"item_code": item.item,
                                        "qty": item.qty                                        })
        stock_entry.stock_entry_type = "Material Issue"
        stock_entry.insert(
            ignore_permissions=True,
        )
        print("Done")
    
    def check_if_delivered(self):
        print("Checking if delivered")
    def return_items(self):
        print("Returning items")
        stock_settings = frappe.get_doc("Shop Settings")
        stock_entry = frappe.new_doc("Stock Entry")
        stock_entry.to_warehouse = stock_settings.resturn_warehouse
        
        for item in self.products :
            stock_entry.append("items", {"item_code": item.item,
                                        "qty": item.qty                                        })
        stock_entry.stock_entry_type = "Material Receipt"
        stock_entry.insert(
            ignore_permissions=True,
        )
        print("Done")
        
    def after_delete(self):
        print("After deleting ................")
        if self.custom_tracking_id:
            response=delete_yalidine_order(self.custom_tracking_id)
            print(response.text)