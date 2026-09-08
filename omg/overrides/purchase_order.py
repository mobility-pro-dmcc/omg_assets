import frappe 
import json
from frappe.model.mapper import get_mapped_doc
from frappe.utils import cint, cstr, flt, get_link_to_form

@frappe.whitelist()
def make_subcontracting_order(source_name, target_doc=None, save=False, submit=False, notify=False):
	if not is_po_fully_subcontracted(source_name):
		target_doc = get_mapped_subcontracting_order(source_name, target_doc)

		if (save or submit) and frappe.has_permission(target_doc.doctype, "create"):
			target_doc.save()

			if submit and frappe.has_permission(target_doc.doctype, "submit", target_doc):
				try:
					target_doc.submit()
				except Exception as e:
					target_doc.add_comment("Comment", _("Submit Action Failed") + "<br><br>" + str(e))

			if notify:
				frappe.msgprint(
					_("Subcontracting Order {0} created.").format(
						get_link_to_form(target_doc.doctype, target_doc.name)
					),
					indicator="green",
					alert=True,
				)

		return target_doc
	else:
		frappe.throw(_("This PO has been fully subcontracted."))


def is_po_fully_subcontracted(po_name):
	table = frappe.qb.DocType("Purchase Order Item")
	query = (
		frappe.qb.from_(table)
		.select(table.name)
		.where((table.parent == po_name) & (table.qty != table.subcontracted_quantity))
	)
	return not query.run(as_dict=True)


def get_mapped_subcontracting_order(source_name, target_doc=None):
	def post_process(source_doc, target_doc):
		target_doc.populate_items_table()

		if target_doc.set_warehouse:
			for item in target_doc.items:
				item.warehouse = target_doc.set_warehouse
		else:
			if source_doc.set_warehouse:
				for item in target_doc.items:
					item.warehouse = source_doc.set_warehouse
			else:
				for idx, item in enumerate(target_doc.items):
					item.warehouse = source_doc.items[idx].warehouse

	if target_doc and isinstance(target_doc, str):
		target_doc = json.loads(target_doc)
		for key in ["service_items", "items", "supplied_items"]:
			if key in target_doc:
				del target_doc[key]
		target_doc = json.dumps(target_doc)

	target_doc = get_mapped_doc(
		"Purchase Order",
		source_name,
		{
			"Purchase Order": {
				"doctype": "Subcontracting Order",
				"field_map": {},
				"field_no_map": ["total_qty", "total", "net_total"],
				"validation": {
					"docstatus": ["=", 1],
				},
			},
			"Purchase Order Item": {
				"doctype": "Subcontracting Order Service Item",
				"field_map": {
					"name": "purchase_order_item",
					"material_request": "material_request",
					"material_request_item": "material_request_item",
					"base_rate": "rate",
				},
				"field_no_map": ["qty", "fg_item_qty", "amount"],
				"condition": lambda item: item.qty != item.subcontracted_quantity,
			},
		},
		target_doc,
		post_process,
	)

	return target_doc
