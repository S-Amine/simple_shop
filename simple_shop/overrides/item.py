from erpnext.stock.doctype.item.item import Item
import frappe
from erpnext.stock.utils import get_or_make_bin
from simple_shop.utils import generate_random_ean, get_svg_content


class CustomItem(Item):     
    def before_validate(self):
        if self.barcodes == []:
            barcode_number = generate_random_ean()
            barcode_svg = get_svg_content(barcode_number)
            self.custom_barcode_svg = barcode_svg
            self.append("barcodes", 
                        {"barcode": barcode_number, 
                        "barcode_type": "EAN-12"
                        }
                        )   
    def on_change(self):
        stock_settings = frappe.get_doc("Shop Settings")
        default_warehouse = stock_settings.default_warehouse
        bin_name = get_or_make_bin(self.item_code, default_warehouse)
        bin = frappe.get_doc("Bin", bin_name)
        self.custom_qty = bin.actual_qty
