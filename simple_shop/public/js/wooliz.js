document.addEventListener("DOMContentLoaded", function () {
    // Fetch data from the API
    fetch("/api/method/simple_shop.api.get_data")
      .then((response) => response.json())
      .then((data) => {
        // Get the ul element
        const ul = document.getElementById("wilayaList");
        const result = data["message"];

        let htmlContent = "";

        // Loop through the data and create li elements
        result.forEach((item) => {
          htmlContent += `<li class="search-suggestion__item js-search-select" data-wilaya="${item.id}" data-item-name="${item.id} ${item.name}" onclick="removeContentVisibleClass(this,'wilayaList');setDeleveryFees(this)">${item.id} ${item.name}</li>`;
        });
        ul.innerHTML = htmlContent;
      })
      .catch((error) => console.error("Error fetching data:", error));
    getCommunsList((has_stop_desk = true));
  });
  const getCommunsList = (has_stop_desk) => {
    // Check if data is already in localStorage

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
  }
  const getAllCommunsList = () => {
    let storedData = localStorage.getItem("allCommunsList");
    if (storedData) {
      let communs = JSON.parse(storedData);
      return communs
    }
    // If data is not in localStorage, fetch it from the API
    return fetch("/api/method/simple_shop.api.get_communs", {
      // Include any headers if needed
    })
      .then((response) => response.json())
      .then((data) => {
        let communs = data["message"]["communs"];
        // Store the data in localStorage for future use
        localStorage.setItem("allCommunsList", JSON.stringify(communs));
        return communs;
      })
      .catch((error) => {
        console.error("Error fetching or storing data:", error);
        throw error;
      });

  }
  const renderCommunsView = (element) => {
    let communs = getAllCommunsList();
    let baladiaUlList = document.getElementById("baladiaList");
    let wilayaID = element.getAttribute("data-wilaya");
    let homeShipping = document.getElementById("checkout_shipping_type_home");
    let officeShipping = document.getElementById("checkout_shipping_type_office");
    officeShipping.setAttribute("data-wilaya", wilayaID);
    homeShipping.setAttribute("data-wilaya", wilayaID);
    document.getElementById("communs-dropdown").value = "";
    let htmlContent = "";
    // Loop through the data and create li elements
    communs.forEach((item) => {
      if (item.wilaya_id == wilayaID)
        htmlContent += `<li class="search-suggestion__item js-search-select"  data-item-name="${item.name}" onclick="removeContentVisibleClass(this,'baladiaList')">${item.name}</li>`;
    });
    baladiaUlList.innerHTML = htmlContent;
  }

  const getCentresList = () => {
    let centers;
    const storedDataCenters = localStorage.getItem("centers");

    if (storedDataCenters) {
      centers = JSON.parse(storedDataCenters);
      return centers;
    }

    // If data is not in localStorage, fetch it from the API
    return fetch("/api/method/simple_shop.api.get_centers", {
      // Include any headers if needed
    })
      .then((response) => response.json())
      .then((data) => {
        centers = data["message"]["centers"];

        // Store the data in localStorage for future use
        localStorage.setItem("centers", JSON.stringify(centers));
        // Return the fetched data
        return centers;
      })
      .catch((error) => {
        console.error("Error fetching or storing data:", error);
        throw error;
      });
    console.log(centers);
  };

  const renderCentersListView = (element) => {
    let centers = getCentresList();
    let baladiaUlList = document.getElementById("baladiaList");
    let wilayaID = element.getAttribute("data-wilaya");
    let homeShipping = document.getElementById("checkout_shipping_type_home");
    let officeShipping = document.getElementById("checkout_shipping_type_office");
    officeShipping.setAttribute("data-wilaya", wilayaID);
    homeShipping.setAttribute("data-wilaya", wilayaID);
    document.getElementById("communs-dropdown").value = "";
    let htmlContent = "";
    // Loop through the data and create li elements
    centers.forEach((item) => {
      if (item.wilaya_id == wilayaID)
        htmlContent += `<li class="search-suggestion__item js-search-select" data-item-id="${item.center_id}"  data-item-name="${item.name}" onclick="removeContentVisibleClass(this,'baladiaList');setCurrentCenter(this)">${item.name}</li>`;
    });
    baladiaUlList.innerHTML = htmlContent;
  };


  const setCurrentCenter = (element) =>{
    let centerId = element.getAttribute("data-item-id");
    localStorage.setItem("currentCenter", centerId);
  }


  const fillCheckoutItems = (source) => {
  if (source === "global") {
    // Handle global source if needed in the future
  } else {
    // Retrieve existing cart items from local storage
    const existingCartItems = JSON.parse(localStorage.getItem("cartItems")) || [];

    // Get references to DOM elements
    const parentCartItemsCheckout = document.getElementById("checkout-cart-items");
    const subTotalCountElements = document.querySelectorAll(".sub-total-count");

    // Update subtotal and data attributes for each sub-total count element
    subTotalCountElements.forEach((subTotalElement) => {
      const cartTotalPrices = localStorage.getItem("cart-total-prices") || 0;
      subTotalElement.innerHTML = `DA ${cartTotalPrices} `;
      subTotalElement.setAttribute("data-subtotal", getSubTotal());
    });

    // Clear existing content in the checkout table
    parentCartItemsCheckout.innerHTML = "";

    // Populate checkout table with cart items
    existingCartItems.forEach((item) => {
      parentCartItemsCheckout.innerHTML += `
        <tr>
          <td>
            ${item.name} x ${item.qty}
          </td>
          <td>
            DA ${item.price * item.qty}
          </td>
        </tr>
      `;
    });
  }
};

  const setDeleveryFees = (element) => {
    if (element) {
      // select wilaya from user
      let wilaya_id = element.getAttribute("data-wilaya");
      localStorage.setItem("selected_wilaya", wilaya_id);
    }
    let shipping_fees = document.getElementById("shipping_fees");
    let storeddeleveryFeesData = localStorage.getItem("deleveryFees");
    let deleveryFees = JSON.parse(storeddeleveryFeesData);
    let checkout_shipping_type_home = document.getElementById(
      "checkout_shipping_type_home"
    );
    let checkout_shipping_type_office = document.getElementById(
      "checkout_shipping_type_office"
    );
    deleveryFees.forEach((e) => {
      if (e.wilaya_id == localStorage.getItem("selected_wilaya")) {
        checkout_shipping_type_home.setAttribute("data-fee", e.home_fee);
        checkout_shipping_type_office.setAttribute("data-fee", e.desk_fee);
        shipping_fees.innerHTML =
          getShippingTypeOption() === "checkout_shipping_type_home"
            ? `${e.home_fee} DA`
            : `${e.desk_fee} DA`;
        shipping_fees.setAttribute(
          "data-shipping-fee",
          getShippingTypeOption() === "checkout_shipping_type_home"
            ? e.home_fee
            : e.desk_fee
        );
      }
    });

    setCheckoutTotal();
  };

  const setCheckoutTotal = () => {
    let sub_total = document
      .getElementById("checkout-total-amount")
      .getAttribute("data-subtotal");
      console.log(sub_total);
    let shipping_fees = document
      .getElementById("shipping_fees")
      .getAttribute("data-shipping-fee");
    let totalAmount = document.getElementById("total-checkout-amount");
    totalAmount.innerHTML = `${
      parseFloat(sub_total) + parseFloat(shipping_fees)
    } DA`;
  };

  const getShippingTypeOption = () => {
    let checkedShippingType = document.querySelector(
      'input[name="checkout_shipping_type"]:checked'
    );
    return checkedShippingType.getAttribute("id");
  };

  const ToggleStreetInput = (option) => {
    /* Toggle display street address field input depending at shipping type*/
    let street = document.getElementById("checkout_street_address");
    const hidden =
      option == "hidden"
        ? street.classList.add("d-none")
        : street.classList.remove("d-none");
  };

  const sendRequest = (rawData) => {
    let myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");
    myHeaders.append("X-Frappe-CSRF-Token", frappe.csrf_token);

    let requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: JSON.stringify(rawData),
    };

    return fetch("/api/method/simple_shop.api.post_order", requestOptions)
      .then((response) => response.json()) // Parse JSON response
      .then((data) => {
        if (data.message.success) {
          const orderId = data.message.data.order_id;
          // remove cart items after successful processing
          localStorage.removeItem("cartItems");
          // Redirect to success page with order_id
          window.location.href = `/success_page/?id=${orderId}`;
        } else {
          // Handle other cases where success is not true if needed
          console.log("Request was not successful:", data);
        }
      })
      .catch((error) => {
        console.log("error", error);
        throw error; // Rethrow the error to be caught by the caller if needed
      });
  };

  const verifyOrderInputs = (orderData) => {
    const { lastName, phone, wilaya, commun } = orderData;

    const isEmpty = (value) => value.trim().length < 1;

    if (isEmpty(lastName.value)) {
      handleInvalidInput(lastName, "full name must be filled");
    } else if (isEmpty(phone.value) || phone.value.trim().length < 10) {
      handleInvalidInput(phone, "Phone number must be at least 10 characters");
    } else if (!wilaya.value.trim() || !commun.value.trim()) {
      handleInvalidInput(wilaya, "State and city must be provided");
    } else {
      handleValidInput([lastName, phone, wilaya, commun]);
      return [true, "order sent successfully"];
    }

    return [false, ""]; // Return a default error message for invalid cases

    function handleInvalidInput(element, errorMessage) {
      element.classList.add("is-invalid");
      element.classList.remove("is-valid");
      return [false, errorMessage];
    }

    function handleValidInput(elements) {
      elements.forEach((element) => {
        element.classList.remove("is-invalid");
        element.classList.add("is-valid");
      });
    }
  };

  const placeOrderItems = (element, orderType) => {
    element.preventDefault();

    // OrderType may be 'product' or 'cart' depending on the order type
    if (orderType === "product") {
      const checkoutStreetAddress = document.getElementById(
        "checkout_input_street_address"
      );
      const phoneField = document.getElementById("checkout_input_phone_field");
      const lastNameField = document.getElementById("checkout_last_name");
      const wilayaField = document.getElementById("wilaya-dropdown");
      const communField = document.getElementById("communs-dropdown");
      const shippingField = document.getElementById(
        "checkout_shipping_type_office"
      );

      let orderData = {
        lastName: lastNameField,
        phone: phoneField,
        wilaya: wilayaField,
        commun: communField,
      };
      const [success, msg] = verifyOrderInputs(orderData);
      console.log(success, msg);
      if (success) {
        orderData = {
          lastName: lastNameField.value,
          phone: phoneField.value,
          wilaya: wilayaField.value,
          commun: communField.value,
          product: "{{item.item_code}}",
          is_stop_desk: shippingField.checked,
          qty: 1,
          center_id: localStorage.getItem("currentCenter")
        };
        sendRequest(orderData);
      }
    }
  };

  document.getElementById("place_order").addEventListener("click", (e) => {
    placeOrderItems(e, "product");
  });
  //fillCheckoutItems();
  setCheckoutTotal();