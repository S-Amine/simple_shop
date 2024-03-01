from erpnext.stock.doctype.stock_ledger_entry.stock_ledger_entry import StockLedgerEntry
import frappe
from erpnext.stock.utils import get_or_make_bin
from erpnext.stock.serial_batch_bundle import SerialBatchBundle

class CustomStockLedgerEntry(StockLedgerEntry):
    def on_change(self):
        frappe.enqueue('simple_shop.tasks.update_item_stocks', queue='short', item_code=self.item_code)