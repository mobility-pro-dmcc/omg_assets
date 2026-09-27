import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields

def execute():
    custom_fields = {
        "Item": [
            {
                "fieldname": "safety_stock_section",
                "label": "Safety Stock",
                "fieldtype": "Section Break",
                "insert_after": "customer",
            },
            {
                "fieldname": "safety_stock_items",
                "label": "Safety Stock Items",
                "fieldtype": "Table",
                "insert_after": "safety_stock_section",
                "options": "Safety Stock Balances",
            }
        ],
        "Notification":[
            {
                "fieldname": "triggered",
                "label": "Triggered At",
                "fieldtype": "Datetime",
                "read_only": 1,
            }
        ]
    }

    create_custom_fields(custom_fields)
    print(f"[PATCH] Safety Stock Fields created")
