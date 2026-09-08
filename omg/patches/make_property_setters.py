import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    target_doctype = "Subcontracting Receipt Item"
    
    # List of fields involved in the GL amount calculation
    target_fields = [
        "rate",
        "rm_cost_per_qty",
        "service_cost_per_qty",
        "additional_cost_per_qty",
        "scrap_cost_per_qty",
        "amount"
    ]

    for field in target_fields:
        # make_property_setter automatically updates if it exists, or creates if it doesn't
        make_property_setter(
            doctype=target_doctype,
            fieldname=field,
            property="precision",
            value="9",
            property_type="Select"
        )
        
    # Clear the doctype cache to ensure the UI and backend logic pick up the new precision
    frappe.clear_cache(doctype=target_doctype)
    frappe.db.commit()
    
    return "Precision Property Setters created successfully."

# If running in System Console, uncomment the line below:
# update_subcontracting_precision()