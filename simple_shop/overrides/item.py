from erpnext.stock.doctype.item.item import Item
import frappe
from erpnext.stock.utils import get_or_make_bin
from simple_shop.utils import generate_random_ean


class CustomItem(Item):        
    def on_change(self):
        if self.barcodes == []:
            random_barcode = generate_random_ean()
            self.append("barcodes", 
                        {"barcode": random_barcode, 
                        "barcode_type": "EAN-12"
                        }
                        )
        stock_settings = frappe.get_doc("Shop Settings")
        default_warehouse = stock_settings.default_warehouse
        bin_name = get_or_make_bin(self.item_code, default_warehouse)
        bin = frappe.get_doc("Bin", bin_name)
        self.custom_qty = bin.actual_qty
