// Copyright (c) 2024, The Zoldycks and contributors
// For license information, please see license.txt

frappe.ui.form.on("Wooliz Order", {
    refresh: function(frm) {
        // Add a custom button to the toolbar
        frm.add_custom_button("Generate bordereau", function() {
            // Get the value of the custom_bordereau field
            var customBordereau = frm.doc.custom_bordereau;

            // Check if the custom_bordereau field is not empty
            if (customBordereau) {
                // Redirect to the custom_bordereau URL
                window.location.href = customBordereau;
            } else {
                // Show a message if the custom_bordereau field is empty
                frappe.msgprint("The custom_bordereau field is empty.");
            }
        });
    }
});
