// Copyright (c) 2024, The Zoldycks and contributors
// For license information, please see license.txt

function getCommunsList(has_stop_desk,wilaya) {
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
    }
  }
function getCentersList() {
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
          if (item.wilaya_name === frm.selected_doc.wilaya) {
            centerOptions.push(item.name);
          }
        });
        frm.set_df_property("custom_center", "options", centerOptions);
}

const renderCommunView = (frm) => {
    var filteredCommuns = [];
    frm.set_df_property("commun", "options", ["loading..."]);
    let communs = getCommunsList((has_stop_desk = false))["communs"];
    communs.forEach((e) => {
      if (e.wilaya_name === frm.selected_doc.wilaya) {
        filteredCommuns.push(e.name);
      }
    });
    frm.set_df_property("commun", "options", filteredCommuns);
}
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
    console.log(frm.selected_doc.wilaya)
    // Fetch options for the wilaya field
    fetch("/api/method/simple_shop.api.get_data")
      .then((response) => response.json())
      .then((data) => {
        const result = data["message"];
        let options = [];
        result.forEach((item) => {
          options.push(item.name);
        });
        frm.set_df_property("wilaya", "options", options);

        renderCommunView(frm) // render the communs
        renderCentersView(frm) // render the centers
      })
      .catch((error) => console.error("Error fetching data:", error));

    frm.cscript.wilaya = function (doc, cdt, cdn) {
      // Get the current value of the wilaya field
      var wilayaValue = locals[cdt][cdn].wilaya;
      // Check if the wilaya field has changed
      if (wilayaValue) {
        renderCommunView(frm) // render the communs
        renderCentersView(frm) // render the centers
      }
    };
  },
});
