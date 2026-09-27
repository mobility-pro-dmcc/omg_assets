import frappe

def evaluate_notification(doc, method):
    target_items = []

    if doc.doctype == "Stock Entry":
        for item in doc.get("items"):
            if item.s_warehouse:
                target_items.append([item.s_warehouse, item.item_code, item.qty])

    elif doc.doctype == "Sales Invoice" and doc.update_stock:
        for item in doc.get("items"):
            if item.warehouse:
                target_items.append([item.warehouse, item.item_code, item.qty])


    low_stock_items = []

    checked = set()

    for row in target_items:
        warehouse, item_code, doc_qty = row[0], row[1], row[2]
        
        combo = f"{warehouse}_{item_code}"
        if combo in checked:
            continue
        checked.add(combo)
        
        actual_qty = frappe.db.get_value("Bin", 
            {"item_code": item_code, "warehouse": warehouse}, 
            "actual_qty") or 0.0
            
        safety_stock = frappe.db.get_value("Safety Stock Balances", 
            {"parent": item_code, "warehouse": warehouse, "parenttype": "Item"}, 
            "qty") or 0.0
            
        if safety_stock > 0 and actual_qty < safety_stock:
            low_stock_items.append([warehouse, item_code, actual_qty, safety_stock])

    if low_stock_items:
        notif = frappe.get_doc("Notification", "Safety Stock notification")
        notif.flags.low_stock_items = low_stock_items
        notif.send(notif)