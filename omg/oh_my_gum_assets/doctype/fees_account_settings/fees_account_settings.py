import frappe
from frappe import _
from frappe.model.document import Document


class FeesAccountSettings(Document):
	def validate(self):
		for field in ("fees_commission_account", "fees_processing_order_account"):
			account_company = frappe.db.get_value("Account", self.get(field), "company")
			if account_company != self.company:
				frappe.throw(
					_("Account {0} does not belong to company {1}").format(
						frappe.bold(self.get(field)), frappe.bold(self.company)
					)
				)
