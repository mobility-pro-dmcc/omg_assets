frappe.ui.form.on("Fees Account Settings", {
	setup(frm) {
		["fees_commission_account", "fees_processing_order_account"].forEach((field) => {
			frm.set_query(field, () => ({
				filters: { company: frm.doc.company, is_group: 0 },
			}));
		});
	},
});
