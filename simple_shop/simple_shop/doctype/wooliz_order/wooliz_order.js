// Copyright (c) 2024, The Zoldycks and contributors
// For license information, please see license.txt
const getAllCommuns = () => {
  const storedCommunsAll = localStorage.getItem("communs_all");
  if (storedCommunsAll) {
    let communs = JSON.parse(storedCommunsAll);
    return { communs: communs };
  } else {
    // If data is not in localStorage, fetch it from the API
    return fetch("/api/method/simple_shop.api.get_communs", {
      // Include any headers if needed
    })
      .then((response) => response.json())
      .then((data) => {
        console.log(data);
        let communs = data["message"]["communs"];

        // Store the data in localStorage for future use
        localStorage.setItem("communs_all", JSON.stringify(communs));

        // Return the fetched data
        return { communs: communs };
      })
      .catch((error) => {
        console.error("Error fetching or storing data:", error);
        throw error;
      });
  }
};
const getCommunsList = (has_stop_desk, wilaya) => {
  // Check if data is already in localStorage
  if (has_stop_desk) {
    const storedData = localStorage.getItem("communsList");
    const storeddeleveryFeesData = localStorage.getItem("deleveryFees");

    if (storedData && storeddeleveryFeesData) {
      let communs = JSON.parse(storedData);
      let deleveryFees = JSON.parse(storeddeleveryFeesData);
      return { communs: communs, deliveryfees: deleveryFees };
    }

    // If data is not in localStorage, fetch it from the API
    return fetch("/api/method/simple_shop.api.get_communs_true", {
      // Include any headers if needed
    })
      .then((response) => response.json())
      .then((data) => {
        let communs = data["message"]["communs"];
        let deleveryFees = data["message"]["deliveryfees"];

        // Store the data in localStorage for future use
        localStorage.setItem("communsList", JSON.stringify(communs));
        localStorage.setItem("deleveryFees", JSON.stringify(deleveryFees));

        // Return the fetched data
        return { communs: communs, deliveryfees: deleveryFees };
      })
      .catch((error) => {
        console.error("Error fetching or storing data:", error);
        throw error;
      });
  } else {
    return getAllCommuns();
  }
};
const getCentersList = () => {
  // Check if data is already in localStorage

  const storedDataCenters = localStorage.getItem("centers");

  if (storedDataCenters) {
    let centers = JSON.parse(storedDataCenters);
    return centers;
  }

  // If data is not in localStorage, fetch it from the API
  return fetch("/api/method/simple_shop.api.get_centers", {
    // Include any headers if needed
  })
    .then((response) => response.json())
    .then((data) => {
      let centers = data["message"]["centers"];
      // Store the data in localStorage for future use
      localStorage.setItem("centers", JSON.stringify(centers));
      // Return the fetched data
      return centers;
    })
    .catch((error) => {
      console.error("Error fetching or storing data:", error);
      throw error;
    });
}
const renderCentersView = (frm) => {
  // fetch centers
  const centers = getCentersList();
  let centerOptions = [];
  centers.forEach((item) => {
    if (item.wilaya_name === frm.selected_doc.wilaya.replace(/\d/g, '').trim()) {
      let centerOption = `${item.center_id} - ${item.name}`;
      centerOptions.push(centerOption);
    }
  });
  frm.set_df_property("custom_center", "options", centerOptions);
};

const renderWilayaView = (frm) => {
  console.log(frm)
  fetch("/api/method/simple_shop.api.get_data")
    .then((response) => response.json())
    .then((data) => {
      const result = data["message"];
      let options = [];
      result.forEach((item) => {
        options.push(`${item.id} ${item.name}`);
      });
      frm.set_df_property("wilaya", "options", options);

      renderCommunView(frm); // render the communs
      renderCentersView(frm); // render the centers
    })
    .catch((error) => console.error("Error fetching data:", error));
};

/*** renderCommunView to render communs in select options ***/

const renderCommunView = (frm) => {
  var filteredCommuns = [];
  frm.set_df_property("commun", "options", ["loading..."]);
  let communs = getCommunsList((has_stop_desk = false))["communs"];
  communs.forEach((e) => {
    if (e.wilaya_name === frm.selected_doc.wilaya.replace(/\d/g, '').trim()) {
      filteredCommuns.push(e.name);
    }
  });
  frm.set_df_property("commun", "options", filteredCommuns);
};


/*** Using frappe SDK to rendering ***/

frappe.ui.form.on("Wooliz Order", {
  refresh: function (frm) {
    // Add a custom button to the toolbar
    frm.add_custom_button("Generate bordereau", function () {
      // Get the value of the custom_bordereau field
      var customBordereau = frm.doc.custom_bordereau;

      // Check if the custom_bordereau field is not empty
      if (customBordereau) {
        // Open the custom_bordereau URL in a new tab
        window.open(customBordereau, "_blank");
      } else {
        // Show a message if the custom_bordereau field is empty
        frappe.msgprint("The custom_bordereau field is empty.");
      }
    });
    // Fetch options for the wilaya field
    renderWilayaView(frm);
    frm.cscript.wilaya = function (doc, cdt, cdn) {
      // Get the current value of the wilaya field
      var wilayaValue = locals[cdt][cdn].wilaya;
      // Check if the wilaya field has changed
      if (wilayaValue) {
        renderCommunView(frm); // render the communs
        renderCentersView(frm); // render the centers
      }
    };
  },
});


frappe.ui.form.on("Wooliz Order", {
  refresh: function (frm) {
    // Add a custom button to the toolbar
    frm.add_custom_button("Scan Barcode", function () {
      // Create a new Scanner instance
      const scanner = new frappe.ui.Scanner({
        dialog: true, // Open camera scanner in a dialog
        multiple: false, // Stop after scanning one value
        on_scan(data) {
          // Handle the scanned barcode
          handle_scanned_barcode(frm, data.decodedText);
        }
      });
    });

    // Fetch options for the wilaya field
    renderWilayaView(frm);
    frm.cscript.wilaya = function (doc, cdt, cdn) {
      // Get the current value of the wilaya field
      var wilayaValue = locals[cdt][cdn].wilaya;
      // Check if the wilaya field has changed
      if (wilayaValue) {
        renderCommunView(frm); // render the communs
        renderCentersView(frm); // render the centers
      }
    };
  },
});

// Function to handle the scanned barcode
function handle_scanned_barcode(frm, barcode) {
  // Get the list of products from the form
  var products = frm.doc.products || [];
  var found = false;

  // Iterate through the products to check if barcode matches
  for (var i = 0; i < products.length; i++) {
    var product = products[i];
    if (product.barcode === barcode) {
      found = true;
      break;
    }
  }

  // Display appropriate message based on barcode match
  if (found) {
    frappe.msgprint("Barcode matches a product in the list.");
  } else {
    frappe.msgprint("Barcode does not match any product in the list.");
  }
}

frappe.ui.form.on("Wooliz Order", {
  scan_barcode: (frm) => {
		const opts = {
			frm,
			items_table_name: 'products',
			qty_field: 'qty',
			max_qty_field: 'qty',
			dont_allow_new_row: true,
			prompt_qty: frm.doc.prompt_qty,
			serial_no_field: "not_supported",  // doesn't make sense for picklist without a separate field.
		};
		const barcode_scanner = new erpnext.utils.BarcodeScanner(opts);
		barcode_scanner.process_scan();
	},
  refresh: function(frm) {
      // Add a custom button to the toolbar
      frm.add_custom_button("Scan Barcode", function() {
          // Create a new scanner instance
          const scanner = new frappe.ui.Scanner({
              dialog: true, // open camera scanner in a dialog
              multiple: false, // stop after scanning one value
              on_scan(data) {
                  // Get the scanned barcode value
                  const scannedBarcode = data.decodedText;
                  
                  // Get the list of products from the form
                  const products = frm.doc.products || [];
                  
                  // Check if the scanned barcode matches any product
                  const matchingProduct = products.find(product => product.barcode === scannedBarcode);
                  
                  if (matchingProduct) {
                      // If a matching product is found, display a positive message
                      frappe.msgprint(`Product ${scannedBarcode} is valid.`);
                  } else {
                      // If no matching product is found, display a negative message
                      frappe.msgprint(`Product ${scannedBarcode} is not found in the list.`);
                  }
              }
          });
      });
  }
});




