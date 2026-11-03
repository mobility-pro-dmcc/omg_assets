import frappe
from frappe import _
from frappe.utils import flt

from erpnext.subcontracting.doctype.subcontracting_order.subcontracting_order import SubcontractingOrder


class CustomSubcontractingOrder(SubcontractingOrder):
	def validate(self):
		super().validate()
		self.validate_rows_with_purchase_order()

	def get_purchase_order_items(self):
		po_items = frappe.get_all(
			"Purchase Order Item",
			filters={"parent": self.purchase_order, "parenttype": "Purchase Order"},
			fields=["name", "item_code", "fg_item", "base_rate"],
		)
		return {d.name: d for d in po_items}

	def validate_rows_with_purchase_order(self):
		po_items = self.get_purchase_order_items()
		for item in self.items:
			po_item = po_items.get(item.purchase_order_item)
			if not po_item or item.item_code != po_item.fg_item:
				frappe.throw(
					_("Row {0}: Item {1} is not the Finished Good of Purchase Order {2}.").format(
						item.idx, item.item_code, self.purchase_order
					)
				)

		for service_item in self.service_items:
			po_item = po_items.get(service_item.purchase_order_item)
			precision = service_item.precision("rate")
			if (
				not po_item
				or service_item.item_code != po_item.item_code
				or flt(service_item.rate, precision) != flt(po_item.base_rate, precision)
			):
				frappe.throw(
					_("Row {0}: Service Item {1} and its rate must match Purchase Order {2}.").format(
						service_item.idx, service_item.item_code, self.purchase_order
					)
				)
