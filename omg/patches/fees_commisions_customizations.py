import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields


def execute():
	custom_fields = {
		"Sales Invoice": [
			{
				"fieldname": "custom_fees_section",
				"label": "Fees",
				"fieldtype": "Section Break",
				"insert_after": "disable_rounded_total",
				"collapsible": 1,
			},
			{
				"fieldname": "custom_fees_commission",
				"label": "Fees Commission",
				"fieldtype": "Currency",
				"options": "currency",
				"insert_after": "custom_fees_section",
			},
			{
				"fieldname": "custom_fees_column_break",
				"fieldtype": "Column Break",
				"insert_after": "custom_fees_commission",
			},
			{
				"fieldname": "custom_fees_processing_order",
				"label": "Fees Processing Order",
				"fieldtype": "Currency",
				"options": "currency",
				"insert_after": "custom_fees_column_break",
			},
		]
	}
	create_custom_fields(custom_fields)
	name = "Sales Invoice-custom_order_method"
	if not frappe.db.exists("Custom Field", name):
		return

	frappe.db.set_value(
		"Custom Field",
		name,
		{"fieldtype": "Link", "options": "Order Platform"},
		update_modified=False,
	)
	frappe.clear_cache(doctype="Sales Invoice")
