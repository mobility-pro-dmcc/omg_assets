import frappe
from frappe import _
from frappe.utils import flt


def create_fees_journal_entry(doc, method=None):
	"""On Sales Invoice submit: Dr fees accounts / Cr customer receivable account."""
	commission = flt(doc.get("custom_fees_commission"))
	processing = flt(doc.get("custom_fees_processing_order"))
	if commission <= 0 and processing <= 0:
		return

	settings = frappe.db.get_value(
		"Fees Account Settings",
		doc.company,
		["fees_commission_account", "fees_processing_order_account"],
		as_dict=True,
	)
	if not settings:
		frappe.throw(
			_("Please create a Fees Account Settings record for company {0}").format(
				frappe.bold(doc.company)
			)
		)

	rate = flt(doc.conversion_rate) or 1
	company_currency = frappe.get_cached_value("Company", doc.company, "default_currency")
	total = commission + processing

	je = frappe.new_doc("Journal Entry")
	je.voucher_type = "Journal Entry"
	je.company = doc.company
	je.posting_date = doc.posting_date
	je.title = _fees_je_title(doc.name)
	je.multi_currency = 1 if doc.currency != company_currency else 0
	je.user_remark = _("Fees for Sales Invoice {0}").format(doc.name)

	for amount, account in (
		(commission, settings.fees_commission_account),
		(processing, settings.fees_processing_order_account),
	):
		if amount > 0:
			je.append(
				"accounts",
				{
					"account": account,
					"debit_in_account_currency": flt(amount * rate, doc.precision("base_grand_total")),
					"cost_center": doc.cost_center,
				},
			)

	je.append(
		"accounts",
		{
			"account": doc.debit_to,
			"party_type": "Customer",
			"party": doc.customer,
			"account_currency": doc.party_account_currency,
			"exchange_rate": rate,
			"credit_in_account_currency": total,
			"reference_type": "Sales Invoice",
			"reference_name": doc.name,
			"cost_center": doc.cost_center,
		},
	)

	je.insert(ignore_permissions=True)
	je.submit()


def cancel_fees_journal_entry(doc, method=None):
	# Linked through the standard Journal Entry Account reference to this invoice.
	je_names = frappe.get_all(
		"Journal Entry",
		filters={"title": _fees_je_title(doc.name), "docstatus": 1},
		pluck="name",
	)
	for name in je_names:
		linked = frappe.db.exists(
			"Journal Entry Account",
			{"parent": name, "reference_type": "Sales Invoice", "reference_name": doc.name},
		)
		if linked:
			frappe.get_doc("Journal Entry", name).cancel()


def _fees_je_title(sales_invoice):
	return f"Fees - {sales_invoice}"
