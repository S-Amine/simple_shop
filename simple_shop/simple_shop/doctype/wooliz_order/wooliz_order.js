// Copyright (c) 2024, The Zoldycks and contributors
// For license information, please see license.txt
const getAllCommuns = async () => {
  let storedData = localStorage.getItem("allCommunsList");
  
  if (storedData) {
    let communs = JSON.parse(storedData);
    return communs;
  }

  try {
    // Fetch data from the local JSON file
    const response = await fetch("/assets/simple_shop/js/communes.json");
    const data = await response.json();
    
    let communs = data;
    
    // Store the data in localStorage for future use
    localStorage.setItem("allCommunsList", JSON.stringify(communs));
    
    return communs;
  } catch (error) {
    console.error("Error fetching or storing data:", error);
    throw error;
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

const renderCommunView =async (frm) => {
  var filteredCommuns = [];
  frm.set_df_property("commun", "options", ["loading..."]);
  let communs = await getAllCommuns();
  console.log(communs);
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
  scan_barcode: (frm) => {
		const opts = {
			frm,
			items_table_name: 'validation',
			qty_field: 'qty',
			max_qty_field: 'max_qty',
			dont_allow_new_row: true,
			prompt_qty: frm.doc.prompt_qty,
			serial_no_field: "not_supported",
		};
		const barcode_scanner = new erpnext.utils.BarcodeScanner(opts);
		barcode_scanner.process_scan();
	}
});